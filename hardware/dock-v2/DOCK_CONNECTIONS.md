# Dock v2 — Connection & Placement Guide

Use this to understand the v2 dock circuit, sheet by sheet (sketches, reasons, placement). **To wire the schematic, use the component-by-component list [DOCK_WIRING.md](DOCK_WIRING.md)**: every part, every pin, what it connects to and which label to draw.
All parts are already on their sheets (`hardware/dock-v2/`, placed, not wired) with the references used here.
Why each part was chosen is in `docs/dock-v2-*.md`; where it goes on the board is in [PCB_PLACEMENT.md](PCB_PLACEMENT.md).

The tables are generated from one connection model and checked against the placed schematic: 154 parts, 494 connected pins on 92 nets, 77 no-connect pins. Every pin of every part is listed once, either on a net or as a no-connect.

How to read the tables:

- **Parts**: what is on the sheet (value, footprint and LCSC number are already filled in).
- **Wiring**: each row is one pin and the net it belongs to. Everything with the same net name is wired together.
  Nets in **bold** leave the sheet: use a **global label** with exactly that name. The rest are **local labels** (or plain wires) inside the sheet.
- **Placement**: what has to sit next to what on the PCB, and why.

Net names used everywhere:

| Net | What it is |
|---|---|
| **GND** | Board ground (also the two PCs' and the charger's ground) |
| **VBUS_IN** | Charger input after J101: 9 V with a PD charger, 5 V without |
| **+5V** | Buck output, 5.16 V (≈ 4.7 V pass-through on a 5 V-only charger) |
| **+3V3** | AMS1117 output: both RP2354A, the ESP32-C3, all pull-ups |
| **KBD_VBUS** | Keyboard 5 V after the SY6280 switch (off until a keyboard is detected) |
| **POGO_5V** | Pad 5 V after the pogo SY6280 switch (on while the pad is docked); two contacts, limit ≈ 1.45 A |
| A_1V1, B_1V1 | Each RP2354A's own 1.1 V core rail. **Local labels, never a `+1V1` power symbol**: a power symbol is global and would join A's and B's regulators |
| PC1_VBUS, PC2_VBUS | The PCs' VBUS: **sense only**, never joined to a dock rail |

## Contents

