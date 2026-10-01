# Pad — Connection & Placement Guide

Use this to redraw the pad schematic by hand, one block per sheet, and later to place the PCB.
Every connection below comes from the first generated schematic (commit `3bca535`), which passes ERC.
The "Ref" column shows that schematic's references so you can cross-check; renumber freely when you redraw.

How to read the tables:

- **Parts**: what to put on the sheet.
- **Wiring**: each row is one pin and the net it belongs to. Everything with the same net name is wired together.
  Nets in **bold** leave the block (global labels / hierarchical pins); the rest stay inside the block.
- **Placement**: what has to sit next to what on the PCB, and why.

Net names used everywhere:

| Net | What it is |
|---|---|
| **GND** | Board ground (= battery pack negative after the protection FETs) |
| **POGO_5V** | 5 V from the dock through the pogo contacts (only when docked) |
| **VBAT** | Battery + (2 × 21700 in parallel, 3.3–4.2 V) |
| **PAD_SYS** | System rail after the power mux: ≈ 5 V docked, VBAT on battery |
| **+3V3** | 3.3 V made by the Pico (its 3V3 pin, max ≈ 300 mA) |
| **5V_RGB** | 5 V from the boost converter, LEDs only, switched off when not needed |

## Contents

1. [Dock interface (pogo)](#1-dock-interface-pogo)
2. [Battery, protection and charger](#2-battery-protection-and-charger)
3. [Power path and RGB boost](#3-power-path-and-rgb-boost)
4. [MCU (Pico 2 WH)](#4-mcu-pico-2-wh)
5. [Inputs (keys, encoders, selector)](#5-inputs-keys-encoders-selector)
6. [RGB LEDs](#6-rgb-leds)
7. [Display](#7-display)
8. [Signals that cross between blocks](#8-signals-that-cross-between-blocks)
9. [Board-wide rules](#9-board-wide-rules)
10. [Appendix: full net index](#appendix--full-net-index-generated)

## The whole pad at a glance

```text
 DOCK ══ pogo ══► [1 Dock interface] ── POGO_5V ──┬──► [2 Charger TP4056] ── VBAT ──► battery 2×21700
                        │ UART                     │                          │   (DW01A + FS8205A)
                        │                          └──► [3 Power mux TPS2116] ◄┘
                        ▼                                       │ PAD_SYS
                  [4 Pico 2 WH] ◄───────────────────────────────┤
                        │ +3V3                                  └──► [3 Boost TPS61023] ── 5V_RGB ──► [6 36 LEDs]
                        ├──► [5 Inputs: TCA9555, 12 keys, 2 encoders, selector]
                        └──► [7 OLED + load switch]
```

Each sketch below is only a reading aid: `●` is a junction, `─` a wire, `→`/`←` show which way a signal goes. The tables under each sketch are the exact reference.

---

## 1. Dock interface (pogo)

The pogo connector lives on a **separate small pogo board** mounted vertically in the pad's back wall (DESIGN.md §15), because the main board is sloped. A 4-wire cable links it to the main board.

### 1a. Pogo board (its own small PCB and schematic, `hardware/pogo/`)

Cable order (same on both boards, straight-through): **1 GND, 2 POGO_DRX, 3 POGO_DTX, 4 POGO_5V**.

**7 contacts since the v2 dock review:** +5V and GND each on two contacts (rated 1 A per contact), so the dock can supply ≈ 1.45 A and the pad needs no LED dimming while docked. Since 2026-10-01 +5V sits at **both ends** (pins 2 and 6), like GND (pins 1 and 7): the order is mirror-symmetric for power, so a pad docked the wrong way round is still powered correctly; only the UART lines cross (through 1 kΩ, harmless).

```text
 J1 pin 1 ─────────── GND ──► J2 pin 1
 J1 pins 2, 6 (+5V) ──●── POGO_5V (labels) ──► J2 pin 4
                      └── D1 SMAJ5.0A cathode (pin 1, K); anode (pin 2, A) ── GND
 J1 pin 3 (dock TX) ──●── POGO_DTX ──► J2 pin 3 ──(cable)──► main board → 1k → PAD_UART_RX (Pico GP1)
                      └── U1 pin 4 (ESD clamp to GND)
 J1 pin 4 (dock RX) ──●── POGO_DRX ◄── J2 pin 2 ◄─(cable)─── main board ← 1k ← PAD_UART_TX (Pico GP0)
                      └── U1 pin 1 (ESD clamp to GND)
 J1 pin 5 (DET) ───── GND           (this tells the dock to switch its 5 V on)
 J1 pin 7 ─────────── GND
 U1 pin 2 ─── GND;  U1 pins 3, 6: no-connect flags (unused channels);  U1 pin 5: NC
 H1, H2: M2 mounting holes, no connection
```

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| J1 | Pogo connector, 7 pin, 90° with ears (pad half of the Motorobit set) | Pogo 7-pin | `dock:Pogo-7` | Contacts to the dock |
| D1 | TVS diode (unidirectional) | SMAJ5.0A | D_SMA | Clamps spikes on POGO_5V |
| U1 | ESD array | TPD4E1U06DBVR | SOT-23-6 | ESD on the two data contacts |
| J2 | JST-XH 4 pin | Cable | JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical | To the main board |
| H1, H2 | Mounting hole | M2 | MountingHole_2.2mm_M2 | Screws to the back wall |

| Part.pin | Net | Also on this net |
|---|---|---|
| J1.1, J1.5 (DET), J1.7 | GND | D1.2 (A), U1.2, J2.1 |
| J1.2, J1.6 | POGO_5V | D1.1 (K), J2.4 |
| J1.3 (dock's TX contact) | POGO_DTX | U1.4, J2.3 |
| J1.4 (dock's RX contact) | POGO_DRX | U1.1, J2.2 |
| U1.3, U1.6 | not connected (no-connect flags) | unused ESD channels |
| U1.5 | NC | |

Add a PWR_FLAG on GND (and one on POGO_5V) so ERC knows the connectors supply them.

Pin order on the pad is the mirror of the dock's (`GND | +5V | DET | RX | TX | +5V | GND`): `GND | +5V | TX | RX | DET | +5V | GND`.
**Orientation check (3D design):** mated face to face, pad pin 1 meets dock pin 7. Reversed, +5V still meets +5V and GND meets GND (both ends), so nothing is damaged and the pad is still powered; only the pogo UART won't work. Mark pin 1 on the silkscreen and on the case anyway.

**Placement (pogo board)**

- J1 on the board edge, its face flush with the back wall at the height of the dock's pogo connector (J601 on the v2 dock); magnets beside it (mechanical). Its position is part of the pad redesign.
- POGO_5V to both J1 pins 2 and 6 with a wide trace (they're at opposite ends); D1 near the +5V pins, U1 right at J1 pins 3–4.
- J2 on the inner side, where the cable leaves.
- H1/H2 to fix the board to the wall; the wall takes the docking forces.
- POGO_5V and GND traces ≥ 0.6 mm.

### 1b. Main board side (your schematic: J1, R32, R33, C56)

```text
 J1 pin 1 ─── GND
 J1 pin 2 ─── POGO_DRX ── R33 1k ◄── PAD_UART_TX ◄── Pico GP0
 J1 pin 3 ─── POGO_DTX ── R32 1k ──► PAD_UART_RX ──► Pico GP1
 J1 pin 4 ──●── POGO_5V ──► charger, power mux
            └── C56 10 µF ── GND
```

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| J1 | JST-XH 4 pin, side entry (S4B-XH-A) | Pogo cable | JST_XH_S4B-XH-A_1x04_P2.50mm_Horizontal | From the pogo board |
| C56 | Capacitor | 10 µF | 0805 | POGO_5V bulk |
| R32 | Resistor | 1 kΩ | 0805 | Series, dock TX → pad RX |
| R33 | Resistor | 1 kΩ | 0805 | Series, pad TX → dock RX |

**Placement (main board)**

- J1 at the main board's back edge, nearest the pogo board. C56 right at J1 pin 4.
- R32/R33 anywhere between J1 and the Pico.

---

## 2. Battery, protection and charger

```text
 Charger
 POGO_5V ──●────────────── U2 pin 4 VCC          U2 pin 5 BAT ──●── VBAT ──► battery +, power mux
           ├── C2 10 µF ── GND                                   └── C3 10 µF ── GND
           ├── R8 100k ──●── U2 pin 8 CE
           │             └── Q2 drain   (Q2: gate = CHG_INHIBIT ← Pico GP18, R9 100k to GND; source = GND)
           └── R3 5.6k ──●── U2 pin 1 TEMP
                         ├── R4 75k ── GND
                         └── J2 NTC ── GND
 U2 pin 2 PROG ──●── R5 8.2k ── GND
                 └── R6 3.3k ── Q1 drain (Q1: gate = CHG_FAST ← Pico GP17, R7 100k to GND; source = GND)
 U2 pin 7 CHRG  ──●── CHG_CHRG_N  ──► Pico GP19      (R10 10k to +3V3)
 U2 pin 6 STDBY ──●── CHG_STDBY_N ──► Pico GP20      (R11 10k to +3V3)
 U2 pins 3, 9 ─── GND

 Protection (sits in the battery's negative lead)
 J3 pin 1 (battery +) ── VBAT ── R12 100 Ω ──●── DW_VCC ── U3 pin 5 VCC
                                             └── C4 100 nF ── CELL_N
 J3 pin 2 (battery −) ── CELL_N ──●── U3 pin 6 GND
                                  └── Q3 S1 (pins 2,3) ═[FET 1]═ drain ═[FET 2]═ Q3 S2 (pins 6,7) ── GND
                                           gate G1 (pin 4) ← U3 pin 1 OD    gate G2 (pin 5) ← U3 pin 3 OC
 U3 pin 2 CS ── R13 1k ── GND

 Battery sense
 VBAT ── R14 100k ──●── VBAT_SENSE ──► Pico GP26
                    ├── R15 100k ── GND
                    └── C5 100 nF ── GND
```

**Parts**

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| J3 | JST-XH 2 pin, side entry (S2B-XH-A) | Battery | JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal | Battery holder leads (1 = +, 2 = −) |
| J2 | JST-XH 2 pin, side entry (S2B-XH-A) | NTC | JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal | 10 k B3950 thermistor taped between the cells |
| U2 | Li-ion charger | TP4056 | `dock:SOIC-8-1EP_3.9x4.9mm_HandSolder` (1 mm hole in the pad, solder it from the top) | Charges the battery from POGO_5V |
| C2 | Capacitor | 10 µF | 0805 | Charger input |
| C3 | Capacitor | 10 µF | 0805 | Charger output / battery |
| R3 | Resistor | 5.6 kΩ | 0805 | NTC divider top |
| R4 | Resistor | 75 kΩ | 0805 | NTC divider, parallel to the NTC |
| R5 | Resistor | 8.2 kΩ | 0805 | Charge current, slow (≈ 146 mA) |
| R6 | Resistor | 3.3 kΩ | 0805 | Adds fast current (≈ 510 mA total) |
| Q1 | N-MOSFET | 2N7002 | SOT-23 | Switches R6 in (CHG_FAST) |
| R7 | Resistor | 100 kΩ | 0805 | Q1 gate pull-down (slow by default) |
| Q2 | N-MOSFET | 2N7002 | SOT-23 | Pulls CE low (stops charging) |
| R8 | Resistor | 100 kΩ | 0805 | CE pull-up to POGO_5V (charging on by default) |
| R9 | Resistor | 100 kΩ | 0805 | Q2 gate pull-down |
| R10 | Resistor | 10 kΩ | 0805 | CHRG pull-up |
| R11 | Resistor | 10 kΩ | 0805 | STDBY pull-up |
| U3 | Protection IC | DW01A | SOT-23-6 | Watches the cell |
| Q3 | Dual N-MOSFET | FS8205A | TSSOP-8 | Cuts the battery − lead on a fault |
| R12 | Resistor | 100 Ω | 0805 | DW01A supply filter |
| C4 | Capacitor | 100 nF | 0805 | DW01A supply filter |
| R13 | Resistor | 1 kΩ | 0805 | DW01A current sense |
| R14 | Resistor | 100 kΩ | 0805 | Battery sense divider top |
| R15 | Resistor | 100 kΩ | 0805 | Battery sense divider bottom |
| C5 | Capacitor | 100 nF | 0805 | Battery sense filter |

**Wiring — charger (U2 TP4056)**

| U2 pin | Net | Also on this net |
|---|---|---|
| 1 TEMP | CHG_TEMP | R3.2, R4.1, J2.1 (NTC) |
| 2 PROG | CHG_PROG | R5.1, R6.1 |
| 3 GND | GND | — |
| 4 VCC | **POGO_5V** | C2.1, R3.1, R8.1 |
| 5 BAT | **VBAT** | C3.1, J3.1, R12.1, R14.1, mux VIN2 |
| 6 STDBY | **CHG_STDBY_N** | R11.2, Pico GP20 |
| 7 CHRG | **CHG_CHRG_N** | R10.2, Pico GP19 |
| 8 CE | CHG_CE | R8.2, Q2 drain |
| 9 exposed pad | GND | — |

| Part | Pin 1 / top | Pin 2 / bottom |
|---|---|---|
| C2 | POGO_5V | GND |
| C3 | VBAT | GND |
| R3 | POGO_5V | CHG_TEMP |
| R4 | CHG_TEMP | GND |
| J2 (NTC) | CHG_TEMP | GND |
| R5 | CHG_PROG | GND |
| R6 | CHG_PROG | CHG_PROG_SW |
| Q1 | gate = **CHG_FAST** (Pico GP17), drain = CHG_PROG_SW, source = GND | |
| R7 | CHG_FAST | GND |
| R8 | POGO_5V | CHG_CE |
| Q2 | gate = **CHG_INHIBIT** (Pico GP18), drain = CHG_CE, source = GND | |
| R9 | CHG_INHIBIT | GND |
| R10 | +3V3 | CHG_CHRG_N |
| R11 | +3V3 | CHG_STDBY_N |

**Wiring — protection (U3 DW01A + Q3 FS8205A)**

CELL_N is the battery's own negative; GND is the board ground. The two FETs sit between them.

| Part.pin | Net | Also on this net |
|---|---|---|
| J3.1 (battery +) | **VBAT** | charger BAT, R12.1, R14.1 |
| J3.2 (battery −) | CELL_N | U3.6, Q3.2, Q3.3, C4.2 |
| U3.5 VCC | DW_VCC | R12.2, C4.1 |
| U3.6 GND | CELL_N | — |
| U3.2 CS | DW_CS | R13.1 |
| U3.1 OD | DW_OD | Q3.4 (G1, discharge FET) |
| U3.3 OC | DW_OC | Q3.5 (G2, charge FET) |
| U3.4 TD | not connected | |
| Q3.2, Q3.3 (S1) | CELL_N | |
| Q3.6, Q3.7 (S2) | GND | |
| Q3.1, Q3.8 (common drain) | FET_D12 | only each other (no other connection) |
| R13.2 | GND | |

**Wiring — battery sense**

| Part | Pin 1 | Pin 2 |
|---|---|---|
| R14 | VBAT | VBAT_SENSE |
| R15 | VBAT_SENSE | GND |
| C5 | VBAT_SENSE | GND |

VBAT_SENSE goes to Pico GP26 (ADC0) and reads VBAT / 2.

**Placement**

- **U2 TP4056**: near J1/POGO_5V. It gets warm (≈ 0.65 W at 510 mA), so give the exposed pad a solid GND copper area with several vias to the bottom GND plane (and the hand-solder hole). Keep it away from the battery holder and the NTC.
- C2 at U2 pin 4, C3 at U2 pin 5: within 2–3 mm.
- R5/R6/Q1 right at U2 pin 2 (PROG). The PROG trace must be short and not run next to noisy traces.
- R3/R4 near U2 pin 1. J2 goes where the NTC wires arrive, near J3.
- Q2/R8/R9 and R10/R11 near U2; their other ends are just Pico GPIOs.
- **U3 + Q3 + J3 as one tight group** where the battery leads land. The path J3.2 → Q3 → GND carries all battery current: traces ≥ 1 mm. VBAT from J3.1 to U2/mux also ≥ 1 mm.
- R12/C4 right at U3 pin 5; R13 right at U3 pin 2.
- R14/R15/C5: anywhere on the way to the Pico; put C5 close to the Pico's GP26 pin.

---

## 3. Power path and RGB boost

```text
 Power mux
 POGO_5V ──●── U4 pin 3 VIN1 and U4 pin 5 MODE
           └── R16 300k ──●── U4 pin 4 PR1
                          └── R17 100k ── GND
 VBAT ─────●── U4 pin 6 VIN2
           └── C6 1 µF ── GND
 U4 pins 2 and 7 VOUT ── PAD_SYS ──●── C7, C8 10 µF ── GND
                                   ├──► Pico VSYS
                                   └──► boost input (below)
 U4 pin 8 ST ── DOCKED ──●──► Pico GP21
                         └── R18 10k ── +3V3

 Boost (PAD_SYS → 5V_RGB)
 PAD_SYS ──●── U5 pin 3 VIN
           ├── C9 10 µF ── GND
           └── L1 1 µH ── BOOST_SW ── U5 pin 5 SW
 U5 pin 6 VOUT ── 5V_RGB ──●── C10, C11 22 µF ── GND
                           ├── R20 750k ──●── U5 pin 1 FB
                           │              └── R21 100k ── GND
                           └──► level shifter and LEDs
 Pico GP16 ── RGB_EN ──●── U5 pin 2 EN
                       └── R19 100k ── GND
 U5 pin 4 ── GND
```

**Parts**

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| U4 | Power mux | TPS2116DRL | `dock:SOT-583-8_HandSolder` | Chooses POGO_5V or VBAT |
| R16 | Resistor | 300 kΩ | 0805 | Switchover divider top (≈ 4.0 V) |
| R17 | Resistor | 100 kΩ | 0805 | Switchover divider bottom |
| C6 | Capacitor | 1 µF | 0805 | VIN2 (battery side) |
| C7, C8 | Capacitor | 10 µF | 0805 | PAD_SYS |
| R18 | Resistor | 10 kΩ | 0805 | ST pull-up (DOCKED) |
| U5 | Boost converter | TPS61023DRLR | `dock:SOT-563-6_HandSolder` | PAD_SYS → 5V_RGB |
| L1 | Inductor | 1 µH, Isat ≥ 4.5 A | 4 × 4 mm | Boost inductor |
| C9 | Capacitor | 10 µF | 1206 | Boost input |
| C10, C11 | Capacitor | 22 µF, ≥ 16 V | 1206 | Boost output |
| R19 | Resistor | 100 kΩ | 0805 | EN pull-down (LEDs off at boot) |
| R20 | Resistor | 750 kΩ | 0805 | Feedback top |
| R21 | Resistor | 100 kΩ | 0805 | Feedback bottom |

**Wiring — U4 TPS2116**

| U4 pin | Net | Also on this net |
|---|---|---|
| 1 GND | GND | — |
| 2 VOUT, 7 VOUT (hidden) | **PAD_SYS** | C7, C8, C9, L1.1, U5 VIN, Pico VSYS |
| 3 VIN1 | **POGO_5V** | R16.1, U4.5 |
| 4 PR1 | MUX_PR1 | R16.2, R17.1 |
| 5 MODE | **POGO_5V** | (tied to VIN1, as on the dock) |
| 6 VIN2 | **VBAT** | C6.1 |
| 8 ST | **DOCKED** | R18.2, Pico GP21 |

R17.2 → GND. R18.1 → +3V3.

**Wiring — U5 TPS61023**

| U5 pin | Net | Also on this net |
|---|---|---|
| 1 FB | BOOST_FB | R20.2, R21.1 |
| 2 EN | **RGB_EN** | R19.1, Pico GP16 |
| 3 VIN | **PAD_SYS** | C9.1, L1.1 |
| 4 GND | GND | — |
| 5 SW | BOOST_SW | L1.2 |
| 6 VOUT | **5V_RGB** | C10.1, C11.1, R20.1, LEDs, level shifter |

R19.2, R21.2, C9.2, C10.2, C11.2 → GND.

**Placement**

- U4 between the charger/battery area and the Pico. C6 at pin 6, C7/C8 at pins 2/7, R16/R17 at pin 4.
- **U5 boost is the one layout-critical block** (1 MHz switching, amps of current):
  - C9 between U5 VIN and GND, as close as possible.
  - L1 right next to U5 pin 5 (SW). Keep the SW copper small; no signal traces under or next to it.
  - C10/C11 between U5 VOUT and GND, as close as possible, with GND of C9/C10/C11/U5 joined on top copper and stitched with several vias.
  - R20/R21 right at U5 pin 1 (FB), on the side away from L1.
- Put the boost near where 5V_RGB feeds the LEDs; 5V_RGB and PAD_SYS traces ≥ 0.6 mm.

---

## 4. MCU (Pico 2 WH)

**Parts**

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| A1 | Raspberry Pi Pico 2 WH | — | `dock:RaspberryPi_Pico2W_Socket_NoSWD` | MCU + BLE, socketed |

No SWD header on the pad: the footprint's SWD holes would land under key 5's centre post. Debug with a probe on the Pico 2 WH's own 3-pin JST-SH connector (bottom cover off).

**Wiring — A1**

| Pico pin | GPIO / name | Net | Goes to |
|---|---|---|---|
| 1 | GP0 | **PAD_UART_TX** | R33 (pogo) |
| 2 | GP1 | **PAD_UART_RX** | R32 (pogo) |
| 4 | GP2 | **ENC1_A** | encoder 1 A, R25, C13 |
| 5 | GP3 | **ENC1_B** | encoder 1 B, R26, C14 |
| 6 | GP4 | **I2C_SDA** | TCA9555 SDA, R22 |
| 7 | GP5 | **I2C_SCL** | TCA9555 SCL, R23 |
| 9 | GP6 | **ENC2_A** | encoder 2 A, R27, C15 |
| 10 | GP7 | **ENC2_B** | encoder 2 B, R28, C16 |
| 11 | GP8 | **TCA_INT_N** | TCA9555 INT, R24 |
| 12 | GP9 | **RGB_DATA_3V3** | level shifter input |
| 14 | GP10 | **OLED_SCK** | OLED pin 3 |
| 15 | GP11 | **OLED_MOSI** | OLED pin 4 |
| 16 | GP12 | **OLED_DC** | OLED pin 6 |
| 17 | GP13 | **OLED_CS** | OLED pin 7 |
| 19 | GP14 | **OLED_RES** | OLED pin 5 |
| 20 | GP15 | not connected | (1×19 socket possible) |
| 21 | GP16 | **RGB_EN** | boost EN, R19 |
| 22 | GP17 | **CHG_FAST** | Q1 gate, R7 |
| 24 | GP18 | **CHG_INHIBIT** | Q2 gate, R9 |
| 25 | GP19 | **CHG_CHRG_N** | charger CHRG, R10 |
| 26 | GP20 | **CHG_STDBY_N** | charger STDBY, R11 |
| 27 | GP21 | **DOCKED** | mux ST, R18 |
| 29 | GP22 | **OLED_EN** | load switch ON, R30 |
| 30 | RUN | not connected | |
| 31 | GP26 / ADC0 | **VBAT_SENSE** | battery divider |
| 32 | GP27 | **OLED_BLK** | backlight MOSFET gate (Q4), R34 |
| 34 | GP28 | not connected | spare ADC pin |
| 33 | AGND | GND | |
| 35 | ADC_VREF | not connected | |
| 36 | 3V3 | **+3V3** | everything on 3.3 V |
| 37 | 3V3_EN | not connected | (internal pull-up) |
| 39 | VSYS | **PAD_SYS** | mux output |
| 40 | VBUS | not connected | |
| 3, 8, 13, 18, 23, 28, 38 | GND | GND | |
| D1–D3, TP1–TP6 | SWD / test pads | not connected | (copper-only placeholders in the footprint) |

**Placement**

- The Pico's **antenna end** (away from USB) at a board edge with no copper, battery, metal screws or encoder bodies in or near the keep-out; the enclosure wall there must be plastic.
- USB end reachable if possible (flashing with the case open).
- Keep the Pico central to the key area and encoders; its GPIO rows face the TCA9555 and the OLED connector.

---

## 5. Inputs (keys, encoders, selector)

```text
 +3V3 ── R22 4.7k ──●── I2C_SDA ── U6 pin 23 SDA ◄──► Pico GP4
 +3V3 ── R23 4.7k ──●── I2C_SCL ── U6 pin 22 SCL ◄── Pico GP5
 +3V3 ── R24 10k ───●── TCA_INT_N ── U6 pin 1 INT ──► Pico GP8
 +3V3 ── U6 pin 24 VCC (C12 100 nF to GND);  U6 pins 12, 21, 2, 3 ── GND

 U6 port ── KEYn ── SWn ── GND                  (×12, P00–P07 then P10–P13)

 Encoder (×2)
 +3V3 ── R 10k ──●── ENCx_A ──► Pico     encoder pin A
                 └── C 10 nF ── GND
 +3V3 ── R 10k ──●── ENCx_B ──► Pico     encoder pin B
                 └── C 10 nF ── GND
 encoder pin C ── GND;  S1 ── ENCx_SW ── U6 P14/P15;  S2 ── GND

 Selector: J5 pin 1 ── SEL_A ── U6 P16;  J5 pin 2 ── GND (toggle common);  J5 pin 3 ── SEL_B ── U6 P17
```

**Parts**

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| U6 | I/O expander | TCA9555PWR | TSSOP-24 | Reads 12 keys, 2 encoder pushes, selector |
| C12 | Capacitor | 100 nF | 0805 | U6 supply |
| R22, R23 | Resistor | 4.7 kΩ | 0805 | I2C pull-ups (SDA, SCL) |
| R24 | Resistor | 10 kΩ | 0805 | INT pull-up |
| SW1–SW12 | Key switch | Razer Yellow (MX) | `dock:SW_MX_Hotswap_Kailh` | Keys 1–12 |
| SW13, SW14 | Rotary encoder + push | PEC11R-4220F-S0024 | `dock:RotaryEncoder_Bourns_PEC11R-4xxxF-S_Vertical` | Encoder 1 (volume), 2 (mic) |
| R25–R28 | Resistor | 10 kΩ | 0805 | Encoder A/B pull-ups |
| C13–C16 | Capacitor | 10 nF | 0805 | Encoder A/B debounce |
| J5 | JST-XH 3 pin | Selector | JST_XH_B3B | PERSONAL/OFF/WORK toggle wires |

The TCA9555 has internal 100 k pull-ups, so keys, encoder pushes and the selector need no resistors: each one just shorts its input to GND.

**Wiring — U6 TCA9555**

| U6 pin | Name | Net | Goes to |
|---|---|---|---|
| 24 | VCC | **+3V3** | C12 |
| 12 | GND | GND | |
| 21, 2, 3 | A0, A1, A2 | GND | address 0x20 |
| 23 | SDA | **I2C_SDA** | Pico GP4, R22 |
| 22 | SCL | **I2C_SCL** | Pico GP5, R23 |
| 1 | INT | **TCA_INT_N** | Pico GP8, R24 |
| 4–11 | P00–P07 | KEY1–KEY8 | SW1–SW8 pin 1 |
| 13–16 | P10–P13 | KEY9–KEY12 | SW9–SW12 pin 1 |
| 17 | P14 | ENC1_SW | SW13 S1 |
| 18 | P15 | ENC2_SW | SW14 S1 |
| 19 | P16 | SEL_A | J5.1 |
| 20 | P17 | SEL_B | J5.3 |

**Wiring — switches, encoders, selector**

| Part.pin | Net |
|---|---|
| SWn.1 | KEYn (n = 1…12) |
| SWn.2 | GND |
| SW13 A / B / C | ENC1_A / ENC1_B / GND |
| SW13 S1 / S2 | ENC1_SW / GND |
| SW14 A / B / C | ENC2_A / ENC2_B / GND |
| SW14 S1 / S2 | ENC2_SW / GND |
| R25 / R26 | +3V3 → ENC1_A / ENC1_B |
| R27 / R28 | +3V3 → ENC2_A / ENC2_B |
| C13 / C14 | ENC1_A / ENC1_B → GND |
| C15 / C16 | ENC2_A / ENC2_B → GND |
| R22 / R23 / R24 | +3V3 → I2C_SDA / I2C_SCL / TCA_INT_N |
| J5.1 / J5.2 / J5.3 | SEL_A / GND (toggle common) / SEL_B |

Selector states (DESIGN.md §8.3): SEL_A low = PERSONAL, SEL_B low = WORK, both high = OFF.

**Placement**

- Keys on a 19.05 mm grid, 4 × 3. Hot-swap sockets are on the **bottom**; each key also gets an LED cutout (section 6).
- U6 between the key grid and the Pico so the 12 key traces stay short; C12 at pin 24.
- Encoders where the enclosure puts the knobs (DESIGN.md §17: above the key grid, display between them). C13–C16 close to the encoder pins; R25–R28 anywhere on the way.
- J5 near where the toggle mounts on the case.
- I2C pull-ups near U6 or the Pico, either is fine.

---

## 6. RGB LEDs

```text
 Pico GP9 ── RGB_DATA_3V3 ── U7 pin 2 A     U7 pin 4 Y ── R29 47 Ω ── LED 1 DIN
 U7 pin 1 OE and pin 3 ── GND;  U7 pin 5 VCC ── 5V_RGB (C17 100 nF to GND)

 LED 1 DOUT ──► LED 2 DIN ──► LED 3 DIN ──► … ──► LED 36 DIN      (LED 36 DOUT open)
 every LED: VDD ── 5V_RGB (own 100 nF to GND), VSS ── GND
```

**Parts**

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| U7 | Buffer | 74AHCT1G125 | SOT-23-5 | 3.3 V data → 5 V data |
| C17 | Capacitor | 100 nF | 0805 | U7 supply |
| R29 | Resistor | 47 Ω | 0805 | Data series resistor |
| D2–D37 | LED | SK6812MINI-E ×36 | `LED_SK6812MINI-E…ReverseMount` | 12 keys + 2 rings of 12 |
| C18–C53 | Capacitor | 100 nF ×36 | 0805 | One per LED |

**Wiring**

| Part.pin | Net | Goes to |
|---|---|---|
| U7.1 (OE, active low) | GND | always enabled |
| U7.2 (A) | **RGB_DATA_3V3** | Pico GP9 |
| U7.3 | GND | |
| U7.4 (Y) | RGB_BUF | R29.1 |
| U7.5 | **5V_RGB** | C17 |
| R29.2 | LED_DIN1 | first LED DIN |
| LED k: VDD (3) | **5V_RGB** | its own 100 nF |
| LED k: VSS (1) | GND | |
| LED k: DIN (2) | LED_DINk | previous LED's DOUT (or R29 for the first) |
| LED k: DOUT (4) | LED_DIN(k+1) | next LED's DIN; last LED's DOUT not connected |

It's one chain: R29 → LED 1 → LED 2 → … → LED 36. Only the order matters, so choose it at layout (for example keys 1–12, then ring 1, then ring 2) and number the LEDs to match.

**Placement**

- Each LED's 100 nF within ≈ 2 mm of its VDD pin.
- Key LEDs: reverse-mounted in a cutout under each switch's LED lens (MX LED window side).
- Ring LEDs: 12 on a circle around each encoder shaft, **12 mm radius** (just outside a 20 mm knob), so each ring is ≈ 27 mm across. Keep 2 mm to the display area.
- U7 + R29 near the first LED; R29 right at U7 pin 4. The 3.3 V data trace from the Pico can be long.
- Route the chain in one continuous path; keep 5V_RGB ≥ 0.6 mm to the rings and keys, branches can be thinner.

---

## 7. Display

1.69" 240 × 280 colour IPS TFT, ST7789 (Meon Otomasyon), on a 9-wire JST-PH cable (pin 9 = second GND). The pin order below is the usual one for these modules, **check it on your module** and wire the cable to match.

```text
 +3V3 ──●── U8 pin 1 IN               U8 pin 6 OUT ──●── OLED_VCC ──● J7 pin 2 (VCC)
        └── C54 1 µF ── GND                          ├── C55 1 µF ── GND
 Pico GP22 ── OLED_EN ──●── U8 pin 3 ON              ├── R31 100 Ω ── U8 pin 5 QOD
                        └── R30 100k ── GND          ├── Q4 source (AO3401A, P-MOSFET)
 U8 pin 2 ── GND                                     └── R34 10k ──●── Q4 gate ◄── OLED_BLK ◄── Pico GP27
                                                     Q4 drain ── J7 pin 8 (BLK)
 J7: 1 GND, 3 SCL ← GP10, 4 SDA ← GP11, 5 RES ← GP14, 6 DC ← GP12, 7 CS ← GP13, 9 GND (second ground)
```

**Parts**

| Ref | Part | Value | Footprint | Job |
|---|---|---|---|---|
| U8 | Load switch | TPS22919DCK | SC-70-6 | Switches the display's power |
| C54 | Capacitor | 1 µF | 0805 | U8 input |
| C55 | Capacitor | 1 µF | 0805 | U8 output |
| R30 | Resistor | 100 kΩ | 0805 | ON pull-down (display off at boot) |
| R31 | Resistor | 100 Ω | 0805 | Quick-discharge resistor |
| Q4 | P-MOSFET | AO3401A | SOT-23 | Switches/dims the backlight (≈ 41 mA) |
| R34 | Resistor | 10–100 kΩ | 0805 | Q4 gate pull-up (gate to OLED_VCC): backlight off by default |
| J7 | JST-PH 9 pin, side entry (S9B-PH-K-S) | Display cable | JST_PH_S9B-PH-K_1x09_P2.00mm_Horizontal | 9-wire cable to the display in the case window |

**Wiring**

| Part.pin | Net | Goes to |
|---|---|---|
| U8.1 IN | **+3V3** | C54 |
| U8.2 GND | GND | |
| U8.3 ON | **OLED_EN** | Pico GP22, R30 |
| U8.4 NC | not connected | |
| U8.5 QOD | OLED_QOD | R31.2 |
| U8.6 OUT | OLED_VCC | C55, R31.1, J7.2, Q4 source, R34.1 |
| Q4 gate | **OLED_BLK** | Pico GP27, R34.2 |
| Q4 drain | OLED_BLK_OUT | J7.8 |
| J7.1 | GND | module GND |
| J7.2 | OLED_VCC | module VCC |
| J7.3 | **OLED_SCK** | Pico GP10 (module pin "SCL") |
| J7.4 | **OLED_MOSI** | Pico GP11 (module pin "SDA") |
| J7.5 | **OLED_RES** | Pico GP14 |
| J7.6 | **OLED_DC** | Pico GP12 |
| J7.7 | **OLED_CS** | Pico GP13 |
| J7.8 | OLED_BLK_OUT | module BLK |
| J7.9 | GND | second ground wire, soldered to the module's GND pad too |

GP27 low = backlight on; PWM on GP27 dims it (inverted: higher duty cycle = dimmer).

**Placement**

- The display itself is mounted to the case behind its window (between the encoders) and reaches J7 through a ≈ 10 cm 9-wire JST-PH cable; its bare end is soldered to the module pads. Measure the module's outline, window and holes for the case.
- J7 anywhere near the display area of the board, oriented so the cable runs straight up to the module.
- U8, C54/C55, R31, Q4 and R34 near J7.

---

## 8. Signals that cross between blocks

| Net | From | To |
|---|---|---|
| POGO_5V | Pogo J1.5 | charger VCC, CE pull-up, NTC divider, mux VIN1/MODE/PR1 divider |
| VBAT | Battery J3.1 / charger BAT | mux VIN2, DW01A supply, battery sense |
| PAD_SYS | Mux VOUT | Pico VSYS, boost VIN + inductor |
| +3V3 | Pico 3V3 | TCA9555, all pull-ups, OLED switch |
| 5V_RGB | Boost VOUT | level shifter, 36 LEDs |
| PAD_UART_TX / RX | Pico GP0 / GP1 | pogo series resistors |
| GND, POGO_DRX, POGO_DTX, POGO_5V (cable pins 1–4) | Pogo board J2 | main board J1 (4-wire cable) |
| I2C_SDA / I2C_SCL | Pico GP4 / GP5 | TCA9555 |
| TCA_INT_N | TCA9555 INT | Pico GP8 |
| ENC1_A/B, ENC2_A/B | Encoders | Pico GP2/GP3, GP6/GP7 |
| RGB_DATA_3V3 | Pico GP9 | level shifter |
| RGB_EN | Pico GP16 | boost EN |
| CHG_FAST / CHG_INHIBIT | Pico GP17 / GP18 | charger MOSFET gates |
| CHG_CHRG_N / CHG_STDBY_N | Charger | Pico GP19 / GP20 |
| DOCKED | Mux ST | Pico GP21 |
| OLED_EN | Pico GP22 | load switch ON |
| OLED_BLK | Pico GP27 | backlight MOSFET gate (Q4), pull-up R34 |
| OLED_SCK/MOSI/DC/CS/RES | Pico GP10/11/12/13/14 | OLED socket |
| VBAT_SENSE | Battery divider | Pico GP26 |

## 9. Board-wide rules

- 2 layers, bottom = GND pour (as on the dock). Hot-swap sockets and reverse-mount LEDs also live on the bottom side, so keep the pour stitched around them.
- Wide traces (≥ 0.6 mm): POGO_5V, PAD_SYS, 5V_RGB. Battery path VBAT / CELL_N / protection FETs ≥ 1 mm.
- Signals 0.25 mm is plenty.
- Heat sources: TP4056 (charging), boost U5 (full LED brightness). Keep both away from the battery holder and the NTC.
- The complete net list, generated from the schematic, is in the appendix below.

---

## Appendix — full net index (generated)

Generated from the verified schematic (commit `b6046e3`). Blocks 1 (pogo board split) and 7 (1.69" display, backlight MOSFET, GP27) changed after that; the tables in those sections are the current design.

<details>
<summary>Show the full net index</summary>

| Net | Pins (ref.pin function) |
|---|---|
| GND | 149 pins (every GND pin on the board) |
| +3V3 | A1.36 (3V3), C12.1, C54.1, R10.1, R11.1, R18.1, R22.1, R23.1, R24.1, R25.1, R26.1, R27.1, R28.1, U6.24 (VCC), U8.1 (IN) |
| 5V_RGB | C10.1, C11.1, C17.1, R20.1, U5.6 (VOUT), U7.5 (VCC), plus VDD of all 36 LEDs (D2–D37) and their 100 nF (C18–C53) |
| BOOST_FB | R20.2, R21.1, U5.1 (FB) |
| BOOST_SW | L1.2 (2), U5.5 (SW) |
| CELL_N | C4.2, J3.2, Q3.2 (S1), Q3.3 (S1), U3.6 (GND) |
| CHG_CE | Q2.3 (D), R8.2, U2.8 (CE) |
| CHG_CHRG_N | A1.25 (GPIO19), R10.2, U2.7 (CHRG) |
| CHG_FAST | A1.22 (GPIO17), Q1.1 (G), R7.1 |
| CHG_INHIBIT | A1.24 (GPIO18), Q2.1 (G), R9.1 |
| CHG_PROG | R5.1, R6.1, U2.2 (PROG) |
| CHG_PROG_SW | Q1.3 (D), R6.2 |
| CHG_STDBY_N | A1.26 (GPIO20), R11.2, U2.6 (STDBY) |
| CHG_TEMP | J2.1, R3.2, R4.1, U2.1 (TEMP) |
| DOCKED | A1.27 (GPIO21), R18.2, U4.8 (ST) |
| DW_CS | R13.1, U3.2 (CS) |
| DW_OC | Q3.5 (G2), U3.3 (OC) |
| DW_OD | Q3.4 (G1), U3.1 (OD) |
| DW_VCC | C4.1, R12.2, U3.5 (VCC) |
| ENC1_A | A1.4 (GPIO2), C13.1, R25.2, SW13.A (A_A) |
| ENC1_B | A1.5 (GPIO3), C14.1, R26.2, SW13.B (B_B) |
| ENC1_SW | SW13.S1 (S1_S1), U6.17 (P14) |
| ENC2_A | A1.9 (GPIO6), C15.1, R27.2, SW14.A (A_A) |
| ENC2_B | A1.10 (GPIO7), C16.1, R28.2, SW14.B (B_B) |
| ENC2_SW | SW14.S1 (S1_S1), U6.18 (P15) |
| FET_D12 | Q3.1 (D12), Q3.8 (D12) |
| I2C_SCL | A1.7 (GPIO5), R23.2, U6.22 (SCL) |
| I2C_SDA | A1.6 (GPIO4), R22.2, U6.23 (SDA) |
| KEY1 | SW1.1 (1), U6.4 (P00) |
| KEY10 | SW10.1 (1), U6.14 (P11) |
| KEY11 | SW11.1 (1), U6.15 (P12) |
| KEY12 | SW12.1 (1), U6.16 (P13) |
| KEY2 | SW2.1 (1), U6.5 (P01) |
| KEY3 | SW3.1 (1), U6.6 (P02) |
| KEY4 | SW4.1 (1), U6.7 (P03) |
| KEY5 | SW5.1 (1), U6.8 (P04) |
| KEY6 | SW6.1 (1), U6.9 (P05) |
| KEY7 | SW7.1 (1), U6.10 (P06) |
| KEY8 | SW8.1 (1), U6.11 (P07) |
| KEY9 | SW9.1 (1), U6.13 (P10) |
| LED_DIN1 | D2.2 (DIN), R29.2 |
| LED_DIN10 | D10.4 (DOUT), D11.2 (DIN) |
| LED_DIN11 | D11.4 (DOUT), D12.2 (DIN) |
| LED_DIN12 | D12.4 (DOUT), D13.2 (DIN) |
| LED_DIN13 | D13.4 (DOUT), D14.2 (DIN) |
| LED_DIN14 | D14.4 (DOUT), D15.2 (DIN) |
| LED_DIN15 | D15.4 (DOUT), D16.2 (DIN) |
| LED_DIN16 | D16.4 (DOUT), D17.2 (DIN) |
| LED_DIN17 | D17.4 (DOUT), D18.2 (DIN) |
| LED_DIN18 | D18.4 (DOUT), D19.2 (DIN) |
| LED_DIN19 | D19.4 (DOUT), D20.2 (DIN) |
| LED_DIN2 | D2.4 (DOUT), D3.2 (DIN) |
| LED_DIN20 | D20.4 (DOUT), D21.2 (DIN) |
| LED_DIN21 | D21.4 (DOUT), D22.2 (DIN) |
| LED_DIN22 | D22.4 (DOUT), D23.2 (DIN) |
| LED_DIN23 | D23.4 (DOUT), D24.2 (DIN) |
| LED_DIN24 | D24.4 (DOUT), D25.2 (DIN) |
| LED_DIN25 | D25.4 (DOUT), D26.2 (DIN) |
| LED_DIN26 | D26.4 (DOUT), D27.2 (DIN) |
| LED_DIN27 | D27.4 (DOUT), D28.2 (DIN) |
| LED_DIN28 | D28.4 (DOUT), D29.2 (DIN) |
| LED_DIN29 | D29.4 (DOUT), D30.2 (DIN) |
| LED_DIN3 | D3.4 (DOUT), D4.2 (DIN) |
| LED_DIN30 | D30.4 (DOUT), D31.2 (DIN) |
| LED_DIN31 | D31.4 (DOUT), D32.2 (DIN) |
| LED_DIN32 | D32.4 (DOUT), D33.2 (DIN) |
| LED_DIN33 | D33.4 (DOUT), D34.2 (DIN) |
| LED_DIN34 | D34.4 (DOUT), D35.2 (DIN) |
| LED_DIN35 | D35.4 (DOUT), D36.2 (DIN) |
| LED_DIN36 | D36.4 (DOUT), D37.2 (DIN) |
| LED_DIN4 | D4.4 (DOUT), D5.2 (DIN) |
| LED_DIN5 | D5.4 (DOUT), D6.2 (DIN) |
| LED_DIN6 | D6.4 (DOUT), D7.2 (DIN) |
| LED_DIN7 | D7.4 (DOUT), D8.2 (DIN) |
| LED_DIN8 | D8.4 (DOUT), D9.2 (DIN) |
| LED_DIN9 | D9.4 (DOUT), D10.2 (DIN) |
| MUX_PR1 | R16.2, R17.1, U4.4 (PR1) |
| OLED_CS | A1.17 (GPIO13), J6.7 |
| OLED_DC | A1.16 (GPIO12), J6.6 |
| OLED_EN | A1.29 (GPIO22), R30.1, U8.3 (ON) |
| OLED_MOSI | A1.15 (GPIO11), J6.4 |
| OLED_QOD | R31.2, U8.5 (QOD) |
| OLED_RES | A1.19 (GPIO14), J6.5 |
| OLED_SCK | A1.14 (GPIO10), J6.3 |
| OLED_VCC | C55.1, J6.2, R31.1, U8.6 (OUT) |
| PAD_SYS | A1.39 (VSYS), C7.1, C8.1, C9.1, L1.1 (1), U4.2 (VOUT), U4.7 (VOUT), U5.3 (VIN) |
| PAD_UART_RX | A1.2 (GPIO1), R1.2 |
| PAD_UART_TX | A1.1 (GPIO0), R2.1 |
| POGO_5V | C1.1, C2.1, D1.1 (K), J1.5, R3.1, R8.1, R16.1, U2.4 (VCC), U4.3 (VIN1), U4.5 (MODE) |
| POGO_DRX | J1.3, R2.2, U1.3 (D2+) |
| POGO_DTX | J1.2, R1.1, U1.1 (D1+) |
| RGB_BUF | R29.1, U7.4 |
| RGB_DATA_3V3 | A1.12 (GPIO9), U7.2 |
| RGB_EN | A1.21 (GPIO16), R19.1, U5.2 (EN) |
| SEL_A | J5.1, U6.19 (P16) |
| SEL_B | J5.3, U6.20 (P17) |
| TCA_INT_N | A1.11 (GPIO8), R24.2, U6.1 (INT) |
| VBAT | C3.1, C6.1, J3.1, R12.1, R14.1, U2.5 (BAT), U4.6 (VIN2) |
| VBAT_SENSE | A1.31 (GPIO26), C5.1, R14.2, R15.1 |

Not connected: A1.20, A1.32, A1.34, A1.35, A1.37, A1.40, A1.TP1, A1.TP2, A1.TP3, A1.TP4, A1.TP5, A1.TP6, D37.4, U1.4, U1.5, U1.6, U3.4, U8.4

</details>
