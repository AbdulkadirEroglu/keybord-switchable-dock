# Dock PCB placement groups

Parts that belong together on the dock PCB. Place each group as a cluster, then route between groups. References match `hardware/dock` (69 parts).

| # | Group | Ref | Part code | Package / footprint | Function |
|---|---|---|---|---|---|
| **1** | **Keyboard USB-C port** (board edge) | J1 | KLS L-KLS1-5416-L1-01-R | USB-C 16-pin SMD | Keyboard connector |
| | | U4 | TPD4E1U06DBVR | SOT-23-6 | ESD on D+, D−, CC1, CC2, **≤5 mm from J1** |
| | | R7, R8 | 56 kΩ | 0805 | CC pull-ups (Rp) |
| | | R9, C1 | 330 Ω, 100 nF | 0805 | Shield termination |
| **2** | **Keyboard power switch** (between `SYS_5V` and J1) | U3 | TPS2553DBVR | SOT-23-6 | 1 A current-limited switch |
| | | C6 | 1 µF | 0805 | U3 input |
| | | R5 | 26.1 kΩ | 0805 | ILIM, **short to U3 pin 5** |
| | | R6 | 10 kΩ | 0805 | FAULT pull-up |
| | | R28 | 100 kΩ | 0805 | EN pull-down |
| | | C7 | 1 µF | 0805 | Output, near J1 VBUS |
| | | C15, C16 | Panasonic EEE-FK1E101XP (100 µF 25 V) | 6.3 × 7.7 mm can | Keyboard VBUS bulk, **near J1 VBUS pads** |
| **3** | **Personal PC USB-C port** (board edge) | J4 | KLS L-KLS1-5416-L1-01-R | USB-C 16-pin SMD | Personal PC connector |
| | | U5 | TPD4E1U06DBVR | SOT-23-6 | ESD on D+, D−, CC1, CC2, **≤5 mm from J4** |
| | | R11, R12 | 5.1 kΩ | 0805 | CC pull-downs (Rd) |
| | | R10, C2 | 330 Ω, 100 nF | 0805 | Shield termination |
| **4** | **Work PC USB-C port** (board edge) | J5 | KLS L-KLS1-5416-L1-01-R | USB-C 16-pin SMD | Work PC connector |
| | | U6 | TPD4E1U06DBVR | SOT-23-6 | ESD on D+, D−, CC1, CC2, **≤5 mm from J5** |
| | | R15, R16 | 5.1 kΩ | 0805 | CC pull-downs (Rd) |
| | | R14, C10 | 330 Ω, 100 nF | 0805 | Shield termination |
| **5** | **Power mux** (between J4 and J5 VBUS) | U1 | TPS2116DRLR | SOT-583-8, `dock:SOT-583-8_HandSolder` (extended pads) | Personal/Work priority mux → `SYS_5V` |
| | | C9 | 1 µF | 0805 | VIN1 (Personal), **at U1 pin 3** |
| | | C8 | 1 µF | 0805 | VIN2 (Work), **at U1 pin 6** |
| | | R1, R2 | 300 kΩ, 100 kΩ | 0805 | PR1 divider (≈4.0 V switchover), **at U1 pin 4** |
| | | C3 | 1 µF | 0805 | Output |
| | | C13, C14 | Panasonic EEE-FK1E101XP (100 µF 25 V) | 6.3 × 7.7 mm can | `SYS_5V` bulk, **at U1 output** |
| | | R3 | 10 kΩ | 0805 | ST (`MUX_STATUS`) pull-up |
| **6** | **Host** (centre, USB end → J1) | A1 | Raspberry Pi Pico 2 | Socketed + 4 probes | Keyboard host, router |
| | | J2 | 1×5 pin header 2.54 mm | THT | Host SWD |
| **7** | **HID-A Personal** (USB end → J4) | A2 | Raspberry Pi Pico 2 | Socketed + 4 probes | Personal PC endpoint |
| | | J3 | 1×5 pin header 2.54 mm | THT | SWD |
| | | R13 | 10 kΩ | 0805 | Role strap (GP2 → GND) |
| | | R19, R20 | 22 kΩ, 33 kΩ | 0805 | VBUS sense, **near GP4 (pin 6)** |
| | | R29, R30 | 10 kΩ | 0805 | CC sense, **near GP26/27 (pins 31/32)** |
| | | R33, R36 | 1 kΩ, 10 kΩ | 0805 | RUN control + pull-up |
| **8** | **HID-B Work** (USB end → J5) | A3 | Raspberry Pi Pico 2 | Socketed + 4 probes | Work PC endpoint |
| | | J6 | 1×5 pin header 2.54 mm | THT | SWD |
| | | R17 | 10 kΩ | 0805 | Role strap (GP2 → 3V3) |
| | | R21, R22 | 22 kΩ, 33 kΩ | 0805 | VBUS sense, near GP4 (pin 6) |
| | | R31, R32 | 10 kΩ | 0805 | CC sense, near GP26/27 (pins 31/32) |
| | | R34, R37 | 1 kΩ, 10 kΩ | 0805 | RUN control + pull-up |
| **9** | **BLE** (antenna end → board edge) | U7 | Seeed XIAO nRF52840 | Socketed + 3 probes | BLE link to the pad |
| | | J8 | 1×5 pin header 2.54 mm | THT | XIAO SWD |
| | | R35 | 1 kΩ | 0805 | Reset control from the host |
| | | R18 | 10 kΩ | 0805 | DET pull-up |
| **10** | **Pogo interface** (pad-docking edge) | J7 | 6-pin pogo connector | `dock:Pogo-6` | GND, +5V, DET, RX, TX, GND |
| | | U9 | TPD4E1U06DBVR | SOT-23-6 | ESD, **right at J7** |
| | | R25, R26, R27 | 1 kΩ | 0805 | Series resistors on TX/RX/DET, between U9 and the XIAO |
| | | U8 | TPS2552DBVR | SOT-23-6 | Pogo +5V switch, on when docked |
| | | C11, C12 | 1 µF | 0805 | U8 in/out |
| | | R23 | 26.1 kΩ | 0805 | U8 ILIM |
| | | R24 | 10 kΩ | 0805 | U8 FAULT pull-up |

