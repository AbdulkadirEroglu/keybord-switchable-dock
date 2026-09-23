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
│ Dock nRF52840 ── UART ──► RP2350            │
│                              ▲              │
│ Keyboard ───── USB Host ─────┘              │
│                              │              │
│                   ┌──────────┴─────────┐    │
│                   │                    │    │
│               UART 1M             UART 1M  │
│                   │                    │    │
│               RP2040-A             RP2040-B│
│                   │                    │    │
│                  USB                  USB   │
└───────────────────┼────────────────────┼────┘
                    ▼                    ▼
                PERSONAL               WORK
```

## Main Hardware

| Function | Selected Part / Design |
|---|---|
| Dock main MCU / USB host | RP2350 |
| Personal PC HID endpoint | RP2040 |
| Work PC HID endpoint | RP2040 |
| Dock wireless MCU | nRF52840 |
| Pad MCU / wireless | nRF52840 |
| Pad GPIO expander | TCA9555 |
| Pad charger / power path | BQ25185 |
| Battery | Power-Xtra IFR32700, 3.2 V 5000 mAh LiFePO4 |
| Pad 3.3 V regulator | TPS63802 |
| RGB 5 V boost | TPS61023 |
| OLED load switch | TPS22919 |
| RGB logic buffer | SN74AHCT1G125 |
| RGB LEDs | 36 × WS2812C-2020 class |
| Dock dual-input power mux | TPS2121 |
| Keyboard VBUS switch | TPS2553 |
| USB data ESD | 3 × TPD2EUSB30 |
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
Toggle → Pad nRF52840 → BLE → Dock nRF52840 → UART → RP2350
```

If the pad/BLE connection is lost, the RP2350 must eventually release all active HID states and enter `OFF`.

## Communications

- Keyboard → RP2350: USB Host
- Pad ↔ Dock: BLE
- Dock nRF52840 ↔ RP2350: 1 Mbaud full-duplex UART
- RP2350 ↔ RP2040-A: independent 1 Mbaud UART
- RP2350 ↔ RP2040-B: independent 1 Mbaud UART
- RP2040-A → Personal PC: USB HID
- RP2040-B → Work PC: USB HID
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
- RP2040 communication timeout → local HID endpoint sends released state and enters safe idle.
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
keyboard-router/
├── hardware/
│   ├── dock/
│   └── pad/
├── mechanical/
│   ├── dock/
│   └── pad/
├── firmware/
│   ├── rp2350/
│   ├── rp2040-hid/
│   ├── dock-nrf52840/
│   └── pad-nrf52840/
├── datasheets/
├── docs/
├── README.md
└── DESIGN.md
```

## Current Project State

The V1 system architecture and major IC selections are considered frozen. The next phase is KiCad schematic capture, beginning with the main dock and then the wireless pad.

Implementation details still to finalize during schematic/PCB work include:

- Exact MCU/module variants and footprints
- USB-C connector SKUs and CC networks
- Passive values and decoupling
- TPS2121 configuration
- TPS2553 current-limit resistor
- BQ25185 configuration and NTC network
- TPS63802 and TPS61023 magnetics/passives
- OLED module/controller
- Encoder and mechanical switch SKUs
- nRF52840 antenna keepout
- Battery ADC divider
- Debug connector pinouts
- PCB layer count and final stack-up
- Enclosure CAD and exact dimensions

See [DESIGN.md](DESIGN.md) for the detailed engineering baseline.
