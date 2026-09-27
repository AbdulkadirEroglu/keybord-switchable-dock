# DESIGN.md — V1 Engineering Baseline

## 1. Design Goals

This document freezes the V1 architecture before schematic capture.

Primary requirements:

- One physical USB keyboard shared between two computers.
- PC-side connections remain wired USB.
- No software running on either PC is required for basic keyboard routing.
- Physical `PERSONAL | OFF | WORK` selection.
- Detachable wireless control pad.
- Robust recovery and debug access.
- No external power adapter for the dock.
- Pad charges automatically while docked.
- BLE is used only between the pad and dock.
- Failure states must avoid stuck keyboard/modifier/media reports.

---

## 2. System Partitioning

### 2.1 Main Dock

Responsibilities:

- USB-host the physical keyboard.
- Parse incoming HID reports.
- Maintain target routing state.
- Forward HID state to one of two independent USB-device endpoints.
- Receive pad events/status over BLE (the host's own radio).
- Provide USB power to the keyboard.
- Select power automatically from Personal or Work PC.
- Charge/power the pad through the pogo interface.

Primary devices:

- Host/router + BLE — Raspberry Pi Pico 2 W (RP2350 + CYW43439 radio), `A1`
- HID-A / Personal endpoint — Raspberry Pi Pico 2 (RP2350), `A2`
- HID-B / Work endpoint — Raspberry Pi Pico 2 (RP2350), `A3`
- TPS2116 — PC VBUS priority power mux, `U1`
- TPS2553 — keyboard VBUS current-limited switch, `U3`
- TPS2552 — pogo +5V current-limited switch, enabled by `DET`, `U8`
- 4 × TPD4E1U06 — ESD protection: each USB-C port's D+, D−, CC1, CC2 (`U4`–`U6`) and the pogo contacts (`U9`). SOT-23-6, each channel clamps to GND only (no VBUS rail pin, so no back-feed path into an unpowered PC's VBUS)

All three Pico boards are socketed modules (see §18.1). Each module generates its own 3.3 V from `SYS_5V`; the dock has no separate 3.3 V regulator.

### 2.2 Wireless Control Pad

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
- 12 × Razer Yellow Linear (MX-compatible, 3-pin) switches in Kailh hot-swap sockets, FR4 switch plate
- 2 × Bourns PEC11R-4220F-S0024 encoders with push switch

All parts are hand-solderable (leaded packages, or the TPS2116/TPS61023 TI SOT-5x3 family with extended hand-solder pads). No BGA/QFN/WSON parts: the BQ25185 and TPS63802 were dropped for that reason.

The Pico 2 WH has its own buck-boost 3.3 V regulator that runs from 1.8–5.5 V on `VSYS`, so the pad needs no 3.3 V regulator; the Pico's `3V3` pin (≤ 300 mA recommended) powers the TCA9555, pull-ups and the OLED switch.

---

## 3. Main Dock Detailed Design

### 3.1 USB Ports

Three USB-C connectors are required.

#### Keyboard Port

Role:

- USB 2.0 Host / Source

Requirements:

- RP2350 USB host data
- Correct USB-C source-side CC configuration
- VBUS supplied from `SYS_5V` through TPS2553 (≈0.92–1.07 A limit, R<sub>ILIM</sub> 26.1 kΩ)
- 2 × 100 µF + 1 µF on `KEYBOARD_VBUS` (≥120 µF USB host requirement, met even at −20% tolerance)
- 100 kΩ pull-down on `KEYBOARD_VBUS_EN` so the keyboard stays off until firmware enables it
- CC1/CC2 → 56 kΩ Rp to `KEYBOARD_VBUS` (default USB power advertisement)
- TPD4E1U06 close to connector, protecting D+, D−, CC1 and CC2
- Shield termination: 330 Ω ∥ 100 nF to GND

#### Personal PC Port

Role:

- USB 2.0 Device / Sink

Requirements:

- HID-A (Pico 2) D+/D− via the Pico's USB test pads (§18.1)
- CC1 → 5.1 kΩ → GND
- CC2 → 5.1 kΩ → GND
- CC1/CC2 also sensed by the HID endpoint's ADC (§4.3)
- VBUS routed to the TPS2116 input and to the endpoint's VBUS sense divider (§5)
- TPD4E1U06 close to connector, protecting D+, D−, CC1 and CC2

#### Work PC Port

Same electrical architecture as Personal PC, using HID-B and the second TPS2116 input.

No USB Power Delivery is required.

