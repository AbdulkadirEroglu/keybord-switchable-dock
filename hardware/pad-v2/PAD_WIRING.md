# Pad v2 — Wiring List (component by component)

Open a sheet, go through its parts in the order below (same order as the dashed group boxes), and for each pin draw what the **Draw** column says. After wiring, `python3 hardware/tools/pad_v2_connections/check_wiring.py` compares the schematic with this list (it checks which pins are joined; net names may differ).

How to draw each kind of connection:

- **power symbol** `GND`, `+3V3`: KiCad power symbols (they connect across all sheets).
- **global label**: the net continues on another sheet. Same name on every sheet where it appears.
- **wire (or local label)**: the net stays on this sheet.
- **no-connect flag**: the pin is deliberately unused: put an X on it.
- Each connection appears at both of its ends. Draw it once.
- Resistors, capacitors, inductors and push switches may be drawn either way round. The four ESD channels of a TPD4E1U06 (pins 1, 3, 4, 6) are interchangeable.

## 1. Power chain

```text
 pogo +5V (J101 2, 6) ─ D101 TVS ─ U102 WS3222D (cuts off at 5.69 V) ─ VIN_PROT ─ U103 ETA6003 ─┬─ VSYS ─┬─ U105 LDO ─ +3V3 ─ ESP32, display, pull-ups
                                                                                │        └─ U401 boost ─ 5V_RGB ─ 36 LEDs, U402
                                                                                └─ VBAT ─ J102 battery + ;  battery − = BAT_N ─ Q101 ─ GND
```

- `BAT_N` (battery minus) is **not** GND: it reaches GND only through Q101 (the protection FETs). Only J102 pin 2, U104 GND, C107 and Q101 S1 are on BAT_N.
- Put a PWR_FLAG on: `POGO_5V`, `VIN_PROT`, `VSYS`, `VBAT`, `BAT_N`, `+3V3`, `GND`, `5V_RGB`, `DISP_VCC` (ERC needs one on every supply net that no power-output pin drives).

## 2. ESP32-S3 pin map

Chosen for the placement in PCB_PLACEMENT.md (module at the front-left, rotation 90°): each signal leaves the module on the side facing its destination. All 39 GPIOs are used.

| GPIO | Module pin | Net | Leaves the module at | Goes to |
|---|---|---|---|---|
| IO0 | 4 | BOOT | front edge row (via under the module) | SW202 (BOOT button); strapping pin, internal pull-up |
| IO1 | 5 | KEY2 | front edge row (via under the module) | SW302 (key 2) |
| IO2 | 6 | KEY6 | front edge row (via under the module) | SW306 (key 6) |
| IO3 | 7 | KEY10 | front edge row (via under the module) | SW310 (key 10) |
| IO4 | 8 | KEY3 | front edge row (via under the module) | SW303 (key 3) |
| IO5 | 9 | KEY7 | front edge row (via under the module) | SW307 (key 7) |
| IO6 | 10 | KEY11 | front edge row (via under the module) | SW311 (key 11) |
| IO7 | 11 | KEY4 | front edge row (via under the module) | SW304 (key 4) |
| IO8 | 12 | KEY8 | front edge row (via under the module) | SW308 (key 8) |
| IO9 | 13 | KEY12 | front edge row (via under the module) | SW312 (key 12) |
| IO10 | 14 | VBAT_SENSE | front edge row (via under the module) | R117/R118 divider (ADC1_CH9) |
| IO11 | 15 | VIN_SENSE | front edge row (via under the module) | R106/R107 divider: dock 5 V present (ADC2_CH0 or digital) |
| IO12 | 16 | TGL_WORK | right row, south of USB (pocket: via, bottom layer) | J301 pin 3 |
| IO13 | 17 | TGL_PERSONAL | right row, south of USB (pocket: via, bottom layer) | J301 pin 1 |
| IO14 | 18 | CHG_STAT | right row, south of USB (pocket: via, bottom layer) | ETA6003 STAT (open drain, R114 pull-up) |
| IO15 | 19 | CHG_EN_N | right row, south of USB (pocket: via, bottom layer) | ETA6003 ENB: low = charge (R113 pull-down) |
| IO16 | 20 | ENC2_SW | right row, south of USB (pocket: via, bottom layer) | SW314 push switch |
| IO17 | 21 | ENC2_B | right row, south of USB (pocket: via, bottom layer) | SW314 B through R308/C304 |
| IO18 | 22 | ENC2_A | right row, south of USB (pocket: via, bottom layer) | SW314 A through R307/C303 |
| IO19 | 23 | USB_DN | right row | J201 D- (fixed pin) |
| IO20 | 24 | USB_DP | right row | J201 D+ (fixed pin) |
| IO21 | 25 | CHG_ISEL | right row, north of USB | ETA6003 USB_DET: low = 1.0 A, high = 0.45 A |
| IO26 | 26 | RGB_EN | right row, north of USB | TPS61023 EN (R403 pull-down) |
| IO47 | 27 | DISP_EN_N | right row, north | Q501 gate: low = display on (R501 pull-up) |
| IO33 | 28 | DISP_SCL | right row, north | J501 pin 6 |
| IO34 | 29 | DISP_SDA | right row, north | J501 pin 5 |
| IO48 | 30 | DISP_RES | right row, north | J501 pin 4 |
| IO35 | 31 | DISP_DC | back row, east end | J501 pin 3 |
| IO36 | 32 | DISP_CS | back row, east end | J501 pin 2 |
| IO37 | 33 | DISP_BLK | back row, east end | J501 pin 1 (backlight PWM) |
| IO38 | 34 | KEY9 | back row | SW309 (key 9) |
| IO39 | 35 | KEY5 | back row | SW305 (key 5) |
| IO40 | 36 | KEY1 | back row | SW301 (key 1) |
| IO41 | 37 | ENC1_B | back row | SW313 B through R304/C302 |
| IO42 | 38 | ENC1_A | back row | SW313 A through R303/C301 |
| TXD0 (IO43) | 39 | PAD_TX | back row (via, bottom layer) | R102 -> pogo pin 4 (UART0 TX, also the ROM bootloader) |
| RXD0 (IO44) | 40 | PAD_RX | back row (via, bottom layer) | R101 <- pogo pin 3 (UART0 RX) |
| IO45 | 41 | ENC1_SW | back row, west | SW313 push switch (strapping pin IO45: no external pull-up) |
| IO46 | 44 | RGB_DATA | back row, west | U402 input (strapping pin IO46: low at reset) |

Notes:

- **Strapping pins:** IO0 = BOOT button. IO45 must not be pulled high at reset (it carries only the encoder switch to GND). IO46 is low at reset (RGB data idles low). IO3 is a key to GND (harmless).
- The display, encoder and key pins can be swapped among themselves in firmware (GPIO matrix); USB (IO19/20), UART0 (TXD0/RXD0) and the ADC pin IO10 are fixed.
- Firmware: enable the internal pull-ups on the key, encoder-switch, toggle and BOOT pins.

## 3. LED chain (firmware index = reference − 401)

