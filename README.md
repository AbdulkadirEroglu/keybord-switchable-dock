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
   - 1.69" colour IPS display (SPI).
   - Physical `PERSONAL | OFF | WORK` metal toggle switch.
   - Li-ion 21700 battery and dock charging.
   - BLE is the normal data link; pogo UART is reserved for diagnostics/recovery.

## High-Level Architecture

```text
┌──────────── WIRELESS CONTROL PAD ────────────┐
│                                             │
│ Pico 2 WH (RP2350 + CYW43439)               │
│ ├─ 12 × mechanical key                     │
│ ├─ 2 × rotary encoder + push               │
│ ├─ 36 × addressable RGB                    │
│ ├─ 1.69" colour TFT                         │
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
| Pad MCU / wireless | Raspberry Pi Pico 2 WH, socketed (on-board buck-boost 3.3 V) |
| Pad GPIO expander | TCA9555 |
| Pad charger | TP4056 (switchable ≈ 146 / 510 mA, NTC 0–45 °C, Pico-controlled enable for a 70–80 % docked window) |
| Pad power path | TPS2116 (pogo 5 V priority, battery fallback) |
| Cell protection | DW01A + FS8205A |
| Battery | 2 × Samsung SDI INR21700-50E in parallel (3.6 V, ≈ 9.8 Ah Li-ion), dual 21700 holder |
| RGB 5 V boost | TPS61023 |
| Display load switch | TPS22919 |
| RGB logic buffer | SN74AHCT1G125 |
| RGB LEDs | 36 × SK6812MINI-E (reverse mount) |
| Dock dual-input power mux | TPS2116 |
| Keyboard VBUS switch | TPS2553 |
| Pogo +5V switch | TPS2552 (enabled by dock detect) |
| ESD protection | 4 × TPD4E1U06 (each USB-C port: D+, D−, CC1, CC2; pogo contacts) |
| Module USB/SWD contacts | P50-B1 spring probes to the modules' underside pads |
| Keys | 12 × Razer Yellow Linear (3-pin MX) in Kailh hot-swap sockets, FR4 plate |
| Encoders | 2 × Bourns PEC11R-4220F-S0024 (24 detents, push switch) |
| Target selector | Metal SPDT ON-OFF-ON toggle |
| Display | 1.69" 240×280 IPS TFT, ST7789, SPI, PWM backlight |

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
Toggle → Pad Pico 2 WH → BLE → Host Pico 2 W
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
│   └── pad-rp2350/
├── datasheets/
├── docs/
├── README.md
└── DESIGN.md
```

## V2 Direction: Chips on the Board, JLCPCB Assembly

Research on 2026-09-28 (details, part numbers and the full price table: [docs/dock-v2-plan.md](docs/dock-v2-plan.md)) showed that a dock with the chips soldered directly on the PCB and machine-assembled by JLCPCB costs less than the v1 dock built from Pico modules. **The project starts over on this basis.**

| | v1 dock (modules) | v2 dock (chips on the board) |
|---|---|---|
| Keyboard host + PC1 endpoint | Pico 2 W + Pico 2 | RP2354A **A** (PIO-USB host + native USB device) |
| PC2 endpoint | Pico 2 | RP2354A **B** (native USB device) |
| BLE | Pico 2 W radio | ESP32-C3-MINI-1-H4X module (pre-certified, PCB antenna), UART to RP2354A A |
| Power | from the PCs' VBUS | own USB-C PD input: CH224A asks for 9 V (or 12 V), TPS54331 buck to 5 V, AMS1117 to 3.3 V; the PC ports only sense VBUS |
| Build | hand-soldered, socketed modules | JLCPCB Economic PCBA |

Key findings:

- **No cheap chip has three USB controllers**, so two chips is the minimum. Two RP2354A (RP2350 with 2 MB flash inside) keep the v1 firmware (TinyUSB + Pico-PIO-USB, keyboards with built-in hubs work) and flash as UF2 drives from each PC, no programmer needed. CH32V203 + CH32X035 would save only about $7 per order and has no USB-hub support yet; CH9350L + CH9329 (KVM chips) has no NKRO and raw reports.
- **CH224K is discontinued**; CH224A replaces it pin for pin. Ask for **9 V**, not 12 V: 12 V is optional in USB PD and many chargers skip it. On a plain 5 V charger the buck passes about 4.75 V through, and the CH224A's PG pin tells the firmware to limit the pad's charging.
- **The dock needs a USB-C charger** in v2 (v1 needed none).
- **JLCPCB Economic PCBA fees:** setup $8.18, stencil $1.53, $0.0016 per SMD joint, $3.07 per unique Extended part (Preferred Extended parts are free), through-hole $3.58 + $0.0164 per joint. Assembly starts at **2 boards**; you can fabricate 5 and assemble 2.
- **Turkey import tax:** since about February 2026 parcels from China pay a flat 60 % (the €30 exemption is gone). Plan on 1.6 × (goods + shipping).
- **Parts that need JLCPCB's placement** (no iron can do them without hot air): RP2354A (QFN-60), ESP32-C3-MINI-1 (pads underneath), CH224A (exposed pad), the 0806 core inductor and the USB-C receptacles (fine pitch). SOT-23 parts, the TVS, the 10 mm inductor and the USB-A port are easy to hand-solder.

Cost (estimates marked; PCB price and shipping must be checked in the real quote):

| Build | Before tax | Landed in Turkey |
|---|---|---|
| v1 dock, one unit (BOM.xlsx) | — | 3500 TL ≈ $72 |
| v2, 5 PCBs, **2 assembled**, JLCPCB places only the 5 hard parts, the rest hand-soldered | ≈ $65–70 | ≈ $105–115, **≈ $55 per working dock** |
| v2, 5 PCBs, all 5 fully assembled | ≈ $114–123 | ≈ $180–195, ≈ $37 per dock |

## Current Project State

**Starting over with the v2 dock** (see above). For v1: the architecture is frozen, the **dock schematic and PCB are complete** (routed, DRC clean, Gerbers generated locally); a silkscreen pass remains before ordering. The **pad parts are selected** (DESIGN.md §2.2, §8–§15); next is the pad schematic.

Still to finalize:

- Dock silkscreen pass and order (enclosure clearance: spring-probe tails need 3–4 mm below the dock PCB)
- Pad schematic, PCB and FR4 switch plate
- Display module measurement (outline, window, holes, pin order), encoder knobs
- Pogo board (separate small PCB in the pad's back wall) and FR4 switch plate
- Pad Pico 2 WH antenna keep-out in the pad layout and enclosure
- Enclosure CAD and exact dimensions

See [DESIGN.md](DESIGN.md) for the detailed engineering baseline.
