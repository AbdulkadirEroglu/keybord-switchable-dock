# Dock v2 — PCB placement groups

Where the parts of the v2 dock go. What each part does and why it was chosen is in the design docs:
[power input](../../docs/dock-v2-power-input.md), [USB ports](../../docs/dock-v2-usb-ports.md), [pogo](../../docs/dock-v2-pogo.md), [MCU support](../../docs/dock-v2-mcu-support.md), [MCU selection](../../docs/dock-v2-mcu-selection.md).

There is no schematic yet, so references below are **suggestions** using one hundred-block per schematic sheet (KiCad: *Annotate → Use first free number after sheet number × 100*). Renumber freely.

| Sheet | File | Refs |
|---|---|---|
| 1 Power | `power.kicad_sch` | 1xx |
| 2 USB ports | `usb_ports.kicad_sch` | 2xx |
| 3 MCU A | `mcu_a.kicad_sch` | 3xx |
| 4 MCU B | `mcu_b.kicad_sch` | 4xx |
| 5 BLE | `ble.kicad_sch` | 5xx |
| 6 Pogo | `pogo.kicad_sch` | 6xx |

## Contents

1. [Edges and board outline](#1-edges-and-board-outline)
2. [Floor plan](#2-floor-plan)
3. [Groups](#3-groups)
4. [Pogo: front edge or pad on top](#4-pogo-front-edge-or-pad-on-top)
5. [Layers, sides and net classes](#5-layers-sides-and-net-classes)
6. [Placement rules](#6-placement-rules)
7. [Checklist before routing](#7-checklist-before-routing)
8. [Project files and libraries](#8-project-files-and-libraries)

## 1. Edges and board outline

| Edge | What sits there | Why |
|---|---|---|
| **Back** | J202 **Personal PC** (left), J203 **Work PC** (right) | the two long cables to the PCs leave together at the back |
| **Left** | J201 **keyboard** | keyboard sits left of the dock |
| **Right** | J101 **power** (USB-C PD charger) | charger cable away from the data cables; the noisy buck stays on this side |
| **Front** | J601 **pogo** to the pad | pad docks at the front (or on top, §4) |

Coordinates are **mm from the board's back-left corner**, seen from the top, x to the right, y towards the front (same system as the pad's placement guide):

```text
 (0,0) ──────────── x → ──────────── (90,0)     BACK edge (PC cables)
   │
   y
   ↓
 (0,70) ─────────────────────────── (90,70)     FRONT edge (pogo, pad)
```

- **Outline (starting size): 90 × 70 mm**, (0, 0) to (90, 70), 1 mm corner radius. Inside JLCPCB's 100 × 100 mm price tier; shrink once everything is placed.
- **Mounting holes:** 4 × M3 (`MountingHole:MountingHole_3.2mm_M3`) at (4, 4), (86, 4), (86, 66) and (20, 66). The front-left hole moves in from the corner to stay clear of the antenna (§3, group 8).
- KiCad setup (as for the pad): draw the outline, **Place → Grid Origin** on its top-left corner, then *Preferences → PCB Editor → Display Options*: origin = grid origin, y increases down. Place parts with **E** (exact X/Y), lock them with **L** once final.

## 2. Floor plan

Approximate zones, to scale-ish (1 character ≈ 2 mm):

```text
 x=0         20          40          60          80   90
 ┌──────────[J202 PC1]─────────────────[J203 PC2]──────┐ y=0  BACK
 │ ○                                                ○  │
 │   ┌─────────────────┐              ┌────────────┐   │
[J201┤  MCU A  (U301)  │◄── UART, ───►│ MCU B      │   │
 KBD │  crystal, VREG  │    RUN, SWD  │ (U401)     │   │ y≈20
 │   │  BOOTSEL/RESET  │              │ BOOTSEL B  │   │
 │ KBD switch  └───────┘  3V3 LDO     └────────────┘   │
 │ 220µF (C2xx)            (U104)          CH224A ─────┤
 ├──────┐                                  PD, TVS    [J101
 │ANT ▒▒│ ESP32-C3                        ┌───────────┤ PWR  y≈48
 │▒▒▒▒▒▒│ (U501)                          │ 5 V buck  │
 ├──────┘                                 │ TPS54331  │
 │           ┌──[pogo switch, ESD]──┐     │ L101, D102│
 │    ○      └────[J601 POGO]───────┘     └───────────┤ ○
 └─────────────────────────────────────────────────────┘ y=70 FRONT
```

## 3. Groups

Place each group as a cluster at its zone, then route between groups.

| # | Group (zone) | Refs | Part | Package | Notes |
|---|---|---|---|---|---|
| **1** | **Power input** (right edge, y ≈ 40–56) | J101 | TYPE-C-31-M-12 (C165948) | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | mouth on the right edge, centre ≈ (86.5, 48) |
| | | U101 | TPD4E1U06 | SOT-23-6 | ESD on CC1, CC2, D+, D−, **≤ 5 mm from J101** |
| | | D101 | SMBJ15A | SMB | VBUS TVS, **at J101 VBUS pads** |
| | | U102 | CH224A | ESSOP-10 (exposed pad) | next to J101; CC and D± straight in |
| | | R1xx, C1xx | 6.8 k CFG1, 1 µF VHV, 10 k PG pull-up, 4.7 k ×2 I2C pull-ups | 0402 | CFG1 resistor right at the pin; I2C pull-ups can sit at either end |
| **2** | **5 V buck** (front-right corner, x ≈ 60–88, y ≈ 54–68) | U103 | TPS54331DR | SOIC-8 | copper pour under/around it for heat |
| | | D102 | SS54 | SMC | catch diode, **shortest loop**: VIN cap → U103 → PH → D102 → GND |
| | | L101 | 6.8 µH (SMDRH105R-6R8NT or a Basic 10 × 10 part) | 10 × 10 mm | next to the PH pin |
| | | C1xx | 2 × 10 µF 25 V (in), 3 × 22 µF 25 V 1206 (out), boot 100 nF, SS, comp, feedback | 0805/1206/0402 | input caps **at VIN/GND pins**; feedback divider near VSENSE, away from L101/D102 |
| **3** | **3.3 V LDO** (centre, ≈ (45, 38)) | U104 | AMS1117-3.3 | SOT-223 | central: 3.3 V goes to A, B and the ESP32; tab on a copper pad |
| | | C1xx | 10 µF in, 10 µF out | 0805 | |
| **4** | **Keyboard port** (left edge, y ≈ 10–36) | J201 | TYPE-C-31-M-12 | USB-C | mouth on the left edge, centre ≈ (3.5, 18) |
| | | U201 | TPD4E1U06 | SOT-23-6 | ESD on D+, D−, CC1, CC2, **≤ 5 mm from J201** |
| | | R2xx | 33 k ×2 (Rp to 3.3 V), 15 k ×2 (D± pull-downs), 22 Ω ×2 | 0402 | Rp at the connector; 22 Ω **near MCU A** |
| | | U202 | SY6280AAC | SOT-23-5 | keyboard VBUS switch, between the 5 V trunk and J201 |
| | | R2xx | 6.8 k ISET, 100 k EN pull-down, 10 k / 15 k KBD_VBUS divider | 0402 | ISET **short to U202 pin 3** |
| | | C201 | **220 µF 16 V THT** (Koshin PKRJ-016V221ME070-T/A5.0) | radial D6.3, P5.00 (check leads) | **hand-soldered**, at J201 VBUS; ≈ (11, 29) |
| | | C2xx | 10 µF 0805 + 1 µF (out), 1 µF (in) | | at J201 VBUS / U202 IN |
| **5** | **Personal PC port** (back edge, left) | J202 | TYPE-C-31-M-12 | USB-C | mouth on the back edge, centre ≈ (22, 3.5) |
| | | U203 | TPD4E1U06 | SOT-23-6 | **≤ 5 mm from J202** |
| | | R2xx | 5.1 k ×2 (Rd), 22 k / 33 k VBUS sense, 22 Ω ×2 | 0402 | Rd at the connector; 22 Ω **near MCU A**; VBUS is sense-only (no power) |
| **6** | **Work PC port** (back edge, right) | J203 | TYPE-C-31-M-12 | USB-C | centre ≈ (68, 3.5) |
| | | U204 | TPD4E1U06 | SOT-23-6 | **≤ 5 mm from J203** |
| | | R2xx | as group 5 | 0402 | 22 Ω **near MCU B** |
| **7a** | **MCU A** (back-left, centre ≈ (24, 22)) | U301 | RP2354A | QFN-60 7 × 7 (RPi footprint recommended) | USB_DP/DM side towards J202; PIO-USB GPIO pair towards J201 |
| | | L301, C3xx, R3xx | 3.3 µH AOTA-B201610S3R3 (**polarity dot**), 4.7 µF ×3, 33 Ω | 0806 / 0402 | **copy RPi's Minimal layout exactly** (§6) |
| | | Y301, C3xx, R3xx | ABM8-272-T3, 15 pF ×2, 1 k | 3225 / 0402 | crystal **as close as possible** to XIN/XOUT, no traces under it |
| | | C3xx | 100 nF × ≈ 11, 10 µF | 0402 / 0805 | one per power pin, on the pin |
| | | SW301, SW302 | TS-1187A: BOOTSEL A, RESET A | 5.1 × 5.1 mm | reachable from above; 1 k from QSPI_SS to SW301 near the chip |
| | | TP301–303 | SWD A (SWCLK, SWDIO, GND) | test pads | |
| | | D301, R3xx | status LED A | 0603 / 0402 | optional |
| **7b** | **MCU B** (back-right, centre ≈ (64, 22)) | U401 + same support parts | RP2354A | as 7a | USB side towards J203 |
| | | SW401 | BOOTSEL B | TS-1187A | |
| | | R4xx | 1 k B_BOOTSEL (from A) | 0402 | at B's QSPI_SS |
| | | TP401–403 | SWD B | test pads | A's SWD lines join here too |
| **8** | **BLE** (left edge, front half, ≈ x 0–17, y 40–53) | U501 | ESP32-C3-MINI-1-H4X | module 13.2 × 16.6 mm | **antenna end on the left edge**, keep-out: no copper on any layer, no parts (§6) |
| | | R5xx, C5xx | 10 k + 1 µF EN, 10 k GPIO8, 10 k GPIO2, 10 µF + 100 nF | 0402 / 0805 | decoupling at the 3V3 pin |
| | | TP501–504 | GPIO18/19 (USB), TXD0/RXD0 | test pads | fallback flashing |
| **9** | **Pogo** (front edge, centre) | J601 | 6-pin 2.54 mm magnetic pogo, right-angle (Motorobit) | `dock:Pogo-6` (25.2 × 4.6 mm) | **hand-soldered**; centre ≈ (45, 67.7); see §4 |
| | | U601 | TPD4E1U06 | SOT-23-6 | ESD on DET, TX, RX, **right at J601** |
| | | R6xx | 1 k ×3 (TX, RX, DET), 10 k DET pull-up, 100 k EN pull-up, 6.8 k ISET, 10 k / 15 k POGO_5V divider | 0402 | series resistors between U601 and the MCU A traces |
| | | Q601 | 2N7002 | SOT-23 | DET inverter → SY6280 EN |
| | | U602 | SY6280AAC | SOT-23-5 | pogo 5 V switch |
| | | C6xx | 1 µF (in), 10 µF + 1 µF (out) | | output caps at J601 +5V pin |

## 4. Pogo: front edge or pad on top

Two ways to dock the pad; the **electronics are identical**, only J601's footprint and position change:

| | Pad in front (current) | Pad on top of the dock |
|---|---|---|
| J601 | right-angle pogo at the **front edge**, contacts face forward | **vertical** pogo on the top side, contacts face up, near the front edge |
| Table space | dock + pad side by side, front to back | only the pad's footprint: the dock (≈ 90 × 70) hides under the pad (≈ 160 × 110–120) |
| Pad side | pogo board in the pad's back wall (as designed, DESIGN.md §15) | pogo board moves to the pad's **underside**; the pad enclosure and its pogo board change |
| Pad height | unchanged | raised by the dock's height (USB-C ≈ 3.3 mm + board + case ≈ 12–15 mm): keys sit higher |
| BLE | antenna free | pad covers the antenna while docked (distance is centimetres, fine); undocked it's free |
| Cables | exit back and sides | exit from under the pad's edges |

Nothing else on the board depends on this choice. Keep the pogo group at the front-centre zone either way, and pick J601's footprint when the enclosure is designed.

## 5. Layers, sides and net classes

- **All SMD parts on the top side** (one-sided JLCPCB assembly is cheaper). Only the two hand-soldered THT parts (C201, J601) have pins through the board.
- **4 layers recommended:** L1 parts + signals, **L2 solid GND**, L3 3.3 V / 5 V pours + a few signals, L4 signals. Two QFN-60s, four USB pairs and the buck route much more easily over an unbroken ground. The empty board file is set up with 4 copper layers; change it in *Board Setup → Physical Stackup* if you prefer 2.
- Net classes (copied from v1): **Default** 0.2 mm; **Power** 0.6 mm (VBUS_IN, +9V/VIN, +5V, KBD_VBUS, POGO_5V, +3V3, GND); **USB** differential pairs, 90 Ω (use JLCPCB's impedance calculator for the 4-layer stack and set width/gap).

## 6. Placement rules

- **ESD first:** each TPD4E1U06 within 5 mm of its connector, signals pass through its pads before anything else.
- **RP2354A core regulator:** copy the L1/C6/C7/R3/C9 layout from Raspberry Pi's *RP2350A Minimal* KiCad design, including the **inductor orientation (polarity dot)**. RPi: other layouts are "at your own risk".
- **Crystals:** right at XIN/XOUT, short equal traces, GND under them, no other traces nearby.
- **Buck loop:** VIN caps → U103 VIN/GND → PH → L101 / D102 → output caps: keep this loop small and on L1 with the L2 ground under it. Feedback trace away from L101 and D102.
- **Antenna:** ESP32-C3 antenna end on the board edge; no copper on any layer and no parts in the antenna area (follow the module footprint's keep-out and Espressif's *Hardware Design Guidelines*). Keep the pogo magnets and mounting screws ≥ 15 mm away from the antenna.
- **USB pairs:** connector → ESD → (22 Ω near the MCU) → MCU, short, as differential pairs over solid ground; no vias if possible.
- **Buttons and test pads:** along an edge or in an area reachable with the lid off.
- **5 V trunk:** from the buck (front-right) along the front to the pogo switch and on to the keyboard switch (left); 3.3 V from the central LDO to A, B and the ESP32.

## 7. Checklist before routing

- [ ] Outline and mounting holes placed and locked.
- [ ] Connectors at their edges, mouths flush with / slightly over the edge (check the footprint's board-edge line).
- [ ] ESD parts within 5 mm of each connector.
- [ ] Each RP2354A's regulator layout copied from RPi's Minimal design; inductor dot orientation checked.
- [ ] Crystals next to XIN/XOUT.
- [ ] ESP32-C3 antenna on the edge, keep-out zone clear on all layers.
- [ ] Buck loop compact; U103 has copper for heat.
- [ ] C201 (220 µF THT) at J201; its lead spacing checked against the delivered parts.
- [ ] Pogo footprint chosen (front right-angle vs top vertical, §4).

## 8. Project files and libraries

`hardware/dock-v2/` is an empty KiCad 10 project:

- `dock-v2.kicad_sch` (top level) with six empty sheets: `power`, `usb_ports`, `mcu_a`, `mcu_b`, `ble`, `pogo`. Annotation is set to *sheet number × 100* (refs in this doc match).
- `dock-v2.kicad_pcb`: empty, **4 copper layers**, v1's design rules. No outline yet (§1 gives the starting 90 × 70 mm), so DRC reports "no edges on Edge.Cuts" until you draw it.
- Net classes Default / Power / USB from v1, with patterns for the v2 net names (`VBUS_IN`, `+5V`, `+3V3`, `KBD_VBUS`, `POGO_5V`, `GND`; `*USB*_D_P` / `*USB*_D_N`). Rename the patterns if you name nets differently.
- Libraries: `dock_v2_custom.kicad_sym` (project symbols, starts with v1's `TPD4E1U06DBV`) and the shared `../libraries/dock.pretty` (has `Pogo-6`).

What exists in KiCad's stock libraries and what needs a custom symbol or footprint:

| Part | Symbol | Footprint |
|---|---|---|
| RP2354A | `MCU_RaspberryPi:RP2354A` ✔ | `Package_DFN_QFN:QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm` ✔ (or RPi's own footprint from the Minimal design) |
| ESP32-C3-MINI-1 | **custom** (not in stock libs) | **custom** (Espressif KiCad library or LCSC/EasyEDA export) |
| CH224A | `Interface_USB:CH224K` is pin-compatible; copy and rename the pins (CFG2/SCL, CFG3/SDA) | `Package_SO:SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm` (check against the ESSOP-10 drawing) |
| TPS54331DR | **custom** (stock has TPS5430/TPS54336, different pinout) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` ✔ |
| SY6280AAC | **custom** (5 pins: OUT, GND, ISET, EN, IN) | `Package_TO_SOT_SMD:SOT-23-5` ✔ |
| TPD4E1U06 | project lib ✔ (from v1) | `Package_TO_SOT_SMD:SOT-23-6` ✔ |
| AMS1117-3.3 | `Regulator_Linear:AMS1117-3.3` ✔ | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` ✔ |
| USB-C (TYPE-C-31-M-12) | `Connector:USB_C_Receptacle_USB2.0_16P` ✔ | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` ✔ |
| ABM8-272-T3 | `Device:Crystal_GND24` ✔ | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` ✔ |
| 2N7002 | `Transistor_FET:2N7002` ✔ | SOT-23 ✔ |
| SMBJ15A, SS54 | `Device:D_TVS`, `Device:D_Schottky` ✔ | `Diode_SMD:D_SMB`, `D_SMC` ✔ |
| 6.8 µH 10 × 10 inductor | `Device:L` ✔ | pick after the part is chosen (SMDRH105R or a Basic alternative) |
| 3.3 µH AOTA-B201610S3R3 | `Device:L` ✔ | 0806 (2016 metric): RPi's footprint from the Minimal design |
| Pogo 6-pin | generic `Connector_Generic:Conn_01x06` ✔ | `dock:Pogo-6` ✔ |
| 220 µF THT | `Device:C_Polarized` ✔ | `Capacitor_THT:CP_Radial_D6.3mm_P5.00mm` (check leads) |