| Index | LED | Where |
|---|---|---|
| 0 | D401 | key 9 (SK6812MINI-E, bottom) |
| 1 | D402 | key 10 (SK6812MINI-E, bottom) |
| 2 | D403 | key 11 (SK6812MINI-E, bottom) |
| 3 | D404 | key 12 (SK6812MINI-E, bottom) |
| 4 | D405 | key 8 (SK6812MINI-E, bottom) |
| 5 | D406 | key 7 (SK6812MINI-E, bottom) |
| 6 | D407 | key 6 (SK6812MINI-E, bottom) |
| 7 | D408 | key 5 (SK6812MINI-E, bottom) |
| 8 | D409 | key 1 (SK6812MINI-E, bottom) |
| 9 | D410 | key 2 (SK6812MINI-E, bottom) |
| 10 | D411 | key 3 (SK6812MINI-E, bottom) |
| 11 | D412 | key 4 (SK6812MINI-E, bottom) |
| 12 | D413 | ring 2, 7 o'clock (XL-2020, top) |
| 13 | D414 | ring 2, 6 o'clock (XL-2020, top) |
| 14 | D415 | ring 2, 5 o'clock (XL-2020, top) |
| 15 | D416 | ring 2, 4 o'clock (XL-2020, top) |
| 16 | D417 | ring 2, 3 o'clock (XL-2020, top) |
| 17 | D418 | ring 2, 2 o'clock (XL-2020, top) |
| 18 | D419 | ring 2, 1 o'clock (XL-2020, top) |
| 19 | D420 | ring 2, 12 o'clock (XL-2020, top) |
| 20 | D421 | ring 2, 11 o'clock (XL-2020, top) |
| 21 | D422 | ring 2, 10 o'clock (XL-2020, top) |
| 22 | D423 | ring 2, 9 o'clock (XL-2020, top) |
| 23 | D424 | ring 2, 8 o'clock (XL-2020, top) |
| 24 | D425 | ring 1, 4 o'clock (XL-2020, top) |
| 25 | D426 | ring 1, 3 o'clock (XL-2020, top) |
| 26 | D427 | ring 1, 2 o'clock (XL-2020, top) |
| 27 | D428 | ring 1, 1 o'clock (XL-2020, top) |
| 28 | D429 | ring 1, 12 o'clock (XL-2020, top) |
| 29 | D430 | ring 1, 11 o'clock (XL-2020, top) |
| 30 | D431 | ring 1, 10 o'clock (XL-2020, top) |
| 31 | D432 | ring 1, 9 o'clock (XL-2020, top) |
| 32 | D433 | ring 1, 8 o'clock (XL-2020, top) |
| 33 | D434 | ring 1, 7 o'clock (XL-2020, top) |
| 34 | D435 | ring 1, 6 o'clock (XL-2020, top) |
| 35 | D436 | ring 1, 5 o'clock (XL-2020, top) |

## Sheets

---

## Sheet POWER

File `power.kicad_sch` · 44 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `CHG_EN_N`, `CHG_ISEL`, `CHG_STAT`, `PAD_RX`, `PAD_TX`, `VBAT_SENSE`, `VIN_SENSE`, `VSYS`
- PWR_FLAG on: `+3V3`, `BAT_N`, `GND`, `POGO_5V`, `VBAT`, `VIN_PROT`, `VSYS`
- No-connect flags: 5

### Pogo input (front strip)


#### J101 · Pogo cable (to floor board) · HAND-SOLDER, bottom. 1 GND, 2 +5V, 3 PAD_RX (dock TX), 4 PAD_TX (dock RX), 5 DET -> GND, 6 +5V, 7 GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | GND |  | power symbol `GND` |
| 2 Pin_2 | POGO_5V | D101.1 (A1), U102.6 (IN), U102.7 (IN), U102.8 (IN), C101.1, R103.1 | wire (or local label `POGO_5V`) |
| 3 Pin_3 | PAD_RX_J | U101.1 (D1+), R101.1 | wire (or local label `PAD_RX_J`) |
| 4 Pin_4 | PAD_TX_J | U101.3 (D2+), R102.1 | wire (or local label `PAD_TX_J`) |
| 5 Pin_5 | GND |  | power symbol `GND` |
| 6 Pin_6 | POGO_5V | D101.1 (A1), U102.6 (IN), U102.7 (IN), U102.8 (IN), C101.1, R103.1 | wire (or local label `POGO_5V`) |
| 7 Pin_7 | GND |  | power symbol `GND` |

#### D101 · SMBJ15A · TVS on the pogo +5V (before the OVP switch): pin 1 (cathode band) to +5V, pin 2 to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 A1 | POGO_5V | J101.2 (Pin_2), J101.6 (Pin_6), U102.6 (IN), U102.7 (IN), U102.8 (IN), C101.1, R103.1 | wire (or local label `POGO_5V`) |
| 2 A2 | GND |  | power symbol `GND` |