## Parts not on the schematic (mechanical)

| Item | Qty | Part code | Notes |
|---|---|---|---|
| Female socket, 1×20, 2.54 mm, 8.5 mm tall | 6 | generic | 2 per Pico, on the dock |
| Female socket, 1×7, 2.54 mm | 2 | generic (cut from a longer strip) | XIAO, on the dock |
| Male pin header, 1×20 / 1×7, 2.54 mm | 6 + 2 | generic | Soldered to the Picos and the XIAO |
| Spring probe | 15 required, +7 optional | P50-B1 | Pico: TP2, TP3, D1, D3 (+TP1, D2 GND). XIAO: SWDIO, SWCLK, RST (+GND) |

## Placement rules

- ESD parts (U4, U5, U6, U9) sit right at their connectors. Protection only works when the surge hits the ESD part first.
- Keep the D+/D− pairs short and direct: connector → ESD → the Pico's TP2/TP3 probe holes, with the Pico's USB end pointing at its connector. Route them as differential pairs (USB net class).
- Nothing under the modules except the probes. Probe tails stick out about 2.7 mm below the board at each Pico's two ends and at the XIAO's USB end, so keep bottom-side parts away from those spots.
- XIAO antenna end: at a board edge, with no copper under it. The footprint's keep-out zone enforces this.
- SWD headers J2, J3, J6, J8: along one edge you can reach with the lid off.
- Power nets (`SYS_5V`, `PERSONAL_VBUS`, `WORK_VBUS`, `KEYBOARD_VBUS`, `POGO_5V`, GND) use the Power net class (0.6 mm); keep the U1 → C13/C14 → loads path short and wide.
