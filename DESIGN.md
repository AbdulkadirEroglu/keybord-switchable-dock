# DESIGN.md — Engineering Baseline

**Status (2026-09-29, branch `dock-v2`):**

- **Dock: v2**, chips on the board, JLCPCB assembly. Decided part by part in the design review; the reasoning is in `docs/dock-v2-mcu-selection.md`, `dock-v2-power-input.md`, `dock-v2-usb-ports.md`, `dock-v2-pogo.md`, `dock-v2-mcu-support.md`. The wiring is in [`hardware/dock-v2/DOCK_CONNECTIONS.md`](hardware/dock-v2/DOCK_CONNECTIONS.md), placement in [`hardware/dock-v2/PCB_PLACEMENT.md`](hardware/dock-v2/PCB_PLACEMENT.md). Sections 1–7 and 16–22 below describe the v2 dock.
- **Pad: to be redesigned.** Sections 8–14 are the v1 pad plan, kept unchanged as the starting point. Section 15 (docking) already has the v2 7-pin interface.
- **v1 dock** (three Pico modules, powered from the PCs): complete on `master` (`hardware/dock/`, the v1 version of this file).

## 1. Design Goals

- One physical USB keyboard shared between two computers.
- PC-side connections remain wired USB.
- No software running on either PC is required for basic keyboard routing.
- Physical `PERSONAL | OFF | WORK` selection (on the pad).
- Detachable wireless control pad.
- Robust recovery and debug access: every MCU can be reflashed without special tools.
- **The dock is powered by its own USB-C PD charger** (≥ 18 W; a 30 W charger is used). It does not draw power from the PCs, and it never back-feeds a PC that is switched off. (v1 ran from the PCs; dropped in v2, see `docs/dock-v2-power-input.md`.)
- Pad charges automatically while docked.
- BLE is used only between the pad and the dock.
- Failure states must avoid stuck keyboard/modifier/media reports.
- **Built by JLCPCB** (machine assembly of the fine-pitch parts); only a few through-hole parts are hand-soldered.

---

## 2. System Partitioning

### 2.1 Main Dock (v2)

Responsibilities:

- USB-host the physical keyboard (USB-C port, the dock is the source).
- Present a USB keyboard to each PC.
- Route keyboard/HID reports to the selected target.
- Receive pad events and the selector state over BLE.
- Power the keyboard (switched, current-limited) and the docked pad (switched by DET, current-limited).
- Negotiate 9 V from a USB-C PD charger and make 5 V and 3.3 V.

```text
 charger ═ J101 ─ CH224A (9 V) ─ TPS54331 ─ +5V ─┬─ AMS1117 ─ +3V3
                                                 ├─ SY6280 ─ KBD_VBUS ─► keyboard
                                                 └─ SY6280 ─ POGO_5V ──► pad
 keyboard ═ J201 ═ PIO-USB ─┐
                            ▼
 Personal PC ═ J202 ═══ RP2354A A ◄── UART0, RUN, BOOTSEL, SWD ──► RP2354A B ═══ J203 ═ Work PC
                            │  └── UART1 ──► ESP32-C3-MINI-1 ~~ BLE ~~ pad
                            └── PIO UART, DET ──► pogo J601 ═ pad (docked)
```

| Device | Ref | Job |
|---|---|---|
| RP2354A **A** (RP2350 + 2 MB flash, QFN-60) | U301 | Keyboard host (Pico-PIO-USB), Personal PC device (native USB), router, controls B, the ESP32 and the pogo |
| RP2354A **B** | U401 | Work PC device (native USB) |
| ESP32-C3-MINI-1-H4X | U501 | BLE central to the pad (pre-certified module, PCB antenna), UART to A |
| CH224A | U102 | USB-PD sink: asks for 9 V; I2C status to A |
| TPS54331 + SS54 + 6.8 µH | U103, D102, L101 | 5 V buck (5.16 V), 3 A; 100 % duty pass-through on a 5 V-only charger |
| AMS1117-3.3 | U104 | 3.3 V for A, B, the ESP32 |
| SY6280AAC × 2 | U202, U602 | Keyboard VBUS switch (1.0 A), pogo 5 V switch (1.45 A) |
| TPD4E1U06 × 5 | U101, U201, U203, U204, U601 | ESD on every USB-C port and the pogo contacts (clamps to GND only: no back-feed path into an unpowered PC) |
| TYPE-C-31-M-12 × 4 | J101, J201, J202, J203 | Power, keyboard, Personal PC, Work PC |
| Magnetic pogo, 7 pins | J601 | Pad docking (hand-soldered) |

Why two chips: no affordable MCU has three USB 2.0 controllers (researched in `docs/dock-v2-mcu-selection.md`); A does the host and one device, B the other device. Why RP2354A: same firmware base as v1 (TinyUSB + Pico-PIO-USB, hub support), UF2 flashing, no programmer needed.

### 2.2 Wireless Control Pad (v1 plan, to be redesigned)

Responsibilities:

- Read 12 mechanical keys.
- Decode two rotary encoders.
- Read two encoder push switches.
- Read the target selector.
- Drive 36 addressable RGB LEDs.
- Drive the display.
- Communicate with dock over BLE.
- Monitor battery and charger state.
- Manage sleep/wake and switched peripheral power.
- Charge from docked 5 V input.

Primary devices:

- MCU + BLE — Raspberry Pi Pico 2 WH (RP2350 + CYW43439), socketed like the dock modules (§18.1)
- TCA9555 — 16-bit I2C GPIO expander (keys, encoder switches, selector)
- TP4056 — Li-ion linear charger (ESOP-8), Pico-controlled enable
- TPS2116 — power path: pogo 5 V (priority) or battery → `PAD_SYS`
- DW01A + FS8205A — cell protection (over-discharge, overcurrent, short)
- TPS61023 — 5 V boost for the RGB LEDs
- TPS22919 — OLED load switch
- SN74AHCT1G125 — RGB data level shifter
- 2 × Samsung SDI INR21700-50E Li-ion cells (4900 mAh each, 9.8 Ah total) in parallel, in a dual 21700 holder, with a 10 k NTC between them
- 36 × SK6812MINI-E reverse-mount RGB LEDs
- 1.69" 240 × 280 ST7789 colour IPS display
- Separate small pogo board in the back wall (pogo connector, TVS, ESD), cable to the main board
- 12 × Razer Yellow Linear (MX-compatible, 3-pin) switches in Kailh hot-swap sockets, FR4 switch plate
- 2 × Bourns PEC11R-4220F-S0024 encoders with push switch

