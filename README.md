# Dual-PC Keyboard Router & Wireless Control Pad

A custom hardware project for sharing one physical USB keyboard between two computers while adding a detachable wireless control pad for call controls, media controls, macros, status feedback, and target selection.

The design prioritizes **reliability, recoverability, wired PC connections, explicit physical control, and independent debug paths**.

## System Overview

The project consists of two custom devices:

1. **Main Dock / Keyboard Router (v2)**
   - Accepts a normal USB keyboard (USB-C).
   - Connects to both Personal and Work PCs over USB and appears as a keyboard to each.
   - Routes keyboard/HID reports to the selected target.
   - Receives the pad's events and selector state over BLE.
   - Powered by its own **USB-C PD charger** (asks for 9 V; a 30 W charger is used). It never draws power from, or back-feeds, the PCs.
   - Chips on the board, built by **JLCPCB** (machine assembly); two through-hole parts are hand-soldered.

2. **Wireless Control Pad** (to be redesigned; current plan below)
   - Detachable and battery powered.
   - 12 mechanical keys.
   - Two rotary encoders with push switches.
   - 36 addressable RGB LEDs.
   - 1.69" colour IPS display (SPI).
   - Physical `PERSONAL | OFF | WORK` metal toggle switch.
   - Li-ion 21700 battery pack, charged while docked.
   - BLE is the normal data link; the pogo UART is reserved for diagnostics/recovery.

## High-Level Architecture

```text
┌──────────── WIRELESS CONTROL PAD ────────────┐
│ Pico 2 WH (RP2350 + CYW43439)   [v1 plan]    │
│ keys, encoders, RGB, display, selector,      │
│ battery + charger                            │
└──────────┬──────────────────────┬────────────┘
           │ BLE                  │ 7-pin magnetic pogo (5 V, DET, UART)
           ▼                      ▼
┌────────────────────── MAIN DOCK (v2) ──────────────────────┐
│ ESP32-C3-MINI-1 (BLE) ── UART ──┐                          │
│                                 ▼                          │
│ keyboard ═ USB-C ═ PIO-USB ═► RP2354A A ═ USB ═► PERSONAL  │
│                                 │ UART, RUN, BOOTSEL, SWD  │
│                                 ▼                          │
│                             RP2354A B ═══ USB ═► WORK      │
│                                                            │
│ USB-C PD charger ─ CH224A (9 V) ─ TPS54331 5 V ─ 3.3 V LDO │
└────────────────────────────────────────────────────────────┘
```

## Main Hardware

### Dock (v2)

