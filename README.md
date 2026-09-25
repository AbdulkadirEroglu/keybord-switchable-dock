# Dual-PC Keyboard Router & Wireless Control Pad

A custom hardware project for sharing one physical USB keyboard between two computers while adding a detachable wireless control pad for call controls, media controls, macros, status feedback, and target selection.

The design prioritizes **reliability, recoverability, wired PC connections, explicit physical control, and independent debug paths**.

## System Overview

The project consists of two custom PCBs:

1. **Main Dock / Keyboard Router**
   - Accepts a normal USB keyboard.
   - Connects to both Personal and Work PCs over USB.
   - Routes keyboard/HID reports to the selected target.
   - Receives commands from the detachable pad over BLE.
   - Is powered automatically from either connected PC; no external adapter is required.

2. **Wireless Control Pad**
   - Detachable and battery powered.
   - 12 mechanical keys.
   - Two rotary encoders with push switches.
   - 36 addressable RGB LEDs.
   - SPI OLED display.
   - Physical `PERSONAL | OFF | WORK` metal toggle switch.
   - LiFePO4 battery and dock charging.
   - BLE is the normal data link; pogo UART is reserved for diagnostics/recovery.

## High-Level Architecture

```text
┌──────────── WIRELESS CONTROL PAD ────────────┐
│                                             │
│ nRF52840                                    │
│ ├─ 12 × mechanical key                     │
│ ├─ 2 × rotary encoder + push               │
│ ├─ 36 × addressable RGB                    │
│ ├─ SPI OLED                                │
│ ├─ PERSONAL / OFF / WORK selector          │
│ └─ battery / charging / power management   │
└───────────────────┬─────────────────────────┘
                    │ BLE
                    ▼
┌────────────────── MAIN DOCK ─────────────────┐
│                                             │
│ BLE ──► Host Pico 2 W (on-board radio)      │
│                              ▲              │
│ Keyboard ───── USB Host ─────┘              │
│                              │              │
│                   ┌──────────┴─────────┐    │
│                   │                    │    │
│               UART 1M             UART 1M   │
│                   │                    │    │
│            HID-A Pico 2       HID-B Pico 2  │
│                   │                    │    │
│                  USB                  USB   │
└───────────────────┼────────────────────┼────┘
                    ▼                    ▼
                PERSONAL               WORK
```

## Main Hardware

| Function | Selected Part / Design |
|---|---|
| Dock main MCU / USB host / BLE | Raspberry Pi Pico 2 W (RP2350 + CYW43439), socketed |
| Personal PC HID endpoint | Raspberry Pi Pico 2 (RP2350), socketed |
| Work PC HID endpoint | Raspberry Pi Pico 2 (RP2350), socketed |
| Pad MCU / wireless | nRF52840 |
| Pad GPIO expander | TCA9555 |
| Pad charger / power path | BQ25185 |
| Battery | Power-Xtra IFR32700, 3.2 V 5000 mAh LiFePO4 |
| Pad 3.3 V regulator | TPS63802 |
| RGB 5 V boost | TPS61023 |
| OLED load switch | TPS22919 |
| RGB logic buffer | SN74AHCT1G125 |
| RGB LEDs | 36 × WS2812C-2020 class |
| Dock dual-input power mux | TPS2116 |
| Keyboard VBUS switch | TPS2553 |
| Pogo +5V switch | TPS2552 (enabled by dock detect) |
| ESD protection | 4 × TPD4E1U06 (each USB-C port: D+, D−, CC1, CC2; pogo contacts) |
| Module USB/SWD contacts | P50-B1 spring probes to the modules' underside pads |
| Keys | 12 × MX-compatible mechanical switches |
| Encoders | 2 × rotary encoder with push |
| Target selector | Metal SPDT ON-OFF-ON toggle |
| Display | SPI OLED; exact controller/module TBD |

Exact passive values, packages, footprints, connector SKUs, inductors and configuration resistors must be verified against the current manufacturer datasheets during schematic capture.

## Target Selection

The physical selector is located on the **control pad**, not the dock.

```text
PERSONAL
   │
  OFF
   │
 WORK
```

The mechanical switch is the source of truth. Its state travels:

```text
Toggle → Pad nRF52840 → BLE → Host Pico 2 W
```

If the pad/BLE connection is lost, the RP2350 must eventually release all active HID states and enter `OFF`.

## Communications

- Keyboard → RP2350: USB Host
- Pad ↔ Dock: BLE
- Pad ↔ Host Pico 2 W: BLE (host's on-board radio)
- Host ↔ HID-A: independent 1 Mbaud UART
- Host ↔ HID-B: independent 1 Mbaud UART
- HID-A → Personal PC: USB HID
- HID-B → Work PC: USB HID
- Pogo UART: debug/recovery only

The internal UART protocol uses framed binary packets:

```text
SOF | TYPE | SEQ | LEN | PAYLOAD | CRC
```

Normal HID reports may be fire-and-forget. Critical control operations can require acknowledgement.

## Fail-Safe Philosophy

The design should fail toward **released keys and no routing**, not toward a stuck input.

Examples:

- Target change → release previous endpoint before changing route.
- `OFF` → release both endpoints.
- BLE/pad timeout → release all and route OFF.
- Host communication timeout → local HID endpoint sends released state and enters safe idle.
- Keyboard host faults → RP2350 can power-cycle keyboard VBUS.
- Every MCU receives a physical debug/recovery interface.

## Mechanical Baseline

Control pad target envelope:

- Width: approximately 160 mm
- Depth: approximately 110–120 mm
- Front height: approximately 18–22 mm
- Rear height: approximately 35–40 mm
- Wedge/sloped enclosure

The Ø32 × 70 mm 32700 battery sits in the **rear thick section below the display/encoder area**, not below the mechanical keys.

The rear dock interface uses magnets for alignment and six pogo contacts:

```text
GND | +5V | DET | RX | TX | GND
```

## Repository Layout

```text
dock-pad/
├── hardware/
│   ├── dock/
│   └── pad/
├── mechanical/
│   ├── dock/
│   └── pad/
├── firmware/
│   ├── host-rp2350/
│   ├── hid-endpoint/
│   ├── dock-ble-nrf52840/
│   └── pad-nrf52840/
├── datasheets/
├── docs/
├── README.md
└── DESIGN.md
```

## Current Project State

The V1 architecture is frozen. The **dock schematic is captured and reviewed**; next are the dock PCB layout and then the wireless pad schematic.

Still to finalize:

- Dock PCB outline, placement, routing and enclosure clearances (spring-probe tails need 3–4 mm below the dock PCB)
- BQ25185 configuration, NTC network and switchable charge current
- TPS63802 and TPS61023 magnetics/passives
- OLED module/controller
- Encoder and mechanical switch SKUs
- Pad nRF52840 antenna keepout
- Battery ADC divider
- PCB layer count and final stack-up
- Enclosure CAD and exact dimensions

See [DESIGN.md](DESIGN.md) for the detailed engineering baseline.