All parts are hand-solderable (leaded packages, or the TPS2116/TPS61023 TI SOT-5x3 family with extended hand-solder pads). No BGA/QFN/WSON parts: the BQ25185 and TPS63802 were dropped for that reason.

The Pico 2 WH has its own buck-boost 3.3 V regulator that runs from 1.8–5.5 V on `VSYS`, so the pad needs no 3.3 V regulator; the Pico's `3V3` pin (≤ 300 mA recommended) powers the TCA9555, pull-ups and the OLED switch.

---

## 3. Dock USB Ports (v2)

All four are the same 16-pin USB 2.0 USB-C receptacle (TYPE-C-31-M-12, rated 20 V / 5 A), each with a TPD4E1U06 within 5 mm (D+, D−, CC1, CC2).

| Port | Role | CC | Data | VBUS |
|---|---|---|---|---|
| J101 power (right edge) | sink | CH224A (built-in Rd) | CH224A D+/D− (QC/BC1.2) | VBUS_IN, SMBJ15A TVS |
| J201 keyboard (left edge) | **source** | 33 k Rp to 3.3 V (Default USB), read by A's ADC | A GPIO3 D+ / GPIO2 D− (PIO-USB, `PIO_USB_PINOUT_DMDP`) via 22 Ω, 15 k host pull-downs | KBD_VBUS from SY6280, 220 µF THT + 10 µF + 1 µF |
| J202 Personal PC (back) | sink | 5.1 k Rd | A USB_DP/DM via 22 Ω | **sense only**: 22 k / 33 k divider to A GPIO1 |
| J203 Work PC (back) | sink | 5.1 k Rd | B USB_DP/DM via 22 Ω | **sense only**: divider to B GPIO29 |

- **Keyboard port (cold socket):** KBD_VBUS stays off until A sees a sink's Rd on CC (≈ 0.44 V) for > 100 ms; off again on unplug. A charger or PC plugged in by mistake shows Rp, so the dock never turns VBUS on against it. EN has a 100 k pull-down: off at reset and with blank firmware.
- **PC ports:** the dock takes no power from the PCs. Each MCU enables its D+ pull-up (connects) only while its PC's VBUS is present.
- Ground is shared by both PCs, the charger and the dock (as in v1 and every KVM switch); the charger is isolated.

---

## 4. Dock Power (v2)

### 4.1 Input

```text
J101 VBUS ─ VBUS_IN ─┬─ SMBJ15A ─ GND
                     ├─ CH224A VHV/VBUS (CFG1 = 6.8 k → asks 9 V; SCL/SDA/PG → MCU A)
                     └─ TPS54331 VIN
```

- **9 V** is mandatory on every PD source above 15 W (12 V is optional and often missing).
- CH224A over I2C (0x22): which protocol won, requested voltage, maximum current of the current profile; can re-request 5 V. PG is a backup. The pad's charge speed follows from this (§12.2).
- On a charger without PD the dock still runs: the TPS54331 runs at 100 % duty and passes ≈ 4.7 V through; firmware then keeps pad charging slow.

### 4.2 Rails

| Rail | Source | Notes |
|---|---|---|
| +5V | TPS54331, 12 k / 2.2 k → 5.16 V | TI Table 7-1 values on Basic parts: 51 k + 4.7 nF + 47 pF compensation, 10 nF soft start, 3 × 22 µF out; L101 SLO0630H6R8MTT (Isat 8 A > 5.8 A max current limit). EN left open (a UVLO divider would stop the 5 V pass-through). |
| +3V3 | AMS1117-3.3 from +5V | ≤ 0.4 A peak (A, B, ESP32 BLE TX ≈ 170 mA at 0 dBm) |
| KBD_VBUS | SY6280, R_SET 6.8 k → 1.0 A (0.75–1.25 A) | EN from A (100 k pull-down); KBD_VBUS measured by A's ADC (replaces a fault pin) |
| POGO_5V | SY6280, R_SET 4.7 k → 1.45 A (1.09–1.81 A) | EN pulled high only when the pad grounds DET (hardware); A can veto (§15); POGO_5V measured by A's ADC |

### 4.3 Budget

| Load | Typical | Limit |
|---|---|---|
| Keyboard | 0.1–0.2 A (current keyboard: 200 mA rated) | 1.0 A |
| Pad (charging 0.51 A + electronics + LEDs) | 0.7–0.8 A | 1.45 A |
| 3.3 V rail | 0.15 A | 0.4 A |
| **+5V total** | **≈ 1 A** | ≈ 2.85 A at the nominal limits (TPS54331: 3 A) |

From 9 V at ≈ 90 % efficiency, even the worst case is ≈ 17 W: fine for the 30 W charger.

---

## 5. USB Endpoint Architecture (v2)