---

## 4. Dock Power

### 4.1 Dual-PC Input

```text
PERSONAL_VBUS ──► TPS2116 VIN1 (priority)
WORK_VBUS     ──► TPS2116 VIN2

TPS2116 VOUT  ──► SYS_5V  (1 µF + 2 × 100 µF)
```

Implementation (TPS2116 priority mode):

- `MODE` tied to VIN1; PR1 divider 300 kΩ / 100 kΩ from `PERSONAL_VBUS` → switches to Work when Personal VBUS falls below ≈4.0 V (3.7–4.3 V over V<sub>REF</sub> tolerance).
- Reverse current blocking: neither PC is back-fed.
- Switchover is break-before-make (t<sub>SW</sub> ≈ 8 µs); the 2 × 100 µF bulk holds `SYS_5V` droop to ≈0.08 V at 2 A.
- Plug-in inrush is limited by the TPS2116 soft start: ≈0.6 A for ≈1.7 ms with ≈211 µF total. Do not substantially increase `SYS_5V` bulk capacitance without re-checking this.
- `ST` (open drain, high when VIN1 is in use) → `MUX_STATUS` → RP2350 GP28, pulled up to `HOST_3V3`.
- The TPS2116 has no current limit; downstream loads are limited individually (TPS2553 keyboard, TPS2552 pogo).

### 4.2 Keyboard VBUS

```text
SYS_5V → TPS2553 → KEYBOARD_VBUS
```

Connections:

- `EN` (active high) → RP2350 GP26 (`KEYBOARD_VBUS_EN`), 100 kΩ pull-down
- `FAULT` (open drain) → RP2350 GP27 (`KEYBOARD_VBUS_FAULT`), 10 kΩ pull-up to `HOST_3V3`
- Current limit: R<sub>ILIM</sub> = 26.1 kΩ → 0.92–1.07 A (TPS2553 datasheet I<sub>OS</sub> equations). Non-latching version: current is held at the limit during an overload and `FAULT` stays asserted.

This allows deliberate keyboard power cycling for recovery/re-enumeration.

### 4.3 Power Budget and Port Current Sensing

The whole dock (three MCUs, keyboard up to ~1 A, pad charging up to ~1 A) runs from one PC port at a time, which can exceed a USB 2.0 port's 500 mA. The dock therefore measures what the active port allows instead of assuming it.

Each HID endpoint reads its own port's USB-C CC pins through 10 kΩ series resistors:

```text
CC1 → 10k → GP26 (ADC0)
CC2 → 10k → GP27 (ADC1)
```

With the 5.1 kΩ Rd pull-downs, the active CC pin (the other stays near 0 V, depending on plug orientation) reads:

| CC voltage | Port advertises |
|---|---|
| 0.25–0.61 V | Default USB (500 mA / 900 mA) |
| 0.70–1.16 V | 1.5 A |
| 1.31–2.04 V | 3.0 A |

A USB-A-to-C cable always reads as Default, which is the safe result. Each endpoint reports its reading to the RP2350 over its UART link; `MUX_STATUS` tells the RP2350 which port is currently powering the dock.

Firmware policy: full pad charging when the active port advertises 1.5 A or 3 A; reduced or paused pad charging on a Default port, particularly while the keyboard draws high current. Enable keyboard VBUS only after the dock has booted, so the keyboard inrush does not coincide with the plug-in inrush.

---

## 5. USB HID Endpoint Architecture

Two independent HID endpoint MCUs (Pico 2 modules) are used rather than switching a single USB device electrically between computers.

Each endpoint exposes at minimum:

- Keyboard HID
- Consumer Control HID

Optional future interface:

- Vendor HID

Both endpoints use the same firmware image. A hardware role strap on GP2 identifies them:

- HID-A / Personal: GP2 pulled low (10 kΩ to GND)
- HID-B / Work: GP2 pulled high (10 kΩ to the endpoint's 3.3 V)

Each endpoint remains enumerated with its PC even when it is not the selected target.

VBUS sense: each endpoint reads its own PC's VBUS on GP4 through a 22 kΩ / 33 kΩ divider (5.25 V → 3.15 V). The endpoints are powered from `SYS_5V` even when their own PC is off, so firmware must only enable the USB D+ pull-up (connect) while GP4 is high, and disconnect when it goes low. Otherwise the endpoint would back-feed a powered-down PC's USB port.

---

## 6. Internal UART Architecture

### 6.1 Dock BLE (host Pico 2 W)

The host is a Pico 2 W; its on-board CYW43439 radio provides BLE to the pad directly, so the dock has no separate BLE module and no BLE UART link.

- Firmware: USB host, HID routing and the HID UART links on core 0; the BLE stack on core 1, so radio activity cannot delay keystrokes.
- Keystrokes never pass through BLE. BLE carries only pad events and the selector state.
- The CYW43439 is driven by the RP2350 over an internal interface using GP23/GP24/GP25/GP29 and one PIO state machine; those GPIOs are not available on the header.

### 6.2 RP2350 ↔ HID-A/B

Two independent full-duplex UART links:

```text
RP2350 TX-A → HID-A RX
RP2350 RX-A ← HID-A TX

RP2350 TX-B → HID-B RX
RP2350 RX-B ← HID-B TX
```

Each endpoint uses hardware UART0 on the pins facing the host: HID-A on GP16 (TX) / GP17 (RX), HID-B on GP12 (TX) / GP13 (RX). Firmware selects the pin pair from the role strap (GP2). Net names are from the RP2350's point of view: `HID_PERSONAL_TX` is driven by the RP2350.

Target baud: 1 Mbaud.

No level shifting required on-board.

### 6.3 RP2350 UART Allocation

The two HID links carry every keystroke and use the two hardware UARTs. The pogo diagnostic UART to the pad uses a PIO-implemented UART.

| Link | RP2350 TX | RP2350 RX | Implementation |
|---|---|---|---|
| HID-A / Personal | GP12 | GP13 | Hardware UART0 |
| HID-B / Work | GP20 | GP21 | Hardware UART1 |
| Pogo diagnostic UART (to pad) | GP16 (`POGO_TX`) | GP17 (`POGO_RX`) | PIO UART (TX + RX state machines) |

A PIO UART is electrically identical on the wire to a hardware UART; the pad side needs no special handling. PIO does not provide hardware framing-error flags, so link integrity relies on the packet CRC (§6.4).

UART0 and UART1 are both in use by the HID links, so the pogo UART stays on PIO.

Pins were chosen by PCB position so each link leaves the host on the side facing its destination: HID-A (left) on the host's left column, HID-B (right) and the pogo interface on its right column.

Other host control pins:

| RP2350 GPIO | Signal |
|---|---|
| GP26 | `KEYBOARD_VBUS_EN` |
| GP27 | `KEYBOARD_VBUS_FAULT` |
| GP28 | `MUX_STATUS` |
| GP18 | `POGO_5V_FAULT` |
| GP2 | `HID_PERSONAL_RUN_CTRL` |
| GP19 | `HID_WORK_RUN_CTRL` |
| GP22 | `POGO_DET` (pad docked = low) |

### 6.4 Packet Framing

Baseline:

```text
SOF | TYPE | SEQ | LEN | PAYLOAD | CRC
```

Likely message classes:

- `KEYBOARD_REPORT`
- `CONSUMER_REPORT`
- `RELEASE_ALL`
- `PING`
- `PONG`
- `GET_STATUS`
- `STATUS`
- `RESET_USB`
- `SET_MODE`

Prefer complete HID state/report messages over relying exclusively on key-down/key-up event streams.

Normal HID traffic need not wait for an ACK.

Critical control operations may use ACK/sequence verification.

---

## 7. Routing Safety

### PERSONAL → WORK

1. Receive new physical selector state.
2. Send `RELEASE_ALL` to Personal endpoint.
3. Confirm/reach safe state.
4. Change active route.
5. Ensure Work endpoint begins from released state.
6. Forward current/new HID state to Work.

### WORK → PERSONAL

Equivalent reversed sequence.

### Any Target → OFF

- Release Personal.
- Release Work.
- Set active route to NONE.

### BLE Loss

If the dock stops receiving valid pad state for the defined timeout:

- Release all keyboard/consumer states.
- Route OFF.

### RP2350 ↔ HID Endpoint Loss

Each HID endpoint independently watches its command link.

On timeout:

- Send released keyboard report.
- Send released consumer-control report.
- Remain enumerated.
- Enter safe idle.

---

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

Module: 1.3" 128 × 64 OLED, 7-pin four-wire SPI ("1.30' OLED VER1.2 4-SPI", direnc.net). Pinout:

```text
GND
VCC
SCK
SDA   (SPI MOSI, not I2C)
RES
DC
CS
```

Controller: almost certainly SH1106 (the shop listing says SSD1306). Firmware tries one and falls back to the other; a 2-column shift means SH1106. No hardware impact.

VCC accepts 3–5 V (on-module regulator).

Mechanical allowance:

- approximately 40 × 35 mm maximum module envelope
- Board outline and hole spacing to be measured on the real module before placement

Power:

```text
Pico 3V3 → TPS22919 → OLED_VCC
```

Shutdown sequence:

1. Put display into sleep/off state.
2. Put SPI/control pins into safe low/high-impedance state.
3. Disable TPS22919.

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
- The charge speed is chosen by the dock over BLE from the active PC port's advertised current (§4.3). Fast ≈ 510 mA is ≈ 0.05C for the 9.8 Ah pack; dissipation ≈ (5 − 3.7) V × 0.51 A ≈ 0.65 W.
- Both status pins high means no input, sleep, or temperature fault.
- SMAJ5.0A TVS on the pad's `POGO_5V` (pogo contacts hot-plug; ceramic input capacitors can ring).

No single leaded IC combines Li-ion charging, power path and protection (BQ2407x, BQ25185, MCP73871, ISL9301, LTC4089 are all QFN/DFN/WSON), so the pad uses three leaded blocks: TP4056 (charger), TPS2116 (power path, §12.3) and DW01A + FS8205A (protection, §12.4).

### 12.3 Power Path

A TPS2116 (same part and hand-solder footprint as the dock's `U1`) selects the pad's system rail:

```text
POGO_5V ──► VIN1 (priority) ─┐
                             ├──► PAD_SYS
BAT (protected) ──► VIN2 ────┘
```

- PR1 divider 300 kΩ / 100 kΩ from `POGO_5V` (≈ 4.0 V switchover), MODE tied to VIN1, as on the dock.
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

Six pogo contacts:

```text
GND | +5V | DET | RX | TX | GND
```

Normal behavior:

- `+5V`: powers charger/pad
- `DET`: dock presence (read by the host on GP22, and drives the TPS2552 enable)
- BLE remains the normal data link

The pad must tie DET to GND. Without that the pogo stays off.

The dock's pogo `+5V` is switched by a TPS2552 whose active-low `EN` is driven directly by `DET` (pulled up to `HOST_3V3` on the dock by R18). With no pad docked the contacts are unpowered; when docked the output is current-limited to approximately 1 A and `FAULT` is reported to the RP2350.

`RX/TX` connect through 1 kΩ series resistors to the host's PIO UART (GP16 TX / GP17 RX; names from the dock's side, so the pad must receive on the TX contact). They are reserved for:

- diagnostics
- recovery
- fallback communication

Pogo UART should not automatically replace BLE during normal docking.

Magnets on both sides of the pogo area provide mechanical alignment/retention.

Pad side (face-to-face mating mirrors the order):

```text
GND | TX-side | RX-side | DET | +5V | GND
```

- `DET` tied to pad GND.
- `+5V` → SMAJ5.0A TVS → `POGO_5V` (charger and TPS2116 VIN1).
- The pad receives on the dock's TX contact and transmits on its RX contact, into a Pico UART, with 1 kΩ series resistors on the pad side as well. Docked, the link sees 2 kΩ in series; with ~20 pF of pin and trace capacitance that is a ~40 ns time constant, negligible even at 1 Mbaud. The pad-side resistors protect the pad Pico when undocked: the contacts are exposed, and a coin or tool bridging `+5V` to RX/TX then injects at most ~1.4 mA.
- TPD4E1U06 ESD (same part as the dock) on the pad's pogo TX/RX lines. The dock's ESD only protects the dock; the pad's contacts are exposed whenever it is carried around.

---

## 16. Debug and Recovery

Every programmable MCU receives a physical debug/recovery path.

### Dock

- Host (Pico 2) SWD — J2
- HID-A (Pico 2) SWD — J3
- HID-B (Pico 2) SWD — J6

HID-A/HID-B SWD pads are reached with spring probes; the host's SWD comes through a 1×3 socket under its debug holes (§18.1). The host can also reset HID-A and HID-B (§18.2).

### Pad

- Pico 2 WH SWD: the H version's debug connector is replaced by a 1×3 male header pointing down into the pad PCB, the same way as the dock host (§18.1)
- USB on the Pico itself (BOOTSEL/UF2) when the enclosure is open
- Pogo UART (§15) when docked

Dock SWD header pinout (1×5, 2.54 mm), identical on J2/J3/J6:

```text
1  SWCLK
2  SWDIO
3  GND
4  RUN / RESET
5  3V3 (target voltage reference only; do not power the target from the probe)
```

UART test access should also be available where practical.

Recommended dock silkscreen identifiers:

```text
HOST
HID-A
HID-B
```

Pad recovery hierarchy:

```text
BLE  → normal operation
UART → diagnostics/recovery
SWD  → low-level recovery
```

---

## 17. Mechanical Baseline

Target pad dimensions before detailed CAD:

- Width: ~160 mm
- Depth: ~110–120 mm
- Front height: ~18–22 mm
- Rear height: ~35–40 mm

Wedge-shaped enclosure.

Top-level layout:

```text
┌────────────────────────────────────┐
│                                    │
│   ( VOL )    [ DISPLAY ]   ( MIC ) │
│                                    │
│ [01] [02] [03] [04]        ╱       │
│ [05] [06] [07] [08]       ●        │
│ [09] [10] [11] [12]        ╲       │
│                         P/O/W       │
└────────────────────────────────────┘
```

The 32700 battery belongs in the rear thick section under the display/encoder region.

It must **not** be placed under the key field.

Approximate reserved battery volume:

```text
~75 × 36 × 36 mm
```

including reasonable mechanical clearance/contact allowance.

---

## 18. PCB Design Direction

Initial expectation:

- Prefer 2-layer if routing, RF grounding and USB integrity remain acceptable.
- Do not force single-layer routing.
- 4-layer is not automatically required, but can be reconsidered if the actual placement/routing benefits justify it.
- Maintain continuous ground reference under USB differential routing wherever possible.
- Keep the host Pico 2 W antenna keep-out (14 × 9 mm at its bottom end) free of copper and components, with the antenna end at the board edge.
- Place USB ESD devices at the connectors.
- Keep switching-regulator hot loops compact.
- Keep RGB high-current paths away from sensitive RF/analog areas.
- Separate functional blocks clearly in placement.

### 18.1 Dock MCU Module Mounting (Pico 2 + Spring Probes)

All three dock MCUs (RP2350 host, HID-A, HID-B) are Raspberry Pi Pico 2 boards, socketed so they can be swapped without desoldering:

- Pico 2: two 1×20 2.54 mm male headers soldered on, pointing down.
- Dock PCB: two 1×20 2.54 mm female sockets, 8.5 mm tall. Pico underside sits ≈11 mm above the dock PCB.
- Footprint: `dock:RaspberryPi_Pico2_Socket_Pogo` (KiCad Pico THT footprint plus probe holes).

USB and SWD are only on pads on the Pico 2 underside, not on the header pins. They are reached with P50-B1 spring probes (0.68 mm barrel, 16.35 mm long, 2.65 mm stroke, 75 g, 45° spear tip) soldered into 0.8 mm holes in the dock PCB:

| Pico 2 pad | Signal | Probe |
|---|---|---|
| TP2 / TP3 | USB D− / D+ | required |
| D1 / D3 | SWCLK / SWDIO | required |
| TP1 / D2 | GND | optional (GND is also on the header pins) |

Positions come from the Pico 2 datasheet, Figures 3 and 5. Leave the factory tinning on the Pico pads; the spear tip cuts through the surface oxide.

Probe soldering procedure (sets ≈1.5 mm compression, whatever the header height):

1. Solder the female sockets to the dock PCB first.
2. Drop the probes loose into their holes, spring end up. Each sinks until its Ø0.9 mm tip head rests on the board.
3. Put a ≈1.5 mm shim (1.6 mm PCB offcut or two stacked ID cards) on the sockets and plug the Pico in on top of it.
4. Turn the stack upside down. The probes slide until their tips rest on the Pico pads.
5. Solder the probe barrels on the dock PCB underside. Keep the joints quick.
6. Remove the shim and seat the Pico fully.

Solder each Pico's probe set against that Pico. The barrels protrude ≈2.7 mm below the dock PCB; the enclosure needs 3–4 mm clearance there. Do not cut the barrels, because the spring is inside.

Never connect a cable to a docked Pico's micro-USB port: its USB lines share the bus with the probes.

The host is a **Pico 2 W** (footprint `dock:RaspberryPi_Pico2W_Socket_Pogo`), mounted the same way with these differences (Pico 2 W datasheet Figs 3 and 5):

- USB test pads TP1–TP3 are in the same place as on the Pico 2, so the USB probes are identical.
- SWD is on three through-holes (SWCLK, GND, SWDIO) 19.8 mm from the bottom edge. Solder a 1×3 male header there pointing down, into a 1×3 female socket on the dock; no SWD probes are needed.
- The antenna is at the bottom end (opposite USB). The footprint carries a 14 × 9 mm copper keep-out there. Place the host with its antenna end at the board edge, with nothing in front of it, and use a non-metal enclosure.

Before ordering the PCB, print the layout at 1:1 and check the Pico pads against the probe holes.

### 18.2 Endpoint Reset Control

The host can reset the two HID endpoints through 1 kΩ series resistors, so a debug probe on the SWD header can still override the line:

| RP2350 GPIO | Target |
|---|---|
| GP2 (`HID_PERSONAL_RUN_CTRL`) | HID-A RUN |
| GP19 (`HID_WORK_RUN_CTRL`) | HID-B RUN |

Each HID Pico RUN line has an external 10 kΩ pull-up. This keeps the endpoints out of reset while the RP2350's default GPIO pull-downs are active during its own boot. Firmware keeps these GPIOs as inputs with no pull and drives them low only to reset a target.

---

## 19. KiCad Project Structure

Recommended:

```text
hardware/
├── dock/
│   ├── dock.kicad_pro
│   ├── dock.kicad_sch
│   └── dock.kicad_pcb
│
└── pad/
    ├── pad.kicad_pro
    ├── pad.kicad_sch
    └── pad.kicad_pcb
```

Recommended dock hierarchical sheets:

```text
ROOT
├── POWER
├── USB_KEYBOARD_HOST
├── RP2350_HOST
├── HID_PERSONAL
├── HID_WORK
└── BLE_BASE
```

Recommended pad hierarchical sheets:

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

### Dock

Schematic captured and reviewed (ERC clean apart from the intentional Pico ground-pin exclusions). Next: PCB outline, placement and routing. Order used:

1. USB-C Personal/Work power inputs
2. TPS2116 and `SYS_5V` bulk capacitance
3. Host Pico 2 (power, SWD, control GPIOs)
4. Keyboard USB host connector + ESD + TPS2553
5. HID-A Pico 2 + Personal USB (VBUS/CC sensing, role strap)
6. HID-B Pico 2 + Work USB
7. Pogo interface (TPS2552, ESD, series resistors) to the host
8. Three internal UART links
9. SWD headers and reset control
10. Final ERC review

### Pad

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

## 21. Items to Verify, Not Redesign

The architecture is frozen, but the following are intentionally finalized during schematic work:

Resolved for the dock during schematic capture:

- MCU implementation: Raspberry Pi Pico 2 W (host + BLE) and Pico 2 (HID-A, HID-B), all socketed; no crystals or MCU decoupling needed on the dock
- USB-C connector: KLS L-KLS1-5416-L1-01-R (footprint checked against the manufacturer drawing)
- CC resistors: 5.1 kΩ Rd on PC ports, 56 kΩ Rp on the keyboard port
- Power mux: TPS2116 (replaces TPS2121), priority mode, ≈4.0 V switchover
- TPS2553 R<sub>ILIM</sub> 26.1 kΩ (≈1 A); TPS2552 on pogo +5V with the same limit
- SWD connector standard: 1×5 2.54 mm header (§16)

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
- Display: 1.3" SPI OLED, SH1106/SSD1306 chosen in firmware
- Battery measurement: permanent 100 kΩ / 100 kΩ divider + Pico VSYS/3

Still open:

- Dock: pre-order silkscreen pass, Gerber check
- Pad: PCB outline, placement, routing
- TCA9555 pull-up requirements
- RGB data series resistor value
- OLED module outline and hole spacing (measure)
- Toggle switch SKU/panel hole
- Pogo connector dimensions (awaiting the supplier's reply)
- FR4 plate outline and spacer positions
- Final mechanical dimensions

A change to one of these implementation details does not necessarily constitute an architecture change.

---

## 22. V1 Design Rule

When choosing between a slightly simpler implementation and one that materially improves diagnosis/recovery, prefer the recoverable implementation.

The project intentionally retains:

- independent USB endpoint MCUs
- BLE normal link
- pogo UART fallback
- physical SWD access
- keyboard VBUS power control
- endpoint watchdogs
- explicit OFF state
- fail-safe HID release behavior

These are deliberate design features rather than temporary development conveniences.

Exception: BLE runs on the host's own radio (Pico 2 W) rather than a separate BLE MCU, to cut cost and board space. A BLE-stack fault is contained by running BLE on its own core, by the host watchdog, and by the HID endpoints' independent link-timeout release.