1. [Power input and PD (J101, CH224A)](#1-power-input-and-pd-j101-ch224a)
2. [5 V buck and 3.3 V LDO](#2-5-v-buck-and-33-v-ldo)
3. [Keyboard port (J201, USB-C source)](#3-keyboard-port-j201-usb-c-source)
4. [PC ports (J202 Personal, J203 Work)](#4-pc-ports-j202-personal-j203-work)
5. [MCU A (RP2354A)](#5-mcu-a-rp2354a)
6. [MCU B (RP2354A)](#6-mcu-b-rp2354a)
7. [BLE (ESP32-C3-MINI-1)](#7-ble-esp32-c3-mini-1)
8. [Pogo interface](#8-pogo-interface)
9. [Signals that cross between sheets](#9-signals-that-cross-between-sheets)
10. [Board-wide rules, PWR_FLAGs and no-connects](#10-board-wide-rules-pwr_flags-and-no-connects)
11. [Appendix: full net index](#appendix--full-net-index-generated)

## The whole dock at a glance

```text
 charger ═ J101 ─ VBUS_IN ─┬─ CH224A (asks 9 V) ── I2C, PG ──────────────────────────┐
                           └─ TPS54331 ── +5V ─┬─ AMS1117 ── +3V3 ──► A, B, ESP32      │
                                               ├─ SY6280 ── KBD_VBUS ──► J201 keyboard │
                                               └─ SY6280 ── POGO_5V ───► J601 pogo     │
                                                                                       ▼
 keyboard ═ J201 ── PIO-USB (GPIO6/7) ──►┌────────────┐── UART0 ──►┌────────────┐
                    CC1/CC2 → ADC        │ RP2354A  A │◄─ RUN, BOOTSEL, SWD ─│ RP2354A  B │══ J203 ═ Work PC
 Personal PC ═ J202 ══ native USB ═══════│  (U301)    │            │  (U401)    │
                                         └─────┬──────┘            └────────────┘
                              UART1, EN, BOOT  │  PIO UART, DET, OFF, ADC
                                  ESP32-C3 ◄───┴───► pogo J601 ═ pad
```

Each sketch below is only a reading aid: `●` is a junction, `─` a wire, `→`/`←` show which way a signal goes. The tables under each sketch are the exact reference.

---

## 1. Power input and PD (J101, CH224A)

Sheet `power.kicad_sch`.

```text
 J101 VBUS (A4, A9, B4, B9) ──●── VBUS_IN ──► buck VIN (section 2)
                              ├── D101 SMBJ15A cathode (pin 1); anode (pin 2) ── GND
                              ├── C101 1 µF 50 V ── GND
                              └── U102 pin 1 VHV and pin 8 VBUS (tied together, datasheet)
 J101 CC1 (A5) ──●── PD_CC1 ── U102 pin 7        J101 D+ (A6, B6) ──●── PD_DP ── U102 pin 4
                 └── U101 pin 3 (ESD)                               └── U101 pin 1
 J101 CC2 (B5) ──●── PD_CC2 ── U102 pin 6        J101 D− (A7, B7) ──●── PD_DM ── U102 pin 5
                 └── U101 pin 4                                     └── U101 pin 6
 U102 pin 9 CFG1 ── PD_CFG1 ── R101 6.8 k ── GND            (requests 9 V on its own)
 U102 pin 2 CFG2/SCL ──●── PD_SCL ──► MCU A GPIO21      (R103 4.7 k to +3V3)
 U102 pin 3 CFG3/SDA ──●── PD_SDA ◄─► MCU A GPIO20      (R104 4.7 k to +3V3)
 U102 pin 10 PG ───────●── PD_PG ───► MCU A GPIO22      (R102 10 k to +3V3)
 U102 pin 11 (exposed pad) ── GND;  J101 A1, A12, B1, B12, SH ── GND;  SBU A8/B8: no-connect
```

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| J101 | TYPE-C-31-M-12 | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | Power input: charger, 9 V PD |
| U101 | TPD4E1U06DBVR | `SOT-23-6` | C124691 | ESD on CC1, CC2, D+, D-, <=5 mm from J101 |
| D101 | SMBJ15A | `D_SMB` | C113988 | VBUS_IN TVS, at J101 VBUS |
| U102 | CH224A | `SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm` | C42459160 | VBUS (8) tied to VHV (1) |
| C101 | 1uF 50V | `C_0603_1608Metric` | C15849 | VHV to GND |
| R101 | 6.8k | `R_0402_1005Metric` | C25917 | CFG1 to GND: requests 9 V |
| R102 | 10k | `R_0402_1005Metric` | C25744 | PG pull-up to 3V3 |
| R103 | 4.7k | `R_0402_1005Metric` | C25900 | SCL pull-up to 3V3 |
| R104 | 4.7k | `R_0402_1005Metric` | C25900 | SDA pull-up to 3V3 |

**Wiring — J101 (USB-C, power input)**

| J101 pin | Name | Net | Also on this net |
|---|---|---|---|
| A1 | GND | **GND** | 138 other pins |
| A4 | VBUS | **VBUS_IN** | D101.1, U102.1, U102.8, C101.1, U103.2, C102.1, C103.1 |
| A5 | CC1 | **PD_CC1** | U101.3, U102.7 |
| A6 | D+ | **PD_DP** | U101.1, U102.4 |
| A7 | D- | **PD_DM** | U101.6, U102.5 |
| A8 | SBU1 | no-connect flag | |
| A9 | VBUS | **VBUS_IN** | D101.1, U102.1, U102.8, C101.1, U103.2, C102.1, C103.1 |
| A12 | GND | **GND** | 138 other pins |
| B1 | GND | **GND** | 138 other pins |
| B4 | VBUS | **VBUS_IN** | D101.1, U102.1, U102.8, C101.1, U103.2, C102.1, C103.1 |
| B5 | CC2 | **PD_CC2** | U101.4, U102.6 |
| B6 | D+ | **PD_DP** | U101.1, U102.4 |
| B7 | D- | **PD_DM** | U101.6, U102.5 |
| B8 | SBU2 | no-connect flag | |
| B9 | VBUS | **VBUS_IN** | D101.1, U102.1, U102.8, C101.1, U103.2, C102.1, C103.1 |
| B12 | GND | **GND** | 138 other pins |
| SH | SHIELD | **GND** | 138 other pins |

**Wiring — U101 (ESD) and U102 (CH224A)**

| U101 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | D1+ | **PD_DP** | J101.A6, J101.B6, U102.4 |
| 2 | GND | **GND** | 142 other pins |
| 3 | D2+ | **PD_CC1** | J101.A5, U102.7 |
| 4 | D2- | **PD_CC2** | J101.B5, U102.6 |
| 5 | NC | no-connect flag | |
| 6 | D1- | **PD_DM** | J101.A7, J101.B7, U102.5 |

| U102 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | VHV | **VBUS_IN** | J101.A4, J101.A9, J101.B4, J101.B9, D101.1, C101.1, U103.2, C102.1 … |
| 2 | CFG2/SCL | **PD_SCL** | R103.2, U301.33 |
| 3 | CFG3/SDA | **PD_SDA** | R104.2, U301.32 |
| 4 | DP | **PD_DP** | J101.A6, J101.B6, U101.1 |
| 5 | DM | **PD_DM** | J101.A7, J101.B7, U101.6 |
| 6 | CC2 | **PD_CC2** | J101.B5, U101.4 |
| 7 | CC1 | **PD_CC1** | J101.A5, U101.3 |
| 8 | VBUS | **VBUS_IN** | J101.A4, J101.A9, J101.B4, J101.B9, D101.1, C101.1, U103.2, C102.1 … |
| 9 | CFG1 | PD_CFG1 | R101.1 |
| 10 | PG | **PD_PG** | R102.2, U301.34 |
| 11 | GND | **GND** | 142 other pins |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| D101 (1 = cathode band) | **VBUS_IN** | **GND** |
| C101 | **VBUS_IN** | **GND** |
| R101 | PD_CFG1 | **GND** |
| R102 | **+3V3** | **PD_PG** |
| R103 | **+3V3** | **PD_SCL** |
| R104 | **+3V3** | **PD_SDA** |

Notes:
- D101 uses KiCad's `D_TVS` symbol, drawn bidirectional (pins A1/A2). The SMBJ15A is **unidirectional**: pin 1 (A1) is the footprint's **cathode-band** pad, so pin 1 goes to VBUS_IN.
- Not verified: the level of the CH224A's internal CFG2/CFG3 pull-ups. Measure SCL/SDA idle voltage on the first board before connecting the I2C lines to MCU A (both are rated 6.5 V; the RP2354A pins are 3.3 V).

**Placement**

- J101 on the right edge. U101 within 5 mm of J101, signals pass its pads first. D101 right at J101's VBUS pads.
- U102 next to J101: short CC and D± runs. C101 at U102 pin 1. R101 at pin 9.
- VBUS_IN is a Power-class net (0.6 mm).

---

## 2. 5 V buck and 3.3 V LDO

Sheet `power.kicad_sch`. Values from TI's TPS54331 Table 7-1 (5 V design), on JLCPCB Basic parts: see `docs/dock-v2-power-input.md` §4b.

```text
 VBUS_IN ──●── U103 pin 2 VIN                    U103 pin 8 PH ──●── BUCK_SW ──●── L101 6.8 µH ──●── +5V
           ├── C102 10 µF ── GND                                 │             └── D102 SS54 cathode; anode ── GND
           └── C103 10 µF ── GND                                 └── C104 100 nF ── U103 pin 1 BOOT
 U103 pin 3 EN: no-connect (internal pull-up; a UVLO divider would stop the 5 V pass-through)
 U103 pin 4 SS ── BUCK_SS ── C105 10 nF ── GND                       (≈ 4 ms soft start)
 U103 pin 6 COMP ──●── BUCK_COMP ── R105 51 k ── BUCK_COMP_RC ── C106 4.7 nF ── GND
                   └── C107 47 pF ── GND
 +5V ── R106 12 k ──●── BUCK_FB ── U103 pin 5 VSENSE            (0.8 V × (1 + 12/2.2) = 5.16 V)
                    └── R107 2.2 k ── GND
 +5V ──●── C108, C109, C110 22 µF ── GND
       └── U104 pin 3 VI (AMS1117)   U104 pin 2 VO ──●── +3V3     U104 pin 1 GND
           C111 10 µF at VI                          └── C112 10 µF ── GND
```

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| U103 | TPS54331DR | `SOIC-8_3.9x4.9mm_P1.27mm` | C9865 | EN left open (5 V pass-through) |
| C102 | 10uF 25V | `C_0805_2012Metric` | C15850 | VIN, at pins 2/7 |
| C103 | 10uF 25V | `C_0805_2012Metric` | C15850 | VIN |
| C104 | 100nF | `C_0402_1005Metric` | C1525 | BOOT to PH |
| C105 | 10nF | `C_0402_1005Metric` | C15195 | SS: ~4 ms soft start |
| R105 | 51k | `R_0402_1005Metric` | C25794 | COMP series R |
| C106 | 4.7nF | `C_0402_1005Metric` | C1538 | COMP series C |
| C107 | 47pF | `C_0402_1005Metric` | C1567 | COMP to GND |
| R106 | 12k | `R_0402_1005Metric` | C25752 | FB top: 0.8*(1+12/2.2)=5.16 V |
| R107 | 2.2k | `R_0402_1005Metric` | C25879 | FB bottom |
| D102 | SS54 | `D_SMC` | C22452 | catch diode PH to GND |
| L101 | 6.8uH | `L_TechFuse_SL0630` | C207841 | SLO0630H6R8MTT: Isat 8 A (> 5.8 A max current limit), 45 mOhm, 7.1x6.6x3.0 |
| C108 | 22uF 25V | `C_1206_3216Metric` | C12891 | +5V output |
| C109 | 22uF 25V | `C_1206_3216Metric` | C12891 | +5V output |
| C110 | 22uF 25V | `C_1206_3216Metric` | C12891 | +5V output |
| U104 | AMS1117-3.3 | `SOT-223-3_TabPin2` | C6186 | +5V to +3V3, tab on copper |
| C111 | 10uF | `C_0805_2012Metric` | C15850 | LDO input |
| C112 | 10uF | `C_0805_2012Metric` | C15850 | LDO output |
| H101 | MountingHole | `MountingHole_3.2mm_M3` | — |  |
| H102 | MountingHole | `MountingHole_3.2mm_M3` | — |  |
| H103 | MountingHole | `MountingHole_3.2mm_M3` | — |  |
| H104 | MountingHole | `MountingHole_3.2mm_M3` | — |  |

**Wiring — U103 (TPS54331) and U104 (AMS1117)**

| U103 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | BOOT | BUCK_BOOT | C104.1 |
| 2 | VIN | **VBUS_IN** | J101.A4, J101.A9, J101.B4, J101.B9, D101.1, U102.1, U102.8, C101.1 … |
| 3 | EN | no-connect flag | |
| 4 | SS | BUCK_SS | C105.1 |
| 5 | VSENSE | BUCK_FB | R106.2, R107.1 |
| 6 | COMP | BUCK_COMP | R105.1, C107.1 |
| 7 | GND | **GND** | 142 other pins |
| 8 | PH | BUCK_SW | C104.2, D102.1, L101.1 |

| U104 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | GND | **GND** | 142 other pins |
| 2 | VO | **+3V3** | 57 other pins |
| 3 | VI | **+5V** | 10 other pins |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| C102 | **VBUS_IN** | **GND** |
| C103 | **VBUS_IN** | **GND** |
| C104 | BUCK_BOOT | BUCK_SW |
| C105 | BUCK_SS | **GND** |
| R105 | BUCK_COMP | BUCK_COMP_RC |
| C106 | BUCK_COMP_RC | **GND** |
| C107 | BUCK_COMP | **GND** |
| R106 | **+5V** | BUCK_FB |
| R107 | BUCK_FB | **GND** |
| D102 (1 = K, 2 = A) | BUCK_SW | **GND** |
| L101 | BUCK_SW | **+5V** |
| C108 | **+5V** | **GND** |
| C109 | **+5V** | **GND** |
| C110 | **+5V** | **GND** |
| C111 | **+5V** | **GND** |
| C112 | **+3V3** | **GND** |

H101–H104 (M3 holes) have no pins.

**Placement**

- Front-right corner. The **hot loop**: C102/C103 → U103 VIN/GND → PH → D102 → GND. Keep it tiny, on the top layer, over the In1 ground plane.
- L101 next to the PH pin; C108–C110 between L101 and the +5V trunk. Copper pour around U103 GND and D102 for heat.
- R106/R107 at U103 pin 5, fed from the +5V side of C108–C110; keep BUCK_FB away from BUCK_SW, L101 and D102.
- C104 right at pins 1 and 8. C105, R105/C106/C107 right at pins 4 and 6.
- U104 in the centre of the board (it feeds A, B and the ESP32); tab on a copper area. C111/C112 at its pins.
- L101 = Sunltech **SLO0630H6R8MTT** (C207841): 6.8 µH, saturation 8 A (above the TPS54331's 5.8 A maximum current limit, so it can't saturate in an overload), 45 mΩ, 7.1 × 6.6 × 3.0 mm, footprint `Inductor_SMD:L_TechFuse_SL0630` (same body and pad gap as Sunltech's land pattern). Extended part: JLCPCB has no Basic power inductor.

---

## 3. Keyboard port (J201, USB-C source)

Sheet `usb_ports.kicad_sch`. The dock is the **source** here: Rp pull-ups on CC, 5 V only after the firmware sees a keyboard (docs/dock-v2-usb-ports.md §4).

```text
 +5V ──●── U202 pin 5 IN (SY6280)        U202 pin 1 OUT ──●── KBD_VBUS ──► J201 VBUS (A4, A9, B4, B9)
       └── C204 1 µF ── GND                               ├── C201 220 µF THT (+ = pin 1), hand-soldered
 U202 pin 4 EN ──●── KBD_VBUS_EN ◄── MCU A GPIO5          ├── C202 10 µF, C203 1 µF ── GND
                 └── R208 100 k ── GND  (off at reset)    └── R209 10 k ──●── KBD_VBUS_SENSE ──► MCU A GPIO28 (ADC2)
 U202 pin 3 ISET ── R207 6.8 k ── GND  (1.0 A)                             └── R210 15 k ── GND
 +3V3 ── R201 33 k ──●── KBD_CC1 ── J201 CC1 (A5) ──► MCU A GPIO26 (ADC0);  U201 pin 3
 +3V3 ── R202 33 k ──●── KBD_CC2 ── J201 CC2 (B5) ──► MCU A GPIO27 (ADC1);  U201 pin 4
 J201 D+ (A6, B6) ──●── KBD_USBJ_D_P ── R205 22 Ω ── KBD_USB_D_P ──► MCU A GPIO6 (PIO-USB D+)
                    ├── U201 pin 1;  R203 15 k ── GND
 J201 D− (A7, B7) ──●── KBD_USBJ_D_N ── R206 22 Ω ── KBD_USB_D_N ──► MCU A GPIO7 (PIO-USB D−)
                    ├── U201 pin 6;  R204 15 k ── GND
 J201 A1, A12, B1, B12, SH ── GND;  SBU A8/B8: no-connect
```

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| J201 | TYPE-C-31-M-12 | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | Keyboard |
| U201 | TPD4E1U06DBVR | `SOT-23-6` | C124691 | ESD D+, D-, CC1, CC2 |
| R201 | 33k | `R_0402_1005Metric` | C25779 | CC1 Rp to 3V3 (Default USB) |
| R202 | 33k | `R_0402_1005Metric` | C25779 | CC2 Rp to 3V3 |
| R203 | 15k | `R_0402_1005Metric` | C25756 | D+ host pull-down |
| R204 | 15k | `R_0402_1005Metric` | C25756 | D- host pull-down |
| R205 | 22 | `R_0402_1005Metric` | C25092 | D+ series, near MCU A |
| R206 | 22 | `R_0402_1005Metric` | C25092 | D- series, near MCU A |
| U202 | SY6280AAC | `SOT-23-5` | C55136 | KBD_VBUS switch, EN from MCU A |
| R207 | 6.8k | `R_0402_1005Metric` | C25917 | ISET: 1.0 A |
| R208 | 100k | `R_0402_1005Metric` | C25741 | EN pull-down (off at reset) |
| C201 | 220uF 16V | `CP_Radial_D6.3mm_P5.00mm` | — | HAND-SOLDER: Koshin PKRJ-016V221ME070-T/A5.0 (Ozdisan) |
| C202 | 10uF | `C_0805_2012Metric` | C15850 | KBD_VBUS at J201 |
| C203 | 1uF | `C_0402_1005Metric` | C52923 | KBD_VBUS at J201 |
| C204 | 1uF | `C_0402_1005Metric` | C52923 | U202 input |
| R209 | 10k | `R_0402_1005Metric` | C25744 | KBD_VBUS divider top -> ADC |
| R210 | 15k | `R_0402_1005Metric` | C25756 | KBD_VBUS divider bottom |

**Wiring**

| J201 pin | Name | Net | Also on this net |
|---|---|---|---|
| A1 | GND | **GND** | 138 other pins |
| A4 | VBUS | **KBD_VBUS** | U202.1, C201.1, C202.1, C203.1, R209.1 |
| A5 | CC1 | **KBD_CC1** | U201.3, R201.2, U301.40 |
| A6 | D+ | KBD_USBJ_D_P | U201.1, R203.1, R205.1 |
| A7 | D- | KBD_USBJ_D_N | U201.6, R204.1, R206.1 |
| A8 | SBU1 | no-connect flag | |
| A9 | VBUS | **KBD_VBUS** | U202.1, C201.1, C202.1, C203.1, R209.1 |
| A12 | GND | **GND** | 138 other pins |
| B1 | GND | **GND** | 138 other pins |
| B4 | VBUS | **KBD_VBUS** | U202.1, C201.1, C202.1, C203.1, R209.1 |
| B5 | CC2 | **KBD_CC2** | U201.4, R202.2, U301.41 |
| B6 | D+ | KBD_USBJ_D_P | U201.1, R203.1, R205.1 |
| B7 | D- | KBD_USBJ_D_N | U201.6, R204.1, R206.1 |
| B8 | SBU2 | no-connect flag | |
| B9 | VBUS | **KBD_VBUS** | U202.1, C201.1, C202.1, C203.1, R209.1 |
| B12 | GND | **GND** | 138 other pins |
| SH | SHIELD | **GND** | 138 other pins |

| U201 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | D1+ | KBD_USBJ_D_P | J201.A6, J201.B6, R203.1, R205.1 |
| 2 | GND | **GND** | 142 other pins |
| 3 | D2+ | **KBD_CC1** | J201.A5, R201.2, U301.40 |
| 4 | D2- | **KBD_CC2** | J201.B5, R202.2, U301.41 |
| 5 | NC | no-connect flag | |
| 6 | D1- | KBD_USBJ_D_N | J201.A7, J201.B7, R204.1, R206.1 |

| U202 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | OUT | **KBD_VBUS** | J201.A4, J201.A9, J201.B4, J201.B9, C201.1, C202.1, C203.1, R209.1 |
| 2 | GND | **GND** | 142 other pins |
| 3 | ISET | KBD_ISET | R207.1 |
| 4 | EN | **KBD_VBUS_EN** | R208.1, U301.8 |
| 5 | IN | **+5V** | 10 other pins |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| R201 | **+3V3** | **KBD_CC1** |
| R202 | **+3V3** | **KBD_CC2** |
| R203 | KBD_USBJ_D_P | **GND** |
| R204 | KBD_USBJ_D_N | **GND** |
| R205 | KBD_USBJ_D_P | **KBD_USB_D_P** |
| R206 | KBD_USBJ_D_N | **KBD_USB_D_N** |
| R207 | KBD_ISET | **GND** |
| R208 | **KBD_VBUS_EN** | **GND** |
| C201 (1 = +) | **KBD_VBUS** | **GND** |
| C202 | **KBD_VBUS** | **GND** |
| C203 | **KBD_VBUS** | **GND** |
| C204 | **+5V** | **GND** |
| R209 | **KBD_VBUS** | **KBD_VBUS_SENSE** |
| R210 | **KBD_VBUS_SENSE** | **GND** |

**Placement**

- J201 on the left edge. U201 within 5 mm. R201/R202 near J201.
- U202 between the +5V trunk and J201; R207 short to U202 pin 3. C201 (Ø 6.3 mm, THT) and C202/C203 at J201's VBUS pads.
- R205/R206 **near MCU A** (series termination at the driver); R203/R204 anywhere on the pair, near J201 is fine.
- KBD_USB pair as a 90 Ω differential pair; GPIO6/GPIO7 are on MCU A's left side, facing J201.
- KBD_VBUS is Power class.

---

## 4. PC ports (J202 Personal, J203 Work)

Sheet `usb_ports.kicad_sch`. The dock is a **sink** (Rd) but draws no power: VBUS is only sensed.

```text
 J202 (Personal PC, back edge)                               J203 (Work PC) is the same with R217–R222, U204,
 J202 VBUS ── PC1_VBUS ── R213 22 k ──●── PC1_VBUS_DET ──► MCU A GPIO0     PC2_* nets, MCU B GPIO2 and B's USB pins
                                      └── R214 33 k ── GND
 J202 CC1 (A5) ──●── PC1_CC1 ── R211 5.1 k ── GND;  U203 pin 3
 J202 CC2 (B5) ──●── PC1_CC2 ── R212 5.1 k ── GND;  U203 pin 4
 J202 D+ (A6, B6) ──●── PC1_USBJ_D_P ── R215 22 Ω ── PC1_USB_D_P ──► MCU A pin 52 USB_DP
                    └── U203 pin 1
 J202 D− (A7, B7) ──●── PC1_USBJ_D_N ── R216 22 Ω ── PC1_USB_D_N ──► MCU A pin 51 USB_DM
                    └── U203 pin 6
 J202 A1, A12, B1, B12, SH ── GND;  SBU A8/B8: no-connect
```

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| J202 | TYPE-C-31-M-12 | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | Personal PC |
| U203 | TPD4E1U06DBVR | `SOT-23-6` | C124691 | ESD D+, D-, CC1, CC2 |
| R211 | 5.1k | `R_0402_1005Metric` | C25905 | CC1 Rd |
| R212 | 5.1k | `R_0402_1005Metric` | C25905 | CC2 Rd |
| R213 | 22k | `R_0402_1005Metric` | C25768 | VBUS sense top |
| R214 | 33k | `R_0402_1005Metric` | C25779 | VBUS sense bottom |
| R215 | 22 | `R_0402_1005Metric` | C25092 | D+ series, near MCU A |
| R216 | 22 | `R_0402_1005Metric` | C25092 | D- series, near MCU A |
| J203 | TYPE-C-31-M-12 | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | Work PC |
| U204 | TPD4E1U06DBVR | `SOT-23-6` | C124691 | ESD D+, D-, CC1, CC2 |
| R217 | 5.1k | `R_0402_1005Metric` | C25905 | CC1 Rd |
| R218 | 5.1k | `R_0402_1005Metric` | C25905 | CC2 Rd |
| R219 | 22k | `R_0402_1005Metric` | C25768 | VBUS sense top |
| R220 | 33k | `R_0402_1005Metric` | C25779 | VBUS sense bottom |
| R221 | 22 | `R_0402_1005Metric` | C25092 | D+ series, near MCU B |
| R222 | 22 | `R_0402_1005Metric` | C25092 | D- series, near MCU B |

**Wiring — J202 / U203 (Personal)**

| J202 pin | Name | Net | Also on this net |
|---|---|---|---|
| A1 | GND | **GND** | 138 other pins |
| A4 | VBUS | **PC1_VBUS** | R213.1 |
| A5 | CC1 | **PC1_CC1** | U203.3, R211.1 |
| A6 | D+ | PC1_USBJ_D_P | U203.1, R215.1 |
| A7 | D- | PC1_USBJ_D_N | U203.6, R216.1 |
| A8 | SBU1 | no-connect flag | |
| A9 | VBUS | **PC1_VBUS** | R213.1 |
| A12 | GND | **GND** | 138 other pins |
| B1 | GND | **GND** | 138 other pins |
| B4 | VBUS | **PC1_VBUS** | R213.1 |
| B5 | CC2 | **PC1_CC2** | U203.4, R212.1 |
| B6 | D+ | PC1_USBJ_D_P | U203.1, R215.1 |
| B7 | D- | PC1_USBJ_D_N | U203.6, R216.1 |
| B8 | SBU2 | no-connect flag | |
| B9 | VBUS | **PC1_VBUS** | R213.1 |
| B12 | GND | **GND** | 138 other pins |
| SH | SHIELD | **GND** | 138 other pins |

| U203 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | D1+ | PC1_USBJ_D_P | J202.A6, J202.B6, R215.1 |
| 2 | GND | **GND** | 142 other pins |
| 3 | D2+ | **PC1_CC1** | J202.A5, R211.1 |
| 4 | D2- | **PC1_CC2** | J202.B5, R212.1 |
| 5 | NC | no-connect flag | |
| 6 | D1- | PC1_USBJ_D_N | J202.A7, J202.B7, R216.1 |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| R211 | **PC1_CC1** | **GND** |
| R212 | **PC1_CC2** | **GND** |
| R213 | **PC1_VBUS** | **PC1_VBUS_DET** |
| R214 | **PC1_VBUS_DET** | **GND** |
| R215 | PC1_USBJ_D_P | **PC1_USB_D_P** |
| R216 | PC1_USBJ_D_N | **PC1_USB_D_N** |

**Wiring — J203 / U204 (Work)**

| J203 pin | Name | Net | Also on this net |
|---|---|---|---|
| A1 | GND | **GND** | 138 other pins |
| A4 | VBUS | **PC2_VBUS** | R219.1 |
| A5 | CC1 | **PC2_CC1** | U204.3, R217.1 |
| A6 | D+ | PC2_USBJ_D_P | U204.1, R221.1 |
| A7 | D- | PC2_USBJ_D_N | U204.6, R222.1 |
| A8 | SBU1 | no-connect flag | |
| A9 | VBUS | **PC2_VBUS** | R219.1 |
| A12 | GND | **GND** | 138 other pins |
| B1 | GND | **GND** | 138 other pins |
| B4 | VBUS | **PC2_VBUS** | R219.1 |
| B5 | CC2 | **PC2_CC2** | U204.4, R218.1 |
| B6 | D+ | PC2_USBJ_D_P | U204.1, R221.1 |
| B7 | D- | PC2_USBJ_D_N | U204.6, R222.1 |
| B8 | SBU2 | no-connect flag | |
| B9 | VBUS | **PC2_VBUS** | R219.1 |
| B12 | GND | **GND** | 138 other pins |
| SH | SHIELD | **GND** | 138 other pins |

| U204 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | D1+ | PC2_USBJ_D_P | J203.A6, J203.B6, R221.1 |
| 2 | GND | **GND** | 142 other pins |
| 3 | D2+ | **PC2_CC1** | J203.A5, R217.1 |
| 4 | D2- | **PC2_CC2** | J203.B5, R218.1 |
| 5 | NC | no-connect flag | |
| 6 | D1- | PC2_USBJ_D_N | J203.A7, J203.B7, R222.1 |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| R217 | **PC2_CC1** | **GND** |
| R218 | **PC2_CC2** | **GND** |
| R219 | **PC2_VBUS** | **PC2_VBUS_DET** |
| R220 | **PC2_VBUS_DET** | **GND** |
| R221 | PC2_USBJ_D_P | **PC2_USB_D_P** |
| R222 | PC2_USBJ_D_N | **PC2_USB_D_N** |

**Placement**

- J202 back edge, left (towards MCU A); J203 back edge, right (towards MCU B). ESD within 5 mm of each.
- R215/R216 near MCU A's USB pins, R221/R222 near MCU B's.
- PCx_VBUS is **never** connected to +5V or any dock rail. Firmware connects each MCU's USB (D+ pull-up) only while its PCx_VBUS_DET is high, so a switched-off PC is never back-fed.

---

## 5. MCU A (RP2354A)

Sheet `mcu_a.kicad_sch`. Core circuit = Raspberry Pi's Minimal design (`hardware/reference/rpi-rp2350a-minimal`); after F8, `hardware/tools/copy_rpi_core_layout.py … U301` copies RPi's layout.

```text
 +3V3 ──●── U301 IOVDD (1, 11, 20, 30, 38, 45), ADC_AVDD (44), USB_OTP_VDD (53), QSPI_IOVDD (54)
        ├── U301 pin 49 VREG_VIN ── C301 4.7 µF ── GND
        └── R301 33 Ω ──●── A_VREG_AVDD ── U301 pin 46;  C303 4.7 µF ── GND
 U301 pin 48 VREG_LX ── A_VREG_LX ── L301 pin 2      L301 pin 1 (dot) ──●── A_1V1
 A_1V1 ── U301 DVDD (6, 23, 39) and VREG_FB (50);  C302 4.7 µF, C304–C306 100 nF ── GND
 +3V3 ── C307–C313 100 nF, C314 10 µF ── GND          U301 pin 47 VREG_PGND, pin 61 pad ── GND
 U301 pin 21 XIN ──●── A_XIN ── Y301 pin 1;  C315 15 pF ── GND
 U301 pin 22 XOUT ── A_XOUT ── R302 1 k ── A_XOUT_R ──●── Y301 pin 3;  C316 15 pF ── GND
 Y301 pins 2, 4 ── GND
 U301 pin 60 QSPI_SS ── A_QSPI_SS ── R303 1 k ── A_BOOTSEL_BTN ── SW301 ── GND      (BOOTSEL A)
 U301 pin 26 RUN ── A_RUN ── SW302 ── GND                                            (RESET A)
 U301 pins 24/25 SWCLK/SWDIO ── TP301/TP302;  TP303 ── GND
 U301 GPIO2 ── A_LED ── R305 1 k ── A_LED_R ── D301 anode (2); cathode (1) ── GND
 QSPI_SD0–3, QSPI_SCLK (55–59): no-connect (the 2 MB flash inside uses them)
```

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| U301 | RP2354A | `RP2350A_QFN-60_RPi_Vias` | C41378174 | A: keyboard host (PIO-USB) + Personal PC |
| L301 | 3.3uH | `L_Abracon_AOTA-B201610S3R3_0806` | C42411119 | pin 1 (dot) = +1V1, pin 2 = VREG_LX |
| C301 | 4.7uF | `C_0402_RPi_Wide` | C23733 | VREG_VIN (RPi C6) |
| C302 | 4.7uF | `C_0402_RPi_Wide` | C23733 | +1V1 output (RPi C7) |
| C303 | 4.7uF | `C_0402_1005Metric` | C23733 | VREG_AVDD (RPi C9) |
| R301 | 33 | `R_0402_1005Metric` | C25105 | 3V3 -> VREG_AVDD (RPi R3) |
| C304 | 100nF | `C_0402_1005Metric` | C1525 | DVDD 1 (+1V1) |
| C305 | 100nF | `C_0402_1005Metric` | C1525 | DVDD 2 (+1V1) |
| C306 | 100nF | `C_0402_1005Metric` | C1525 | DVDD 3 (+1V1) |
| C307 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C308 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C309 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C310 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C311 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C312 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C313 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C314 | 10uF | `C_0805_2012Metric` | C15850 | +3V3 bulk |
| Y301 | 12MHz | `Crystal_SMD_3225-4Pin_3.2x2.5mm` | C20625731 | ABM8-272-T3 (10 pF, 50 ohm) |
| C315 | 15pF | `C_0402_1005Metric` | C1548 | XIN load |
| C316 | 15pF | `C_0402_1005Metric` | C1548 | XOUT load |
| R302 | 1k | `R_0402_1005Metric` | C11702 | XOUT series (RPi R2) |
| SW301 | SW_Push | `SW_Push_1P1T_XKB_TS-1187A` | C318884 | BOOTSEL A |
| R303 | 1k | `R_0402_1005Metric` | C11702 | QSPI_SS -> BOOTSEL button |
| SW302 | SW_Push | `SW_Push_1P1T_XKB_TS-1187A` | C318884 | RESET A (RUN to GND) |
| TP301 | TestPoint | `TestPoint_Pad_D1.0mm` | — | SWCLK |
| TP302 | TestPoint | `TestPoint_Pad_D1.0mm` | — | SWDIO |
| TP303 | TestPoint | `TestPoint_Pad_D1.0mm` | — | GND |
| D301 | LED red | `LED_0603_1608Metric` | C2286 | status LED |
| R305 | 1k | `R_0402_1005Metric` | C11702 | LED series |

**Pin map — MCU A GPIOs**

| GPIO | Pin | Net | Goes to |
|---|---|---|---|
| GPIO0 | 2 | **PC1_VBUS_DET** | J202 VBUS divider (R213/R214) |
| GPIO1 | 3 | spare (no-connect flag) |  |
| GPIO2 | 4 | A_LED | R305 → D301 |
| GPIO3 | 5 | spare (no-connect flag) |  |
| GPIO4 | 7 | spare (no-connect flag) |  |
| GPIO5 | 8 | **KBD_VBUS_EN** | U202 EN (R208 pull-down) |
| GPIO6 | 9 | **KBD_USB_D_P** | PIO-USB D+ → R205 → J201 |
| GPIO7 | 10 | **KBD_USB_D_N** | PIO-USB D− → R206 → J201 (D− = D+ + 1) |
| GPIO8 | 12 | **BLE_TX** | UART1 TX → ESP32 RXD0 (U501.30) |
| GPIO9 | 13 | **BLE_RX** | UART1 RX ← ESP32 TXD0 (U501.31) |
| GPIO10 | 14 | **BLE_EN** | ESP32 EN, open-drain |
| GPIO11 | 15 | **BLE_BOOT** | ESP32 GPIO9, open-drain |
| GPIO12 | 16 | **POGO_TX** | PIO UART TX → R601 → pogo pin 5 |
| GPIO13 | 17 | **POGO_RX** | PIO UART RX ← R602 ← pogo pin 4 |
| GPIO14 | 18 | **POGO_DET** | pogo DET (low = docked), also Q601 gate |
| GPIO15 | 19 | **POGO_OFF** | Q602 gate: high = pogo 5 V off |
| GPIO16 | 27 | **B_LINK_TX** | UART0 TX → B GPIO1 (RX) |
| GPIO17 | 28 | **B_LINK_RX** | UART0 RX ← B GPIO0 (TX) |
| GPIO18 | 29 | **B_RUN** | B RUN, open-drain (R406 pull-up) |
| GPIO19 | 31 | **B_BOOTSEL** | R404 → B QSPI_SS, open-drain (R407 pull-up) |
| GPIO20 | 32 | **PD_SDA** | I2C0 SDA → CH224A CFG3/SDA |
| GPIO21 | 33 | **PD_SCL** | I2C0 SCL → CH224A CFG2/SCL |
| GPIO22 | 34 | **PD_PG** | CH224A PG (R102 pull-up) |
| GPIO23 | 35 | **B_SWCLK** | B SWCLK (PIO SWD probe) |
| GPIO24 | 36 | **B_SWDIO** | B SWDIO |
| GPIO25 | 37 | spare (no-connect flag) |  |
| GPIO26 | 40 | **KBD_CC1** | ADC0: J201 CC1 (Rp R201) |
| GPIO27 | 41 | **KBD_CC2** | ADC1: J201 CC2 (Rp R202) |
| GPIO28 | 42 | **KBD_VBUS_SENSE** | ADC2: R209/R210 divider |
| GPIO29 | 43 | **POGO_5V_SENSE** | ADC3: R607/R608 divider |

Why these pins: hardware UART0 TX/RX only exist on GPIO 0/1, 12/13, 16/17, 28/29 (UART1 on 4/5, 8/9, 20/21, 24/25); I2C0 on 20/21; the ADC only on 26–29; PIO-USB needs two adjacent GPIOs (D− = D+ + 1). Sides of the QFN-60 (top view, pin 1 top-left, counter-clockwise): left = GPIO0–11 (faces J201 and the ESP32), bottom = GPIO12–18 (faces the pogo), right = GPIO19–29 (faces MCU B and the CH224A), top = regulator and USB (faces J202).

**Wiring — U301**

| U301 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | IOVDD | **+3V3** | 48 other pins |
| 2 | GPIO0 | **PC1_VBUS_DET** | R213.2, R214.1 |
| 3 | GPIO1 | no-connect flag | |
| 4 | GPIO2 | A_LED | R305.1 |
| 5 | GPIO3 | no-connect flag | |
| 6 | DVDD | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 |
| 7 | GPIO4 | no-connect flag | |
| 8 | GPIO5 | **KBD_VBUS_EN** | U202.4, R208.1 |
| 9 | GPIO6 | **KBD_USB_D_P** | R205.2 |
| 10 | GPIO7 | **KBD_USB_D_N** | R206.2 |
| 11 | IOVDD | **+3V3** | 48 other pins |
| 12 | GPIO8 | **BLE_TX** | U501.30, TP504.1 |
| 13 | GPIO9 | **BLE_RX** | U501.31, TP503.1 |
| 14 | GPIO10 | **BLE_EN** | U501.8, R501.2, C501.1 |
| 15 | GPIO11 | **BLE_BOOT** | U501.23, R504.2 |
| 16 | GPIO12 | **POGO_TX** | R601.1 |
| 17 | GPIO13 | **POGO_RX** | R602.2 |
| 18 | GPIO14 | **POGO_DET** | R603.2, Q601.1, R604.2 |
| 19 | GPIO15 | **POGO_OFF** | Q602.1, R609.1 |
| 20 | IOVDD | **+3V3** | 48 other pins |
| 21 | XIN | A_XIN | Y301.1, C315.1 |
| 22 | XOUT | A_XOUT | R302.1 |
| 23 | DVDD | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 |
| 24 | SWCLK | A_SWCLK | TP301.1 |
| 25 | SWDIO | A_SWDIO | TP302.1 |
| 26 | RUN | A_RUN | SW302.1 |
| 27 | GPIO16 | **B_LINK_TX** | U401.3 |
| 28 | GPIO17 | **B_LINK_RX** | U401.2 |
| 29 | GPIO18 | **B_RUN** | U401.26, R406.2 |
| 30 | IOVDD | **+3V3** | 48 other pins |
| 31 | GPIO19 | **B_BOOTSEL** | R404.1, R407.2 |
| 32 | GPIO20 | **PD_SDA** | U102.3, R104.2 |
| 33 | GPIO21 | **PD_SCL** | U102.2, R103.2 |
| 34 | GPIO22 | **PD_PG** | U102.10, R102.2 |
| 35 | GPIO23 | **B_SWCLK** | U401.24, TP401.1 |
| 36 | GPIO24 | **B_SWDIO** | U401.25, TP402.1 |
| 37 | GPIO25 | no-connect flag | |
| 38 | IOVDD | **+3V3** | 48 other pins |
| 39 | DVDD | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 |
| 40 | GPIO26/ADC0 | **KBD_CC1** | J201.A5, U201.3, R201.2 |
| 41 | GPIO27/ADC1 | **KBD_CC2** | J201.B5, U201.4, R202.2 |
| 42 | GPIO28/ADC2 | **KBD_VBUS_SENSE** | R209.2, R210.1 |
| 43 | GPIO29/ADC3 | **POGO_5V_SENSE** | R607.2, R608.1 |
| 44 | ADC_AVDD | **+3V3** | 48 other pins |
| 45 | IOVDD | **+3V3** | 48 other pins |
| 46 | VREG_AVDD | A_VREG_AVDD | C303.1, R301.2 |
| 47 | VREG_PGND | **GND** | 141 other pins |
| 48 | VREG_LX | A_VREG_LX | L301.2 |
| 49 | VREG_VIN | **+3V3** | 48 other pins |
| 50 | VREG_FB | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 |
| 51 | USB_DM | **PC1_USB_D_N** | R216.2 |
| 52 | USB_DP | **PC1_USB_D_P** | R215.2 |
| 53 | USB_OTP_VDD | **+3V3** | 48 other pins |
| 54 | QSPI_IOVDD | **+3V3** | 48 other pins |
| 55 | QSPI_SD3 | no-connect flag | |
| 56 | QSPI_SCLK | no-connect flag | |
| 57 | QSPI_SD0 | no-connect flag | |
| 58 | QSPI_SD2 | no-connect flag | |
| 59 | QSPI_SD1 | no-connect flag | |
| 60 | QSPI_SS | A_QSPI_SS | R303.1 |
| 61 | GND | **GND** | 141 other pins |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| L301 | A_1V1 | A_VREG_LX |
| C301 | **+3V3** | **GND** |
| C302 | A_1V1 | **GND** |
| C303 | A_VREG_AVDD | **GND** |
| R301 | **+3V3** | A_VREG_AVDD |
| C304 | A_1V1 | **GND** |
| C305 | A_1V1 | **GND** |
| C306 | A_1V1 | **GND** |
| C307 | **+3V3** | **GND** |
| C308 | **+3V3** | **GND** |
| C309 | **+3V3** | **GND** |
| C310 | **+3V3** | **GND** |
| C311 | **+3V3** | **GND** |
| C312 | **+3V3** | **GND** |
| C313 | **+3V3** | **GND** |
| C314 | **+3V3** | **GND** |
| C315 | A_XIN | **GND** |
| C316 | A_XOUT_R | **GND** |
| R302 | A_XOUT | A_XOUT_R |
| R303 | A_QSPI_SS | A_BOOTSEL_BTN |
| SW301 | A_BOOTSEL_BTN | **GND** |
| SW302 | A_RUN | **GND** |
| R305 | A_LED | A_LED_R |
| D301 (1 = K, 2 = A) | **GND** | A_LED_R |

Crystal: Y301 → A_XIN is 4 pins — 1 = A_XIN, 3 = A_XOUT_R, 2 and 4 = GND. Test pads: TP301 → A_SWCLK, TP302 → A_SWDIO, TP303 → **GND**.

**Placement**

- U301 back-left; top side (regulator, USB pins) towards J202, left side towards J201.
- Run `copy_rpi_core_layout.py … U301`: it places L301, C301–C313, R301, Y301, C315, C316, R302 exactly as RPi does (inductor dot towards A_1V1) and copies the pours and tracks.
- C314 (10 µF) near U104's +3V3 feed into this chip. SW301/SW302 reachable from above; TP301–303 in a row.

---

## 6. MCU B (RP2354A)

Sheet `mcu_b.kicad_sch`. Same core as MCU A (B_ nets, U401 …). What differs: B has no reset button (A resets it), and A controls B's RUN, BOOTSEL and SWD.

```text
 (core: as MCU A, with U401, L401, C401–C416, R401, R402, Y401, B_* local nets)
 U401 pin 26 RUN ── B_RUN ◄── MCU A GPIO18 (open-drain);  R406 10 k to +3V3
 U401 pin 60 QSPI_SS ──●── B_QSPI_SS ── R403 1 k ── B_BOOTSEL_BTN ── SW401 ── GND     (BOOTSEL B)
                       └── R404 1 k ── B_BOOTSEL ◄── MCU A GPIO19 (open-drain);  R407 10 k to +3V3
 U401 pins 24/25 SWCLK/SWDIO ──●── B_SWCLK / B_SWDIO ◄── MCU A GPIO23 / GPIO24
                               └── TP401 / TP402;  TP403 ── GND
 U401 GPIO0 (UART0 TX) ── B_LINK_RX ──► MCU A GPIO17 (UART0 RX)
 U401 GPIO1 (UART0 RX) ◄── B_LINK_TX ◄── MCU A GPIO16 (UART0 TX)
 U401 GPIO2 ◄── PC2_VBUS_DET;   U401 GPIO3 ── B_LED ── R405 1 k ── D401 ── GND
 U401 pins 52/51 USB_DP/DM ── PC2_USB_D_P / PC2_USB_D_N (from R221/R222)
```

R406/R407 matter: at reset and in BOOTSEL mode, MCU A's pins are inputs with weak pull-downs. Without the 10 k pull-ups, B_RUN and B_BOOTSEL would sit at mid-level against B's weak internal pull-ups, and B could stay in reset or boot into BOOTSEL whenever A restarts.

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| U401 | RP2354A | `RP2350A_QFN-60_RPi_Vias` | C41378174 | B: Work PC device |
| L401 | 3.3uH | `L_Abracon_AOTA-B201610S3R3_0806` | C42411119 | pin 1 (dot) = +1V1, pin 2 = VREG_LX |
| C401 | 4.7uF | `C_0402_RPi_Wide` | C23733 | VREG_VIN (RPi C6) |
| C402 | 4.7uF | `C_0402_RPi_Wide` | C23733 | +1V1 output (RPi C7) |
| C403 | 4.7uF | `C_0402_1005Metric` | C23733 | VREG_AVDD (RPi C9) |
| R401 | 33 | `R_0402_1005Metric` | C25105 | 3V3 -> VREG_AVDD (RPi R3) |
| C404 | 100nF | `C_0402_1005Metric` | C1525 | DVDD 1 (+1V1) |
| C405 | 100nF | `C_0402_1005Metric` | C1525 | DVDD 2 (+1V1) |
| C406 | 100nF | `C_0402_1005Metric` | C1525 | DVDD 3 (+1V1) |
| C407 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C408 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C409 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C410 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C411 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C412 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C413 | 100nF | `C_0402_1005Metric` | C1525 | IOVDD / ADC / USB_OTP / QSPI (+3V3) |
| C414 | 10uF | `C_0805_2012Metric` | C15850 | +3V3 bulk |
| Y401 | 12MHz | `Crystal_SMD_3225-4Pin_3.2x2.5mm` | C20625731 | ABM8-272-T3 (10 pF, 50 ohm) |
| C415 | 15pF | `C_0402_1005Metric` | C1548 | XIN load |
| C416 | 15pF | `C_0402_1005Metric` | C1548 | XOUT load |
| R402 | 1k | `R_0402_1005Metric` | C11702 | XOUT series (RPi R2) |
| SW401 | SW_Push | `SW_Push_1P1T_XKB_TS-1187A` | C318884 | BOOTSEL B |
| R403 | 1k | `R_0402_1005Metric` | C11702 | QSPI_SS -> BOOTSEL button |
| R404 | 1k | `R_0402_1005Metric` | C11702 | QSPI_SS <- B_BOOTSEL from MCU A |
| R406 | 10k | `R_0402_1005Metric` | C25744 | B_RUN pull-up (beats A pull-down at reset) |
| R407 | 10k | `R_0402_1005Metric` | C25744 | B_BOOTSEL pull-up (beats A pull-down) |
| TP401 | TestPoint | `TestPoint_Pad_D1.0mm` | — | SWCLK |
| TP402 | TestPoint | `TestPoint_Pad_D1.0mm` | — | SWDIO |
| TP403 | TestPoint | `TestPoint_Pad_D1.0mm` | — | GND |
| D401 | LED red | `LED_0603_1608Metric` | C2286 | status LED |
| R405 | 1k | `R_0402_1005Metric` | C11702 | LED series |

**Pin map — MCU B GPIOs**

| GPIO | Pin | Net | Goes to |
|---|---|---|---|
| GPIO0 | 2 | **B_LINK_RX** | UART0 TX → A GPIO17 |
| GPIO1 | 3 | **B_LINK_TX** | UART0 RX ← A GPIO16 |
| GPIO2 | 4 | **PC2_VBUS_DET** | J203 VBUS divider (R219/R220) |
| GPIO3 | 5 | B_LED | R405 → D401 |
| GPIO4–29 | … | spare (no-connect flags) | |

**Wiring — U401**

| U401 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | IOVDD | **+3V3** | 48 other pins |
| 2 | GPIO0 | **B_LINK_RX** | U301.28 |
| 3 | GPIO1 | **B_LINK_TX** | U301.27 |
| 4 | GPIO2 | **PC2_VBUS_DET** | R219.2, R220.1 |
| 5 | GPIO3 | B_LED | R405.1 |
| 6 | DVDD | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 |
| 7 | GPIO4 | no-connect flag | |
| 8 | GPIO5 | no-connect flag | |
| 9 | GPIO6 | no-connect flag | |
| 10 | GPIO7 | no-connect flag | |
| 11 | IOVDD | **+3V3** | 48 other pins |
| 12 | GPIO8 | no-connect flag | |
| 13 | GPIO9 | no-connect flag | |
| 14 | GPIO10 | no-connect flag | |
| 15 | GPIO11 | no-connect flag | |
| 16 | GPIO12 | no-connect flag | |
| 17 | GPIO13 | no-connect flag | |
| 18 | GPIO14 | no-connect flag | |
| 19 | GPIO15 | no-connect flag | |
| 20 | IOVDD | **+3V3** | 48 other pins |
| 21 | XIN | B_XIN | Y401.1, C415.1 |
| 22 | XOUT | B_XOUT | R402.1 |
| 23 | DVDD | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 |
| 24 | SWCLK | **B_SWCLK** | U301.35, TP401.1 |
| 25 | SWDIO | **B_SWDIO** | U301.36, TP402.1 |
| 26 | RUN | **B_RUN** | U301.29, R406.2 |
| 27 | GPIO16 | no-connect flag | |
| 28 | GPIO17 | no-connect flag | |
| 29 | GPIO18 | no-connect flag | |
| 30 | IOVDD | **+3V3** | 48 other pins |
| 31 | GPIO19 | no-connect flag | |
| 32 | GPIO20 | no-connect flag | |
| 33 | GPIO21 | no-connect flag | |
| 34 | GPIO22 | no-connect flag | |
| 35 | GPIO23 | no-connect flag | |
| 36 | GPIO24 | no-connect flag | |
| 37 | GPIO25 | no-connect flag | |
| 38 | IOVDD | **+3V3** | 48 other pins |
| 39 | DVDD | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 |
| 40 | GPIO26/ADC0 | no-connect flag | |
| 41 | GPIO27/ADC1 | no-connect flag | |
| 42 | GPIO28/ADC2 | no-connect flag | |
| 43 | GPIO29/ADC3 | no-connect flag | |
| 44 | ADC_AVDD | **+3V3** | 48 other pins |
| 45 | IOVDD | **+3V3** | 48 other pins |
| 46 | VREG_AVDD | B_VREG_AVDD | C403.1, R401.2 |
| 47 | VREG_PGND | **GND** | 141 other pins |
| 48 | VREG_LX | B_VREG_LX | L401.2 |
| 49 | VREG_VIN | **+3V3** | 48 other pins |
| 50 | VREG_FB | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 |
| 51 | USB_DM | **PC2_USB_D_N** | R222.2 |
| 52 | USB_DP | **PC2_USB_D_P** | R221.2 |
| 53 | USB_OTP_VDD | **+3V3** | 48 other pins |
| 54 | QSPI_IOVDD | **+3V3** | 48 other pins |
| 55 | QSPI_SD3 | no-connect flag | |
| 56 | QSPI_SCLK | no-connect flag | |
| 57 | QSPI_SD0 | no-connect flag | |
| 58 | QSPI_SD2 | no-connect flag | |
| 59 | QSPI_SD1 | no-connect flag | |
| 60 | QSPI_SS | B_QSPI_SS | R403.1, R404.2 |
| 61 | GND | **GND** | 141 other pins |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| L401 | B_1V1 | B_VREG_LX |
| C401 | **+3V3** | **GND** |
| C402 | B_1V1 | **GND** |
| C403 | B_VREG_AVDD | **GND** |
| R401 | **+3V3** | B_VREG_AVDD |
| C404 | B_1V1 | **GND** |
| C405 | B_1V1 | **GND** |
| C406 | B_1V1 | **GND** |
| C407 | **+3V3** | **GND** |
| C408 | **+3V3** | **GND** |
| C409 | **+3V3** | **GND** |
| C410 | **+3V3** | **GND** |
| C411 | **+3V3** | **GND** |
| C412 | **+3V3** | **GND** |
| C413 | **+3V3** | **GND** |
| C414 | **+3V3** | **GND** |
| C415 | B_XIN | **GND** |
| C416 | B_XOUT_R | **GND** |
| R402 | B_XOUT | B_XOUT_R |
| R403 | B_QSPI_SS | B_BOOTSEL_BTN |
| R404 | **B_BOOTSEL** | B_QSPI_SS |
| R406 | **+3V3** | **B_RUN** |
| R407 | **+3V3** | **B_BOOTSEL** |
| SW401 | B_BOOTSEL_BTN | **GND** |
| R405 | B_LED | B_LED_R |
| D401 (1 = K, 2 = A) | **GND** | B_LED_R |

Crystal: Y401 → B_XIN (1 = B_XIN, 3 = B_XOUT_R, 2 and 4 = GND). Test pads: TP401 → **B_SWCLK**, TP402 → **B_SWDIO**, TP403 → **GND**.

**Placement**

- U401 back-right; top side towards J203. Its left side (GPIO0–3) faces MCU A.
- `copy_rpi_core_layout.py … U401` for the core.
- R406/R407 near U401 (RUN pin 26, QSPI_SS pin 60); R404 at QSPI_SS.

---

## 7. BLE (ESP32-C3-MINI-1)

Sheet `ble.kicad_sch`.

```text
 +3V3 ──●── U501 pin 3 3V3;  C502 10 µF, C503 100 nF ── GND (at pin 3)
        ├── R501 10 k ──●── BLE_EN ── U501 pin 8 EN;  C501 1 µF ── GND;  ◄── MCU A GPIO10 (open-drain)
        ├── R504 10 k ──●── BLE_BOOT ── U501 pin 23 GPIO9 ◄── MCU A GPIO11 (open-drain; low at reset = download mode)
        ├── R502 10 k ──── BLE_GPIO8 ── U501 pin 22 GPIO8   (must be high for UART download)
        └── R503 10 k ──── BLE_GPIO2 ── U501 pin 5 GPIO2    (Espressif: keep high)
 U501 pin 30 RXD0 ◄── BLE_TX ◄── MCU A GPIO8 (UART1 TX);  TP504
 U501 pin 31 TXD0 ──► BLE_RX ──► MCU A GPIO9 (UART1 RX);  TP503
 U501 pin 26 GPIO18 (USB D−) ── TP501;  pin 27 GPIO19 (USB D+) ── TP502;  TP505 ── GND
 GND pins 1, 2, 11, 14, 36–53 ── GND;  NC and unused GPIOs: no-connect flags
```

R504 is needed for the same reason as R406/R407: the ESP32's GPIO9 pull-up is weak, and A's reset-state pull-down could drag it low and start the ESP32 in download mode.

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| U501 | ESP32-C3-MINI-1-H4X | `ESP32-C3-MINI-1` | C41349510 | BLE; UART0 to MCU A UART1 |
| C502 | 10uF | `C_0805_2012Metric` | C15850 | 3V3 bulk |
| C503 | 100nF | `C_0402_1005Metric` | C1525 | 3V3 at pin 3 |
| R501 | 10k | `R_0402_1005Metric` | C25744 | EN pull-up (also MCU A, open-drain) |
| C501 | 1uF | `C_0402_1005Metric` | C52923 | EN RC delay |
| R502 | 10k | `R_0402_1005Metric` | C25744 | GPIO8 pull-up |
| R503 | 10k | `R_0402_1005Metric` | C25744 | GPIO2 pull-up |
| R504 | 10k | `R_0402_1005Metric` | C25744 | GPIO9 (BOOT) pull-up, beats A pull-down |
| TP501 | TestPoint | `TestPoint_Pad_D1.0mm` | — | GPIO18 USB_D- |
| TP502 | TestPoint | `TestPoint_Pad_D1.0mm` | — | GPIO19 USB_D+ |
| TP503 | TestPoint | `TestPoint_Pad_D1.0mm` | — | TXD0 |
| TP504 | TestPoint | `TestPoint_Pad_D1.0mm` | — | RXD0 |
| TP505 | TestPoint | `TestPoint_Pad_D1.0mm` | — | GND |

**Wiring — U501**

| U501 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | GND | **GND** | 121 other pins |
| 2 | GND | **GND** | 121 other pins |
| 3 | 3V3 | **+3V3** | 57 other pins |
| 4 | NC | no-connect flag | |
| 5 | GPIO2/ADC1_CH2 | BLE_GPIO2 | R503.2 |
| 6 | GPIO3/ADC1_CH3 | no-connect flag | |
| 7 | NC | no-connect flag | |
| 8 | EN/CHIP_PU | **BLE_EN** | U301.14, R501.2, C501.1 |
| 9 | NC | no-connect flag | |
| 10 | NC | no-connect flag | |
| 11 | GND | **GND** | 121 other pins |
| 12 | GPIO0/ADC1_CH0/XTAL_32K_P | no-connect flag | |
| 13 | GPIO1/ADC1_CH1/XTAL_32K_N | no-connect flag | |
| 14 | GND | **GND** | 121 other pins |
| 15 | NC | no-connect flag | |
| 16 | GPIO10 | no-connect flag | |
| 17 | NC | no-connect flag | |
| 18 | GPIO4/ADC1_CH4 | no-connect flag | |
| 19 | GPIO5/ADC2_CH0 | no-connect flag | |
| 20 | GPIO6 | no-connect flag | |
| 21 | GPIO7 | no-connect flag | |
| 22 | GPIO8 | BLE_GPIO8 | R502.2 |
| 23 | GPIO9 | **BLE_BOOT** | U301.15, R504.2 |
| 24 | NC | no-connect flag | |
| 25 | NC | no-connect flag | |
| 26 | GPIO18/USB_D- | **BLE_USB_D_N** | TP501.1 |
| 27 | GPIO19/USB_D+ | **BLE_USB_D_P** | TP502.1 |
| 28 | NC | no-connect flag | |
| 29 | NC | no-connect flag | |
| 30 | GPIO20/U0RXD | **BLE_TX** | U301.12, TP504.1 |
| 31 | GPIO21/U0TXD | **BLE_RX** | U301.13, TP503.1 |
| 32 | NC | no-connect flag | |
| 33 | NC | no-connect flag | |
| 34 | NC | no-connect flag | |
| 35 | NC | no-connect flag | |
| 36 | GND | **GND** | 121 other pins |
| 37 | GND | **GND** | 121 other pins |
| 38 | GND | **GND** | 121 other pins |
| 39 | GND | **GND** | 121 other pins |
| 40 | GND | **GND** | 121 other pins |
| 41 | GND | **GND** | 121 other pins |
| 42 | GND | **GND** | 121 other pins |
| 43 | GND | **GND** | 121 other pins |
| 44 | GND | **GND** | 121 other pins |
| 45 | GND | **GND** | 121 other pins |
| 46 | GND | **GND** | 121 other pins |
| 47 | GND | **GND** | 121 other pins |
| 48 | GND | **GND** | 121 other pins |
| 49 | GND | **GND** | 121 other pins |
| 50 | GND | **GND** | 121 other pins |
| 51 | GND | **GND** | 121 other pins |
| 52 | GND | **GND** | 121 other pins |
| 53 | GND | **GND** | 121 other pins |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| C502 | **+3V3** | **GND** |
| C503 | **+3V3** | **GND** |
| R501 | **+3V3** | **BLE_EN** |
| C501 | **BLE_EN** | **GND** |
| R502 | **+3V3** | BLE_GPIO8 |
| R503 | **+3V3** | BLE_GPIO2 |
| R504 | **+3V3** | **BLE_BOOT** |

Test pads: TP501 → **BLE_USB_D_N**, TP502 → **BLE_USB_D_P**, TP503 → **BLE_RX**, TP504 → **BLE_TX**, TP505 → **GND**.

**Placement**

- Left edge, front half, **antenna end on the board edge**. The footprint's keep-out: no copper on any layer, no parts under or in front of the antenna. Keep pogo magnets and screws ≥ 15 mm away.
- C502/C503 at pin 3; R501/C501 at pin 8. Test pads where a probe or USB lead can reach.

---

## 8. Pogo interface

Sheet `pogo.kicad_sch`. **7 contacts**, dock side: `GND | +5V | +5V | DET | RX | TX | GND`; pad pin 1 meets dock pin 7 (the pad's pogo board is the mirror: `GND | TX | RX | DET | +5V | +5V | GND`). Two contacts each for +5V and GND: the contacts are rated 1 A, so the pad can draw up to ≈ 1.45 A (the switch limit) with no LED dimming.

```text
 J601 pin 1, pin 7 ── GND
 J601 pins 2 and 3 (+5V, +5V) ──●── POGO_5V ◄── U602 pin 1 OUT (SY6280)
                    ├── C602 10 µF, C603 1 µF ── GND
                    └── R607 10 k ──●── POGO_5V_SENSE ──► MCU A GPIO29 (ADC3)
                                    └── R608 15 k ── GND
 +5V ──●── U602 pin 5 IN;  C601 1 µF ── GND        U602 pin 3 ISET ── R606 4.7 k ── GND (1.45 A)
 U602 pin 4 EN ──●── POGO_EN ── R605 100 k ── +3V3
                 ├── Q601 drain   (Q601 gate = POGO_DET, source = GND)
                 └── Q602 drain   (Q602 gate = POGO_OFF ◄── MCU A GPIO15, R609 100 k to GND; source = GND)
 J601 pin 4 (DET) ──●── POGO_DET_J ── R603 1 k ──●── POGO_DET ──► MCU A GPIO14, Q601 gate
                    └── U601 pin 3 (ESD)         └── R604 10 k ── +3V3
 J601 pin 5 (RX)  ──●── POGO_RX_J ── R602 1 k ── POGO_RX ──► MCU A GPIO13 (PIO UART RX)
                    └── U601 pin 6
 J601 pin 6 (TX)  ──●── POGO_TX_J ── R601 1 k ── POGO_TX ◄── MCU A GPIO12 (PIO UART TX)
                    └── U601 pin 1
 U601 pin 2 ── GND;  pins 4, 5: no-connect
```

How the enable works: undocked, DET is pulled up → Q601 on → EN low → contacts dead. Docked, the pad grounds DET → Q601 off → R605 pulls EN high → 5 V on, **with no firmware**. MCU A can veto by driving POGO_OFF high (Q602 on). Q602 exists so that A's reset-state pull-down on GPIO15 means "no veto": a direct connection to EN would drag it to ≈ 1.1 V and stop pad charging whenever A has no firmware.

**Parts**

| Ref | Value | Footprint | LCSC | Job |
|---|---|---|---|---|
| J601 | Pogo 7-pin | `Pogo-7` | — | HAND-SOLDER: Motorobit 7-pin 90deg magnetic (order: guide §8) |
| U601 | TPD4E1U06DBVR | `SOT-23-6` | C124691 | ESD on DET, TX, RX (1 spare) |
| R601 | 1k | `R_0402_1005Metric` | C11702 | TX series |
| R602 | 1k | `R_0402_1005Metric` | C11702 | RX series |
| R603 | 1k | `R_0402_1005Metric` | C11702 | DET series |
| U602 | SY6280AAC | `SOT-23-5` | C55136 | POGO_5V switch |
| Q601 | 2N7002 | `SOT-23` | C8545 | DET inverter -> U602 EN |
| Q602 | 2N7002 | `SOT-23` | C8545 | POGO_OFF veto: pulls EN low |
| R604 | 10k | `R_0402_1005Metric` | C25744 | DET pull-up to 3V3 |
| R605 | 100k | `R_0402_1005Metric` | C25741 | EN pull-up to 3V3 |
| R606 | 4.7k | `R_0402_1005Metric` | C25900 | ISET: 6800/4700 = 1.45 A (1.09-1.81 A); 2 x 1 A +5V contacts |
| R609 | 100k | `R_0402_1005Metric` | C25741 | Q602 gate pull-down (no veto at reset) |
| C601 | 1uF | `C_0402_1005Metric` | C52923 | U602 input |
| C602 | 10uF | `C_0805_2012Metric` | C15850 | POGO_5V output |
| C603 | 1uF | `C_0402_1005Metric` | C52923 | POGO_5V output |
| R607 | 10k | `R_0402_1005Metric` | C25744 | POGO_5V divider top -> ADC |
| R608 | 15k | `R_0402_1005Metric` | C25756 | POGO_5V divider bottom |

**Wiring**

| J601 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | Pin_1 | **GND** | 141 other pins |
| 2 | Pin_2 | **POGO_5V** | U602.1, C602.1, C603.1, R607.1 |
| 3 | Pin_3 | **POGO_5V** | U602.1, C602.1, C603.1, R607.1 |
| 4 | Pin_4 | POGO_DET_J | U601.3, R603.1 |
| 5 | Pin_5 | POGO_RX_J | U601.6, R602.1 |
| 6 | Pin_6 | POGO_TX_J | U601.1, R601.2 |
| 7 | Pin_7 | **GND** | 141 other pins |

| U601 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | D1+ | POGO_TX_J | J601.6, R601.2 |
| 2 | GND | **GND** | 142 other pins |
| 3 | D2+ | POGO_DET_J | J601.4, R603.1 |
| 4 | D2- | no-connect flag | |
| 5 | NC | no-connect flag | |
| 6 | D1- | POGO_RX_J | J601.5, R602.1 |

| U602 pin | Name | Net | Also on this net |
|---|---|---|---|
| 1 | OUT | **POGO_5V** | J601.2, J601.3, C602.1, C603.1, R607.1 |
| 2 | GND | **GND** | 142 other pins |
| 3 | ISET | POGO_ISET | R606.1 |
| 4 | EN | POGO_EN | Q601.3, Q602.3, R605.2 |
| 5 | IN | **+5V** | 10 other pins |

| Part | Gate (1) | Source (2) | Drain (3) |
|---|---|---|---|
| Q601 | **POGO_DET** | **GND** | POGO_EN |
| Q602 | **POGO_OFF** | **GND** | POGO_EN |

| Part | Pin 1 | Pin 2 |
|---|---|---|
| R601 | **POGO_TX** | POGO_TX_J |
| R602 | POGO_RX_J | **POGO_RX** |
| R603 | POGO_DET_J | **POGO_DET** |
| R604 | **+3V3** | **POGO_DET** |
| R605 | **+3V3** | POGO_EN |
| R606 | POGO_ISET | **GND** |
| R609 | **POGO_OFF** | **GND** |
| C601 | **+5V** | **GND** |
| C602 | **POGO_5V** | **GND** |
| C603 | **POGO_5V** | **GND** |
| R607 | **POGO_5V** | **POGO_5V_SENSE** |
| R608 | **POGO_5V_SENSE** | **GND** |

**Placement**

- J601 at the front edge, centre: Motorobit **7-pin 2.54 mm 90° magnetic set with ears** (a straight 7-pin version exists for the pad-on-top alternative, PCB_PLACEMENT.md §4). Hand-soldered. Footprint `dock:Pogo-7` is scaled from Pogo-6: check the body and ears against the delivered part.
- U601 right at J601; R601–R603 between U601 and the MCU A traces.
- U602, Q601, Q602 and their resistors behind J601; C602/C603 at J601 pins 2–3. Join pins 2 and 3 with a wide trace (Power class) right at the connector so both contacts share the current.
- POGO_5V is Power class. Mark pin 1 on the silkscreen.

---

## 9. Signals that cross between sheets

Use a **global label** with exactly these names (the power nets GND, +3V3 and +5V are power symbols).

| Net | Sheets | Pins |
|---|---|---|
| BLE_BOOT | BLE, MCU_A | U301.15, U501.23, R504.2 |
| BLE_EN | BLE, MCU_A | U301.14, U501.8, R501.2, C501.1 |
| BLE_RX | BLE, MCU_A | U301.13, U501.31, TP503.1 |
| BLE_TX | BLE, MCU_A | U301.12, U501.30, TP504.1 |
| B_BOOTSEL | MCU_A, MCU_B | U301.31, R404.1, R407.2 |
| B_LINK_RX | MCU_A, MCU_B | U301.28, U401.2 |
| B_LINK_TX | MCU_A, MCU_B | U301.27, U401.3 |
| B_RUN | MCU_A, MCU_B | U301.29, U401.26, R406.2 |
| B_SWCLK | MCU_A, MCU_B | U301.35, U401.24, TP401.1 |
| B_SWDIO | MCU_A, MCU_B | U301.36, U401.25, TP402.1 |
| KBD_CC1 | MCU_A, USB_PORTS | J201.A5, U201.3, R201.2, U301.40 |
| KBD_CC2 | MCU_A, USB_PORTS | J201.B5, U201.4, R202.2, U301.41 |
| KBD_USB_D_N | MCU_A, USB_PORTS | R206.2, U301.10 |
| KBD_USB_D_P | MCU_A, USB_PORTS | R205.2, U301.9 |
| KBD_VBUS_EN | MCU_A, USB_PORTS | U202.4, R208.1, U301.8 |
| KBD_VBUS_SENSE | MCU_A, USB_PORTS | R209.2, R210.1, U301.42 |
| PC1_USB_D_N | MCU_A, USB_PORTS | R216.2, U301.51 |
| PC1_USB_D_P | MCU_A, USB_PORTS | R215.2, U301.52 |
| PC1_VBUS_DET | MCU_A, USB_PORTS | R213.2, R214.1, U301.2 |
| PC2_USB_D_N | MCU_B, USB_PORTS | R222.2, U401.51 |
| PC2_USB_D_P | MCU_B, USB_PORTS | R221.2, U401.52 |
| PC2_VBUS_DET | MCU_B, USB_PORTS | R219.2, R220.1, U401.4 |
| PD_PG | MCU_A, POWER | U102.10, R102.2, U301.34 |
| PD_SCL | MCU_A, POWER | U102.2, R103.2, U301.33 |
| PD_SDA | MCU_A, POWER | U102.3, R104.2, U301.32 |
| POGO_5V_SENSE | MCU_A, POGO | U301.43, R607.2, R608.1 |
| POGO_DET | MCU_A, POGO | U301.18, R603.2, Q601.1, R604.2 |
| POGO_OFF | MCU_A, POGO | U301.19, Q602.1, R609.1 |
| POGO_RX | MCU_A, POGO | U301.17, R602.2 |
| POGO_TX | MCU_A, POGO | U301.16, R601.1 |

---

## 10. Board-wide rules, PWR_FLAGs and no-connects

- **Power symbols** (`power:` library) only for GND, +3V3, +5V. VBUS_IN, KBD_VBUS and POGO_5V are global labels (Power net class by name).
- **PWR_FLAG** (so ERC knows these nets are supplied): VBUS_IN (J101 is a passive connector), +5V (comes out of an inductor), A_1V1 and B_1V1 (out of an inductor), A_VREG_AVDD and B_VREG_AVDD (through a resistor). +3V3, KBD_VBUS and POGO_5V are driven by power-output pins.
- **Local vs global**: A_* and B_* core nets (1V1, VREG_LX, VREG_AVDD, XIN, XOUT, XOUT_R, QSPI_SS, BOOTSEL_BTN, LED, LED_R, RUN, SWCLK/SWDIO of A), BUCK_*, PD_CFG1, KBD_ISET, POGO_ISET, POGO_EN, POGO_*_J and the *_USBJ_* connector-side pairs stay on their sheet.
- Net classes (project file): Power = VBUS_IN, +5V, +3V3, KBD_VBUS, POGO_5V, GND (0.6 mm); USB = `*USB*_D_P` / `*USB*_D_N` (both the connector side `*_USBJ_*` and the MCU side); everything else Default. Clearance 0.15 mm everywhere (RPi core layout).
- 4 layers: L1 parts + signals, **L2 solid GND**, L3 +3V3 / +5V pours, L4 signals. All SMD on top; only C201 and J601 are through-hole (hand-soldered).
- BUCK_SW is the noisiest net on the board: short, wide, away from BUCK_FB, crystals and the antenna.

**No-connect flags** (put an X on each):

- **J101**: A8 (SBU1), B8 (SBU2)
- **U101**: 5 (NC)
- **U103**: 3 (EN)
- **J201**: A8 (SBU1), B8 (SBU2)
- **U201**: 5 (NC)
- **J202**: A8 (SBU1), B8 (SBU2)
- **U203**: 5 (NC)
- **J203**: A8 (SBU1), B8 (SBU2)
- **U204**: 5 (NC)
- **U301**: 55 (QSPI_SD3), 56 (QSPI_SCLK), 57 (QSPI_SD0), 58 (QSPI_SD2), 59 (QSPI_SD1), 3 (GPIO1), 5 (GPIO3), 7 (GPIO4), 37 (GPIO25)
- **U401**: 55 (QSPI_SD3), 56 (QSPI_SCLK), 57 (QSPI_SD0), 58 (QSPI_SD2), 59 (QSPI_SD1), 7 (GPIO4), 8 (GPIO5), 9 (GPIO6), 10 (GPIO7), 12 (GPIO8), 13 (GPIO9), 14 (GPIO10), 15 (GPIO11), 16 (GPIO12), 17 (GPIO13), 18 (GPIO14), 19 (GPIO15), 27 (GPIO16), 28 (GPIO17), 29 (GPIO18), 31 (GPIO19), 32 (GPIO20), 33 (GPIO21), 34 (GPIO22), 35 (GPIO23), 36 (GPIO24), 37 (GPIO25), 40 (GPIO26/ADC0), 41 (GPIO27/ADC1), 42 (GPIO28/ADC2), 43 (GPIO29/ADC3)
- **U501**: 4 (NC), 7 (NC), 9 (NC), 10 (NC), 15 (NC), 17 (NC), 24 (NC), 25 (NC), 28 (NC), 29 (NC), 32 (NC), 33 (NC), 34 (NC), 35 (NC), 6 (GPIO3/ADC1_CH3), 12 (GPIO0/ADC1_CH0/XTAL_32K_P), 13 (GPIO1/ADC1_CH1/XTAL_32K_N), 16 (GPIO10), 18 (GPIO4/ADC1_CH4), 19 (GPIO5/ADC2_CH0), 20 (GPIO6), 21 (GPIO7)
- **U601**: 4 (D2-), 5 (NC)

---

## Appendix — full net index (generated)

Generated from the connection model that the tables above come from; checked against the placed schematic (every pin exactly once).

<details>
<summary>Show the full net index</summary>

| Net | Pins (ref.pin name) |
|---|---|
| GND | 143 pins (every GND pin, shield and exposed pad) |
| +3V3 | R102.1, R103.1, R104.1, U104.2 (VO), C112.1, R201.1, R202.1, U301.1 (IOVDD), U301.11 (IOVDD), U301.20 (IOVDD), U301.30 (IOVDD), U301.38 (IOVDD), U301.45 (IOVDD), U301.44 (ADC_AVDD), U301.49 (VREG_VIN), U301.53 (USB_OTP_VDD), U301.54 (QSPI_IOVDD), C301.1, R301.1, C307.1, C308.1, C309.1, C310.1, C311.1, C312.1, C313.1, C314.1, U401.1 (IOVDD), U401.11 (IOVDD), U401.20 (IOVDD), U401.30 (IOVDD), U401.38 (IOVDD), U401.45 (IOVDD), U401.44 (ADC_AVDD), U401.49 (VREG_VIN), U401.53 (USB_OTP_VDD), U401.54 (QSPI_IOVDD), C401.1, R401.1, C407.1, C408.1, C409.1, C410.1, C411.1, C412.1, C413.1, C414.1, R406.1, R407.1, U501.3 (3V3), C502.1, C503.1, R501.1, R502.1, R503.1, R504.1, R604.1, R605.1 |
| +5V | R106.1, L101.2, C108.1, C109.1, C110.1, U104.3 (VI), C111.1, U202.5 (IN), C204.1, U602.5 (IN), C601.1 |
| A_1V1 | U301.6 (DVDD), U301.23 (DVDD), U301.39 (DVDD), U301.50 (VREG_FB), L301.1, C302.1, C304.1, C305.1, C306.1 |
| A_BOOTSEL_BTN | R303.2, SW301.1 |
| A_LED | R305.1, U301.4 (GPIO2) |
| A_LED_R | R305.2, D301.2 (A) |
| A_QSPI_SS | U301.60 (QSPI_SS), R303.1 |
| A_RUN | U301.26 (RUN), SW302.1 |
| A_SWCLK | U301.24 (SWCLK), TP301.1 |
| A_SWDIO | U301.25 (SWDIO), TP302.1 |
| A_VREG_AVDD | U301.46 (VREG_AVDD), C303.1, R301.2 |
| A_VREG_LX | U301.48 (VREG_LX), L301.2 |
| A_XIN | U301.21 (XIN), Y301.1, C315.1 |
| A_XOUT | U301.22 (XOUT), R302.1 |
| A_XOUT_R | Y301.3, C316.1, R302.2 |
| BLE_BOOT | U301.15 (GPIO11), U501.23 (GPIO9), R504.2 |
| BLE_EN | U301.14 (GPIO10), U501.8 (EN/CHIP_PU), R501.2, C501.1 |
| BLE_GPIO2 | U501.5 (GPIO2/ADC1_CH2), R503.2 |
| BLE_GPIO8 | U501.22 (GPIO8), R502.2 |
| BLE_RX | U301.13 (GPIO9), U501.31 (GPIO21/U0TXD), TP503.1 |
| BLE_TX | U301.12 (GPIO8), U501.30 (GPIO20/U0RXD), TP504.1 |
| BLE_USB_D_N | U501.26 (GPIO18/USB_D-), TP501.1 |
| BLE_USB_D_P | U501.27 (GPIO19/USB_D+), TP502.1 |
| BUCK_BOOT | U103.1 (BOOT), C104.1 |
| BUCK_COMP | U103.6 (COMP), R105.1, C107.1 |
| BUCK_COMP_RC | R105.2, C106.1 |
| BUCK_FB | U103.5 (VSENSE), R106.2, R107.1 |
| BUCK_SS | U103.4 (SS), C105.1 |
| BUCK_SW | U103.8 (PH), C104.2, D102.1 (K), L101.1 |
| B_1V1 | U401.6 (DVDD), U401.23 (DVDD), U401.39 (DVDD), U401.50 (VREG_FB), L401.1, C402.1, C404.1, C405.1, C406.1 |
| B_BOOTSEL | U301.31 (GPIO19), R404.1, R407.2 |
| B_BOOTSEL_BTN | R403.2, SW401.1 |
| B_LED | R405.1, U401.5 (GPIO3) |
| B_LED_R | R405.2, D401.2 (A) |
| B_LINK_RX | U301.28 (GPIO17), U401.2 (GPIO0) |
| B_LINK_TX | U301.27 (GPIO16), U401.3 (GPIO1) |
| B_QSPI_SS | U401.60 (QSPI_SS), R403.1, R404.2 |
| B_RUN | U301.29 (GPIO18), U401.26 (RUN), R406.2 |
| B_SWCLK | U301.35 (GPIO23), U401.24 (SWCLK), TP401.1 |
| B_SWDIO | U301.36 (GPIO24), U401.25 (SWDIO), TP402.1 |
| B_VREG_AVDD | U401.46 (VREG_AVDD), C403.1, R401.2 |
| B_VREG_LX | U401.48 (VREG_LX), L401.2 |
| B_XIN | U401.21 (XIN), Y401.1, C415.1 |
| B_XOUT | U401.22 (XOUT), R402.1 |
| B_XOUT_R | Y401.3, C416.1, R402.2 |
| KBD_CC1 | J201.A5 (CC1), U201.3 (D2+), R201.2, U301.40 (GPIO26/ADC0) |
| KBD_CC2 | J201.B5 (CC2), U201.4 (D2-), R202.2, U301.41 (GPIO27/ADC1) |
| KBD_ISET | U202.3 (ISET), R207.1 |
| KBD_USBJ_D_N | J201.A7 (D-), J201.B7 (D-), U201.6 (D1-), R204.1, R206.1 |
| KBD_USBJ_D_P | J201.A6 (D+), J201.B6 (D+), U201.1 (D1+), R203.1, R205.1 |
| KBD_USB_D_N | R206.2, U301.10 (GPIO7) |
| KBD_USB_D_P | R205.2, U301.9 (GPIO6) |
| KBD_VBUS | J201.A4 (VBUS), J201.A9 (VBUS), J201.B4 (VBUS), J201.B9 (VBUS), U202.1 (OUT), C201.1, C202.1, C203.1, R209.1 |
| KBD_VBUS_EN | U202.4 (EN), R208.1, U301.8 (GPIO5) |
| KBD_VBUS_SENSE | R209.2, R210.1, U301.42 (GPIO28/ADC2) |
| PC1_CC1 | J202.A5 (CC1), U203.3 (D2+), R211.1 |
| PC1_CC2 | J202.B5 (CC2), U203.4 (D2-), R212.1 |
| PC1_USBJ_D_N | J202.A7 (D-), J202.B7 (D-), U203.6 (D1-), R216.1 |
| PC1_USBJ_D_P | J202.A6 (D+), J202.B6 (D+), U203.1 (D1+), R215.1 |
| PC1_USB_D_N | R216.2, U301.51 (USB_DM) |
| PC1_USB_D_P | R215.2, U301.52 (USB_DP) |
| PC1_VBUS | J202.A4 (VBUS), J202.A9 (VBUS), J202.B4 (VBUS), J202.B9 (VBUS), R213.1 |
| PC1_VBUS_DET | R213.2, R214.1, U301.2 (GPIO0) |
| PC2_CC1 | J203.A5 (CC1), U204.3 (D2+), R217.1 |
| PC2_CC2 | J203.B5 (CC2), U204.4 (D2-), R218.1 |
| PC2_USBJ_D_N | J203.A7 (D-), J203.B7 (D-), U204.6 (D1-), R222.1 |
| PC2_USBJ_D_P | J203.A6 (D+), J203.B6 (D+), U204.1 (D1+), R221.1 |
| PC2_USB_D_N | R222.2, U401.51 (USB_DM) |
| PC2_USB_D_P | R221.2, U401.52 (USB_DP) |
| PC2_VBUS | J203.A4 (VBUS), J203.A9 (VBUS), J203.B4 (VBUS), J203.B9 (VBUS), R219.1 |
| PC2_VBUS_DET | R219.2, R220.1, U401.4 (GPIO2) |
| PD_CC1 | J101.A5 (CC1), U101.3 (D2+), U102.7 (CC1) |
| PD_CC2 | J101.B5 (CC2), U101.4 (D2-), U102.6 (CC2) |
| PD_CFG1 | U102.9 (CFG1), R101.1 |
| PD_DM | J101.A7 (D-), J101.B7 (D-), U101.6 (D1-), U102.5 (DM) |
| PD_DP | J101.A6 (D+), J101.B6 (D+), U101.1 (D1+), U102.4 (DP) |
| PD_PG | U102.10 (PG), R102.2, U301.34 (GPIO22) |
| PD_SCL | U102.2 (CFG2/SCL), R103.2, U301.33 (GPIO21) |
| PD_SDA | U102.3 (CFG3/SDA), R104.2, U301.32 (GPIO20) |
| POGO_5V | J601.2 (Pin_2), J601.3 (Pin_3), U602.1 (OUT), C602.1, C603.1, R607.1 |
| POGO_5V_SENSE | U301.43 (GPIO29/ADC3), R607.2, R608.1 |
| POGO_DET | U301.18 (GPIO14), R603.2, Q601.1 (G), R604.2 |
| POGO_DET_J | J601.4 (Pin_4), U601.3 (D2+), R603.1 |
| POGO_EN | U602.4 (EN), Q601.3 (D), Q602.3 (D), R605.2 |
| POGO_ISET | U602.3 (ISET), R606.1 |
| POGO_OFF | U301.19 (GPIO15), Q602.1 (G), R609.1 |
| POGO_RX | U301.17 (GPIO13), R602.2 |
| POGO_RX_J | J601.5 (Pin_5), U601.6 (D1-), R602.1 |
| POGO_TX | U301.16 (GPIO12), R601.1 |
| POGO_TX_J | J601.6 (Pin_6), U601.1 (D1+), R601.2 |
| VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1, C103.1 |

</details>
