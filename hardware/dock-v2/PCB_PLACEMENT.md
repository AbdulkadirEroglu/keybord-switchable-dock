# Dock v2 — PCB placement groups

Where the parts of the v2 dock go. **What connects to what: [DOCK_WIRING.md](DOCK_WIRING.md)** (component by component, for wiring) and [DOCK_CONNECTIONS.md](DOCK_CONNECTIONS.md) (the circuit explained, MCU pin maps). What each part does and why it was chosen is in the design docs:
[power input](../../docs/dock-v2-power-input.md), [USB ports](../../docs/dock-v2-usb-ports.md), [pogo](../../docs/dock-v2-pogo.md), [MCU support](../../docs/dock-v2-mcu-support.md), [MCU selection](../../docs/dock-v2-mcu-selection.md).

References below match the placed schematic and DOCK_CONNECTIONS.md, using one hundred-block per schematic sheet (KiCad: *Annotate → Use first free number after sheet number × 100*). Renumber freely.

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
9. [Copying Raspberry Pi's core layout](#9-copying-raspberry-pis-core-layout)

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
| | | L101 | 6.8 µH SLO0630H6R8MTT (C207841) | 7.1 × 6.6 mm, `Inductor_SMD:L_TechFuse_SL0630` | next to the PH pin |
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
| **9** | **Pogo** (front edge, centre) | J601 | 7-pin 2.54 mm magnetic pogo, right-angle with ears (Motorobit) | `dock:Pogo-7` (27.7 × 4.6 mm, scaled from Pogo-6) | **hand-soldered**; centre ≈ (45, 67.7); see §4 |
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
- Net classes (from v1): **Default** 0.2 mm tracks; **Power** 0.6 mm (VBUS_IN, +9V/VIN, +5V, KBD_VBUS, POGO_5V, +3V3, GND); **USB** differential pairs, 90 Ω (use JLCPCB's impedance calculator for the 4-layer stack and set width/gap).
- **Clearance 0.15 mm** in all three classes, **minimum track 0.15 mm**, **minimum drill 0.25 mm**: the values Raspberry Pi's core layout uses around the 0.4 mm-pitch QFN (its vias are 0.6 / 0.25 mm). All well inside JLCPCB's standard 4-layer limits (0.09 mm track/space, 0.15 mm drill). Default route widths stay as in v1.

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

`hardware/dock-v2/` is a KiCad 10 project:

- `dock-v2.kicad_sch` (top level) with six sheets: `power`, `usb_ports`, `mcu_a`, `mcu_b`, `ble`, `pogo` (A3). **All 154 parts are placed, not wired**, in labelled groups, with reference, value, footprint, LCSC number (hidden field `LCSC`) and a short `Note` saying what the part does. Annotation is set to *sheet number × 100* (refs in this doc match).
- `dock-v2.kicad_pcb`: empty, **4 copper layers**, v1's design rules. No outline yet (§1 gives the starting 90 × 70 mm), so DRC reports "no edges on Edge.Cuts" until you draw it.
- Net classes Default / Power / USB from v1, with patterns for the v2 net names (`VBUS_IN`, `+5V`, `+3V3`, `KBD_VBUS`, `POGO_5V`, `GND`; `*USB*_D_P` / `*USB*_D_N`). Rename the patterns if you name nets differently.
- Libraries (project):
  - symbols `dock_v2_custom.kicad_sym`: **RP2354A_RPiFP**, **ESP32-C3-MINI-1**, **CH224A**, **TPS54331DR**, **SY6280AAC**, **TPD4E1U06DBV**;
  - footprints `../libraries/dock_v2.pretty` (library nickname `dock_v2`): **RP2350A_QFN-60_RPi_Vias**, **L_Abracon_AOTA-B201610S3R3_0806**, **C_0402_RPi_Wide**, **ESP32-C3-MINI-1** (with the antenna keep-out zone), 3D model in `../libraries/dock_v2.3dshapes`;
  - `../libraries/dock.pretty` (nickname `dock`, shared with v1): `Pogo-7` (v2), `Pogo-6` (v1).
  - Third-party sources and licences: `../libraries/THIRD_PARTY.md`.

Which symbol and footprint to use for each part (every custom symbol already has its footprint filled in; pins and pads were checked to match one to one):

| Part | Symbol | Footprint |
|---|---|---|
| RP2354A | `dock_v2_custom:RP2354A_RPiFP` (KiCad's RP2350A/RP2354A symbol, same pinout) | `dock_v2:RP2350A_QFN-60_RPi_Vias` (Raspberry Pi's own, thermal vias in the pad) |
| RP2354A core inductor 3.3 µH | `Device:L` | `dock_v2:L_Abracon_AOTA-B201610S3R3_0806` (pad 1 = polarity dot) |
| RP2354A C6/C7 4.7 µF (VREG_VIN, 1.1 V out) | `Device:C` | `dock_v2:C_0402_RPi_Wide` |
| other 4.7 µF / 100 nF / 15 pF / resistors | `Device:C`, `Device:R` | `Capacitor_SMD:C_0402_1005Metric`, `Resistor_SMD:R_0402_1005Metric` |
| ESP32-C3-MINI-1 | `dock_v2_custom:ESP32-C3-MINI-1` (Espressif) | `dock_v2:ESP32-C3-MINI-1` (Espressif) |
| CH224A | `dock_v2_custom:CH224A` (KiCad's CH224K with CH224A pin names; tie pin 8 VBUS to pin 1 VHV) | `Package_SO:SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm` (the one KiCad uses for CH224K) |
| TPS54331DR | `dock_v2_custom:TPS54331DR` | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| SY6280AAC | `dock_v2_custom:SY6280AAC` | `Package_TO_SOT_SMD:SOT-23-5` |
| TPD4E1U06 | `dock_v2_custom:TPD4E1U06DBV` | `Package_TO_SOT_SMD:SOT-23-6` |
| AMS1117-3.3 | `Regulator_Linear:AMS1117-3.3` | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` |
| USB-C (TYPE-C-31-M-12) | `Connector:USB_C_Receptacle_USB2.0_16P` | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` |
| ABM8-272-T3 | `Device:Crystal_GND24` | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` |
| 2N7002 | `Transistor_FET:2N7002` | `Package_TO_SOT_SMD:SOT-23` |
| SMBJ15A, SS54 | `Device:D_TVS`, `Device:D_Schottky` | `Diode_SMD:D_SMB`, `Diode_SMD:D_SMC` |
| 6.8 µH SLO0630H6R8MTT | `Device:L` | `Inductor_SMD:L_TechFuse_SL0630` (same 7.1 × 6.6 mm body and 3.6 mm pad gap as Sunltech's land pattern) |
| Pogo 7-pin | `Connector_Generic:Conn_01x07` | `dock:Pogo-7` |
| 220 µF THT | `Device:C_Polarized` | `dock_v2:CP_Radial_D6.3mm_P5.00mm` (KiCad has only P2.50 for D6.3; check the delivered leads, P2.50 is the stock fallback) |

## 9. Copying Raspberry Pi's core layout

`../reference/rpi-rp2350a-minimal/` is Raspberry Pi's RP2350A Minimal design (MIT licence), unchanged: open it in KiCad to look at the regulator, crystal and decoupling layout.

`../tools/copy_rpi_core_layout.py` copies that layout onto your board, one MCU at a time:

1. Draw the MCU sheet with the core parts (values as in RPi's design: 3.3 µH, 4.7 µF ×3, 33 Ω, 100 nF on 1.1 V ×3 and on 3.3 V, 12 MHz crystal, 15 pF ×2, 1 kΩ on XOUT), then **Update PCB from Schematic** (F8).
2. Place **U301** where you want it (any rotation, top side). Save and **close KiCad**.
3. Run, from the repository root:

   ```sh
   /usr/bin/python3 hardware/tools/copy_rpi_core_layout.py hardware/dock-v2/dock-v2.kicad_pcb U301 --dry-run
   /usr/bin/python3 hardware/tools/copy_rpi_core_layout.py hardware/dock-v2/dock-v2.kicad_pcb U301
   ```

   Repeat for **U401**. It needs KiCad's Python (`/usr/bin/python3`, which has the `pcbnew` module).
4. What it does: maps RPi's nets to yours through the MCU pads; finds your support parts **on the same sheet** by value and nets; places them at RPi's positions, rotated with your MCU; copies the tracks, vias and the 7 small copper pours (1.1 V and 3.3 V rings inside the pad ring, VREG_LX and 1.1 V pads at the inductor, 3.3 V/GND at the regulator, GND under the crystal) with your net names. A backup `dock-v2.before-U301.kicad_pcb` is written first.
5. Afterwards: GND vias drop to the In1 ground plane; connect the 3.3 V ring to your 3.3 V supply and route the GPIOs as usual. Tested on RPi's own board: the copy reproduces all 88 tracks, 30 vias and 7 pours exactly, and after a 90° rotation DRC shows no clearance errors.
