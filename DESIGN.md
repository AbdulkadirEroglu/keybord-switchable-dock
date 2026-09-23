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
- Receive pad events/status over the dock nRF52840.
- Provide USB power to the keyboard.
- Select power automatically from Personal or Work PC.
- Charge/power the pad through the pogo interface.

Primary devices:

- RP2350 — host/router
- RP2040-A — Personal HID endpoint
- RP2040-B — Work HID endpoint
- nRF52840 — BLE base
- TPS2121 — PC VBUS power mux
- TPS2553 — keyboard VBUS current-limited switch
- 3 × TPD2EUSB30 — USB D+/D− ESD protection

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

- nRF52840
- TCA9555
- BQ25185
- TPS63802
- TPS61023
- TPS22919
- SN74AHCT1G125
- Power-Xtra IFR32700 LiFePO4 cell
- 36 × WS2812C-2020-class RGB LEDs

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
- VBUS supplied from `SYS_5V` through TPS2553
- TPD2EUSB30 close to connector
- Shield termination strategy with configurable 0-ohm/RC option if useful

#### Personal PC Port

Role:

- USB 2.0 Device / Sink

Requirements:

- RP2040-A D+/D−
- CC1 → 5.1 kΩ → GND
- CC2 → 5.1 kΩ → GND
- VBUS routed only to TPS2121 input and optional sensing
- TPD2EUSB30 close to connector

#### Work PC Port

Same electrical architecture as Personal PC, using RP2040-B and the second TPS2121 input.

No USB Power Delivery is required.

---

## 4. Dock Power

### 4.1 Dual-PC Input

```text
PERSONAL_VBUS ──► TPS2121 IN1
WORK_VBUS     ──► TPS2121 IN2

TPS2121 OUT   ──► SYS_5V
```

Desired behavior:

- Personal input preferred when available.
- Work input automatically takes over otherwise.
- Reverse current into either computer must be prevented.
- Local bulk capacitance should support source transitions.
- Exact priority/current-limit configuration is finalized from the TPS2121 datasheet during schematic capture.

### 4.2 Keyboard VBUS

```text
SYS_5V → TPS2553 → KEYBOARD_VBUS
```

Connections:

- `EN` → RP2350
- `FAULT` → RP2350
- Current limit target approximately 0.9–1.0 A; calculate exact resistor from datasheet.

This allows deliberate keyboard power cycling for recovery/re-enumeration.

---

## 5. USB HID Endpoint Architecture

Two RP2040 devices are used rather than switching a single USB device electrically between computers.

Each RP2040 exposes at minimum:

- Keyboard HID
- Consumer Control HID

Optional future interface:

- Vendor HID

Both RP2040s should use the same firmware image. A hardware role strap identifies:

- HID-A / Personal
- HID-B / Work

Each endpoint remains enumerated with its PC even when it is not the selected target.

---

## 6. Internal UART Architecture

### 6.1 Dock nRF52840 ↔ RP2350

- Full-duplex UART
- 3.3 V logic
- Target baud: 1 Mbaud
- Dedicated protocol UART; do not mix debug logging into the stream

### 6.2 RP2350 ↔ RP2040-A/B

Two independent full-duplex UART links:

```text
RP2350 TX-A → RP2040-A RX
RP2350 RX-A ← RP2040-A TX

RP2350 TX-B → RP2040-B RX
RP2350 RX-B ← RP2040-B TX
```

Target baud: 1 Mbaud.

No level shifting required on-board.

### 6.3 Packet Framing

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

### RP2350 ↔ RP2040 Loss

Each RP2040 independently watches its command link.

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
- MX-compatible class
- 4 × 3 arrangement
- approximately 19.05 mm pitch

```text
[01] [02] [03] [04]
[05] [06] [07] [08]
[09] [10] [11] [12]
```

### 8.2 Encoders

Two rotary encoders with push switches.

Intended roles:

- Encoder 1: volume
- Encoder 2: microphone/call controls

Quadrature A/B signals connect directly to nRF52840 GPIO.

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

- I2C SDA/SCL → nRF52840
- INT → nRF52840
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

Candidate/frozen class: WS2812C-2020.

Design power budget must tolerate approximately:

```text
36 × 15 mA ≈ 540 mA @ 5 V
≈ 2.7 W
```

even though firmware will normally impose a much lower global brightness.

### 10.2 RGB Power

```text
BQ25185 SYS
    │
TPS61023
    │
  5V_RGB
    ├── SN74AHCT1G125
    └── RGB LEDs
```

TPS61023 `EN` is controlled by nRF52840.

### 10.3 RGB Data

```text
nRF52840 3.3 V GPIO
        │
SN74AHCT1G125
        │
 5 V logic data
        │
 33–100 Ω footprint
        │
 WS2812C-2020 DIN
```

Buffer supply comes from `5V_RGB` so the RGB subsystem loses both power and data drive when disabled.

---

## 11. Display

Display is required in V1.

Existing module pinout:

```text
GND
VCC
SCK
SDA
RES
DC
CS
```

It appears to be a four-wire SPI OLED module, but its controller is not yet identified.

Do not hard-code SSD1306/SH1106 assumptions until the module is identified.

Mechanical allowance:

- approximately 40 × 35 mm maximum module envelope

Power:

```text
3V3_LOGIC → TPS22919 → OLED_VCC
```

Shutdown sequence:

1. Put display into sleep/off state.
2. Put SPI/control pins into safe low/high-impedance state.
3. Disable TPS22919.

---

## 12. Pad Battery and Charging

### 12.1 Cell

Power-Xtra IFR32700:

- LiFePO4
- 1S1P
- 3.2 V nominal
- 5000 mAh
- approximately 16 Wh
- approximately Ø32 × 70 mm

### 12.2 Charger

BQ25185:

```text
POGO_5V → BQ25185
             ├── BAT ↔ IFR32700
             └── SYS → Pad power rails
```

Design targets:

- LiFePO4 charge regulation: 3.65 V
- Charge current: approximately 500 mA
- Battery NTC/temperature monitoring
- Proper power-path operation

Exact VSET/ILIM/ISET/TS networks must be verified from the current datasheet during schematic capture.

### 12.3 Secondary Protection

No separate LFP protection IC is currently planned.

The design relies on:

- BQ25185 protection behavior
- NTC monitoring
- Firmware battery monitoring
- Controlled graceful shutdown

This decision should be revisited if the selected physical cell or cell holder introduces different protection requirements.

---

## 13. Pad Power Rails

```text
POGO +5V
   │
 BQ25185
   │
   ├──────── BAT ↔ IFR32700
   │
   └──────── SYS
              │
              ├── TPS63802 → 3V3_LOGIC
              │      ├── nRF52840
              │      ├── TCA9555
              │      ├── encoders
              │      └── TPS22919 → OLED
              │
              └── TPS61023 → 5V_RGB
                              └── 36 RGB LEDs
```

TPS63802 component values and inductor selection must follow its reference design/datasheet.

TPS61023 must be sized for the full RGB worst-case load, not merely normal firmware brightness.

---

## 14. Battery Measurement

Battery voltage is measured by the nRF52840 ADC through a switched high-value divider.

Sequence:

```text
Enable divider
Wait for settling
Sample ADC
Disable divider
```

Starting firmware thresholds:

- approximately 3.3 V: low-battery warning
- approximately 3.0 V: graceful shutdown

These are initial engineering thresholds, not precise LiFePO4 state-of-charge percentages.

---

## 15. Docking Interface

Six pogo contacts:

```text
GND | +5V | DET | RX | TX | GND
```

Normal behavior:

- `+5V`: powers charger/pad
- `DET`: dock presence
- BLE remains the normal data link

`RX/TX` are reserved for:

- diagnostics
- recovery
- fallback communication

Pogo UART should not automatically replace BLE during normal docking.

Magnets on both sides of the pogo area provide mechanical alignment/retention.

---

## 16. Debug and Recovery

Every programmable MCU receives a physical debug/recovery path.

### Dock

- RP2350 SWD
- RP2040-A SWD
- RP2040-B SWD
- nRF52840 SWD

### Pad

- nRF52840 SWD

Preferred development header exposes:

```text
SWDIO
SWDCLK
RESET
VCC
GND
```

UART test access should also be available where practical.

Recommended dock silkscreen identifiers:

```text
HOST
HID-A
HID-B
BLE
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
- Follow the exact nRF52840 module/reference antenna keepout.
- Place USB ESD devices at the connectors.
- Keep switching-regulator hot loops compact.
- Keep RGB high-current paths away from sensitive RF/analog areas.
- Separate functional blocks clearly in placement.

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
├── NRF52840
├── INPUTS
├── RGB
├── DISPLAY
└── DOCK_INTERFACE
```

---

## 20. Schematic Capture Order

### Dock

1. USB-C Personal/Work power inputs
2. TPS2121 and `SYS_5V`
3. RP2350 core power/clock/debug
4. Keyboard USB host connector + ESD + TPS2553
5. RP2040-A core + Personal USB
6. RP2040-B core + Work USB
7. Dock nRF52840
8. Three internal UART links
9. SWD/debug headers
10. Power decoupling and final ERC review

### Pad

1. IFR32700 connector/holder and NTC
2. Pogo input
3. BQ25185
4. TPS63802 3V3 rail
5. TPS61023 5V RGB rail
6. nRF52840
7. TCA9555 + switches/selector
8. Encoders
9. SN74AHCT1G125 + RGB chain
10. TPS22919 + OLED
11. Battery ADC network
12. SWD/pogo UART/debug
13. Power decoupling and final ERC review

---

## 21. Items to Verify, Not Redesign

The architecture is frozen, but the following are intentionally finalized during schematic work:

- Exact RP2350/RP2040 implementation and packages
- Exact nRF52840 module/SoC implementation
- Crystal requirements
- USB-C connector footprints
- CC resistor implementation
- Decoupling networks
- TPS2121 settings
- TPS2553 RILIM
- BQ25185 VSET/ILIM/ISET/TS values
- TPS63802 inductor/passives
- TPS61023 inductor/passives
- TCA9555 pull-up requirements
- Exact WS2812C-2020 variant
- RGB data series resistor
- Battery ADC resistor values/switch
- Display controller and footprint
- Encoder SKU/footprint
- Toggle switch SKU/panel hole
- Key-switch footprints
- Pogo connector dimensions
- SWD connector standard
- Final PCB stack-up
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