| Function | Part |
|---|---|
| Keyboard host + Personal PC endpoint | RP2354A **A** (RP2350 with 2 MB flash, QFN-60): Pico-PIO-USB host + native USB device |
| Work PC endpoint | RP2354A **B** (native USB device) |
| BLE to the pad | ESP32-C3-MINI-1-H4X module (pre-certified, PCB antenna), UART to A |
| Power input | USB-C, CH224A PD sink (9 V, I2C status to A), SMBJ15A TVS |
| 5 V | TPS54331 buck (5.16 V, 3 A), SLO0630H6R8MTT 6.8 µH, SS54 |
| 3.3 V | AMS1117-3.3 |
| Keyboard VBUS | SY6280AAC, 1.0 A, switched on only when a keyboard is detected on CC |
| Pad 5 V (pogo) | SY6280AAC, 1.45 A, switched on in hardware when the pad is docked (DET) |
| ESD | TPD4E1U06 on every USB-C port and the pogo contacts |
| Connectors | 4 × USB-C (TYPE-C-31-M-12); 7-pin JST-XH header to the pogo board in the dock lid (straight 7-pin magnetic pogo contacts) |
| Crystals | ABM8-272-T3 (Raspberry Pi's recommended part) |

Every part, its value and LCSC number: [`hardware/dock-v2/DOCK_CONNECTIONS.md`](hardware/dock-v2/DOCK_CONNECTIONS.md). Why each was chosen: `docs/dock-v2-*.md`.

### Pad (v1 plan, to be redesigned)

| Function | Selected Part / Design |
|---|---|
| Pad MCU / wireless | Raspberry Pi Pico 2 WH, socketed (on-board buck-boost 3.3 V) |
| Pad GPIO expander | TCA9555 |
| Pad charger | TP4056 (switchable ≈ 146 / 510 mA, NTC 0–45 °C, Pico-controlled enable for a 70–80 % docked window) |
| Pad power path | TPS2116 (pogo 5 V priority, battery fallback) |
| Cell protection | DW01A + FS8205A |
| Battery | 2 × Samsung SDI INR21700-50E in parallel (3.6 V, ≈ 9.8 Ah Li-ion), dual 21700 holder |
| RGB 5 V boost | TPS61023 |
| RGB logic buffer | SN74AHCT1G125 |
| RGB LEDs | 36 × SK6812MINI-E (reverse mount) |
| Keys | 12 × Razer Yellow Linear (3-pin MX) in Kailh hot-swap sockets, FR4 plate |
| Encoders | 2 × Bourns PEC11R-4220F-S0024 (24 detents, push switch) |
| Target selector | Metal SPDT ON-OFF-ON toggle |
| Display | 1.69" 240×280 IPS TFT, ST7789, SPI, PWM backlight |

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
Toggle → Pad → BLE → ESP32-C3 → UART → RP2354A A
```

If the pad/BLE connection is lost, the dock must eventually release all active HID states and enter `OFF`.

## Communications

- Keyboard → RP2354A A: USB host (Pico-PIO-USB)
- RP2354A A → Personal PC: USB HID (native USB)
- RP2354A A ↔ RP2354A B: 1 Mbaud+ UART; B → Work PC: USB HID
- Pad ↔ dock: BLE (ESP32-C3 central, pad peripheral), ESP32-C3 ↔ A: UART
- Pogo UART (A's PIO UART): debug/recovery only

The internal UART protocol uses framed binary packets:

```text
SOF | TYPE | SEQ | LEN | PAYLOAD | CRC
```

Normal HID reports may be fire-and-forget. Critical control operations can require acknowledgement.

## Fail-Safe Philosophy

The design should fail toward **released keys and no routing**, not toward a stuck input.

- Target change → release the previous endpoint before changing the route.
- `OFF` → release both endpoints.
- BLE/pad timeout → release all and route OFF.
- A ↔ B link timeout → B sends a released state and idles; A can reset B.
- Keyboard faults → A power-cycles the keyboard's VBUS.
- Every MCU has a physical recovery path, and A can reflash B (SWD) and the ESP32-C3 (UART) from the Personal PC.

## Mechanical Baseline

- **Dock:** PCB 100 × 100 mm, 2 layers. PC cables leave at the back, the keyboard at the left, the charger at the right. **The pad sits on top of the dock:** the pogo contacts are on a small board in the dock lid, cabled to the dock board.
- **Pad (v1 plan):** wedge enclosure ≈ 160 × 110–120 mm, front ≈ 25 mm, back ≈ 44 mm, battery at the back under the display/encoder row.

Docking contacts (dock side), magnets on both sides:

```text
GND | +5V | DET | RX | TX | +5V | GND
```

## Repository Layout

```text
dock-pad/
├── hardware/
│   ├── dock-v2/        v2 dock: KiCad project, DOCK_CONNECTIONS.md, PCB_PLACEMENT.md
│   ├── dock/           v1 dock (Pico modules), reference
│   ├── pad/            pad (v1 plan)
│   ├── pogo/           pad pogo board
│   ├── libraries/      shared symbols/footprints/3D models (THIRD_PARTY.md)
│   ├── reference/      Raspberry Pi RP2350A Minimal design (MIT)
│   └── tools/          RPi core-layout copy script, dock v2 connection model and wiring checker
├── mechanical/
├── firmware/
├── datasheets/
├── docs/               dock v2 design decisions (dock-v2-*.md), pad drawings
├── README.md
└── DESIGN.md
```

## Current Project State

- **Dock v2 (branch `dock-v2`):** every part decided and placed on the six schematic sheets (154 parts, values, footprints, LCSC numbers). Next: wiring the schematic by hand from [DOCK_WIRING.md](hardware/dock-v2/DOCK_WIRING.md) (component by component; the circuit is explained in DOCK_CONNECTIONS.md) (checked with `hardware/tools/dock_v2_connections/check_wiring.py`), then placement and routing on a 4-layer board. The order cost will be calculated when the PCB is ready.
- **Pad:** being redesigned. Decided so far: **ESP32-S3-MINI-1-N8** (MCU + BLE, JLC assembly), the pad **sits on top of the dock** with its pogo board in the floor, **1 × 21700-50E** with an **ETA6003** switching charger (power path), charged only on the dock, TLV75733P 3.3 V LDO, direct-GPIO keys/encoders, SK6812MINI-E + XL-2020 LEDs on a TPS61023 5 V boost, Meon 1.69" ST7789 module. Decisions: `docs/pad-v2-*.md`. The rest of `hardware/pad/` is still the v1 plan.
- **v1 dock:** complete (routed, DRC clean) on `master`; superseded by v2.

See [DESIGN.md](DESIGN.md) for the engineering baseline.