#### U101 · TPD4E1U06DBVR · ESD on PAD_RX and PAD_TX at J101

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | PAD_RX_J | J101.3 (Pin_3), R101.1 | wire (or local label `PAD_RX_J`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | PAD_TX_J | J101.4 (Pin_4), R102.1 | wire (or local label `PAD_TX_J`) |
| 4 D2- | — | nothing | no-connect flag (X) |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | — | nothing | no-connect flag (X) |

#### R101 · 1k · PAD_RX series (J101 pin 3 to ESP RXD0)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PAD_RX_J | J101.3 (Pin_3), U101.1 (D1+) | wire (or local label `PAD_RX_J`) |
| 2 | PAD_RX | MCU sheet: U201.40 (RXD0) | **global label `PAD_RX`** |

#### R102 · 1k · PAD_TX series (ESP TXD0 to J101 pin 4)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | PAD_TX_J | J101.4 (Pin_4), U101.3 (D2+) | wire (or local label `PAD_TX_J`) |
| 2 | PAD_TX | MCU sheet: U201.39 (TXD0) | **global label `PAD_TX`** |

### Overvoltage switch WS3222D (5.69 V)


#### U102 · WS3222D · pogo +5V -> VIN_PROT (charger input); EP to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 OUT | VIN_PROT | U103.2 (IN), R106.1, C102.1, C103.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 2 OUT | VIN_PROT | U103.2 (IN), R106.1, C102.1, C103.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 3 OUT | VIN_PROT | U103.2 (IN), R106.1, C102.1, C103.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 4 GND | GND |  | power symbol `GND` |
| 5 OVLO | OVLO | R104.2, R105.1 | wire (or local label `OVLO`) |
| 6 IN | POGO_5V | J101.2 (Pin_2), J101.6 (Pin_6), D101.1 (A1), C101.1, R103.1 | wire (or local label `POGO_5V`) |
| 7 IN | POGO_5V | J101.2 (Pin_2), J101.6 (Pin_6), D101.1 (A1), C101.1, R103.1 | wire (or local label `POGO_5V`) |
| 8 IN | POGO_5V | J101.2 (Pin_2), J101.6 (Pin_6), D101.1 (A1), C101.1, R103.1 | wire (or local label `POGO_5V`) |
| 9 EP | GND |  | power symbol `GND` |

#### C101 · 1uF 50V · U102 IN

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_5V | J101.2 (Pin_2), J101.6 (Pin_6), D101.1 (A1), U102.6 (IN), U102.7 (IN), U102.8 (IN), R103.1 | wire (or local label `POGO_5V`) |
| 2 | GND |  | power symbol `GND` |

#### R103 · 51k · OVLO top, part 1 (IN to R104)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | POGO_5V | J101.2 (Pin_2), J101.6 (Pin_6), D101.1 (A1), U102.6 (IN), U102.7 (IN), U102.8 (IN), C101.1 | wire (or local label `POGO_5V`) |
| 2 | OVLO_TOP | R104.1 | wire (or local label `OVLO_TOP`) |

#### R104 · 5.1k · OVLO top, part 2 (R103 to OVLO): 56.1k total

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | OVLO_TOP | R103.2 | wire (or local label `OVLO_TOP`) |
| 2 | OVLO | U102.5 (OVLO), R105.1 | wire (or local label `OVLO`) |

#### R105 · 15k · OVLO bottom: 1.2 x (1 + 56.1/15) = 5.69 V

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | OVLO | U102.5 (OVLO), R104.2 | wire (or local label `OVLO`) |
| 2 | GND |  | power symbol `GND` |

#### R106 · 10k · dock-5V sense top (VIN_PROT -> VIN_SENSE, IO11)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VIN_PROT | U102.1 (OUT), U102.2 (OUT), U102.3 (OUT), U103.2 (IN), C102.1, C103.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 2 | VIN_SENSE | R107.1; MCU sheet: U201.15 (IO11) | **global label `VIN_SENSE`** |

#### R107 · 15k · dock-5V sense bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VIN_SENSE | R106.2; MCU sheet: U201.15 (IO11) | **global label `VIN_SENSE`** |
| 2 | GND |  | power symbol `GND` |

### Charger ETA6003 (1 A / 0.45 A, power path)


#### U103 · ETA6003 · ENPPB to GND; ENB = CHG_EN_N (IO15); USB_DET = CHG_ISEL (IO21); STAT = CHG_STAT (IO14); EP to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 SYS | VSYS | L101.2, C104.1, C105.1, U105.1 (IN), U105.3 (EN), C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 2 IN | VIN_PROT | U102.1 (OUT), U102.2 (OUT), U102.3 (OUT), R106.1, C102.1, C103.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 3 SW | CHG_SW | L101.1 | wire (or local label `CHG_SW`) |
| 4 SW | CHG_SW | L101.1 | wire (or local label `CHG_SW`) |
| 5 PGND | GND |  | power symbol `GND` |
| 6 ENB | CHG_EN_N | R113.1; MCU sheet: U201.19 (IO15) | **global label `CHG_EN_N`** |
| 7 NTC | CHG_NTC | J103.1 (Pin_1), R110.2, R111.2, R112.1 | wire (or local label `CHG_NTC`) |
| 8 ENPPB | GND |  | power symbol `GND` |
| 9 STAT | CHG_STAT | R114.1; MCU sheet: U201.18 (IO14) | **global label `CHG_STAT`** |
| 10 GND | GND |  | power symbol `GND` |
| 11 ISET1 | CHG_ISET1 | R108.1 | wire (or local label `CHG_ISET1`) |
| 12 ISET2 | CHG_ISET2 | R109.1 | wire (or local label `CHG_ISET2`) |
| 13 USB_DET | CHG_ISEL | MCU sheet: U201.25 (IO21) | **global label `CHG_ISEL`** |
| 14 BATT | VBAT | J102.1 (Pin_1), C106.1, R115.1, R117.1 | wire (or local label `VBAT`) |
| 15 SYS | VSYS | L101.2, C104.1, C105.1, U105.1 (IN), U105.3 (EN), C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 16 BATT | VBAT | J102.1 (Pin_1), C106.1, R115.1, R117.1 | wire (or local label `VBAT`) |
| 17 EP | GND |  | power symbol `GND` |

#### C102 · 10uF · IN (pin 2) to PGND (pin 5), closest to the IC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VIN_PROT | U102.1 (OUT), U102.2 (OUT), U102.3 (OUT), U103.2 (IN), R106.1, C103.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 2 | GND |  | power symbol `GND` |

#### C103 · 10uF · IN to GND (pin 10)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VIN_PROT | U102.1 (OUT), U102.2 (OUT), U102.3 (OUT), U103.2 (IN), R106.1, C102.1, R110.1, R111.1 | wire (or local label `VIN_PROT`) |
| 2 | GND |  | power symbol `GND` |

#### L101 · 2.2uH · SW to SYS. Isat >= 3.5 A, 4x4 mm (LCSC number at BOM time)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | CHG_SW | U103.3 (SW), U103.4 (SW) | wire (or local label `CHG_SW`) |
| 2 | VSYS | U103.1 (SYS), U103.15 (SYS), C104.1, C105.1, U105.1 (IN), U105.3 (EN), C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |

#### C104 · 22uF · SYS output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VSYS | U103.1 (SYS), U103.15 (SYS), L101.2, C105.1, U105.1 (IN), U105.3 (EN), C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 2 | GND |  | power symbol `GND` |

#### C105 · 22uF · SYS output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VSYS | U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, U105.1 (IN), U105.3 (EN), C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 2 | GND |  | power symbol `GND` |

#### C106 · 10uF · BATT

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBAT | U103.14 (BATT), U103.16 (BATT), J102.1 (Pin_1), R115.1, R117.1 | wire (or local label `VBAT`) |
| 2 | GND |  | power symbol `GND` |

#### R108 · 1k · ISET1: 1.0 A (USB_DET low)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | CHG_ISET1 | U103.11 (ISET1) | wire (or local label `CHG_ISET1`) |
| 2 | GND |  | power symbol `GND` |

#### R109 · 2.2k · ISET2: 0.45 A (USB_DET high)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | CHG_ISET2 | U103.12 (ISET2) | wire (or local label `CHG_ISET2`) |
| 2 | GND |  | power symbol `GND` |

#### R110 · 10k · NTC top a (IN to NTC), parallel with R111

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VIN_PROT | U102.1 (OUT), U102.2 (OUT), U102.3 (OUT), U103.2 (IN), R106.1, C102.1, C103.1, R111.1 | wire (or local label `VIN_PROT`) |
| 2 | CHG_NTC | U103.7 (NTC), J103.1 (Pin_1), R111.2, R112.1 | wire (or local label `CHG_NTC`) |

#### R111 · 33k · NTC top b: 10k || 33k = 7.67k

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VIN_PROT | U102.1 (OUT), U102.2 (OUT), U102.3 (OUT), U103.2 (IN), R106.1, C102.1, C103.1, R110.1 | wire (or local label `VIN_PROT`) |
| 2 | CHG_NTC | U103.7 (NTC), J103.1 (Pin_1), R110.2, R112.1 | wire (or local label `CHG_NTC`) |

#### R112 · 100k · NTC to GND (parallel with the 10k B3950 NTC): charge window 0-45 C

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | CHG_NTC | U103.7 (NTC), J103.1 (Pin_1), R110.2, R111.2 | wire (or local label `CHG_NTC`) |
| 2 | GND |  | power symbol `GND` |

#### R113 · 100k · ENB pull-down: charging on without firmware

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | CHG_EN_N | U103.6 (ENB); MCU sheet: U201.19 (IO15) | **global label `CHG_EN_N`** |
| 2 | GND |  | power symbol `GND` |

#### R114 · 10k · STAT pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | CHG_STAT | U103.9 (STAT); MCU sheet: U201.18 (IO14) | **global label `CHG_STAT`** |
| 2 | +3V3 |  | power symbol `+3V3` |

### Battery protection and sense


#### J102 · Battery 1x 21700 (holder with leads) · HAND-SOLDER, bottom. 1 B+, 2 B-

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | VBAT | U103.14 (BATT), U103.16 (BATT), C106.1, R115.1, R117.1 | wire (or local label `VBAT`) |
| 2 Pin_2 | BAT_N | U104.6 (GND), Q101.2 (S1), Q101.3 (S1), C107.2 | wire (or local label `BAT_N`) |

#### J103 · NTC 10k B3950 (on the cell) · HAND-SOLDER, bottom. 1 NTC, 2 GND. No thermistor: fit a 10k resistor across it

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | CHG_NTC | U103.7 (NTC), R110.2, R111.2, R112.1 | wire (or local label `CHG_NTC`) |
| 2 Pin_2 | GND |  | power symbol `GND` |

#### U104 · DW01A · cell protection

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 OD | DW_OD | Q101.4 (G1) | wire (or local label `DW_OD`) |
| 2 CS | DW_CS | R116.1 | wire (or local label `DW_CS`) |
| 3 OC | DW_OC | Q101.5 (G2) | wire (or local label `DW_OC`) |
| 4 TD | — | nothing | no-connect flag (X) |
| 5 VCC | DW_VCC | R115.2, C107.1 | wire (or local label `DW_VCC`) |
| 6 GND | BAT_N | J102.2 (Pin_2), Q101.2 (S1), Q101.3 (S1), C107.2 | wire (or local label `BAT_N`) |

#### Q101 · FS8205A · dual N-FET between B- and GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D12 | FET_D | (only this part) | wire (or local label `FET_D`) |
| 2 S1 | BAT_N | J102.2 (Pin_2), U104.6 (GND), C107.2 | wire (or local label `BAT_N`) |
| 3 S1 | BAT_N | J102.2 (Pin_2), U104.6 (GND), C107.2 | wire (or local label `BAT_N`) |
| 4 G1 | DW_OD | U104.1 (OD) | wire (or local label `DW_OD`) |
| 5 G2 | DW_OC | U104.3 (OC) | wire (or local label `DW_OC`) |
| 6 S2 | GND |  | power symbol `GND` |
| 7 S2 | GND |  | power symbol `GND` |
| 8 D12 | FET_D | (only this part) | wire (or local label `FET_D`) |

#### R115 · 100 · DW01A VCC series (100 ohm; LCSC number at BOM time)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBAT | U103.14 (BATT), U103.16 (BATT), J102.1 (Pin_1), C106.1, R117.1 | wire (or local label `VBAT`) |
| 2 | DW_VCC | U104.5 (VCC), C107.1 | wire (or local label `DW_VCC`) |

#### C107 · 100nF · DW01A VCC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | DW_VCC | U104.5 (VCC), R115.2 | wire (or local label `DW_VCC`) |
| 2 | BAT_N | J102.2 (Pin_2), U104.6 (GND), Q101.2 (S1), Q101.3 (S1) | wire (or local label `BAT_N`) |

#### R116 · 1k · DW01A CS

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | DW_CS | U104.2 (CS) | wire (or local label `DW_CS`) |
| 2 | GND |  | power symbol `GND` |

#### R117 · 100k · battery sense top (VBAT -> VBAT_SENSE, IO10)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBAT | U103.14 (BATT), U103.16 (BATT), J102.1 (Pin_1), C106.1, R115.1 | wire (or local label `VBAT`) |
| 2 | VBAT_SENSE | R118.1, C108.1; MCU sheet: U201.14 (IO10) | **global label `VBAT_SENSE`** |

#### R118 · 100k · battery sense bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBAT_SENSE | R117.2, C108.1; MCU sheet: U201.14 (IO10) | **global label `VBAT_SENSE`** |
| 2 | GND |  | power symbol `GND` |

#### C108 · 100nF · battery sense filter

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VBAT_SENSE | R117.2, R118.1; MCU sheet: U201.14 (IO10) | **global label `VBAT_SENSE`** |
| 2 | GND |  | power symbol `GND` |

### 3.3 V LDO (left strip, near the ESP32)


#### U105 · TLV75733PDBV · VSYS -> 3V3, EN tied to IN

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 IN | VSYS | U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, C105.1, C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 2 GND | GND |  | power symbol `GND` |
| 3 EN | VSYS | U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, C105.1, C109.1; RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 4 NC | — | nothing | no-connect flag (X) |
| 5 OUT | +3V3 |  | power symbol `+3V3` |

#### C109 · 1uF · LDO input

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VSYS | U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, C105.1, U105.1 (IN), U105.3 (EN); RGB sheet: U401.3 (VIN), L401.1, C401.1 | **global label `VSYS`** |
| 2 | GND |  | power symbol `GND` |

#### C110 · 1uF · LDO output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

### Mounting holes (M3)


#### H101 · M3 · (4.5, 38)

No pins (mechanical only).

#### H102 · M3 · (95.5, 38)

No pins (mechanical only).

#### H103 · M3 · (4.5, 66)

No pins (mechanical only).

#### H104 · M3 · (95.5, 80)

No pins (mechanical only).

#### H105 · M3 · (60, 93)

No pins (mechanical only).

---

## Sheet MCU

File `mcu.kicad_sch` · 11 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `CHG_EN_N`, `CHG_ISEL`, `CHG_STAT`, `DISP_BLK`, `DISP_CS`, `DISP_DC`, `DISP_EN_N`, `DISP_RES`, `DISP_SCL`, `DISP_SDA`, `ENC1_A`, `ENC1_B`, `ENC1_SW`, `ENC2_A`, `ENC2_B`, `ENC2_SW`, `KEY1`, `KEY10`, `KEY11`, `KEY12`, `KEY2`, `KEY3`, `KEY4`, `KEY5`, `KEY6`, `KEY7`, `KEY8`, `KEY9`, `PAD_RX`, `PAD_TX`, `RGB_DATA`, `RGB_EN`, `TGL_PERSONAL`, `TGL_WORK`, `VBAT_SENSE`, `VIN_SENSE`
- PWR_FLAG on: none
- No-connect flags: 5

### ESP32-S3-MINI-1 (front-left, antenna at the left edge)


#### U201 · ESP32-S3-MINI-1-N8 · position (9.50, 92.30), rotation 90

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 GND | GND |  | power symbol `GND` |
| 2 GND | GND |  | power symbol `GND` |
| 3 3V3 | +3V3 |  | power symbol `+3V3` |
| 4 IO0 | BOOT | SW202.1 | wire (or local label `BOOT`) |
| 5 IO1 | KEY2 | INPUTS sheet: SW302.1 | **global label `KEY2`** |
| 6 IO2 | KEY6 | INPUTS sheet: SW306.1 | **global label `KEY6`** |
| 7 IO3 | KEY10 | INPUTS sheet: SW310.1 | **global label `KEY10`** |
| 8 IO4 | KEY3 | INPUTS sheet: SW303.1 | **global label `KEY3`** |
| 9 IO5 | KEY7 | INPUTS sheet: SW307.1 | **global label `KEY7`** |
| 10 IO6 | KEY11 | INPUTS sheet: SW311.1 | **global label `KEY11`** |
| 11 IO7 | KEY4 | INPUTS sheet: SW304.1 | **global label `KEY4`** |
| 12 IO8 | KEY8 | INPUTS sheet: SW308.1 | **global label `KEY8`** |
| 13 IO9 | KEY12 | INPUTS sheet: SW312.1 | **global label `KEY12`** |
| 14 IO10 | VBAT_SENSE | POWER sheet: R117.2, R118.1, C108.1 | **global label `VBAT_SENSE`** |
| 15 IO11 | VIN_SENSE | POWER sheet: R106.2, R107.1 | **global label `VIN_SENSE`** |
| 16 IO12 | TGL_WORK | INPUTS sheet: J301.3 (Pin_3) | **global label `TGL_WORK`** |
| 17 IO13 | TGL_PERSONAL | INPUTS sheet: J301.1 (Pin_1) | **global label `TGL_PERSONAL`** |
| 18 IO14 | CHG_STAT | POWER sheet: U103.9 (STAT), R114.1 | **global label `CHG_STAT`** |
| 19 IO15 | CHG_EN_N | POWER sheet: U103.6 (ENB), R113.1 | **global label `CHG_EN_N`** |
| 20 IO16 | ENC2_SW | INPUTS sheet: SW314.S1 | **global label `ENC2_SW`** |
| 21 IO17 | ENC2_B | INPUTS sheet: R308.2, C304.1 | **global label `ENC2_B`** |
| 22 IO18 | ENC2_A | INPUTS sheet: R307.2, C303.1 | **global label `ENC2_A`** |
| 23 USB_D- | USB_DN | J201.A7 (D-), J201.B7 (D-), U202.3 (D2+) | wire (or local label `USB_DN`) |
| 24 USB_D+ | USB_DP | J201.A6 (D+), J201.B6 (D+), U202.1 (D1+) | wire (or local label `USB_DP`) |
| 25 IO21 | CHG_ISEL | POWER sheet: U103.13 (USB_DET) | **global label `CHG_ISEL`** |
| 26 IO26 | RGB_EN | RGB sheet: U401.2 (EN), R403.1 | **global label `RGB_EN`** |
| 27 IO47 | DISP_EN_N | DISPLAY sheet: Q501.1 (G), R501.1 | **global label `DISP_EN_N`** |
| 28 IO33 | DISP_SCL | DISPLAY sheet: J501.6 (Pin_6) | **global label `DISP_SCL`** |
| 29 IO34 | DISP_SDA | DISPLAY sheet: J501.5 (Pin_5) | **global label `DISP_SDA`** |
| 30 IO48 | DISP_RES | DISPLAY sheet: J501.4 (Pin_4) | **global label `DISP_RES`** |
| 31 IO35 | DISP_DC | DISPLAY sheet: J501.3 (Pin_3) | **global label `DISP_DC`** |
| 32 IO36 | DISP_CS | DISPLAY sheet: J501.2 (Pin_2) | **global label `DISP_CS`** |
| 33 IO37 | DISP_BLK | DISPLAY sheet: J501.1 (Pin_1) | **global label `DISP_BLK`** |
| 34 IO38 | KEY9 | INPUTS sheet: SW309.1 | **global label `KEY9`** |
| 35 IO39 | KEY5 | INPUTS sheet: SW305.1 | **global label `KEY5`** |
| 36 IO40 | KEY1 | INPUTS sheet: SW301.1 | **global label `KEY1`** |
| 37 IO41 | ENC1_B | INPUTS sheet: R304.2, C302.1 | **global label `ENC1_B`** |
| 38 IO42 | ENC1_A | INPUTS sheet: R303.2, C301.1 | **global label `ENC1_A`** |
| 39 TXD0 | PAD_TX | POWER sheet: R102.2 | **global label `PAD_TX`** |
| 40 RXD0 | PAD_RX | POWER sheet: R101.2 | **global label `PAD_RX`** |
| 41 IO45 | ENC1_SW | INPUTS sheet: SW313.S1 | **global label `ENC1_SW`** |
| 42 GND | GND |  | power symbol `GND` |
| 43 GND | GND |  | power symbol `GND` |
| 44 IO46 | RGB_DATA | RGB sheet: U402.2 | **global label `RGB_DATA`** |
| 45 EN | ESP_EN | R201.2, C203.1, SW201.1 | wire (or local label `ESP_EN`) |
| 46 GND | GND |  | power symbol `GND` |
| 47 GND | GND |  | power symbol `GND` |
| 48 GND | GND |  | power symbol `GND` |
| 49 GND | GND |  | power symbol `GND` |
| 50 GND | GND |  | power symbol `GND` |
| 51 GND | GND |  | power symbol `GND` |
| 52 GND | GND |  | power symbol `GND` |
| 53 GND | GND |  | power symbol `GND` |
| 54 GND | GND |  | power symbol `GND` |
| 55 GND | GND |  | power symbol `GND` |
| 56 GND | GND |  | power symbol `GND` |
| 57 GND | GND |  | power symbol `GND` |
| 58 GND | GND |  | power symbol `GND` |
| 59 GND | GND |  | power symbol `GND` |
| 60 GND | GND |  | power symbol `GND` |
| 61 GND | GND |  | power symbol `GND` |
| 62 GND | GND |  | power symbol `GND` |
| 63 GND | GND |  | power symbol `GND` |
| 64 GND | GND |  | power symbol `GND` |
| 65 GND | GND |  | power symbol `GND` |

#### C201 · 10uF · 3V3 at the module

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

#### C202 · 100nF · 3V3 at the module

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | GND |  | power symbol `GND` |

### Reset and boot


#### R201 · 10k · EN pull-up

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | +3V3 |  | power symbol `+3V3` |
| 2 | ESP_EN | U201.45 (EN), C203.1, SW201.1 | wire (or local label `ESP_EN`) |

#### C203 · 1uF · EN to GND (RC delay)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ESP_EN | U201.45 (EN), R201.2, SW201.1 | wire (or local label `ESP_EN`) |
| 2 | GND |  | power symbol `GND` |

#### SW201 · SW_Push · RESET: EN to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ESP_EN | U201.45 (EN), R201.2, C203.1 | wire (or local label `ESP_EN`) |
| 2 | GND |  | power symbol `GND` |

#### SW202 · SW_Push · BOOT: GPIO0 to GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BOOT | U201.4 (IO0) | wire (or local label `BOOT`) |
| 2 | GND |  | power symbol `GND` |

### USB-C (flashing / debug only, front edge next to the module)


#### J201 · TYPE-C-31-M-12 · FRONT edge, x = 27 (next to the module). D+/D- to IO20/IO19; VBUS pins joined, not used

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A1 GND | GND |  | power symbol `GND` |
| A4 VBUS | USB_VBUS | (only this part) | wire (or local label `USB_VBUS`) |
| A5 CC1 | USB_CC1 | R202.1 | wire (or local label `USB_CC1`) |
| A6 D+ | USB_DP | U201.24 (USB_D+), U202.1 (D1+) | wire (or local label `USB_DP`) |
| A7 D- | USB_DN | U201.23 (USB_D-), U202.3 (D2+) | wire (or local label `USB_DN`) |
| A8 SBU1 | — | nothing | no-connect flag (X) |
| A9 VBUS | USB_VBUS | (only this part) | wire (or local label `USB_VBUS`) |
| A12 GND | GND |  | power symbol `GND` |
| B1 GND | GND |  | power symbol `GND` |
| B4 VBUS | USB_VBUS | (only this part) | wire (or local label `USB_VBUS`) |
| B5 CC2 | USB_CC2 | R203.1 | wire (or local label `USB_CC2`) |
| B6 D+ | USB_DP | U201.24 (USB_D+), U202.1 (D1+) | wire (or local label `USB_DP`) |
| B7 D- | USB_DN | U201.23 (USB_D-), U202.3 (D2+) | wire (or local label `USB_DN`) |
| B8 SBU2 | — | nothing | no-connect flag (X) |
| B9 VBUS | USB_VBUS | (only this part) | wire (or local label `USB_VBUS`) |
| B12 GND | GND |  | power symbol `GND` |
| SH SHIELD | GND |  | power symbol `GND` |

#### U202 · TPD4E1U06DBVR · ESD on D+, D-

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 D1+ | USB_DP | U201.24 (USB_D+), J201.A6 (D+), J201.B6 (D+) | wire (or local label `USB_DP`) |
| 2 GND | GND |  | power symbol `GND` |
| 3 D2+ | USB_DN | U201.23 (USB_D-), J201.A7 (D-), J201.B7 (D-) | wire (or local label `USB_DN`) |
| 4 D2- | — | nothing | no-connect flag (X) |
| 5 NC | — | nothing | no-connect flag (X) |
| 6 D1- | — | nothing | no-connect flag (X) |

#### R202 · 5.1k · CC1 Rd

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | USB_CC1 | J201.A5 (CC1) | wire (or local label `USB_CC1`) |
| 2 | GND |  | power symbol `GND` |

#### R203 · 5.1k · CC2 Rd

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | USB_CC2 | J201.B5 (CC2) | wire (or local label `USB_CC2`) |
| 2 | GND |  | power symbol `GND` |

---

## Sheet INPUTS

File `inputs.kicad_sch` · 27 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `ENC1_A`, `ENC1_B`, `ENC1_SW`, `ENC2_A`, `ENC2_B`, `ENC2_SW`, `KEY1`, `KEY10`, `KEY11`, `KEY12`, `KEY2`, `KEY3`, `KEY4`, `KEY5`, `KEY6`, `KEY7`, `KEY8`, `KEY9`, `TGL_PERSONAL`, `TGL_WORK`
- PWR_FLAG on: none
- No-connect flags: 0

### Keys 1-12 (one GPIO each, other side to GND)


#### SW301 · MX switch (hot-swap socket) · key 1 -> IO40; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY1 | MCU sheet: U201.36 (IO40) | **global label `KEY1`** |
| 2 | GND |  | power symbol `GND` |

#### SW302 · MX switch (hot-swap socket) · key 2 -> IO1; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY2 | MCU sheet: U201.5 (IO1) | **global label `KEY2`** |
| 2 | GND |  | power symbol `GND` |

#### SW303 · MX switch (hot-swap socket) · key 3 -> IO4; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY3 | MCU sheet: U201.8 (IO4) | **global label `KEY3`** |
| 2 | GND |  | power symbol `GND` |

#### SW304 · MX switch (hot-swap socket) · key 4 -> IO7; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY4 | MCU sheet: U201.11 (IO7) | **global label `KEY4`** |
| 2 | GND |  | power symbol `GND` |

#### SW305 · MX switch (hot-swap socket) · key 5 -> IO39; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY5 | MCU sheet: U201.35 (IO39) | **global label `KEY5`** |
| 2 | GND |  | power symbol `GND` |

#### SW306 · MX switch (hot-swap socket) · key 6 -> IO2; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY6 | MCU sheet: U201.6 (IO2) | **global label `KEY6`** |
| 2 | GND |  | power symbol `GND` |

#### SW307 · MX switch (hot-swap socket) · key 7 -> IO5; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY7 | MCU sheet: U201.9 (IO5) | **global label `KEY7`** |
| 2 | GND |  | power symbol `GND` |

#### SW308 · MX switch (hot-swap socket) · key 8 -> IO8; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY8 | MCU sheet: U201.12 (IO8) | **global label `KEY8`** |
| 2 | GND |  | power symbol `GND` |

#### SW309 · MX switch (hot-swap socket) · key 9 -> IO38; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY9 | MCU sheet: U201.34 (IO38) | **global label `KEY9`** |
| 2 | GND |  | power symbol `GND` |

#### SW310 · MX switch (hot-swap socket) · key 10 -> IO3; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY10 | MCU sheet: U201.7 (IO3) | **global label `KEY10`** |
| 2 | GND |  | power symbol `GND` |

#### SW311 · MX switch (hot-swap socket) · key 11 -> IO6; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY11 | MCU sheet: U201.10 (IO6) | **global label `KEY11`** |
| 2 | GND |  | power symbol `GND` |

#### SW312 · MX switch (hot-swap socket) · key 12 -> IO9; socket HAND-SOLDER, bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | KEY12 | MCU sheet: U201.13 (IO9) | **global label `KEY12`** |
| 2 | GND |  | power symbol `GND` |

### Encoder 1: volume (left)


#### SW313 · PEC11R-4220F-S0024 · HAND-SOLDER. C, MP (lugs), S2 to GND; A/B via RC to IO42/IO41; S1 to IO45

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A | ENC1_A_RAW | R301.1, R303.1 | wire (or local label `ENC1_A_RAW`) |
| B | ENC1_B_RAW | R302.1, R304.1 | wire (or local label `ENC1_B_RAW`) |
| C | GND |  | power symbol `GND` |
| MP | GND |  | power symbol `GND` |
| S1 | ENC1_SW | MCU sheet: U201.41 (IO45) | **global label `ENC1_SW`** |
| S2 | GND |  | power symbol `GND` |

#### R301 · 10k · A pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC1_A_RAW | SW313.A, R303.1 | wire (or local label `ENC1_A_RAW`) |
| 2 | +3V3 |  | power symbol `+3V3` |

#### R302 · 10k · B pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC1_B_RAW | SW313.B, R304.1 | wire (or local label `ENC1_B_RAW`) |
| 2 | +3V3 |  | power symbol `+3V3` |

#### R303 · 10k · A series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC1_A_RAW | SW313.A, R301.1 | wire (or local label `ENC1_A_RAW`) |
| 2 | ENC1_A | C301.1; MCU sheet: U201.38 (IO42) | **global label `ENC1_A`** |

#### R304 · 10k · B series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC1_B_RAW | SW313.B, R302.1 | wire (or local label `ENC1_B_RAW`) |
| 2 | ENC1_B | C302.1; MCU sheet: U201.37 (IO41) | **global label `ENC1_B`** |

#### C301 · 10nF · A filter, GPIO side

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC1_A | R303.2; MCU sheet: U201.38 (IO42) | **global label `ENC1_A`** |
| 2 | GND |  | power symbol `GND` |

#### C302 · 10nF · B filter, GPIO side

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC1_B | R304.2; MCU sheet: U201.37 (IO41) | **global label `ENC1_B`** |
| 2 | GND |  | power symbol `GND` |

### Encoder 2: mic / call (right)


#### SW314 · PEC11R-4220F-S0024 · HAND-SOLDER. C, MP, S2 to GND; A/B via RC to IO18/IO17; S1 to IO16

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| A | ENC2_A_RAW | R305.1, R307.1 | wire (or local label `ENC2_A_RAW`) |
| B | ENC2_B_RAW | R306.1, R308.1 | wire (or local label `ENC2_B_RAW`) |
| C | GND |  | power symbol `GND` |
| MP | GND |  | power symbol `GND` |
| S1 | ENC2_SW | MCU sheet: U201.20 (IO16) | **global label `ENC2_SW`** |
| S2 | GND |  | power symbol `GND` |

#### R305 · 10k · A pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC2_A_RAW | SW314.A, R307.1 | wire (or local label `ENC2_A_RAW`) |
| 2 | +3V3 |  | power symbol `+3V3` |

#### R306 · 10k · B pull-up to 3V3

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC2_B_RAW | SW314.B, R308.1 | wire (or local label `ENC2_B_RAW`) |
| 2 | +3V3 |  | power symbol `+3V3` |

#### R307 · 10k · A series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC2_A_RAW | SW314.A, R305.1 | wire (or local label `ENC2_A_RAW`) |
| 2 | ENC2_A | C303.1; MCU sheet: U201.22 (IO18) | **global label `ENC2_A`** |

#### R308 · 10k · B series

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC2_B_RAW | SW314.B, R306.1 | wire (or local label `ENC2_B_RAW`) |
| 2 | ENC2_B | C304.1; MCU sheet: U201.21 (IO17) | **global label `ENC2_B`** |

#### C303 · 10nF · A filter, GPIO side

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC2_A | R307.2; MCU sheet: U201.22 (IO18) | **global label `ENC2_A`** |
| 2 | GND |  | power symbol `GND` |

#### C304 · 10nF · B filter, GPIO side

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | ENC2_B | R308.2; MCU sheet: U201.21 (IO17) | **global label `ENC2_B`** |
| 2 | GND |  | power symbol `GND` |

### Selector toggle (on the case)


#### J301 · Toggle PERSONAL-OFF-WORK · HAND-SOLDER, bottom. 1 PERSONAL (IO13), 2 GND (common), 3 WORK (IO12)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | TGL_PERSONAL | MCU sheet: U201.17 (IO13) | **global label `TGL_PERSONAL`** |
| 2 Pin_2 | GND |  | power symbol `GND` |
| 3 Pin_3 | TGL_WORK | MCU sheet: U201.16 (IO12) | **global label `TGL_WORK`** |

---

## Sheet RGB

File `rgb.kicad_sch` · 83 parts

- Power symbols: `GND`
- Global labels on this sheet: `RGB_DATA`, `RGB_EN`, `VSYS`
- PWR_FLAG on: `5V_RGB`
- No-connect flags: 1

### 5 V boost TPS61023 (power strip)


#### U401 · TPS61023DRLR · VSYS -> 5V_RGB; EN = RGB_EN (IO26), true disconnect when low

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 FB | BOOST_FB | R401.2, R402.1 | wire (or local label `BOOST_FB`) |
| 2 EN | RGB_EN | R403.1; MCU sheet: U201.26 (IO26) | **global label `RGB_EN`** |
| 3 VIN | VSYS | L401.1, C401.1; POWER sheet: U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, C105.1, U105.1 (IN), U105.3 (EN), C109.1 | **global label `VSYS`** |
| 4 GND | GND |  | power symbol `GND` |
| 5 SW | BOOST_SW | L401.2 | wire (or local label `BOOST_SW`) |
| 6 VOUT | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### L401 · 1uH · XRNR4030-1uH/N, Isat 5.26 A

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VSYS | U401.3 (VIN), C401.1; POWER sheet: U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, C105.1, U105.1 (IN), U105.3 (EN), C109.1 | **global label `VSYS`** |
| 2 | BOOST_SW | U401.5 (SW) | wire (or local label `BOOST_SW`) |

#### C401 · 10uF · boost input

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | VSYS | U401.3 (VIN), L401.1; POWER sheet: U103.1 (SYS), U103.15 (SYS), L101.2, C104.1, C105.1, U105.1 (IN), U105.3 (EN), C109.1 | **global label `VSYS`** |
| 2 | GND |  | power symbol `GND` |

#### C402 · 22uF · 5V_RGB output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### C403 · 22uF · 5V_RGB output

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### R401 · 51k · FB top: 0.595 x (1 + 51/6.8) = 5.06 V

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | BOOST_FB | U401.1 (FB), R402.1 | wire (or local label `BOOST_FB`) |

#### R402 · 6.8k · FB bottom

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | BOOST_FB | U401.1 (FB), R401.2 | wire (or local label `BOOST_FB`) |
| 2 | GND |  | power symbol `GND` |

#### R403 · 100k · EN pull-down (LEDs off at reset)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | RGB_EN | U401.2 (EN); MCU sheet: U201.26 (IO26) | **global label `RGB_EN`** |
| 2 | GND |  | power symbol `GND` |

### Data level shifter


#### U402 · SN74AHCT1G125DBVR · input RGB_DATA (IO46); powered from 5V_RGB; OE (pin 1) to GND; place near the ESP32 / key 9

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | GND |  | power symbol `GND` |
| 2 | RGB_DATA | MCU sheet: U201.44 (IO46) | **global label `RGB_DATA`** |
| 3 GND | GND |  | power symbol `GND` |
| 4 | RGB_DATA_5V | R404.1 | wire (or local label `RGB_DATA_5V`) |
| 5 VCC | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C404 · 100nF · U402 VCC

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### R404 · 33 · series, U402 output to D401 DIN (key 9 LED)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | RGB_DATA_5V | U402.4 | wire (or local label `RGB_DATA_5V`) |
| 2 | LED_D0 | D401.2 (DIN) | wire (or local label `LED_D0`) |

### Key LEDs: keys 9, 10, 11, 12 (chain starts here)


#### D401 · SK6812MINI-E · chain index 0: key 9 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D0 | R404.2 | wire (or local label `LED_D0`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D1 | D402.2 (DIN) | wire (or local label `LED_D1`) |

#### C405 · 100nF · at D401 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D402 · SK6812MINI-E · chain index 1: key 10 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D1 | D401.4 (DOUT) | wire (or local label `LED_D1`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D2 | D403.2 (DIN) | wire (or local label `LED_D2`) |

#### C406 · 100nF · at D402 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D403 · SK6812MINI-E · chain index 2: key 11 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D2 | D402.4 (DOUT) | wire (or local label `LED_D2`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D3 | D404.2 (DIN) | wire (or local label `LED_D3`) |

#### C407 · 100nF · at D403 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D404 · SK6812MINI-E · chain index 3: key 12 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D3 | D403.4 (DOUT) | wire (or local label `LED_D3`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D4 | D405.2 (DIN) | wire (or local label `LED_D4`) |

#### C408 · 100nF · at D404 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

### Key LEDs: keys 8, 7, 6, 5


#### D405 · SK6812MINI-E · chain index 4: key 8 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D4 | D404.4 (DOUT) | wire (or local label `LED_D4`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D5 | D406.2 (DIN) | wire (or local label `LED_D5`) |

#### C409 · 100nF · at D405 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D406 · SK6812MINI-E · chain index 5: key 7 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D5 | D405.4 (DOUT) | wire (or local label `LED_D5`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D6 | D407.2 (DIN) | wire (or local label `LED_D6`) |

#### C410 · 100nF · at D406 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D407 · SK6812MINI-E · chain index 6: key 6 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D6 | D406.4 (DOUT) | wire (or local label `LED_D6`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D7 | D408.2 (DIN) | wire (or local label `LED_D7`) |

#### C411 · 100nF · at D407 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D408 · SK6812MINI-E · chain index 7: key 5 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D7 | D407.4 (DOUT) | wire (or local label `LED_D7`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D8 | D409.2 (DIN) | wire (or local label `LED_D8`) |

#### C412 · 100nF · at D408 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

### Key LEDs: keys 1, 2, 3, 4


#### D409 · SK6812MINI-E · chain index 8: key 1 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D8 | D408.4 (DOUT) | wire (or local label `LED_D8`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D9 | D410.2 (DIN) | wire (or local label `LED_D9`) |

#### C413 · 100nF · at D409 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D410 · SK6812MINI-E · chain index 9: key 2 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D9 | D409.4 (DOUT) | wire (or local label `LED_D9`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D10 | D411.2 (DIN) | wire (or local label `LED_D10`) |

#### C414 · 100nF · at D410 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D411 · SK6812MINI-E · chain index 10: key 3 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D10 | D410.4 (DOUT) | wire (or local label `LED_D10`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D11 | D412.2 (DIN) | wire (or local label `LED_D11`) |

#### C415 · 100nF · at D411 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D412 · SK6812MINI-E · chain index 11: key 4 (bottom side, HAND-SOLDER)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 VSS | GND |  | power symbol `GND` |
| 2 DIN | LED_D11 | D411.4 (DOUT) | wire (or local label `LED_D11`) |
| 3 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 4 DOUT | LED_D12 | D413.3 (DIN) | wire (or local label `LED_D12`) |

#### C416 · 100nF · at D412 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

### Ring 2 (ENC2), counter-clockwise from 7 o'clock


#### D413 · XL-2020RGBC-WS2812B · chain index 12: ring 2, 7 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D13 | D414.3 (DIN) | wire (or local label `LED_D13`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D12 | D412.4 (DOUT) | wire (or local label `LED_D12`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C417 · 100nF · at D413 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D414 · XL-2020RGBC-WS2812B · chain index 13: ring 2, 6 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D14 | D415.3 (DIN) | wire (or local label `LED_D14`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D13 | D413.1 (DOUT) | wire (or local label `LED_D13`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C418 · 100nF · at D414 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D415 · XL-2020RGBC-WS2812B · chain index 14: ring 2, 5 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D15 | D416.3 (DIN) | wire (or local label `LED_D15`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D14 | D414.1 (DOUT) | wire (or local label `LED_D14`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C419 · 100nF · at D415 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D416 · XL-2020RGBC-WS2812B · chain index 15: ring 2, 4 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D16 | D417.3 (DIN) | wire (or local label `LED_D16`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D15 | D415.1 (DOUT) | wire (or local label `LED_D15`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C420 · 100nF · at D416 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D417 · XL-2020RGBC-WS2812B · chain index 16: ring 2, 3 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D17 | D418.3 (DIN) | wire (or local label `LED_D17`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D16 | D416.1 (DOUT) | wire (or local label `LED_D16`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C421 · 100nF · at D417 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D418 · XL-2020RGBC-WS2812B · chain index 17: ring 2, 2 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D18 | D419.3 (DIN) | wire (or local label `LED_D18`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D17 | D417.1 (DOUT) | wire (or local label `LED_D17`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C422 · 100nF · at D418 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D419 · XL-2020RGBC-WS2812B · chain index 18: ring 2, 1 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D19 | D420.3 (DIN) | wire (or local label `LED_D19`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D18 | D418.1 (DOUT) | wire (or local label `LED_D18`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C423 · 100nF · at D419 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D420 · XL-2020RGBC-WS2812B · chain index 19: ring 2, 12 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D20 | D421.3 (DIN) | wire (or local label `LED_D20`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D19 | D419.1 (DOUT) | wire (or local label `LED_D19`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C424 · 100nF · at D420 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D421 · XL-2020RGBC-WS2812B · chain index 20: ring 2, 11 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D21 | D422.3 (DIN) | wire (or local label `LED_D21`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D20 | D420.1 (DOUT) | wire (or local label `LED_D20`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C425 · 100nF · at D421 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D422 · XL-2020RGBC-WS2812B · chain index 21: ring 2, 10 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D22 | D423.3 (DIN) | wire (or local label `LED_D22`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D21 | D421.1 (DOUT) | wire (or local label `LED_D21`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C426 · 100nF · at D422 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D423 · XL-2020RGBC-WS2812B · chain index 22: ring 2, 9 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D23 | D424.3 (DIN) | wire (or local label `LED_D23`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D22 | D422.1 (DOUT) | wire (or local label `LED_D22`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C427 · 100nF · at D423 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D424 · XL-2020RGBC-WS2812B · chain index 23: ring 2, 8 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D24 | D425.3 (DIN) | wire (or local label `LED_D24`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D23 | D423.1 (DOUT) | wire (or local label `LED_D23`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C428 · 100nF · at D424 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

### Ring 1 (ENC1), counter-clockwise from 4 o'clock


#### D425 · XL-2020RGBC-WS2812B · chain index 24: ring 1, 4 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D25 | D426.3 (DIN) | wire (or local label `LED_D25`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D24 | D424.1 (DOUT) | wire (or local label `LED_D24`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C429 · 100nF · at D425 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D426 · XL-2020RGBC-WS2812B · chain index 25: ring 1, 3 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D26 | D427.3 (DIN) | wire (or local label `LED_D26`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D25 | D425.1 (DOUT) | wire (or local label `LED_D25`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C430 · 100nF · at D426 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D427 · XL-2020RGBC-WS2812B · chain index 26: ring 1, 2 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D27 | D428.3 (DIN) | wire (or local label `LED_D27`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D26 | D426.1 (DOUT) | wire (or local label `LED_D26`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C431 · 100nF · at D427 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D428 · XL-2020RGBC-WS2812B · chain index 27: ring 1, 1 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D28 | D429.3 (DIN) | wire (or local label `LED_D28`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D27 | D427.1 (DOUT) | wire (or local label `LED_D27`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C432 · 100nF · at D428 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D429 · XL-2020RGBC-WS2812B · chain index 28: ring 1, 12 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D29 | D430.3 (DIN) | wire (or local label `LED_D29`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D28 | D428.1 (DOUT) | wire (or local label `LED_D28`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C433 · 100nF · at D429 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D430 · XL-2020RGBC-WS2812B · chain index 29: ring 1, 11 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D30 | D431.3 (DIN) | wire (or local label `LED_D30`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D29 | D429.1 (DOUT) | wire (or local label `LED_D29`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C434 · 100nF · at D430 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D431 · XL-2020RGBC-WS2812B · chain index 30: ring 1, 10 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D31 | D432.3 (DIN) | wire (or local label `LED_D31`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D30 | D430.1 (DOUT) | wire (or local label `LED_D30`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C435 · 100nF · at D431 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D432 · XL-2020RGBC-WS2812B · chain index 31: ring 1, 9 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D32 | D433.3 (DIN) | wire (or local label `LED_D32`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D31 | D431.1 (DOUT) | wire (or local label `LED_D31`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C436 · 100nF · at D432 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D433 · XL-2020RGBC-WS2812B · chain index 32: ring 1, 8 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D33 | D434.3 (DIN) | wire (or local label `LED_D33`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D32 | D432.1 (DOUT) | wire (or local label `LED_D32`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C437 · 100nF · at D433 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D434 · XL-2020RGBC-WS2812B · chain index 33: ring 1, 7 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D34 | D435.3 (DIN) | wire (or local label `LED_D34`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D33 | D433.1 (DOUT) | wire (or local label `LED_D33`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C438 · 100nF · at D434 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D435 · XL-2020RGBC-WS2812B · chain index 34: ring 1, 6 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | LED_D35 | D436.3 (DIN) | wire (or local label `LED_D35`) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D34 | D434.1 (DOUT) | wire (or local label `LED_D34`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C439 · 100nF · at D435 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

#### D436 · XL-2020RGBC-WS2812B · chain index 35: ring 1, 5 o'clock

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 DOUT | — | nothing | no-connect flag (X) |
| 2 VSS | GND |  | power symbol `GND` |
| 3 DIN | LED_D35 | D435.1 (DOUT) | wire (or local label `LED_D35`) |
| 4 VDD | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |

#### C440 · 100nF · at D436 VDD (top side)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | 5V_RGB | 77 other pins: use the label | wire (or local label `5V_RGB`) |
| 2 | GND |  | power symbol `GND` |

---

## Sheet DISPLAY

File `display.kicad_sch` · 4 parts

- Power symbols: `+3V3`, `GND`
- Global labels on this sheet: `DISP_BLK`, `DISP_CS`, `DISP_DC`, `DISP_EN_N`, `DISP_RES`, `DISP_SCL`, `DISP_SDA`
- PWR_FLAG on: `DISP_VCC`
- No-connect flags: 0

### Display connector (back strip, bottom side)


#### J501 · Display 1.69in ST7789V3 · HAND-SOLDER. 1 BLK IO37, 2 CS IO36, 3 DC IO35, 4 RES IO48, 5 SDA IO34, 6 SCL IO33, 7 VCC, 8 GND, 9 GND

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 Pin_1 | DISP_BLK | MCU sheet: U201.33 (IO37) | **global label `DISP_BLK`** |
| 2 Pin_2 | DISP_CS | MCU sheet: U201.32 (IO36) | **global label `DISP_CS`** |
| 3 Pin_3 | DISP_DC | MCU sheet: U201.31 (IO35) | **global label `DISP_DC`** |
| 4 Pin_4 | DISP_RES | MCU sheet: U201.30 (IO48) | **global label `DISP_RES`** |
| 5 Pin_5 | DISP_SDA | MCU sheet: U201.29 (IO34) | **global label `DISP_SDA`** |
| 6 Pin_6 | DISP_SCL | MCU sheet: U201.28 (IO33) | **global label `DISP_SCL`** |
| 7 Pin_7 | DISP_VCC | Q501.3 (D), C501.1 | wire (or local label `DISP_VCC`) |
| 8 Pin_8 | GND |  | power symbol `GND` |
| 9 Pin_9 | GND |  | power symbol `GND` |

#### C501 · 1uF · DISP_VCC at J501

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | DISP_VCC | J501.7 (Pin_7), Q501.3 (D) | wire (or local label `DISP_VCC`) |
| 2 | GND |  | power symbol `GND` |

### Display power switch


#### Q501 · AO3401A · source 3V3, drain DISP_VCC, gate DISP_EN_N (IO47), low = on

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 G | DISP_EN_N | R501.1; MCU sheet: U201.27 (IO47) | **global label `DISP_EN_N`** |
| 2 S | +3V3 |  | power symbol `+3V3` |
| 3 D | DISP_VCC | J501.7 (Pin_7), C501.1 | wire (or local label `DISP_VCC`) |

#### R501 · 100k · gate pull-up to 3V3 (off at reset)

| Pin | Net | Connects to | Draw |
|---|---|---|---|
| 1 | DISP_EN_N | Q501.1 (G); MCU sheet: U201.27 (IO47) | **global label `DISP_EN_N`** |
| 2 | +3V3 |  | power symbol `+3V3` |
