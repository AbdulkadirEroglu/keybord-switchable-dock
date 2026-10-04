# Dock v2 — Wiring List (component by component)

Open a sheet, go through its parts in the order below (same order as the dashed group boxes on the sheet), and for each pin draw what the **Draw** column says.
Generated from the same checked connection model as [DOCK_CONNECTIONS.md](DOCK_CONNECTIONS.md) (the sketches and reasons are there). After wiring, `python3 hardware/tools/dock_v2_connections/check_wiring.py` compares the schematic with this list.

How to draw each kind of connection:

- **power symbol** `GND`, `+3V3`, `+5V`: the KiCad power symbols (they connect across all sheets by themselves).
- **global label**: the net continues on another sheet. Use a global label with exactly this name on every sheet where it appears.
- **wire (or local label)**: the net stays on this sheet. Draw a wire to the listed pins, or put the same local label on each pin if the parts are far apart.
- **no-connect flag**: the pin is deliberately unused: put an X on it.
- The same net is listed at every pin that belongs to it, so each connection appears twice (once from each end). Draw it once.
- `A_*` and `B_*` nets are each MCU's own (for example A_1V1 and B_1V1): use local labels, never power symbols, or the two chips' rails would be joined.

## Contents

- [POWER](#sheet-power)
- [USB_PORTS](#sheet-usb_ports)
- [MCU_A](#sheet-mcu_a)
- [MCU_B](#sheet-mcu_b)
- [BLE](#sheet-ble)
- [POGO](#sheet-pogo)

---

## Sheet POWER

File `power.kicad_sch` · 31 parts

- Power symbols: `+3V3`, `+5V`, `GND`
- Global labels on this sheet: `PD_PG`, `PD_SCL`, `PD_SDA`
- PWR_FLAG on: `+5V`, `VBUS_IN`
- No-connect flags: 4

### USB-C power input (right edge)

On the PCB: right edge, y ≈ 48 (J101 mouth on the edge; ESD and TVS within 5 mm)

#### J101 · TYPE-C-31-M-12 · Power input: charger, 9 V PD

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A1 GND | GND |  | power symbol `GND` |
| A4 VBUS | VBUS_IN | D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| A5 CC1 | PD_CC1 | U101.3 (D2+), U102.7 (CC1) | wire (or local label `PD_CC1`) |
| A6 D+ | PD_DP | U101.1 (D1+), U102.4 (DP) | wire (or local label `PD_DP`) |
| A7 D- | PD_DM | U101.6 (D1-), U102.5 (DM) | wire (or local label `PD_DM`) |
| A8 SBU1 | — | nothing | no-connect flag (X) |
| A9 VBUS | VBUS_IN | D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| A12 GND | GND |  | power symbol `GND` |
| B1 GND | GND |  | power symbol `GND` |
| B4 VBUS | VBUS_IN | D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| B5 CC2 | PD_CC2 | U101.4 (D2-), U102.6 (CC2) | wire (or local label `PD_CC2`) |
| B6 D+ | PD_DP | U101.1 (D1+), U102.4 (DP) | wire (or local label `PD_DP`) |
| B7 D- | PD_DM | U101.6 (D1-), U102.5 (DM) | wire (or local label `PD_DM`) |
| B8 SBU2 | — | nothing | no-connect flag (X) |
| B9 VBUS | VBUS_IN | D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| B12 GND | GND |  | power symbol `GND` |
| SH SHIELD | GND |  | power symbol `GND` |

#### U101 · TPD4E1U06DBVR · ESD on CC1, CC2, D+, D-, <=5 mm from J101

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | PD_DP | J101.A6 (D+), J101.B6 (D+), U102.4 (DP) | wire (or local label `PD_DP`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | PD_CC1 | J101.A5 (CC1), U102.7 (CC1) | wire (or local label `PD_CC1`) |
| 4 D2- | PD_CC2 | J101.B5 (CC2), U102.6 (CC2) | wire (or local label `PD_CC2`) |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | PD_DM | J101.A7 (D-), J101.B7 (D-), U102.5 (DM) | wire (or local label `PD_DM`) |

#### D101 · SMBJ15A · VBUS_IN TVS, at J101 VBUS

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 A1 | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| 2 A2 | GND |  | power symbol `GND` |

### PD sink CH224A (9 V, I2C to MCU A)

On the PCB: right edge, next to J101

#### U102 · CH224A · VBUS (8) tied to VHV (1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VHV | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| 2 CFG2/SCL | PD_SCL | R103.2; MCU_A sheet: U301.31 (GPIO19) | **global label `PD_SCL`** |
| 3 CFG3/SDA | PD_SDA | R104.2; MCU_A sheet: U301.29 (GPIO18) | **global label `PD_SDA`** |
| 4 DP | PD_DP | J101.A6 (D+), J101.B6 (D+), U101.1 (D1+) | wire (or local label `PD_DP`) |
| 5 DM | PD_DM | J101.A7 (D-), J101.B7 (D-), U101.6 (D1-) | wire (or local label `PD_DM`) |
| 6 CC2 | PD_CC2 | J101.B5 (CC2), U101.4 (D2-) | wire (or local label `PD_CC2`) |
| 7 CC1 | PD_CC1 | J101.A5 (CC1), U101.3 (D2+) | wire (or local label `PD_CC1`) |
| 8 VBUS | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), C101.1, U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| 9 CFG1 | PD_CFG1 | R101.1 | wire (or local label `PD_CFG1`) |
| 10 PG | PD_PG | R102.2; MCU_A sheet: U301.28 (GPIO17) | **global label `PD_PG`** |
| 11 GND | GND |  | power symbol `GND` |

#### C101 · 1uF · VHV to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), U103.2 (VIN), C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| 2 | GND |  | power symbol `GND` |

#### R101 · 6.8k · CFG1 to GND: requests 9 V

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PD_CFG1 | U102.9 (CFG1) | wire (or local label `PD_CFG1`) |
| 2 | GND |  | power symbol `GND` |

#### R102 · 10k · PG pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | PD_PG | U102.10 (PG); MCU_A sheet: U301.28 (GPIO17) | **global label `PD_PG`** |

#### R103 · 4.7k · SCL pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | PD_SCL | U102.2 (CFG2/SCL); MCU_A sheet: U301.31 (GPIO19) | **global label `PD_SCL`** |

#### R104 · 4.7k · SDA pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | PD_SDA | U102.3 (CFG3/SDA); MCU_A sheet: U301.29 (GPIO18) | **global label `PD_SDA`** |

### 5 V buck TPS54331 (TI Table 7-1, 5 V)

On the PCB: front-right corner (keep the hot loop tiny)

#### U103 · TPS54331DR · EN left open (5 V pass-through)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 BOOT | BUCK_BOOT | C104.1 | wire (or local label `BUCK_BOOT`) |
| 2 VIN | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, C102.1, C103.1 | wire (or local label `VBUS_IN`) |
| 3 EN | — | nothing | no-connect flag (X) |
| 4 SS | BUCK_SS | C105.1 | wire (or local label `BUCK_SS`) |
| 5 VSENSE | BUCK_FB | R106.2, R107.1 | wire (or local label `BUCK_FB`) |
| 6 COMP | BUCK_COMP | R105.1, C107.1 | wire (or local label `BUCK_COMP`) |
| 7 GND | GND |  | power symbol `GND` |
| 8 PH | BUCK_SW | C104.2, D102.1 (K), L101.1 | wire (or local label `BUCK_SW`) |

#### C102 · 10uF · VIN, at pins 2/7

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C103.1 | wire (or local label `VBUS_IN`) |
| 2 | GND |  | power symbol `GND` |

#### C103 · 10uF · VIN

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBUS_IN | J101.A4 (VBUS), J101.A9 (VBUS), J101.B4 (VBUS), J101.B9 (VBUS), D101.1 (A1), U102.1 (VHV), U102.8 (VBUS), C101.1, U103.2 (VIN), C102.1 | wire (or local label `VBUS_IN`) |
| 2 | GND |  | power symbol `GND` |

#### C104 · 100nF · BOOT to PH

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_BOOT | U103.1 (BOOT) | wire (or local label `BUCK_BOOT`) |
| 2 | BUCK_SW | U103.8 (PH), D102.1 (K), L101.1 | wire (or local label `BUCK_SW`) |

#### C105 · 10nF · SS: ~4 ms soft start

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_SS | U103.4 (SS) | wire (or local label `BUCK_SS`) |
| 2 | GND |  | power symbol `GND` |

#### R105 · 51k · COMP series R

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_COMP | U103.6 (COMP), C107.1 | wire (or local label `BUCK_COMP`) |
| 2 | BUCK_COMP_RC | C106.1 | wire (or local label `BUCK_COMP_RC`) |

#### C106 · 4.7nF · COMP series C

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_COMP_RC | R105.2 | wire (or local label `BUCK_COMP_RC`) |
| 2 | GND |  | power symbol `GND` |

#### C107 · 47pF · COMP to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_COMP | U103.6 (COMP), R105.1 | wire (or local label `BUCK_COMP`) |
| 2 | GND |  | power symbol `GND` |

#### R106 · 12k · FB top: 0.8*(1+12/2.2)=5.16 V

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | BUCK_FB | U103.5 (VSENSE), R107.1 | wire (or local label `BUCK_FB`) |

#### R107 · 2.2k · FB bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_FB | U103.5 (VSENSE), R106.2 | wire (or local label `BUCK_FB`) |
| 2 | GND |  | power symbol `GND` |

#### D102 · SS54 · catch diode PH to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 K | BUCK_SW | U103.8 (PH), C104.2, L101.1 | wire (or local label `BUCK_SW`) |
| 2 A | GND |  | power symbol `GND` |

#### L101 · 6.8uH · SLO0630H6R8MTT: Isat 8 A (> 5.8 A max current limit), 45 mOhm, 7.1x6.6x3.0

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BUCK_SW | U103.8 (PH), C104.2, D102.1 (K) | wire (or local label `BUCK_SW`) |
| 2 | +5V |  | power symbol `+5V` |

#### C108 · 22uF 25V · +5V output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | GND |  | power symbol `GND` |

#### C109 · 22uF 25V · +5V output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | GND |  | power symbol `GND` |

#### C110 · 22uF 25V · +5V output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | GND |  | power symbol `GND` |

### 3.3 V LDO

On the PCB: centre of the board, ≈ (45, 38)

#### U104 · AMS1117-3.3 · +5V to +3V3, tab on copper

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 GND | GND |  | power symbol `GND` |
| 2 VO | +3V3 |  | power symbol `+3V3` |
| 3 VI | +5V |  | power symbol `+5V` |

#### C111 · 10uF · LDO input

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | GND |  | power symbol `GND` |

#### C112 · 10uF · LDO output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

### Mounting holes (M3)

On the PCB: (4, 4), (86, 4), (86, 66), (20, 66)

#### H101 · (not in the schematic) · not in the schematic

No pins (mechanical only).

#### H102 · (not in the schematic) · not in the schematic

No pins (mechanical only).

#### H103 · (not in the schematic) · not in the schematic

No pins (mechanical only).

#### H104 · (not in the schematic) · not in the schematic

No pins (mechanical only).

---

## Sheet USB_PORTS

File `usb_ports.kicad_sch` · 33 parts

- Power symbols: `+3V3`, `+5V`, `GND`
- Global labels on this sheet: `KBD_CC1`, `KBD_CC2`, `KBD_USB_D_N`, `KBD_USB_D_P`, `KBD_VBUS_EN`, `KBD_VBUS_SENSE`, `PC1_USB_D_N`, `PC1_USB_D_P`, `PC1_VBUS_DET`, `PC2_USB_D_N`, `PC2_USB_D_P`, `PC2_VBUS_DET`
- PWR_FLAG on: none
- No-connect flags: 9

### Keyboard port J201 (USB-C source, left edge)

On the PCB: left edge, y ≈ 18 (22 Ω resistors near MCU A)

#### J201 · TYPE-C-31-M-12 · Keyboard

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A1 GND | GND |  | power symbol `GND` |
| A4 VBUS | KBD_VBUS | U202.1 (OUT), C201.1, C202.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| A5 CC1 | KBD_CC1 | U201.3 (D2+), R201.2; MCU_A sheet: U301.43 (GPIO29/ADC3) | **global label `KBD_CC1`** |
| A6 D+ | KBD_USBJ_D_P | U201.1 (D1+), R203.1, R205.1 | wire (or local label `KBD_USBJ_D_P`) |
| A7 D- | KBD_USBJ_D_N | U201.6 (D1-), R204.1, R206.1 | wire (or local label `KBD_USBJ_D_N`) |
| A8 SBU1 | — | nothing | no-connect flag (X) |
| A9 VBUS | KBD_VBUS | U202.1 (OUT), C201.1, C202.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| A12 GND | GND |  | power symbol `GND` |
| B1 GND | GND |  | power symbol `GND` |
| B4 VBUS | KBD_VBUS | U202.1 (OUT), C201.1, C202.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| B5 CC2 | KBD_CC2 | U201.4 (D2-), R202.2; MCU_A sheet: U301.42 (GPIO28/ADC2) | **global label `KBD_CC2`** |
| B6 D+ | KBD_USBJ_D_P | U201.1 (D1+), R203.1, R205.1 | wire (or local label `KBD_USBJ_D_P`) |
| B7 D- | KBD_USBJ_D_N | U201.6 (D1-), R204.1, R206.1 | wire (or local label `KBD_USBJ_D_N`) |
| B8 SBU2 | — | nothing | no-connect flag (X) |
| B9 VBUS | KBD_VBUS | U202.1 (OUT), C201.1, C202.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| B12 GND | GND |  | power symbol `GND` |
| SH SHIELD | GND |  | power symbol `GND` |

#### U201 · TPD4E1U06DBVR · ESD D+, D-, CC1, CC2

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | KBD_USBJ_D_P | J201.A6 (D+), J201.B6 (D+), R203.1, R205.1 | wire (or local label `KBD_USBJ_D_P`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | KBD_CC1 | J201.A5 (CC1), R201.2; MCU_A sheet: U301.43 (GPIO29/ADC3) | **global label `KBD_CC1`** |
| 4 D2- | KBD_CC2 | J201.B5 (CC2), R202.2; MCU_A sheet: U301.42 (GPIO28/ADC2) | **global label `KBD_CC2`** |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | KBD_USBJ_D_N | J201.A7 (D-), J201.B7 (D-), R204.1, R206.1 | wire (or local label `KBD_USBJ_D_N`) |

#### R201 · 33k · CC1 Rp to 3V3 (Default USB)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | KBD_CC1 | J201.A5 (CC1), U201.3 (D2+); MCU_A sheet: U301.43 (GPIO29/ADC3) | **global label `KBD_CC1`** |

#### R202 · 33k · CC2 Rp to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | KBD_CC2 | J201.B5 (CC2), U201.4 (D2-); MCU_A sheet: U301.42 (GPIO28/ADC2) | **global label `KBD_CC2`** |

#### R203 · 15k · D+ host pull-down

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_USBJ_D_P | J201.A6 (D+), J201.B6 (D+), U201.1 (D1+), R205.1 | wire (or local label `KBD_USBJ_D_P`) |
| 2 | GND |  | power symbol `GND` |

#### R204 · 15k · D- host pull-down

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_USBJ_D_N | J201.A7 (D-), J201.B7 (D-), U201.6 (D1-), R206.1 | wire (or local label `KBD_USBJ_D_N`) |
| 2 | GND |  | power symbol `GND` |

#### R205 · 22 · D+ series, near MCU A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_USBJ_D_P | J201.A6 (D+), J201.B6 (D+), U201.1 (D1+), R203.1 | wire (or local label `KBD_USBJ_D_P`) |
| 2 | KBD_USB_D_P | MCU_A sheet: U301.5 (GPIO3) | **global label `KBD_USB_D_P`** |

#### R206 · 22 · D- series, near MCU A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_USBJ_D_N | J201.A7 (D-), J201.B7 (D-), U201.6 (D1-), R204.1 | wire (or local label `KBD_USBJ_D_N`) |
| 2 | KBD_USB_D_N | MCU_A sheet: U301.4 (GPIO2) | **global label `KBD_USB_D_N`** |

### Keyboard VBUS switch

On the PCB: between J201 and the +5V trunk; C201 (THT) at J201

#### U202 · SY6280AAC · KBD_VBUS switch, EN from MCU A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 OUT | KBD_VBUS | J201.A4 (VBUS), J201.A9 (VBUS), J201.B4 (VBUS), J201.B9 (VBUS), C201.1, C202.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 ISET | KBD_ISET | R207.1 | wire (or local label `KBD_ISET`) |
| 4 EN | KBD_VBUS_EN | R208.1; MCU_A sheet: U301.12 (GPIO8) | **global label `KBD_VBUS_EN`** |
| 5 IN | +5V |  | power symbol `+5V` |

#### R207 · 6.8k · ISET: 1.0 A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_ISET | U202.3 (ISET) | wire (or local label `KBD_ISET`) |
| 2 | GND |  | power symbol `GND` |

#### R208 · 100k · EN pull-down (off at reset)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_VBUS_EN | U202.4 (EN); MCU_A sheet: U301.12 (GPIO8) | **global label `KBD_VBUS_EN`** |
| 2 | GND |  | power symbol `GND` |

#### C201 · 220uF 16V · HAND-SOLDER: Koshin PKRJ-016V221ME070-T/A5.0 (Ozdisan)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_VBUS | J201.A4 (VBUS), J201.A9 (VBUS), J201.B4 (VBUS), J201.B9 (VBUS), U202.1 (OUT), C202.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| 2 | GND |  | power symbol `GND` |

#### C202 · 10uF · KBD_VBUS at J201

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_VBUS | J201.A4 (VBUS), J201.A9 (VBUS), J201.B4 (VBUS), J201.B9 (VBUS), U202.1 (OUT), C201.1, C203.1, R209.1 | wire (or local label `KBD_VBUS`) |
| 2 | GND |  | power symbol `GND` |

#### C203 · 1uF · KBD_VBUS at J201

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_VBUS | J201.A4 (VBUS), J201.A9 (VBUS), J201.B4 (VBUS), J201.B9 (VBUS), U202.1 (OUT), C201.1, C202.1, R209.1 | wire (or local label `KBD_VBUS`) |
| 2 | GND |  | power symbol `GND` |

#### C204 · 1uF · U202 input

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | GND |  | power symbol `GND` |

#### R209 · 10k · KBD_VBUS divider top -> ADC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_VBUS | J201.A4 (VBUS), J201.A9 (VBUS), J201.B4 (VBUS), J201.B9 (VBUS), U202.1 (OUT), C201.1, C202.1, C203.1 | wire (or local label `KBD_VBUS`) |
| 2 | KBD_VBUS_SENSE | R210.1; MCU_A sheet: U301.41 (GPIO27/ADC1) | **global label `KBD_VBUS_SENSE`** |

#### R210 · 15k · KBD_VBUS divider bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KBD_VBUS_SENSE | R209.2; MCU_A sheet: U301.41 (GPIO27/ADC1) | **global label `KBD_VBUS_SENSE`** |
| 2 | GND |  | power symbol `GND` |

### Personal PC port J202 (back, left)

On the PCB: back edge, left, above MCU A (22 Ω near MCU A)

#### J202 · TYPE-C-31-M-12 · Personal PC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A1 GND | GND |  | power symbol `GND` |
| A4 VBUS | PC1_VBUS | R213.1 | wire (or local label `PC1_VBUS`) |
| A5 CC1 | PC1_CC1 | U203.3 (D2+), R211.1 | wire (or local label `PC1_CC1`) |
| A6 D+ | PC1_USBJ_D_P | U203.1 (D1+), R215.1 | wire (or local label `PC1_USBJ_D_P`) |
| A7 D- | PC1_USBJ_D_N | U203.6 (D1-), R216.1 | wire (or local label `PC1_USBJ_D_N`) |
| A8 SBU1 | — | nothing | no-connect flag (X) |
| A9 VBUS | PC1_VBUS | R213.1 | wire (or local label `PC1_VBUS`) |
| A12 GND | GND |  | power symbol `GND` |
| B1 GND | GND |  | power symbol `GND` |
| B4 VBUS | PC1_VBUS | R213.1 | wire (or local label `PC1_VBUS`) |
| B5 CC2 | PC1_CC2 | U203.4 (D2-), R212.1 | wire (or local label `PC1_CC2`) |
| B6 D+ | PC1_USBJ_D_P | U203.1 (D1+), R215.1 | wire (or local label `PC1_USBJ_D_P`) |
| B7 D- | PC1_USBJ_D_N | U203.6 (D1-), R216.1 | wire (or local label `PC1_USBJ_D_N`) |
| B8 SBU2 | — | nothing | no-connect flag (X) |
| B9 VBUS | PC1_VBUS | R213.1 | wire (or local label `PC1_VBUS`) |
| B12 GND | GND |  | power symbol `GND` |
| SH SHIELD | GND |  | power symbol `GND` |

#### U203 · TPD4E1U06DBVR · ESD D+, D-, CC1, CC2

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | PC1_USBJ_D_P | J202.A6 (D+), J202.B6 (D+), R215.1 | wire (or local label `PC1_USBJ_D_P`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | PC1_CC1 | J202.A5 (CC1), R211.1 | wire (or local label `PC1_CC1`) |
| 4 D2- | PC1_CC2 | J202.B5 (CC2), R212.1 | wire (or local label `PC1_CC2`) |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | PC1_USBJ_D_N | J202.A7 (D-), J202.B7 (D-), R216.1 | wire (or local label `PC1_USBJ_D_N`) |

#### R211 · 5.1k · CC1 Rd

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC1_CC1 | J202.A5 (CC1), U203.3 (D2+) | wire (or local label `PC1_CC1`) |
| 2 | GND |  | power symbol `GND` |

#### R212 · 5.1k · CC2 Rd

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC1_CC2 | J202.B5 (CC2), U203.4 (D2-) | wire (or local label `PC1_CC2`) |
| 2 | GND |  | power symbol `GND` |

#### R213 · 22k · VBUS sense top

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC1_VBUS | J202.A4 (VBUS), J202.A9 (VBUS), J202.B4 (VBUS), J202.B9 (VBUS) | wire (or local label `PC1_VBUS`) |
| 2 | PC1_VBUS_DET | R214.1; MCU_A sheet: U301.3 (GPIO1) | **global label `PC1_VBUS_DET`** |

#### R214 · 33k · VBUS sense bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC1_VBUS_DET | R213.2; MCU_A sheet: U301.3 (GPIO1) | **global label `PC1_VBUS_DET`** |
| 2 | GND |  | power symbol `GND` |

#### R215 · 22 · D+ series, near MCU A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC1_USBJ_D_P | J202.A6 (D+), J202.B6 (D+), U203.1 (D1+) | wire (or local label `PC1_USBJ_D_P`) |
| 2 | PC1_USB_D_P | MCU_A sheet: U301.52 (USB_DP) | **global label `PC1_USB_D_P`** |

#### R216 · 22 · D- series, near MCU A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC1_USBJ_D_N | J202.A7 (D-), J202.B7 (D-), U203.6 (D1-) | wire (or local label `PC1_USBJ_D_N`) |
| 2 | PC1_USB_D_N | MCU_A sheet: U301.51 (USB_DM) | **global label `PC1_USB_D_N`** |

### Work PC port J203 (back, right)

On the PCB: back edge, right, above MCU B (22 Ω near MCU B)

#### J203 · TYPE-C-31-M-12 · Work PC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A1 GND | GND |  | power symbol `GND` |
| A4 VBUS | PC2_VBUS | R219.1 | wire (or local label `PC2_VBUS`) |
| A5 CC1 | PC2_CC1 | U204.3 (D2+), R217.1 | wire (or local label `PC2_CC1`) |
| A6 D+ | PC2_USBJ_D_P | U204.1 (D1+), R221.1 | wire (or local label `PC2_USBJ_D_P`) |
| A7 D- | PC2_USBJ_D_N | U204.6 (D1-), R222.1 | wire (or local label `PC2_USBJ_D_N`) |
| A8 SBU1 | — | nothing | no-connect flag (X) |
| A9 VBUS | PC2_VBUS | R219.1 | wire (or local label `PC2_VBUS`) |
| A12 GND | GND |  | power symbol `GND` |
| B1 GND | GND |  | power symbol `GND` |
| B4 VBUS | PC2_VBUS | R219.1 | wire (or local label `PC2_VBUS`) |
| B5 CC2 | PC2_CC2 | U204.4 (D2-), R218.1 | wire (or local label `PC2_CC2`) |
| B6 D+ | PC2_USBJ_D_P | U204.1 (D1+), R221.1 | wire (or local label `PC2_USBJ_D_P`) |
| B7 D- | PC2_USBJ_D_N | U204.6 (D1-), R222.1 | wire (or local label `PC2_USBJ_D_N`) |
| B8 SBU2 | — | nothing | no-connect flag (X) |
| B9 VBUS | PC2_VBUS | R219.1 | wire (or local label `PC2_VBUS`) |
| B12 GND | GND |  | power symbol `GND` |
| SH SHIELD | GND |  | power symbol `GND` |

#### U204 · TPD4E1U06DBVR · ESD D+, D-, CC1, CC2

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | PC2_USBJ_D_P | J203.A6 (D+), J203.B6 (D+), R221.1 | wire (or local label `PC2_USBJ_D_P`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | PC2_CC1 | J203.A5 (CC1), R217.1 | wire (or local label `PC2_CC1`) |
| 4 D2- | PC2_CC2 | J203.B5 (CC2), R218.1 | wire (or local label `PC2_CC2`) |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | PC2_USBJ_D_N | J203.A7 (D-), J203.B7 (D-), R222.1 | wire (or local label `PC2_USBJ_D_N`) |

#### R217 · 5.1k · CC1 Rd

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC2_CC1 | J203.A5 (CC1), U204.3 (D2+) | wire (or local label `PC2_CC1`) |
| 2 | GND |  | power symbol `GND` |

#### R218 · 5.1k · CC2 Rd

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC2_CC2 | J203.B5 (CC2), U204.4 (D2-) | wire (or local label `PC2_CC2`) |
| 2 | GND |  | power symbol `GND` |

#### R219 · 22k · VBUS sense top

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC2_VBUS | J203.A4 (VBUS), J203.A9 (VBUS), J203.B4 (VBUS), J203.B9 (VBUS) | wire (or local label `PC2_VBUS`) |
| 2 | PC2_VBUS_DET | R220.1; MCU_B sheet: U401.43 (GPIO29/ADC3) | **global label `PC2_VBUS_DET`** |

#### R220 · 33k · VBUS sense bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC2_VBUS_DET | R219.2; MCU_B sheet: U401.43 (GPIO29/ADC3) | **global label `PC2_VBUS_DET`** |
| 2 | GND |  | power symbol `GND` |

#### R221 · 22 · D+ series, near MCU B

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC2_USBJ_D_P | J203.A6 (D+), J203.B6 (D+), U204.1 (D1+) | wire (or local label `PC2_USBJ_D_P`) |
| 2 | PC2_USB_D_P | MCU_B sheet: U401.52 (USB_DP) | **global label `PC2_USB_D_P`** |

#### R222 · 22 · D- series, near MCU B

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PC2_USBJ_D_N | J203.A7 (D-), J203.B7 (D-), U204.6 (D1-) | wire (or local label `PC2_USBJ_D_N`) |
| 2 | PC2_USB_D_N | MCU_B sheet: U401.51 (USB_DM) | **global label `PC2_USB_D_N`** |

---

## Sheet MCU_A

File `mcu_a.kicad_sch` · 27 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `A_SWCLK`, `A_SWDIO`, `BLE_BOOT`, `BLE_EN`, `BLE_RX`, `BLE_TX`, `B_BOOTSEL`, `B_LINK_RX`, `B_LINK_TX`, `B_RUN`, `B_SWCLK`, `B_SWDIO`, `KBD_CC1`, `KBD_CC2`, `KBD_USB_D_N`, `KBD_USB_D_P`, `KBD_VBUS_EN`, `KBD_VBUS_SENSE`, `PC1_USB_D_N`, `PC1_USB_D_P`, `PC1_VBUS_DET`, `PD_PG`, `PD_SCL`, `PD_SDA`, `POGO_5V_SENSE`, `POGO_DET`, `POGO_OFF`, `POGO_RX`, `POGO_TX`
- PWR_FLAG on: `A_1V1`, `A_VREG_AVDD`
- No-connect flags: 9

### RP2354A A

On the PCB: back-left, ≈ (24, 22); regulator/USB side towards J202

#### U301 · RP2354A · A: keyboard host (PIO-USB) + Personal PC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 IOVDD | +3V3 |  | power symbol `+3V3` |
| 2 GPIO0 | A_LED | R305.1 | wire (or local label `A_LED`) |
| 3 GPIO1 | PC1_VBUS_DET | USB_PORTS sheet: R213.2, R214.1 | **global label `PC1_VBUS_DET`** |
| 4 GPIO2 | KBD_USB_D_N | USB_PORTS sheet: R206.2 | **global label `KBD_USB_D_N`** |
| 5 GPIO3 | KBD_USB_D_P | USB_PORTS sheet: R205.2 | **global label `KBD_USB_D_P`** |
| 6 DVDD | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 7 GPIO4 | — | nothing | no-connect flag (X) |
| 8 GPIO5 | — | nothing | no-connect flag (X) |
| 9 GPIO6 | — | nothing | no-connect flag (X) |
| 10 GPIO7 | — | nothing | no-connect flag (X) |
| 11 IOVDD | +3V3 |  | power symbol `+3V3` |
| 12 GPIO8 | KBD_VBUS_EN | USB_PORTS sheet: U202.4 (EN), R208.1 | **global label `KBD_VBUS_EN`** |
| 13 GPIO9 | BLE_EN | BLE sheet: U501.8 (EN/CHIP_PU), R501.2, C501.1 | **global label `BLE_EN`** |
| 14 GPIO10 | BLE_BOOT | BLE sheet: U501.23 (GPIO9), R504.2 | **global label `BLE_BOOT`** |
| 15 GPIO11 | POGO_OFF | POGO sheet: Q602.1 (G), R609.1 | **global label `POGO_OFF`** |
| 16 GPIO12 | BLE_TX | BLE sheet: U501.30 (GPIO20/U0RXD), TP504.1 | **global label `BLE_TX`** |
| 17 GPIO13 | BLE_RX | BLE sheet: U501.31 (GPIO21/U0TXD), TP503.1 | **global label `BLE_RX`** |
| 18 GPIO14 | POGO_DET | POGO sheet: R603.2, Q601.1 (G), R604.2 | **global label `POGO_DET`** |
| 19 GPIO15 | POGO_RX | POGO sheet: R602.2 | **global label `POGO_RX`** |
| 20 IOVDD | +3V3 |  | power symbol `+3V3` |
| 21 XIN | A_XIN | Y301.1, C315.1 | wire (or local label `A_XIN`) |
| 22 XOUT | A_XOUT | R302.1 | wire (or local label `A_XOUT`) |
| 23 DVDD | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 24 SWCLK | A_SWCLK | MCU_B sheet: J401.3 (Pin_3) | **global label `A_SWCLK`** |
| 25 SWDIO | A_SWDIO | MCU_B sheet: J401.2 (Pin_2) | **global label `A_SWDIO`** |
| 26 RUN | A_RUN | SW302.1 | wire (or local label `A_RUN`) |
| 27 GPIO16 | POGO_TX | POGO sheet: R601.1 | **global label `POGO_TX`** |
| 28 GPIO17 | PD_PG | POWER sheet: U102.10 (PG), R102.2 | **global label `PD_PG`** |
| 29 GPIO18 | PD_SDA | POWER sheet: U102.3 (CFG3/SDA), R104.2 | **global label `PD_SDA`** |
| 30 IOVDD | +3V3 |  | power symbol `+3V3` |
| 31 GPIO19 | PD_SCL | POWER sheet: U102.2 (CFG2/SCL), R103.2 | **global label `PD_SCL`** |
| 32 GPIO20 | B_RUN | MCU_B sheet: U401.26 (RUN), R406.2 | **global label `B_RUN`** |
| 33 GPIO21 | B_SWDIO | MCU_B sheet: U401.25 (SWDIO); BLE sheet: J501.2 (Pin_2) | **global label `B_SWDIO`** |
| 34 GPIO22 | B_SWCLK | MCU_B sheet: U401.24 (SWCLK); BLE sheet: J501.3 (Pin_3) | **global label `B_SWCLK`** |
| 35 GPIO23 | B_LINK_RX | MCU_B sheet: U401.9 (GPIO6) | **global label `B_LINK_RX`** |
| 36 GPIO24 | B_LINK_TX | MCU_B sheet: U401.8 (GPIO5) | **global label `B_LINK_TX`** |
| 37 GPIO25 | B_BOOTSEL | MCU_B sheet: R404.1, R407.2 | **global label `B_BOOTSEL`** |
| 38 IOVDD | +3V3 |  | power symbol `+3V3` |
| 39 DVDD | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 40 GPIO26/ADC0 | POGO_5V_SENSE | POGO sheet: R607.2, R608.1 | **global label `POGO_5V_SENSE`** |
| 41 GPIO27/ADC1 | KBD_VBUS_SENSE | USB_PORTS sheet: R209.2, R210.1 | **global label `KBD_VBUS_SENSE`** |
| 42 GPIO28/ADC2 | KBD_CC2 | USB_PORTS sheet: J201.B5 (CC2), U201.4 (D2-), R202.2 | **global label `KBD_CC2`** |
| 43 GPIO29/ADC3 | KBD_CC1 | USB_PORTS sheet: J201.A5 (CC1), U201.3 (D2+), R201.2 | **global label `KBD_CC1`** |
| 44 ADC_AVDD | +3V3 |  | power symbol `+3V3` |
| 45 IOVDD | +3V3 |  | power symbol `+3V3` |
| 46 VREG_AVDD | A_VREG_AVDD | C303.1, R301.2 | wire (or local label `A_VREG_AVDD`) |
| 47 VREG_PGND | GND |  | power symbol `GND` |
| 48 VREG_LX | A_VREG_LX | L301.2 | wire (or local label `A_VREG_LX`) |
| 49 VREG_VIN | +3V3 |  | power symbol `+3V3` |
| 50 VREG_FB | A_1V1 | L301.1, C302.1, C304.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 51 USB_DM | PC1_USB_D_N | USB_PORTS sheet: R216.2 | **global label `PC1_USB_D_N`** |
| 52 USB_DP | PC1_USB_D_P | USB_PORTS sheet: R215.2 | **global label `PC1_USB_D_P`** |
| 53 USB_OTP_VDD | +3V3 |  | power symbol `+3V3` |
| 54 QSPI_IOVDD | +3V3 |  | power symbol `+3V3` |
| 55 QSPI_SD3 | — | nothing | no-connect flag (X) |
| 56 QSPI_SCLK | — | nothing | no-connect flag (X) |
| 57 QSPI_SD0 | — | nothing | no-connect flag (X) |
| 58 QSPI_SD2 | — | nothing | no-connect flag (X) |
| 59 QSPI_SD1 | — | nothing | no-connect flag (X) |
| 60 QSPI_SS | A_QSPI_SS | R303.1 | wire (or local label `A_QSPI_SS`) |
| 61 GND | GND |  | power symbol `GND` |

### Core regulator (copy_rpi_core_layout.py)

On the PCB: around the MCU exactly as Raspberry Pi (placed by copy_rpi_core_layout.py)

#### L301 · 3.3uH · pin 1 (dot) = +1V1, pin 2 = VREG_LX

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_1V1 | U301.6 (DVDD), U301.23 (DVDD), U301.39 (DVDD), U301.50 (VREG_FB), C302.1, C304.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 2 | A_VREG_LX | U301.48 (VREG_LX) | wire (or local label `A_VREG_LX`) |

#### C301 · 4.7uF · VREG_VIN (RPi C6)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C302 · 4.7uF · +1V1 output (RPi C7)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_1V1 | U301.6 (DVDD), U301.23 (DVDD), U301.39 (DVDD), U301.50 (VREG_FB), L301.1, C304.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C303 · 4.7uF · VREG_AVDD (RPi C9)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_VREG_AVDD | U301.46 (VREG_AVDD), R301.2 | wire (or local label `A_VREG_AVDD`) |
| 2 | GND |  | power symbol `GND` |

#### R301 · 33 · 3V3 -> VREG_AVDD (RPi R3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | A_VREG_AVDD | U301.46 (VREG_AVDD), C303.1 | wire (or local label `A_VREG_AVDD`) |

### Decoupling

On the PCB: one capacitor on each power pin (placed by copy_rpi_core_layout.py)

#### C304 · 100nF · DVDD 1 (+1V1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_1V1 | U301.6 (DVDD), U301.23 (DVDD), U301.39 (DVDD), U301.50 (VREG_FB), L301.1, C302.1, C305.1, C306.1 | wire (or local label `A_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C305 · 100nF · DVDD 2 (+1V1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_1V1 | U301.6 (DVDD), U301.23 (DVDD), U301.39 (DVDD), U301.50 (VREG_FB), L301.1, C302.1, C304.1, C306.1 | wire (or local label `A_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C306 · 100nF · DVDD 3 (+1V1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_1V1 | U301.6 (DVDD), U301.23 (DVDD), U301.39 (DVDD), U301.50 (VREG_FB), L301.1, C302.1, C304.1, C305.1 | wire (or local label `A_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C307 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C308 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C309 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C310 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C311 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C312 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C313 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C314 · 10uF · +3V3 bulk

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

### Crystal

On the PCB: next to XIN/XOUT (placed by copy_rpi_core_layout.py)

#### Y301 · 12MHz · ABM8-272-T3 (10 pF, 50 ohm)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_XIN | U301.21 (XIN), C315.1 | wire (or local label `A_XIN`) |
| 2 G | GND |  | power symbol `GND` |
| 3 | A_XOUT_R | C316.1, R302.2 | wire (or local label `A_XOUT_R`) |
| 4 G | GND |  | power symbol `GND` |

#### C315 · 15pF · XIN load

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_XIN | U301.21 (XIN), Y301.1 | wire (or local label `A_XIN`) |
| 2 | GND |  | power symbol `GND` |

#### C316 · 15pF · XOUT load

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_XOUT_R | Y301.3, R302.2 | wire (or local label `A_XOUT_R`) |
| 2 | GND |  | power symbol `GND` |

#### R302 · 1k · XOUT series (RPi R2)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_XOUT | U301.22 (XOUT) | wire (or local label `A_XOUT`) |
| 2 | A_XOUT_R | Y301.3, C316.1 | wire (or local label `A_XOUT_R`) |

### Buttons, SWD pads, LED

On the PCB: near the MCU, buttons reachable from above

#### SW301 · SW_Push · BOOTSEL A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_BOOTSEL_BTN | R303.2 | wire (or local label `A_BOOTSEL_BTN`) |
| 2 | GND |  | power symbol `GND` |

#### R303 · 1k · QSPI_SS -> BOOTSEL button

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_QSPI_SS | U301.60 (QSPI_SS) | wire (or local label `A_QSPI_SS`) |
| 2 | A_BOOTSEL_BTN | SW301.1 | wire (or local label `A_BOOTSEL_BTN`) |

#### SW302 · SW_Push · RESET A (RUN to GND)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_RUN | U301.26 (RUN) | wire (or local label `A_RUN`) |
| 2 | GND |  | power symbol `GND` |

#### D301 · LED red · status LED

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 K | GND |  | power symbol `GND` |
| 2 A | A_LED_R | R305.2 | wire (or local label `A_LED_R`) |

#### R305 · 1k · LED series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | A_LED | U301.2 (GPIO0) | wire (or local label `A_LED`) |
| 2 | A_LED_R | D301.2 (A) | wire (or local label `A_LED_R`) |

#### J401 · Conn_01x03

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | GND |  | power symbol `GND` |
| 2 Pin_2 | A_SWDIO | U301.25 (SWDIO) | **global label `A_SWDIO`** |
| 3 Pin_3 | A_SWCLK | U301.24 (SWCLK) | **global label `A_SWCLK`** |

---

## Sheet MCU_B

File `mcu_b.kicad_sch` · 29 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `B_BOOTSEL`, `B_LINK_RX`, `B_LINK_TX`, `B_RUN`, `B_SWCLK`, `B_SWDIO`, `PC2_USB_D_N`, `PC2_USB_D_P`, `PC2_VBUS_DET`
- PWR_FLAG on: `B_1V1`, `B_VREG_AVDD`
- No-connect flags: 31

### RP2354A B

On the PCB: back-right, ≈ (64, 22); regulator/USB side towards J203

#### U401 · RP2354A · B: Work PC device

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 IOVDD | +3V3 |  | power symbol `+3V3` |
| 2 GPIO0 | — | nothing | no-connect flag (X) |
| 3 GPIO1 | — | nothing | no-connect flag (X) |
| 4 GPIO2 | — | nothing | no-connect flag (X) |
| 5 GPIO3 | B_LED | R405.1 | wire (or local label `B_LED`) |
| 6 DVDD | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 7 GPIO4 | — | nothing | no-connect flag (X) |
| 8 GPIO5 | B_LINK_TX | MCU_A sheet: U301.36 (GPIO24) | **global label `B_LINK_TX`** |
| 9 GPIO6 | B_LINK_RX | MCU_A sheet: U301.35 (GPIO23) | **global label `B_LINK_RX`** |
| 10 GPIO7 | — | nothing | no-connect flag (X) |
| 11 IOVDD | +3V3 |  | power symbol `+3V3` |
| 12 GPIO8 | — | nothing | no-connect flag (X) |
| 13 GPIO9 | — | nothing | no-connect flag (X) |
| 14 GPIO10 | — | nothing | no-connect flag (X) |
| 15 GPIO11 | — | nothing | no-connect flag (X) |
| 16 GPIO12 | — | nothing | no-connect flag (X) |
| 17 GPIO13 | — | nothing | no-connect flag (X) |
| 18 GPIO14 | — | nothing | no-connect flag (X) |
| 19 GPIO15 | — | nothing | no-connect flag (X) |
| 20 IOVDD | +3V3 |  | power symbol `+3V3` |
| 21 XIN | B_XIN | Y401.1, C415.1 | wire (or local label `B_XIN`) |
| 22 XOUT | B_XOUT | R402.1 | wire (or local label `B_XOUT`) |
| 23 DVDD | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 24 SWCLK | B_SWCLK | MCU_A sheet: U301.34 (GPIO22); BLE sheet: J501.3 (Pin_3) | **global label `B_SWCLK`** |
| 25 SWDIO | B_SWDIO | MCU_A sheet: U301.33 (GPIO21); BLE sheet: J501.2 (Pin_2) | **global label `B_SWDIO`** |
| 26 RUN | B_RUN | R406.2; MCU_A sheet: U301.32 (GPIO20) | **global label `B_RUN`** |
| 27 GPIO16 | — | nothing | no-connect flag (X) |
| 28 GPIO17 | — | nothing | no-connect flag (X) |
| 29 GPIO18 | — | nothing | no-connect flag (X) |
| 30 IOVDD | +3V3 |  | power symbol `+3V3` |
| 31 GPIO19 | — | nothing | no-connect flag (X) |
| 32 GPIO20 | — | nothing | no-connect flag (X) |
| 33 GPIO21 | — | nothing | no-connect flag (X) |
| 34 GPIO22 | — | nothing | no-connect flag (X) |
| 35 GPIO23 | — | nothing | no-connect flag (X) |
| 36 GPIO24 | — | nothing | no-connect flag (X) |
| 37 GPIO25 | — | nothing | no-connect flag (X) |
| 38 IOVDD | +3V3 |  | power symbol `+3V3` |
| 39 DVDD | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 40 GPIO26/ADC0 | — | nothing | no-connect flag (X) |
| 41 GPIO27/ADC1 | — | nothing | no-connect flag (X) |
| 42 GPIO28/ADC2 | — | nothing | no-connect flag (X) |
| 43 GPIO29/ADC3 | PC2_VBUS_DET | USB_PORTS sheet: R219.2, R220.1 | **global label `PC2_VBUS_DET`** |
| 44 ADC_AVDD | +3V3 |  | power symbol `+3V3` |
| 45 IOVDD | +3V3 |  | power symbol `+3V3` |
| 46 VREG_AVDD | B_VREG_AVDD | C403.1, R401.2 | wire (or local label `B_VREG_AVDD`) |
| 47 VREG_PGND | GND |  | power symbol `GND` |
| 48 VREG_LX | B_VREG_LX | L401.2 | wire (or local label `B_VREG_LX`) |
| 49 VREG_VIN | +3V3 |  | power symbol `+3V3` |
| 50 VREG_FB | B_1V1 | L401.1, C402.1, C404.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 51 USB_DM | PC2_USB_D_N | USB_PORTS sheet: R222.2 | **global label `PC2_USB_D_N`** |
| 52 USB_DP | PC2_USB_D_P | USB_PORTS sheet: R221.2 | **global label `PC2_USB_D_P`** |
| 53 USB_OTP_VDD | +3V3 |  | power symbol `+3V3` |
| 54 QSPI_IOVDD | +3V3 |  | power symbol `+3V3` |
| 55 QSPI_SD3 | — | nothing | no-connect flag (X) |
| 56 QSPI_SCLK | — | nothing | no-connect flag (X) |
| 57 QSPI_SD0 | — | nothing | no-connect flag (X) |
| 58 QSPI_SD2 | — | nothing | no-connect flag (X) |
| 59 QSPI_SD1 | — | nothing | no-connect flag (X) |
| 60 QSPI_SS | B_QSPI_SS | R403.1, R404.2 | wire (or local label `B_QSPI_SS`) |
| 61 GND | GND |  | power symbol `GND` |

### Core regulator (copy_rpi_core_layout.py)

On the PCB: around the MCU exactly as Raspberry Pi (placed by copy_rpi_core_layout.py)

#### L401 · 3.3uH · pin 1 (dot) = +1V1, pin 2 = VREG_LX

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_1V1 | U401.6 (DVDD), U401.23 (DVDD), U401.39 (DVDD), U401.50 (VREG_FB), C402.1, C404.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 2 | B_VREG_LX | U401.48 (VREG_LX) | wire (or local label `B_VREG_LX`) |

#### C401 · 4.7uF · VREG_VIN (RPi C6)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C402 · 4.7uF · +1V1 output (RPi C7)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_1V1 | U401.6 (DVDD), U401.23 (DVDD), U401.39 (DVDD), U401.50 (VREG_FB), L401.1, C404.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C403 · 4.7uF · VREG_AVDD (RPi C9)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_VREG_AVDD | U401.46 (VREG_AVDD), R401.2 | wire (or local label `B_VREG_AVDD`) |
| 2 | GND |  | power symbol `GND` |

#### R401 · 33 · 3V3 -> VREG_AVDD (RPi R3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | B_VREG_AVDD | U401.46 (VREG_AVDD), C403.1 | wire (or local label `B_VREG_AVDD`) |

### Decoupling

On the PCB: one capacitor on each power pin (placed by copy_rpi_core_layout.py)

#### C404 · 100nF · DVDD 1 (+1V1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_1V1 | U401.6 (DVDD), U401.23 (DVDD), U401.39 (DVDD), U401.50 (VREG_FB), L401.1, C402.1, C405.1, C406.1 | wire (or local label `B_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C405 · 100nF · DVDD 2 (+1V1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_1V1 | U401.6 (DVDD), U401.23 (DVDD), U401.39 (DVDD), U401.50 (VREG_FB), L401.1, C402.1, C404.1, C406.1 | wire (or local label `B_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C406 · 100nF · DVDD 3 (+1V1)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_1V1 | U401.6 (DVDD), U401.23 (DVDD), U401.39 (DVDD), U401.50 (VREG_FB), L401.1, C402.1, C404.1, C405.1 | wire (or local label `B_1V1`) |
| 2 | GND |  | power symbol `GND` |

#### C407 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C408 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C409 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C410 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C411 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C412 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C413 · 100nF · IOVDD / ADC / USB_OTP / QSPI (+3V3)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C414 · 10uF · +3V3 bulk

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

### Crystal

On the PCB: next to XIN/XOUT (placed by copy_rpi_core_layout.py)

#### Y401 · 12MHz · ABM8-272-T3 (10 pF, 50 ohm)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_XIN | U401.21 (XIN), C415.1 | wire (or local label `B_XIN`) |
| 2 G | GND |  | power symbol `GND` |
| 3 | B_XOUT_R | C416.1, R402.2 | wire (or local label `B_XOUT_R`) |
| 4 G | GND |  | power symbol `GND` |

#### C415 · 15pF · XIN load

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_XIN | U401.21 (XIN), Y401.1 | wire (or local label `B_XIN`) |
| 2 | GND |  | power symbol `GND` |

#### C416 · 15pF · XOUT load

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_XOUT_R | Y401.3, R402.2 | wire (or local label `B_XOUT_R`) |
| 2 | GND |  | power symbol `GND` |

#### R402 · 1k · XOUT series (RPi R2)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_XOUT | U401.22 (XOUT) | wire (or local label `B_XOUT`) |
| 2 | B_XOUT_R | Y401.3, C416.1 | wire (or local label `B_XOUT_R`) |

### Buttons, SWD pads, LED

On the PCB: near the MCU, buttons reachable from above

#### SW401 · SW_Push · BOOTSEL B

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_BOOTSEL_BTN | R403.2 | wire (or local label `B_BOOTSEL_BTN`) |
| 2 | GND |  | power symbol `GND` |

#### R403 · 1k · QSPI_SS -> BOOTSEL button

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_QSPI_SS | U401.60 (QSPI_SS), R404.2 | wire (or local label `B_QSPI_SS`) |
| 2 | B_BOOTSEL_BTN | SW401.1 | wire (or local label `B_BOOTSEL_BTN`) |

#### R404 · 1k · QSPI_SS <- B_BOOTSEL from MCU A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_BOOTSEL | R407.2; MCU_A sheet: U301.37 (GPIO25) | **global label `B_BOOTSEL`** |
| 2 | B_QSPI_SS | U401.60 (QSPI_SS), R403.1 | wire (or local label `B_QSPI_SS`) |

#### R406 · 10k · B_RUN pull-up (beats A pull-down at reset)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | B_RUN | U401.26 (RUN); MCU_A sheet: U301.32 (GPIO20) | **global label `B_RUN`** |

#### R407 · 10k · B_BOOTSEL pull-up (beats A pull-down)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | B_BOOTSEL | R404.1; MCU_A sheet: U301.37 (GPIO25) | **global label `B_BOOTSEL`** |

#### D401 · LED red · status LED

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 K | GND |  | power symbol `GND` |
| 2 A | B_LED_R | R405.2 | wire (or local label `B_LED_R`) |

#### R405 · 1k · LED series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | B_LED | U401.5 (GPIO3) | wire (or local label `B_LED`) |
| 2 | B_LED_R | D401.2 (A) | wire (or local label `B_LED_R`) |

#### J501 · Conn_01x03

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | GND |  | power symbol `GND` |
| 2 Pin_2 | B_SWDIO | U401.25 (SWDIO); MCU_A sheet: U301.33 (GPIO21) | **global label `B_SWDIO`** |
| 3 Pin_3 | B_SWCLK | U401.24 (SWCLK); MCU_A sheet: U301.34 (GPIO22) | **global label `B_SWCLK`** |

---

## Sheet BLE

File `ble.kicad_sch` · 11 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `BLE_BOOT`, `BLE_EN`, `BLE_RX`, `BLE_TX`
- PWR_FLAG on: none
- No-connect flags: 24

### ESP32-C3-MINI-1 (antenna at the left edge)

On the PCB: left edge, front half, antenna end on the edge, keep-out clear

#### U501 · ESP32-C3-MINI-1-H4X · BLE; UART0 to MCU A UART1

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 GND | GND |  | power symbol `GND` |
| 2 GND | GND |  | power symbol `GND` |
| 3 3V3 | +3V3 |  | power symbol `+3V3` |
| 4 NC | — | nothing | no-connect flag (X) |
| 5 GPIO2/ADC1_CH2 | BLE_GPIO2 | R503.2 | wire (or local label `BLE_GPIO2`) |
| 6 GPIO3/ADC1_CH3 | — | nothing | no-connect flag (X) |
| 7 NC | — | nothing | no-connect flag (X) |
| 8 EN/CHIP_PU | BLE_EN | R501.2, C501.1; MCU_A sheet: U301.13 (GPIO9) | **global label `BLE_EN`** |
| 9 NC | — | nothing | no-connect flag (X) |
| 10 NC | — | nothing | no-connect flag (X) |
| 11 GND | GND |  | power symbol `GND` |
| 12 GPIO0/ADC1_CH0/XTAL_32K_P | — | nothing | no-connect flag (X) |
| 13 GPIO1/ADC1_CH1/XTAL_32K_N | — | nothing | no-connect flag (X) |
| 14 GND | GND |  | power symbol `GND` |
| 15 NC | — | nothing | no-connect flag (X) |
| 16 GPIO10 | — | nothing | no-connect flag (X) |
| 17 NC | — | nothing | no-connect flag (X) |
| 18 GPIO4/ADC1_CH4 | — | nothing | no-connect flag (X) |
| 19 GPIO5/ADC2_CH0 | — | nothing | no-connect flag (X) |
| 20 GPIO6 | — | nothing | no-connect flag (X) |
| 21 GPIO7 | — | nothing | no-connect flag (X) |
| 22 GPIO8 | BLE_GPIO8 | R502.2 | wire (or local label `BLE_GPIO8`) |
| 23 GPIO9 | BLE_BOOT | R504.2; MCU_A sheet: U301.14 (GPIO10) | **global label `BLE_BOOT`** |
| 24 NC | — | nothing | no-connect flag (X) |
| 25 NC | — | nothing | no-connect flag (X) |
| 26 GPIO18/USB_D- | — | nothing | no-connect flag (X) |
| 27 GPIO19/USB_D+ | — | nothing | no-connect flag (X) |
| 28 NC | — | nothing | no-connect flag (X) |
| 29 NC | — | nothing | no-connect flag (X) |
| 30 GPIO20/U0RXD | BLE_TX | TP504.1; MCU_A sheet: U301.16 (GPIO12) | **global label `BLE_TX`** |
| 31 GPIO21/U0TXD | BLE_RX | TP503.1; MCU_A sheet: U301.17 (GPIO13) | **global label `BLE_RX`** |
| 32 NC | — | nothing | no-connect flag (X) |
| 33 NC | — | nothing | no-connect flag (X) |
| 34 NC | — | nothing | no-connect flag (X) |
| 35 NC | — | nothing | no-connect flag (X) |
| 36 GND | GND |  | power symbol `GND` |
| 37 GND | GND |  | power symbol `GND` |
| 38 GND | GND |  | power symbol `GND` |
| 39 GND | GND |  | power symbol `GND` |
| 40 GND | GND |  | power symbol `GND` |
| 41 GND | GND |  | power symbol `GND` |
| 42 GND | GND |  | power symbol `GND` |
| 43 GND | GND |  | power symbol `GND` |
| 44 GND | GND |  | power symbol `GND` |
| 45 GND | GND |  | power symbol `GND` |
| 46 GND | GND |  | power symbol `GND` |
| 47 GND | GND |  | power symbol `GND` |
| 48 GND | GND |  | power symbol `GND` |
| 49 GND | GND |  | power symbol `GND` |
| 50 GND | GND |  | power symbol `GND` |
| 51 GND | GND |  | power symbol `GND` |
| 52 GND | GND |  | power symbol `GND` |
| 53 GND | GND |  | power symbol `GND` |

#### C502 · 10uF · 3V3 bulk

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C503 · 100nF · 3V3 at pin 3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

### Reset / boot straps

On the PCB: at the module's EN (8), GPIO8/9 (22/23), GPIO2 (5) pins

#### R501 · 10k · EN pull-up (also MCU A, open-drain)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | BLE_EN | U501.8 (EN/CHIP_PU), C501.1; MCU_A sheet: U301.13 (GPIO9) | **global label `BLE_EN`** |

#### C501 · 1uF · EN RC delay

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BLE_EN | U501.8 (EN/CHIP_PU), R501.2; MCU_A sheet: U301.13 (GPIO9) | **global label `BLE_EN`** |
| 2 | GND |  | power symbol `GND` |

#### R502 · 10k · GPIO8 pull-up

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | BLE_GPIO8 | U501.22 (GPIO8) | wire (or local label `BLE_GPIO8`) |

#### R503 · 10k · GPIO2 pull-up

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | BLE_GPIO2 | U501.5 (GPIO2/ADC1_CH2) | wire (or local label `BLE_GPIO2`) |

#### R504 · 10k · GPIO9 (BOOT) pull-up, beats A pull-down

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | BLE_BOOT | U501.23 (GPIO9); MCU_A sheet: U301.14 (GPIO10) | **global label `BLE_BOOT`** |

### Test pads (UART, GND)

On the PCB: near the module, reachable with a probe

#### TP503 · TestPoint · TXD0

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BLE_RX | U501.31 (GPIO21/U0TXD); MCU_A sheet: U301.17 (GPIO13) | **global label `BLE_RX`** |

#### TP504 · TestPoint · RXD0

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BLE_TX | U501.30 (GPIO20/U0RXD); MCU_A sheet: U301.16 (GPIO12) | **global label `BLE_TX`** |

#### TP505 · TestPoint · GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | GND |  | power symbol `GND` |

---

## Sheet POGO

File `pogo.kicad_sch` · 17 parts

- Power symbols: `+3V3`, `+5V`, `GND`
- Global labels on this sheet: `POGO_5V_SENSE`, `POGO_DET`, `POGO_OFF`, `POGO_RX`, `POGO_TX`
- PWR_FLAG on: none
- No-connect flags: 2

### Pogo connector (front edge)

On the PCB: front edge, centre (hand-soldered); ESD right at the pins

#### J601 · Pogo 7-pin · HAND-SOLDER: Motorobit 7-pin 90deg magnetic (order: guide §8)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | GND |  | power symbol `GND` |
| 2 Pin_2 | POGO_5V | U602.1 (OUT), C602.1, C603.1, R607.1 | wire (or local label `POGO_5V`) |
| 3 Pin_3 | POGO_DET_J | U601.4 (D2-), R603.1 | wire (or local label `POGO_DET_J`) |
| 4 Pin_4 | POGO_RX_J | U601.3 (D2+), R602.1 | wire (or local label `POGO_RX_J`) |
| 5 Pin_5 | POGO_TX_J | U601.6 (D1-), R601.2 | wire (or local label `POGO_TX_J`) |
| 6 Pin_6 | POGO_5V | U602.1 (OUT), C602.1, C603.1, R607.1 | wire (or local label `POGO_5V`) |
| 7 Pin_7 | GND |  | power symbol `GND` |

#### U601 · TPD4E1U06DBVR · ESD on DET, TX, RX (1 spare)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | — | nothing | no-connect flag (X) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | POGO_RX_J | J601.4 (Pin_4), R602.1 | wire (or local label `POGO_RX_J`) |
| 4 D2- | POGO_DET_J | J601.3 (Pin_3), R603.1 | wire (or local label `POGO_DET_J`) |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | POGO_TX_J | J601.5 (Pin_5), R601.2 | wire (or local label `POGO_TX_J`) |

#### R601 · 1k · TX series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_TX | MCU_A sheet: U301.27 (GPIO16) | **global label `POGO_TX`** |
| 2 | POGO_TX_J | J601.5 (Pin_5), U601.6 (D1-) | wire (or local label `POGO_TX_J`) |

#### R602 · 1k · RX series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_RX_J | J601.4 (Pin_4), U601.3 (D2+) | wire (or local label `POGO_RX_J`) |
| 2 | POGO_RX | MCU_A sheet: U301.19 (GPIO15) | **global label `POGO_RX`** |

#### R603 · 1k · DET series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_DET_J | J601.3 (Pin_3), U601.4 (D2-) | wire (or local label `POGO_DET_J`) |
| 2 | POGO_DET | Q601.1 (G), R604.2; MCU_A sheet: U301.18 (GPIO14) | **global label `POGO_DET`** |

### Pogo 5 V switch (hardware DET enable)

On the PCB: behind J601

#### U602 · SY6280AAC · POGO_5V switch

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 OUT | POGO_5V | J601.2 (Pin_2), J601.6 (Pin_6), C602.1, C603.1, R607.1 | wire (or local label `POGO_5V`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 ISET | POGO_ISET | R606.1 | wire (or local label `POGO_ISET`) |
| 4 EN | POGO_EN | Q601.3 (D), Q602.3 (D), R605.2 | wire (or local label `POGO_EN`) |
| 5 IN | +5V |  | power symbol `+5V` |

#### Q601 · 2N7002 · DET inverter -> U602 EN

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 G | POGO_DET | R603.2, R604.2; MCU_A sheet: U301.18 (GPIO14) | **global label `POGO_DET`** |
| 2 S | GND |  | power symbol `GND` |
| 3 D | POGO_EN | U602.4 (EN), Q602.3 (D), R605.2 | wire (or local label `POGO_EN`) |

#### R604 · 10k · DET pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | POGO_DET | R603.2, Q601.1 (G); MCU_A sheet: U301.18 (GPIO14) | **global label `POGO_DET`** |

#### R605 · 100k · EN pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | POGO_EN | U602.4 (EN), Q601.3 (D), Q602.3 (D) | wire (or local label `POGO_EN`) |

#### Q602 · 2N7002 · POGO_OFF veto: pulls EN low

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 G | POGO_OFF | R609.1; MCU_A sheet: U301.15 (GPIO11) | **global label `POGO_OFF`** |
| 2 S | GND |  | power symbol `GND` |
| 3 D | POGO_EN | U602.4 (EN), Q601.3 (D), R605.2 | wire (or local label `POGO_EN`) |

#### R609 · 100k · Q602 gate pull-down (no veto at reset)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_OFF | Q602.1 (G); MCU_A sheet: U301.15 (GPIO11) | **global label `POGO_OFF`** |
| 2 | GND |  | power symbol `GND` |

#### R606 · 4.7k · ISET: 6800/4700 = 1.45 A (1.09-1.81 A); 2 x 1 A +5V contacts

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_ISET | U602.3 (ISET) | wire (or local label `POGO_ISET`) |
| 2 | GND |  | power symbol `GND` |

#### C601 · 1uF · POGO_5V output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +5V |  | power symbol `+5V` |
| 2 | GND |  | power symbol `GND` |

#### C602 · 10uF · POGO_5V output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_5V | J601.2 (Pin_2), J601.6 (Pin_6), U602.1 (OUT), C603.1, R607.1 | wire (or local label `POGO_5V`) |
| 2 | GND |  | power symbol `GND` |

#### C603 · 1uF · U602 input

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_5V | J601.2 (Pin_2), J601.6 (Pin_6), U602.1 (OUT), C602.1, R607.1 | wire (or local label `POGO_5V`) |
| 2 | GND |  | power symbol `GND` |

#### R607 · 10k · POGO_5V divider top -> ADC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_5V | J601.2 (Pin_2), J601.6 (Pin_6), U602.1 (OUT), C602.1, C603.1 | wire (or local label `POGO_5V`) |
| 2 | POGO_5V_SENSE | R608.1; MCU_A sheet: U301.40 (GPIO26/ADC0) | **global label `POGO_5V_SENSE`** |

#### R608 · 15k · POGO_5V divider bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_5V_SENSE | R607.2; MCU_A sheet: U301.40 (GPIO26/ADC0) | **global label `POGO_5V_SENSE`** |
| 2 | GND |  | power symbol `GND` |
