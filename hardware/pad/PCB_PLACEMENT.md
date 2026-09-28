# Pad — PCB Placement Guide

Companion to [PAD_CONNECTIONS.md](PAD_CONNECTIONS.md) (what connects to what). This file says **where** things go.
References are the ones in your schematic (commit `ab71ad6` and later).

Drawings (to scale, from the real footprints):

| | |
|---|---|
| [Top side](../../docs/pad-pcb-1-top.png) | keys, encoders, holes, all measurements |
| [Bottom side](../../docs/pad-pcb-2-bottom.png) | LEDs, sockets, Pico, connector and part zones (seen from below) |
| [Side cut](../../docs/pad-pcb-3-side-cut.png) | heights front to back: keys, display, Pico, battery, pogo board, dock |
| [Front cut](../../docs/pad-pcb-4-front-cut.png) | left to right through the Pico: antenna at the left wall, toggle at the right |

## Contents

1. [Coordinate system and how to place parts exactly](#1-coordinate-system-and-how-to-place-parts-exactly)
2. [Board outline and mounting holes](#2-board-outline-and-mounting-holes)
3. [Keys (SW1–SW12) and key LEDs](#3-keys-sw1sw12-and-key-leds)
4. [Encoders (SW13, SW14)](#4-encoders-sw13-sw14)
5. [Encoder ring LEDs](#5-encoder-ring-leds)
6. [LED chain order (for firmware)](#6-led-chain-order-for-firmware)
7. [Pico (A1): under the key field](#7-pico-a1-under-the-key-field)
8. [Groups for everything else](#8-groups-for-everything-else)
9. [Which side and how tall](#9-which-side-and-how-tall)
10. [Net classes and track widths](#10-net-classes-and-track-widths)
11. [Checklist before routing](#11-checklist-before-routing)

## 1. Coordinate system and how to place parts exactly

All coordinates below are in **mm from the board's back-left corner**, seen from the top (the side the keys are on):

```text
 (0,0) ───────── x → ───────── (100,0)      BACK edge (docks here; display and encoders)
   │
   y
   ↓
 (0,92) ──────────────────────── (100,92)    FRONT edge
```

KiCad setup, once:

1. Draw the board outline first (section 2).
2. **Place → Grid Origin** (or press **S**), click the outline's top-left corner. The grid origin is now the board origin.
3. **Preferences → PCB Editor → Display Options → Origin & Axes**: set **Display origin: Grid origin**, **X axis: increases right**, **Y axis: increases down**.
   Every coordinate KiCad shows is now a board coordinate from this file.

Placing one part exactly:

- Select it, press **E** (Properties): type **Position X / Y**, **Orientation**, and **Board side** (Front/Back). The footprint's origin goes to that point.
- **Ctrl+Shift+M** (Move Exactly) moves a selection by an exact offset; **Shift+P** (Position Relative To) places a part relative to another part.
- When a part is where it must be, press **L** to **lock** it so it can't be dragged by accident.

Tip: after pressing F8, you can also close KiCad and ask me to place all parts in sections 2–7 by script (outline, holes, 12 keys, 36 LEDs, 2 encoders, the Pico), locked, with a check render. You then place and route the rest.

## 2. Board outline and mounting holes

- **Outline:** rectangle **100 × 92 mm**, from (0, 0) to (100, 92), layer Edge.Cuts, corner radius 1 mm optional. Fits JLCPCB's 100 × 100 price tier.
- **Mounting holes:** 4 × M3, footprint `MountingHole:MountingHole_3.2mm_M3` (add them in the PCB editor; they need no schematic symbol). Kept clear of the key field, the rings and the Pico.

| Hole | X | Y |
|---|---|---|
| H1 | 4.50 | 36.00 |
| H2 | 95.50 | 36.00 |
| H3 | 4.50 | 87.50 |
| H4 | 95.50 | 87.50 |

## 3. Keys (SW1–SW12) and key LEDs

- 4 × 3 grid, **19.05 mm pitch**, centred left-right on the board. Column X: 21.42, 40.47, 59.52, 78.58. Row Y: 40.50, 59.55, 78.60.
- Footprint `dock:SW_MX_Hotswap_Kailh`, origin = switch centre, **orientation 180°**, front side. At 180° the switch's LED window points to the back (north, towards the display), so the LEDs light the top of the keycap legends, and the hot-swap sockets sit on the front side of each switch.
- Each key LED (SK6812MINI-E, reverse mount) sits **5.08 mm behind the switch centre**, under the switch's LED window. The LED footprint goes on the **back side** (press F to flip): the LED is soldered on the bottom and shines up through its cutout.

| Key | Switch | X | Y | Orientation | LED | LED X | LED Y | LED side |
|---|---|---|---|---|---|---|---|---|
| 1 | SW1 | 21.42 | 40.50 | 180° | D14 | 21.42 | 35.42 | back |
| 2 | SW2 | 40.47 | 40.50 | 180° | D15 | 40.47 | 35.42 | back |
| 3 | SW3 | 59.52 | 40.50 | 180° | D16 | 59.52 | 35.42 | back |
| 4 | SW4 | 78.58 | 40.50 | 180° | D17 | 78.58 | 35.42 | back |
| 5 | SW5 | 21.42 | 59.55 | 180° | D33 | 21.42 | 54.47 | back |
| 6 | SW6 | 40.47 | 59.55 | 180° | D32 | 40.47 | 54.47 | back |
| 7 | SW7 | 59.52 | 59.55 | 180° | D31 | 59.52 | 54.47 | back |
| 8 | SW8 | 78.58 | 59.55 | 180° | D30 | 78.58 | 54.47 | back |
| 9 | SW9 | 21.42 | 78.60 | 180° | D34 | 21.42 | 73.52 | back |
| 10 | SW10 | 40.47 | 78.60 | 180° | D35 | 40.47 | 73.52 | back |
| 11 | SW11 | 59.52 | 78.60 | 180° | D36 | 59.52 | 73.52 | back |
| 12 | SW12 | 78.58 | 78.60 | 180° | D37 | 78.58 | 73.52 | back |

Key numbers: 1–4 back row left→right, 5–8 middle row, 9–12 front row (same as KEY1–KEY12 on the TCA9555).

Verify with a real switch before ordering: the Razer switch's LED lens must be on the side opposite its two metal pins (standard for MX). Print the key area 1:1 and drop a switch on it.

## 4. Encoders (SW13, SW14)

- Footprint `dock:RotaryEncoder_Bourns_PEC11R-4xxxF-S_Vertical` (made for the PEC11R: its mounting lugs are 13.2 mm apart, the Alps EC11E footprint had 11.2 mm). Front side, orientation 0°.
- The footprint origin is **pin A**, the shaft is 7.5 mm right and 2.5 mm down from it. So: **footprint position = shaft − (7.5, 2.5)**.

| Encoder | Role | Shaft X | Shaft Y | Footprint X | Footprint Y | Orientation |
|---|---|---|---|---|---|---|
| SW13 | ENC1 volume (left) | 16.60 | 16.60 | 9.10 | 14.10 | 0° |
| SW14 | ENC2 mic/call (right) | 83.40 | 16.60 | 75.90 | 14.10 | 0° |

The display sits between the encoders (x ≈ 31–69, y ≈ 0–31) in the case, not on the board. The ring light holes end ≈ 2 mm short of it.

## 5. Encoder ring LEDs

- 12 LEDs per encoder on a **12.7 mm radius** around the shaft (light holes just outside a 20 mm knob), one every 30°, **back side**, each turned **radially** (its pads point outward). Laid along the circle instead, neighbouring LEDs would overlap by ≈ 0.6 mm (each footprint is 6.8 mm long, neighbours are 6.2 mm apart); pointing outward they have ≈ 2.5 mm between them, and 12.7 mm keeps the inner pads ≥ 0.2 mm from the encoder's pin A/B pads.
- Positions are given as clock positions (12 = towards the back edge, 3 = right, 6 = towards the keys).
- "Orientation" is the value in KiCad's Properties dialog (footprint on the back side). The pads with VDD/DOUT end up on the outer end, where each LED's 100 nF sits.

**SW13, ENC1 volume (left)**, shaft (16.60, 16.60):

| Clock | LED | X | Y | Orientation |
|---|---|---|---|---|
| 6 | D2 | 16.60 | 29.30 | 270° |
| 7 | D3 | 10.25 | 27.60 | 240° |
| 8 | D4 | 5.60 | 22.95 | 210° |
| 9 | D5 | 3.90 | 16.60 | 180° |
| 10 | D6 | 5.60 | 10.25 | 150° |
| 11 | D7 | 10.25 | 5.60 | 120° |
| 12 | D8 | 16.60 | 3.90 | 90° |
| 1 | D9 | 22.95 | 5.60 | 60° |
| 2 | D10 | 27.60 | 10.25 | 30° |
| 3 | D11 | 29.30 | 16.60 | 0° |
| 4 | D12 | 27.60 | 22.95 | 330° |
| 5 | D13 | 22.95 | 27.60 | 300° |

**SW14, ENC2 mic/call (right)**, shaft (83.40, 16.60):

| Clock | LED | X | Y | Orientation |
|---|---|---|---|---|
| 7 | D18 | 77.05 | 27.60 | 240° |
| 8 | D19 | 72.40 | 22.95 | 210° |
| 9 | D20 | 70.70 | 16.60 | 180° |
| 10 | D21 | 72.40 | 10.25 | 150° |
| 11 | D22 | 77.05 | 5.60 | 120° |
| 12 | D23 | 83.40 | 3.90 | 90° |
| 1 | D24 | 89.75 | 5.60 | 60° |
| 2 | D25 | 94.40 | 10.25 | 30° |
| 3 | D26 | 96.10 | 16.60 | 0° |
| 4 | D27 | 94.40 | 22.95 | 330° |
| 5 | D28 | 89.75 | 27.60 | 300° |
| 6 | D29 | 83.40 | 29.30 | 270° |

## 6. LED chain order (for firmware)

The chain in your schematic runs D2 → D3 → … → D37. Assigning the chain to places in this order keeps every data hop short (≤ ~10 mm except one):

| Chain index (firmware) | LEDs | Where |
|---|---|---|
| 0–11 | D2–D13 | Ring 1 (SW13), clockwise from 6 o'clock |
| 12–15 | D14–D17 | Keys 1, 2, 3, 4 |
| 16–27 | D18–D29 | Ring 2 (SW14), clockwise from 7 o'clock |
| 28–31 | D30–D33 | Keys 8, 7, 6, 5 |
| 32–35 | D34–D37 | Keys 9, 10, 11, 12 |

The level shifter U7 and its 47 Ω resistor go next to ring 1's 6 o'clock LED (D2, at about (16.6, 29.3)); in practice they sit at the left end of the back-strip power zone. The one long hop is ring 2 → key 8 (≈ 30 mm).

## 7. Pico (A1): under the key field

The Pico can't sit under the display strip: its antenna must be at a board edge with no copper around it, and both ends of that strip are taken by the encoder rings. It does fit **under the key field, on the back side**:

- Footprint `dock:RaspberryPi_Pico2W_Socket_NoSWD`, **back side**, KiCad orientation **90**, long axis left-right, **antenna end at the left board edge**.
- Its two pin rows fall exactly into the gaps between key rows: **y = 50.00** (between rows 1 and 2) and **y = 67.78** (between rows 2 and 3), running from x ≈ 1.4 to 49.6.
- The antenna keep-out (no copper on either layer) is the strip x ≈ 0–8.5, y ≈ 51.8–66 at the left edge. The case wall there must be plastic.
- Height: the socketed Pico hangs ≈ 13 mm below the board. In the side cut (board 7.5 mm under the case top, 3 mm floor) that leaves **≈ 9 mm** under the Pico. Solder the hot-swap sockets before fitting the Pico.
- Pin 1 (USB end) ends up at about x = 49.6 under keys 6/7. The Pico's USB and its own 3-pin debug connector face the case floor and are reachable with the bottom cover off.

**SWD:** the footprint's SWD holes D1–D3 would land under key 5's centre post hole, so they are gone: J4 is removed from the schematic and A1 uses `dock:RaspberryPi_Pico2W_Socket_NoSWD` (D1–D3 and TP1–TP6 are tiny copper-only placeholders, no holes). For debugging, use the Pico 2 WH's own 3-pin JST-SH debug connector with the bottom cover off.

Placement: pins 1–20 on y = 67.78 (pin 1 at x = 49.63, pin 20 at x = 1.37), pins 21–40 on y = 50.0, antenna end (pins 20/21) at the left edge. In KiCad: back side, orientation 90, position (49.63, 67.78).

## 8. Groups for everything else

Zones (see the [bottom-side drawing](../../docs/pad-pcb-2-bottom.png)): **back strip** = y 0–31 between the two rings; **key field** = y 31–88; **left / right edge** = the 10 mm strips beside the keys.

Everything below is **placed on the board already** (by script, then checked with DRC). The positions are a starting point for routing: move small parts freely, keep the groups.

**Connectors are side-entry (horizontal) JST types on the bottom side, at the board edges**, openings facing out. Over the battery the gap under the board is only ≈ 7 mm, too little for upright connectors with their plug (≈ 12–13 mm).

| Ref | Footprint | Position (x, y, rot), back side | Opening |
|---|---|---|---|
| J1 pogo cable | `Connector_JST:JST_XH_S4B-XH-A_1x04_P2.50mm_Horizontal` | (36.45, 9.2, 0) | back edge |
| J7 display | `Connector_JST:JST_PH_S9B-PH-K_1x09_P2.00mm_Horizontal` | (49.95, 6.25, 0) | back edge |
| J3 battery | `Connector_JST:JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal` | (9.2, 44.3, 90) | left edge |
| J2 NTC | `Connector_JST:JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal` | (90.8, 42.65, 270) | right edge |
| J5 selector | `Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical` (stays upright, ≈ 16–20 mm free under the key field) | (93.5, 80.8, 90) | down |

The back edge between the rings has ≈ 42 mm of full depth: enough for J1 + J7, not for all four connectors. Hence J3/J2 on the side edges.

| Group | Parts (your refs) | Where | Keep together because |
|---|---|---|---|
| Charger | U2 (TP4056, `dock:SOIC-8-1EP_3.9x4.9mm_HandSolder`), C2, C3, R3, R4, R5, R6, Q1, R7, R8, Q2, R9, R10, R11 | Back strip between the rings | U2 gets warm (≈ 0.65 W): its pad has a 1 mm hole for soldering from the top + 4 vias; GND copper around it |
| Battery protection + sense | U3 (DW01A), Q3 (FS8205A), R12, C4, R13, R14, R15, C5 | Back strip, next to the charger | Battery current J3 → Q3 → GND: short, ≥ 1 mm traces |
| Power path | U4 (TPS2116), R16, R17, C6, C7, C8, R18 | Back strip, centre | PAD_SYS to the Pico's VSYS and the boost |
| RGB boost | U5 (TPS61023), L1, C9, C10, C11, R19, R20, R21 | Key field, row between key rows 1 and 2 (x ≈ 53–85) | Tight loop: C9, L1, U5, C10/C11 within a few mm; FB divider away from L1 |
| Display switch | U8, C54, C55, R30, R31, Q4, R34, C56 | Key field, row between key rows 2 and 3 (x ≈ 53–75) | |
| RGB data | U7, R29, C17 | Back strip, top of the power block | U7 → R29 → D2 DIN |
| LED decoupling | 100 nF per LED (C18–C53) | Bottom side, within ≈ 2 mm of each LED's VDD pin | One per LED |
| Pogo UART series | R32, R33 | Next to Pico pins 1/2 (≈ 51.5, 73) | |
| Expander | U6 (TCA9555), C12, R22, R23, R24 | Right edge, x ≈ 88–98, y ≈ 51–72 | Short KEY traces; near J5 |
| Encoder filters | R25–R28, C13–C16 | One row per encoder at y 35, between the mounting hole and the first key LED | Debounce parts close to the contacts |

## 9. Which side and how tall

- **Top side:** switches and encoders. Inside the key field the plate is ≈ 3.5 mm above the board: only flat SMD parts (≤ 3 mm) between switches. Under the display area the display module sits a few mm above the board: keep the top side there empty.
- **Bottom side:** all LEDs (reverse mount), the hot-swap sockets, the Pico on its sockets, all connectors and most small parts.
- **Height under the board:** ≈ 7 mm over the battery (back strip: SMD parts and side-entry connectors only), ≈ 16–22 mm under the key field (Pico, J5).

## 10. Net classes and track widths

| Class | Nets | Width |
|---|---|---|
| Battery | VBAT, CELL_N, GND path through Q3 | ≥ 1.0 mm |
| Power | POGO_5V, PAD_SYS, 5V_RGB, +3V3 | ≥ 0.6 mm (branches to single LEDs 0.3 mm is fine) |
| Default | everything else | 0.25 mm |

GND: pour on the back side (as on the dock) and stitch it to front-side GND areas; keep the pour out of the Pico antenna keep-out and the LED cutouts.

## 11. Checklist before routing

- [ ] F8 (Update PCB from Schematic): all 150+ footprints load with no "footprint not found".
- [ ] Outline, holes, keys, LEDs, encoders, Pico at the coordinates above, locked.
- [ ] Print the key and encoder area 1:1; check a switch, a hot-swap socket and a PEC11R against it.
- [ ] 3D view: no part on the back side collides with the Pico or the hot-swap sockets.
- [x] SWD removed (section 7).