- **MCU A** is the keyboard host *and* the Personal PC's keyboard (native USB device). **MCU B** is the Work PC's keyboard. Each enumerates with its PC and stays enumerated when not selected.
- Each endpoint exposes at least Keyboard HID and Consumer Control HID; a vendor HID interface is optional.
- A and B run different firmware images (A: TinyUSB host + device + router + BLE link; B: device + link only).
- Each MCU watches its own PC's VBUS and connects its D+ pull-up only while VBUS is present (no back-feed into a PC that is off).
- A controls B: **RUN** (reset), **BOOTSEL** (via 1 k to B's QSPI_SS) and **SWD** (A can reflash and recover B, Raspberry Pi debugprobe style). B_RUN and B_BOOTSEL have 10 k pull-ups so A's reset-state pull-downs can't hold B in reset or BOOTSEL.

---

## 6. Internal Links (v2)

| Link | MCU A pins | Other end | Implementation |
|---|---|---|---|
| A ↔ B (HID reports, Work PC) | GPIO24 TX / GPIO23 RX | B GPIO5 RX / GPIO6 TX | hardware UART1 (RX on A and TX on B use the F11 aux function), 1 Mbaud or faster |
| A ↔ ESP32-C3 (BLE data, ESP32 flashing) | GPIO12 TX / GPIO13 RX | ESP32 RXD0 / TXD0 | hardware UART0 |
| ESP32 control | GPIO9 → EN, GPIO10 → GPIO9 (BOOT) | 10 k pull-ups, EN RC 10 k / 1 µF | open-drain |
| Pogo UART (diagnostics/recovery) | GPIO16 TX / GPIO15 RX; GPIO14 DET, GPIO11 OFF | pad, through 1 k on each side | PIO UART |
| CH224A | GPIO18 SDA / GPIO19 SCL, GPIO17 PG | CH224A | I2C1 |
| B control | GPIO20 RUN, GPIO25 BOOTSEL, GPIO22/21 SWCLK/SWDIO | B | open-drain / PIO SWD |

The full pin maps (every GPIO, with the reason for each choice) are in DOCK_CONNECTIONS.md §5–6. Keystrokes never pass through BLE: BLE carries only pad events and the selector state. With the radio on its own module, BLE stack faults can't disturb USB timing on A.

### 6.1 Packet Framing

Baseline (unchanged from v1):

```text
SOF | TYPE | SEQ | LEN | PAYLOAD | CRC
```

Likely message classes: `KEYBOARD_REPORT`, `CONSUMER_REPORT`, `RELEASE_ALL`, `PING`, `PONG`, `GET_STATUS`, `STATUS`, `RESET_USB`, `SET_MODE`.

Prefer complete HID state/report messages over key-down/key-up event streams. Normal HID traffic need not wait for an ACK; critical control operations may use ACK/sequence verification.

---

## 7. Routing Safety

Target changes (the Personal side is A's own USB device; the Work side is B over UART0):

- **PERSONAL → WORK:** receive the new selector state → release all on A's Personal device → change the route → B starts from a released state → forward the current state to B.
- **WORK → PERSONAL:** the same, reversed (`RELEASE_ALL` to B first).
- **Any target → OFF:** release Personal, send `RELEASE_ALL` to B, route NONE.
- **BLE loss** (no valid pad state for the timeout): release all, route OFF.
- **A ↔ B link loss:** B watches the link independently; on timeout it sends released keyboard and consumer reports, stays enumerated and idles safely. A resets B (RUN) if the link doesn't recover.
- **Keyboard faults:** A can power-cycle KBD_VBUS (SY6280 EN) to force re-enumeration.

---

> **Sections 8–14: the v1 pad plan, kept unchanged.** The pad will be redesigned; treat these as the starting point, not as decisions.

## 8. Pad User Interface

### 8.1 Mechanical Keys

V1:

- 12 keys
- Razer Yellow Linear (Gen-3) switches: MX-compatible, 3-pin, 45 g, transparent housing with an LED lens
- Kailh MX hot-swap sockets on the PCB
- 1.5 mm FR4 switch plate (14 mm cutouts), held on spacers to the pad PCB and enclosure. 3-pin switches have no PCB-locating pegs, so the plate carries them.
- 4 × 3 arrangement
- approximately 19.05 mm pitch
- One SK6812MINI-E per key, reverse-mounted under the switch's LED lens (§10)

```text
[01] [02] [03] [04]
[05] [06] [07] [08]
[09] [10] [11] [12]
```

### 8.2 Encoders

Two rotary encoders with push switches: Bourns PEC11R-4220F-S0024 (TME): 24 detents / 24 pulses, 20 mm metal flatted shaft, push switch, EC11-compatible 5-pin THT footprint (datasheet `datasheets/pec11r.pdf`). 24 detents = 2 clicks per LED on the 12-LED ring.

Intended roles:

- Encoder 1: volume
- Encoder 2: microphone/call controls

Quadrature A/B signals connect directly to Pico GPIO and are decoded by PIO. Each A/B line has a 10 kΩ pull-up to 3V3 and 10 nF to GND (debounce); the encoder common goes to GND.

Push switches connect through TCA9555.

### 8.3 Target Selector

Physical metal panel-mount SPDT `ON-OFF-ON` toggle.

States:

```text
PERSONAL
OFF
WORK
```

Two TCA9555 inputs encode the state:

| Input A | Input B | State |
|---:|---:|---|
| 0 | 1 | PERSONAL |
| 1 | 1 | OFF |
| 1 | 0 | WORK |
| 0 | 0 | INVALID / FAULT |

The selector is the authoritative target state.

---

## 9. TCA9555 Allocation

16 GPIO total:

```text
12 × mechanical keys
 2 × encoder push switches
 2 × target-selector contacts
------------------------------
16 × GPIO
```

- I2C SDA/SCL → Pico (hardware I2C)
- INT → Pico GPIO (also the wake source from dormant sleep)
- Exact pull-up implementation must be verified against the selected TCA9555 variant/datasheet during schematic capture.
- Encoder A/B signals do not use the expander.

### 9.1 Pad Pico GPIO Allocation

Initial map from the schematic (grouped by function; may be re-pinned by PCB position, as on the dock):

| GPIO | Pin | Signal | GPIO | Pin | Signal |
|---|---|---|---|---|---|
| GP0 | 1 | PAD_UART_TX (UART0, pogo) | GP16 | 21 | RGB_EN (TPS61023 EN) |
| GP1 | 2 | PAD_UART_RX (UART0, pogo) | GP17 | 22 | CHG_FAST (PROG MOSFET) |
| GP2 | 4 | ENC1_A (PIO) | GP18 | 24 | CHG_INHIBIT (CE MOSFET) |
| GP3 | 5 | ENC1_B (PIO) | GP19 | 25 | CHG_CHRG_N |
| GP4 | 6 | I2C_SDA (I2C0) | GP20 | 26 | CHG_STDBY_N |
| GP5 | 7 | I2C_SCL (I2C0) | GP21 | 27 | DOCKED (TPS2116 ST) |
| GP6 | 9 | ENC2_A (PIO) | GP22 | 29 | OLED_EN (TPS22919 ON) |
| GP7 | 10 | ENC2_B (PIO) | GP26 | 31 | VBAT_SENSE (ADC0, VBAT/2) |
| GP8 | 11 | TCA_INT_N (wake source) | GP27 | 32 | OLED_BLK (display backlight PWM) |
| GP9 | 12 | RGB_DATA_3V3 (PIO) | GP28 | 34 | spare (ADC2) |
| GP10 | 14 | OLED_SCK (SPI1) | GP15 | 20 | free (1×19 socket possible) |
| GP11 | 15 | OLED_MOSI (SPI1 TX) | | | |
| GP12 | 16 | OLED_DC | | | |
| GP13 | 17 | OLED_CS (SPI1 CSn) | | | |
| GP14 | 19 | OLED_RES | | | |

---

## 10. RGB System

### 10.1 LED Count

```text
Volume encoder ring       12
Microphone encoder ring   12
Key LEDs                  12
----------------------------
Total                     36
```

LED: SK6812MINI-E (reverse mount, side legs reachable with an iron), one part for keys and rings, one chain. Each LED sits in a small PCB cutout and shines up through it. Sourced from LCSC (C5149201), combined with the JLCPCB order.

Design power budget must tolerate approximately:

```text
36 × 15 mA ≈ 540 mA @ 5 V
≈ 2.7 W
```

even though firmware will normally impose a much lower global brightness.

### 10.2 RGB Power

```text
PAD_SYS
    │
TPS61023 (boost, EN from Pico)
    │
  5V_RGB
    ├── SN74AHCT1G125
    └── RGB LEDs
```

TPS61023 (SOT-563, hand-solder footprint like the TPS2116):

- Output set to ≈ 5.05 V: R1 = 750 kΩ (VOUT→FB), R2 = 100 kΩ (FB→GND); VREF ≈ 0.6 V ±2.5 %, worst case ≈ 5.2 V (< SK6812 5.5 V max).
- Inductor 1 µH, shielded ~4 × 4 mm, I_sat ≥ 4.5 A, DCR ≤ 20 mΩ (TI-recommended: Würth 74438357010, Coilcraft XEL4030-102ME, or equivalent). Worst-case peak ≈ 3.8 A at 2.7 V in, 1.5 A out.
- C_in 10 µF; C_out 2 × 22 µF X7R ≥ 16 V (≥ 4 µF effective after DC bias).
- `EN` from a Pico GPIO with a 100 kΩ pull-down, so the LEDs stay off while the Pico boots.
- True output disconnect when disabled: the LEDs draw nothing when the rail is off (SK6812 idle current would otherwise drain the cell).
- Docked (`PAD_SYS` ≈ 5 V) the device enters pass-through; on battery it boosts.

### 10.3 RGB Data

```text
Pico 3.3 V GPIO (PIO)
        │
SN74AHCT1G125
        │
 5 V logic data
        │
 33–100 Ω footprint
        │
 SK6812MINI-E DIN
```

Buffer supply comes from `5V_RGB` so the RGB subsystem loses both power and data drive when disabled.

---

## 11. Display

Display is required in V1.

Module: 1.69" 240 × 280 colour IPS TFT, ST7789 (V3) controller, SPI, rounded corners (Meon Otomasyon, "TFT LCD 1.69 İnç 240x280 ST7789 V3 SPI Display Modülü"). Chosen over the 1.3" monochrome OLED for colour and resolution at about the same module size, over the 1.9" 170 × 320 bar (not sold as a bare module in Turkey) and over the 2.0" GMT020-02 (its 62 × 37 mm module would push the board to ≈ 120 mm wide, and its backlight cannot be dimmed).

Typical pinout of these 8-pin modules (verify against the actual board before the PCB):

```text
GND
VCC   (3.3–5 V)
SCL   (SPI clock)
SDA   (SPI MOSI, not I2C)
RES
DC
CS
BLK   (backlight)
```

Backlight: ≈ 41 mA measured on this module type. BLK is driven through a P-MOSFET (AO3401A) from `OLED_VCC`, gate from Pico GP27 with a 10 kΩ pull-up to `OLED_VCC` (backlight off until firmware pulls GP27 low; PWM for dimming). The MOSFET works whether BLK is a direct LED anode or the input of an on-module transistor.

Firmware: ST7789 at 240 × 280 needs a 20-row offset (the controller RAM is 240 × 320).

Connection: the module is mounted to the case behind its window and wired to the main PCB with a short (≈ 10 cm) 9-wire JST-PH 2.0 mm cable (9-pin chosen because the ready-made cable is in stock at Robotistan). Main PCB: JST B9B-PH-K-S (9-pin PH, through-hole, shrouded, keyed; TME). Pins 1–8 carry the module's 8 signals; pin 9 is a second GND for a better SPI return path. The cable's bare end is soldered to the module's pads, both GND wires to the module's GND pad. The display's pads come unpopulated, so no header is needed on the module.

Mechanical allowance:

- module about 31 × 38 mm (typical); measure the real board outline, window and holes before placement

Power:

```text
Pico 3V3 → TPS22919 → OLED_VCC → module VCC and backlight MOSFET
```

The net names keep the `OLED_` prefix from the first design; they now refer to this TFT.

Shutdown sequence:

1. Turn the backlight off (GP27 high).
2. Put the display into sleep.
3. Put SPI/control pins into a safe low/high-impedance state.
4. Disable TPS22919.

---

## 12. Pad Battery and Charging

### 12.1 Cell

Samsung SDI INR21700-50E (datasheet: `datasheets/samsung-inr21700-50e.pdf`, spec v0.2). Buy from TME (authorized distributor, genuine cells); verify weight ≤ 69 g on arrival.

| Item | Datasheet value |
|---|---|
| Chemistry | Li-ion, 3.6 V nominal |
| Capacity | ≥ 4900 mAh (0.2C), ≥ 4753 mAh (1C) |
| Charge voltage | 4.2 V, CC-CV |
| Standard charge | 0.5C = 2450 mA, 0.02C cut-off |
| Max charge current | 4900 mA (not for cycle life) |
| Discharge cut-off | 2.5 V |
| Max continuous discharge | 9.8 A |
| Cycle life | ≥ 80 % after 500 cycles (0.5C charge to 4.2 V / 1C discharge to 2.5 V, full depth) |
| Charge temperature | 0 to 45 °C (cell surface) |
| Discharge temperature | −20 to 60 °C |
| Storage | ex-factory at ~30 % (3.43–3.63 V); 1 year at −20 to 23 °C |
| Size / weight | Ø 21.25 × 70.80 mm max (with sleeve), flat top, 69 g max |

Operating window chosen for maximum life. The datasheet gives only the hard limits; the narrower window is standard Li-ion practice (lower average voltage and shallower cycles slow both calendar and cycle ageing):

| Limit | Value | Enforced by |
|---|---|---|
| Hard max (datasheet) | 4.20 V | Charger CV regulation |
| Docked hold window (default) | stop at 4.00 V, resume below 3.90 V (≈ 80 % / 70 %) | Firmware via the charger enable pin |
| Full charge on request | 4.20 V | Firmware (e.g. before a long undocked session) |
| Charge current | ≈ 510 mA fast / 146 mA slow (≈ 0.05C / 0.015C for the 9.8 Ah pack) | TP4056 PROG network (§12.2) |
| Charge temperature | 0 to 45 °C | Charger NTC input |
| Low-battery warning | ≈ 3.50 V under light load | Firmware |
| Graceful shutdown | ≈ 3.30 V under light load | Firmware |
| Hard min (datasheet) | 2.5 V | — |
| Hardware backstop | ≈ 2.4 V (DW01A) | §12.4 |

Pack: 2 × INR21700-50E in parallel (1S2P, ≈ 9.8 Ah) in Motorobit's dual 21700 holder, which is wired in parallel internally and comes with flying leads. The holder is fixed to the case; its leads go to a 2-pin JST-XH (2.5 mm, 3 A) on the pad PCB, and the NTC to a separate 2-pin JST-XH. The holder's thin leads are adequate: the worst-case pack current is ≈ 1 A (full RGB brightness on battery). Insert both cells at the same voltage (charge each to 4.0 V first); after that they stay balanced. A 10 kΩ B3950 NTC sits between the two cells and goes to the charger's NTC input. Per-cell current is half the pack current, so every datasheet current limit has 2× margin.

### 12.2 Charger

TP4056 (NanJing Top Power, ESOP-8, datasheet `datasheets/tp4056.pdf`; genuine part LCSC C16581, also sold locally). Linear 4.2 V CC-CV Li-ion charger. The CN3058E chosen earlier was LiFePO4-only.

```text
POGO_5V → SMAJ5.0A → TP4056 VCC
                        └── BAT → DW01A/FS8205A → 2 × INR21700-50E
```

| Pin | Name | Connection |
|---|---|---|
| 1 | TEMP | NTC network: R1 = 5.6 kΩ (VCC→TEMP), NTC ∥ R2 = 75 kΩ (TEMP→GND). Charging runs only while TEMP is 45–80 % of VCC → ≈ 0–45 °C (the cell's charge range) |
| 2 | PROG | R_PROG = 8.2 kΩ to GND (≈ 146 mA); a 2N7002/AO3400 N-MOSFET, gate from a Pico GPIO (100 kΩ pull-down), adds 3.3 kΩ in parallel → ≈ 2.35 kΩ (≈ 510 mA). I = 1200 / R_PROG |
| 3 | GND + exposed pad | GND pour with vias; hand-solder hole from the back |
| 4 | VCC | `POGO_5V` (4–8 V), 10 µF |
| 5 | BAT | Pack + (protected side), 10 µF |
| 6 | STDBY | Open-drain, low = charge complete. 10 kΩ pull-up to 3V3, to Pico GPIO |
| 7 | CHRG | Open-drain, low = charging. 10 kΩ pull-up to 3V3, to Pico GPIO |
| 8 | CE | High = charge. 100 kΩ pull-up to `POGO_5V`; a 2N7002 from CE to GND, gate from a Pico GPIO (100 kΩ pull-down), pulls it low |

- Float voltage 4.2 V (4.137–4.263 V), C/10 termination, trickle below 2.9 V, automatic recharge, thermal regulation at 145 °C junction.
- CE defaults to charging. The pad charges even with blank, crashed or mid-flash firmware; the Pico only ever stops charging (docked hold window 3.90–4.00 V, §12.1).
- The charge speed is chosen by the dock over BLE from what its charger offers (CH224A over I2C, §4.1; v1 used the PC port's CC advertisement). Fast ≈ 510 mA is ≈ 0.05C for the 9.8 Ah pack; dissipation ≈ (5 − 3.7) V × 0.51 A ≈ 0.65 W.
- Both status pins high means no input, sleep, or temperature fault.
- SMAJ5.0A TVS on the pad's `POGO_5V` (pogo contacts hot-plug; ceramic input capacitors can ring).

No single leaded IC combines Li-ion charging, power path and protection (BQ2407x, BQ25185, MCP73871, ISL9301, LTC4089 are all QFN/DFN/WSON), so the pad uses three leaded blocks: TP4056 (charger), TPS2116 (power path, §12.3) and DW01A + FS8205A (protection, §12.4).

### 12.3 Power Path

A TPS2116 (same part and hand-solder footprint as the v1 dock's `U1`) selects the pad's system rail:

```text
POGO_5V ──► VIN1 (priority) ─┐
                             ├──► PAD_SYS
BAT (protected) ──► VIN2 ────┘
```

- PR1 divider 300 kΩ / 100 kΩ from `POGO_5V` (≈ 4.0 V switchover), MODE tied to VIN1, as on the v1 dock.
- Docked, the loads run from the pogo, so the charger sees only the cell and terminates correctly.
- `ST` (open-drain, high when VIN1 is in use) is pulled up to 3V3 and read by the Pico as the docked signal.
- Reverse-current blocking: with USB plugged into the Pico for flashing, VBUS reaches `PAD_SYS` but cannot flow back into the cell or the charger. No extra diode is needed.

### 12.4 Cell Protection

Linear chargers of this class have no battery undervoltage disconnect, so a DW01A + FS8205A pair (SOT-23-6 + TSSOP-8, the standard 1S protection) sits in the cell's negative lead:

- Over-discharge cut-off ≈ 2.4 V: a last-resort backstop if firmware hangs undocked (firmware shuts down at ≈ 3.3 V)
- Overcurrent and short-circuit protection
- Overcharge cut-off ≈ 4.3 V: backstop above the charger's 4.2 V.

Firmware remains the primary discharge limit (§14).

---

## 13. Pad Power Rails

```text
POGO +5V ──┬── SMAJ5.0A TVS
           ├── Charger ──► BAT ↔ INR21700-50E (via DW01A/FS8205A)
           │                 │
           └── TPS2116 VIN1  └── TPS2116 VIN2
                     │
                  PAD_SYS  (≈ 5 V docked, 3.3–4.2 V on battery)
                     │
                     ├── Pico 2 WH VSYS ──► on-board buck-boost ──► 3V3
                     │                                                ├── TCA9555
                     │                                                ├── encoder/switch pull-ups
                     │                                                └── TPS22919 → OLED
                     │
                     └── TPS61023 → 5V_RGB
                                     ├── SN74AHCT1G125
                                     └── 36 RGB LEDs
```

TPS61023 must be sized for the full RGB worst-case load, not merely normal firmware brightness (§10.2).

---

## 14. Battery Measurement

- Cell voltage: a permanent 100 kΩ / 100 kΩ divider from BAT to a Pico ADC pin (GP26–GP28), with 100 nF at the ADC pin. It draws ≈ 18 µA, which is negligible against 5000 mAh. It reads the cell even when docked.
- `PAD_SYS`: the Pico's own VSYS/3 on ADC3 (GP29, shared with the radio; the SDK handles the switching).

Firmware thresholds: see the operating-window table in §12.1 (warning ≈ 3.50 V, shutdown ≈ 3.30 V, docked hold 3.90–4.00 V). Voltage-to-charge mapping is approximate; charge counting in firmware can refine it later.

---

## 15. Docking Interface

Seven magnetic pogo contacts (Motorobit **straight** 7-pin 2.54 mm set, rated 1 A per contact). **The pad sits on top of the dock** (decided 2026-10-04): flat contacts on a small pogo board in the dock lid, spring pins on the pad's underside. The lid board connects 1:1 to the dock board's J601 (JST-XH 7-pin B7B-XH-A). Contact order:

```text
 dock (J601):  GND | +5V | DET | RX | TX | +5V | GND
 pad:          GND | +5V | TX  | RX | DET | +5V | GND      (mirror: pad pin 1 meets dock pin 7)
```

- **+5V at both ends (pins 2 and 6), GND at both ends (pins 1 and 7):** Because +5V (pins 2, 6) and GND (pins 1, 7) are mirror-symmetric, a pad fitted the wrong way round still gets +5V on +5V and GND on GND: it is powered and charges normally. Only the UART lines cross (dock TX → pad DET, pad TX → dock DET, RX ↔ RX), all through 1 kΩ, so nothing is damaged; the pogo UART just doesn't work that way round.
- **+5V on two contacts, GND on two:** 2 A capacity, so the dock's pogo switch can be set to 1.45 A (1.09–1.81 A) and the pad needs **no LED dimming while docked** (worst case: charging 0.51 A + electronics 0.15 A + all 36 LEDs white 0.54 A ≈ 1.2 A). On a low-tolerance switch the limit can cap that corner; the pad's power path then falls back to the battery, nothing is damaged.
- **DET:** the pad ties it to GND. On the dock, DET is pulled up to 3.3 V and drives a 2N7002 that holds the pogo switch's EN low while undocked. Docked, EN goes high and the pad gets 5 V **without firmware**. MCU A can veto through a second 2N7002 (POGO_OFF); its gate pull-down means "no veto" while A is in reset or has no firmware. A reads DET and measures POGO_5V.
- **RX/TX:** PIO UART on MCU A (GPIO16 TX / GPIO15 RX) through 1 kΩ on the dock and 1 kΩ on the pad; names from the dock's side. Reserved for diagnostics, recovery and fallback; it does not replace BLE during normal docking.
- ESD (TPD4E1U06) at the contacts on both sides; SMAJ5.0A on the pad's +5V.
- Magnets on both sides of the pogo area provide alignment and retention.
- **Orientation:** reversed docking is harmless (power pins are symmetric, see above), but the pogo UART only works the right way round. Mark pin 1 on both silkscreens and on the case.

Pad side: small pogo board (`hardware/pogo/`, 7 pins: +5V on pins 2 and 6) in the pad's **floor**, cable to the main board. The dock's lid board uses the same design: two identical boards facing each other meet pin 1 to pin 7, which gives the mirrored order above.

---

## 16. Debug and Recovery

Every programmable MCU has a physical debug/recovery path.

### Dock (v2)

| MCU | Normal update | Recovery |
|---|---|---|
| A (U301) | UF2: BOOTSEL A button (or firmware reboot-to-BOOTSEL) → drive on the **Personal PC** | RESET A button; SWD header J401 (GND, SWDIO, SWCLK) |
| B (U401) | UF2: BOOTSEL B button → drive on the **Work PC**; or A puts B into BOOTSEL (B_RUN + B_BOOTSEL) | **A reflashes B over SWD** (B_SWCLK/B_SWDIO); SWD header J501 |
| ESP32-C3 (U501) | A holds GPIO9 low, pulses EN, and bridges esptool from the Personal PC to the ESP32's UART0 | test pads TP503–505: TXD0/RXD0, GND (the native-USB pads were dropped) |

A single USB cable to the Personal PC can therefore update all three chips.

### Pad

- Pico 2 WH SWD: no SWD header on the pad PCB (the Pico's SWD holes would sit under key 5's centre post); a probe goes on the Pico 2 WH's own 3-pin JST-SH debug connector with the bottom cover off
- USB on the Pico itself (BOOTSEL/UF2) when the enclosure is open
- Pogo UART (§15) when docked

Pad recovery hierarchy:

```text
BLE  → normal operation
UART → diagnostics/recovery
SWD  → low-level recovery
```

---

## 17. Mechanical Baseline

### Dock (v2)

- PCB **90 × 70 mm** to start (shrink after placement), 4 layers, all SMD on top. Edges: **PC cables at the back** (Personal left, Work right), **keyboard left**, **charger right**, **pogo front** (see `hardware/dock-v2/PCB_PLACEMENT.md`).
- ESP32-C3 antenna at the left edge, front half; no metal, magnets or screws within ≈ 15 mm.
- **The pad sits on top of the dock** (decided 2026-10-04): saves table space; raises the pad by the dock's height. Pogo contacts on a small board in the dock lid, cabled to J601 (JST-XH 7-pin); the pad's pogo board sits in its floor.

### Pad (v1 plan, to be redesigned)


Wedge-shaped enclosure: keys, encoders and display all sit on one sloped top surface, so the main PCB is mounted at the same slope.

Decided (2026-09-28):

- **Slope 9–10°** (can change if the layout or ergonomics need it).
- **Heights: front ≈ 25 mm, back ≈ 44 mm** over ≈ 115 mm depth (≈ 9.4°). The first estimate (front 18–22, back 35–40 mm) is too low: the 21 mm battery holder at the back would hit the sloped PCB. The PCB underside must clear ≈ 28 mm (3 mm floor + 21 mm holder + 2 mm gap + 2 mm bottom-side parts) over the holder's front edge, which needs ≈ 25 mm at the front.
- **One main PCB** carries the keys, key LEDs, both encoders with their 12-LED rings (SK6812MINI-E on the board), the Pico and all power parts. Only the pogo board (forced by the slope) and the display (for a flush fit in the case window) are on cables. Rejected: off-board WS2812 rings (the locally sold 12-LED rings are 50 mm across, which widens the board instead of shrinking it; 37 mm rings have no reliable local source) and cabled encoder modules (no price gain, generic encoders, two more cables).
- **Display sideways** (landscape): 1.69" module ≈ 38 mm wide × 31 mm tall, between the two encoders, mounted to the case behind its window and connected by a 9-wire JST-PH cable (8 signals + a second GND).
- **Battery at the back**, under the top row (display/encoders), in the thick rear section. Never under the key field: the hot-swap sockets fill the underside there and the front is too thin.
- **Pogo board at the back**, in the back wall, on top of or beside the battery. Its height and position are aligned with the dock's pogo connector (J601 on the v2 dock) in the 3D enclosure design.
- **Selector toggle** (PERSONAL/OFF/WORK) on the right side of the key field, panel-mounted, wired to J5.
- **Pico** on the back side of the main PCB **under the key field**, long axis left-right, pin rows in the gaps between key rows (y = 50.0 and 67.78 mm), antenna end at the left board edge (plastic case wall there). The display strip can't take it: both of its ends are occupied by the encoder rings, and the antenna needs an edge. Exact positions: `hardware/pad/PCB_PLACEMENT.md`, drawings `docs/pad-pcb-1-top.png` … `docs/pad-pcb-4-front-cut.png`.

Main PCB sizing (20 mm knob; ring LEDs on a 12 mm radius, just outside the knob, so each ring is ≈ 27 mm across; 2 mm gaps to the display). Concept drawing: `docs/pad-concept.png`.

```text
                 BACK (high side, docks here; battery, Pico and pogo board below/behind)
 ┌───────────────────────────────────────────────────────┐
 │   ◯ ENC 1       ┌──────────────┐       ◯ ENC 2       │ ← top row ≈ 31–35 mm
 │  (12-LED ring)  │ 1.69" TFT    │    (12-LED ring)     │
 │                 │  sideways    │                      │
 │                 └──────────────┘                      │
 │          [01]   [02]   [03]   [04]                    │
 │          [05]   [06]   [07]   [08]                    │ ← keys 76 × 57 mm
 │          [09]   [10]   [11]   [12]                    │
 └───────────────────────────────────────────────────────┘
                 FRONT (low side)             main PCB 100 × 92 mm
```

Top row width ≈ 27 + 2 + 38 + 2 + 27 mm plus 1.5 mm edges ≈ 99–100 mm: the main PCB just fits the cheapest 100 × 100 mm JLCPCB size. Tight; if it ends a few mm over, the price step is small.

Enclosure envelope (from the first baseline, to be refined in CAD): width ~160 mm, depth ~110–120 mm. The PERSONAL/OFF/WORK toggle is panel-mounted in the enclosure to the right of the keys and wired to J5, so it widens the enclosure, not the PCB.

Still to measure before the PCB: display module outline, window and holes; knob diameter.

---

## 18. PCB Design Direction

### Dock (v2)

- **4 layers:** L1 parts + signals, L2 solid GND, L3 3.3 V / 5 V pours, L4 signals. **All SMD on the top side** (one-sided JLCPCB assembly).
- Rules (project file): clearance 0.15 mm, minimum track 0.15 mm, minimum drill 0.25 mm (what Raspberry Pi's RP2350 core layout uses; inside JLCPCB's standard 4-layer limits). Net classes: Default 0.2 mm, Power 0.6 mm (VBUS_IN, +5V, +3V3, KBD_VBUS, POGO_5V, GND, BUCK_SW), USB 90 Ω pairs.
- **RP2354A core:** Raspberry Pi's RP2350A Minimal layout copied exactly (regulator inductor orientation, pours, crystal), by `hardware/tools/copy_rpi_core_layout.py` after F8.
- ESD at each connector; USB pairs short, over solid ground; series resistors near the MCU.
- Buck hot loop (input caps → TPS54331 → PH → SS54) compact on L1 over L2 ground; feedback away from the switch node.
- ESP32-C3 antenna keep-out on all layers (in the footprint).
- Hand-soldered: C201 (220 µF THT, Özdisan) and J601 (pogo). Everything else is placed by JLCPCB.

### Pad (v1 plan)

- 2 layers, bottom GND pour; see `hardware/pad/PCB_PLACEMENT.md`.

---

## 19. KiCad Project Structure

```text
hardware/
├── dock-v2/                     v2 dock (this design)
│   ├── dock-v2.kicad_pro / .kicad_sch / .kicad_pcb
│   ├── power, usb_ports, mcu_a, mcu_b, ble, pogo .kicad_sch
│   ├── dock_v2_custom.kicad_sym  (RP2354A, ESP32-C3-MINI-1, CH224A, TPS54331, SY6280, TPD4E1U06)
│   ├── DOCK_CONNECTIONS.md       (wiring, pin maps; generated)
│   └── PCB_PLACEMENT.md
├── dock/                        v1 dock (reference; current on master)
├── pad/                         pad (v1 plan; to be redesigned)
├── pogo/                        pad pogo board (7-pin)
├── libraries/
│   ├── dock.pretty              Pogo-6, Pogo-7, v1 footprints
│   ├── dock_v2.pretty           RPi RP2350A QFN-60, core inductor/cap, ESP32-C3-MINI-1, 220 µF P5.00
│   └── THIRD_PARTY.md           sources and licences
├── reference/rpi-rp2350a-minimal/   Raspberry Pi's design (MIT)
└── tools/
    ├── copy_rpi_core_layout.py
    └── dock_v2_connections/     connection model, guide generator, wiring checker
```

Dock v2 sheets (annotation: sheet number × 100): POWER (1xx), USB_PORTS (2xx), MCU_A (3xx), MCU_B (4xx), BLE (5xx), POGO (6xx).

Pad hierarchical sheets (v1 plan):

```text
ROOT
├── BATTERY_CHARGER
├── POWER_RAILS
├── MCU (Pico 2 WH; file still named nrf52840.kicad_sch until renamed)
├── INPUTS
├── RGB
├── DISPLAY
└── DOCK_INTERFACE
```

---

## 20. Schematic Capture Order

### Dock (v2)

All parts are placed on their sheets (values, footprints, LCSC numbers). Wire them following [DOCK_WIRING.md](hardware/dock-v2/DOCK_WIRING.md) (component by component; DOCK_CONNECTIONS.md explains the circuit):

1. POWER: J101, CH224A, TPS54331, AMS1117 (+ PWR_FLAGs)
2. USB_PORTS: keyboard source port and switch, both PC ports
3. MCU_A: core (as RPi), then the GPIO map
4. MCU_B: core, links to A, pull-ups
5. BLE: ESP32-C3 straps and UART
6. POGO: connector, switch, DET/veto transistors
7. `hardware/tools/dock_v2_connections/check_wiring.py` until it reports OK, then ERC
8. F8, board outline, connectors at their edges, `copy_rpi_core_layout.py` for U301 and U401, then placement and routing

### Pad (v1 plan)

1. 21700 holder, NTC, DW01A + FS8205A protection
2. Pogo input (TVS, ESD, series resistors)
3. TP4056 charger with CE control and switchable PROG
4. TPS2116 power path → `PAD_SYS`
5. TPS61023 5V RGB rail
6. Pico 2 WH (socketed, VSYS, SWD header)
7. TCA9555 + switches/selector
8. Encoders
9. SN74AHCT1G125 + SK6812MINI-E chain
10. TPS22919 + OLED
11. Battery ADC divider
12. Power decoupling and final ERC review

---

## 21. Items to Verify

### Dock (v2), on the first boards

- CH224A: idle voltage of SCL/SDA (internal pull-up level) before connecting them to MCU A; behaviour with a charger that has no 9 V.
- TPS54331: loop with a load step on +5V; pass-through voltage on a 5 V-only charger at 2 A.
- USB enumeration with 22 Ω series resistors (RPi uses 27 Ω; 27 Ω is an Extended part).
- 220 µF lead spacing (footprint P5.00) and the 7-pin pogo body/ears (footprint scaled from Pogo-6) against the delivered parts.
- ESP32-C3 BLE with A, B and PIO-USB running together; RP2354A current at 240 MHz.

### Pad

Resolved for the pad before schematic capture:

- MCU: Raspberry Pi Pico 2 WH, socketed; no 3.3 V regulator (on-board buck-boost)
- Cell: 2 × Samsung SDI INR21700-50E in parallel, operating window §12.1
- Encoders: Bourns PEC11R-4220F-S0024 (24/24, 20 mm flatted shaft, push switch)
- Charger: TP4056, R_PROG 8.2 kΩ / 8.2 kΩ ∥ 3.3 kΩ (≈ 146 / 510 mA), CE default-on with Pico override, NTC R1 5.6 kΩ, R2 75 kΩ
- Power path: TPS2116, pogo priority, ST = docked sense
- Cell protection: DW01A + FS8205A
- RGB boost: TPS61023, 750 kΩ / 100 kΩ (≈ 5.05 V), 1 µH ≥ 4.5 A inductor
- LEDs: 36 × SK6812MINI-E (LCSC)
- Switches: Razer Yellow Linear, 3-pin MX, Kailh hot-swap, FR4 plate
- Display: 1.69" 240 × 280 ST7789 IPS TFT (Meon Otomasyon), backlight via P-MOSFET on GP27
- Pogo: separate pogo board (7 pins since the v2 dock review), 4-wire JST-XH cable to the main board; position part of the redesign
- Battery measurement: permanent 100 kΩ / 100 kΩ divider + Pico VSYS/3

---

## 22. Design Rule

When choosing between a slightly simpler implementation and one that materially improves diagnosis/recovery, prefer the recoverable implementation.

The project intentionally retains:

- independent USB endpoint MCUs (v2: A for Personal, B for Work)
- BLE normal link
- pogo UART fallback
- physical SWD access
- keyboard VBUS power control
- endpoint watchdogs
- explicit OFF state
- fail-safe HID release behavior

These are deliberate design features rather than temporary development conveniences.
Exception (v2): BLE runs on a separate pre-certified module (ESP32-C3) instead of a BLE-capable MCU, so no RF layout of our own is needed; A can reset and reflash it. Keystrokes never pass through BLE.
