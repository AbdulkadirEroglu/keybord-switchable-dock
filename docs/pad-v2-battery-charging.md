# Pad v2: battery and charging (research)

**Decision (2026-10-04): 1 × Samsung INR21700-50E, ETA6003 switching charger with power path, DW01A + FS8205 protection, divider + ADC for the battery level. No USB-C charging on the pad (it charges on the dock only).**

Date: 2026-10-04. Prices: LCSC 1-piece tier; Turkish prices include VAT.

## 1. Docking position (decided first, it drives the battery size)

**The pad sits on top of the dock.** The dock's pogo contacts are on a small board in the dock lid (straight Motorobit 7-pin set, flat contacts), cabled to the dock's J601 (JST-XH 7-pin). The pad's spring contacts are on its pogo board in the floor. The same pogo board design serves both sides: two identical boards facing each other meet pin 1 to pin 7, which is the mirrored contact order (DESIGN.md §15).

## 2. Battery: one cell

The pad charges on the dock most of the time; the battery only covers time away from it. Estimates (not measured): in use 100–200 mA → 25–50 h on one 4.9 Ah cell; idle off the dock with the BLE link kept 5–10 mA → 20–40 days. Two cells add 69 g and a 21 × 70 mm cylinder for little gain.

| Cell | Capacity | Turkey |
|---|---|---|
| **Samsung INR21700-50E** | 4.9 Ah at 0.2C, ≥ 3.8 Ah after 500 cycles, ≤ 28–35 mΩ | 354–502 TL (Pilmak, Trendyol, Robolink, Elektrodepo, Pil Paketi) |
| Molicel P45B | 4.5 Ah | 516–614 TL |

Holder: MYOUNG BH-21700-B1BJ001, SMT, JLCPCB-placed ($0.91, C20606791), or a loose holder (Motorobit sells one). Chosen at placement.

## 3. Charger

| Part | Type | Charge current | LCSC / stock | Notes |
|---|---|---|---|---|
| **ETA6003** (C5455585) | switching 3 MHz, power path | ≤ 2.5 A; ISET1/ISET2 chosen by USB_DET (GPIO-selectable, e.g. 1 A / 0.5 A) | **$0.43, ~9,600** | NTC, STAT, ENB (charge enable), ENPPB; SYS regulated 3.6–4.5 V, instant-on with dead/no battery; 2.2 µH; QFN-16 |
| BQ24072 / BQ24074 | linear, power path | 1.5 A | $1.05 / $2.24 | proven; dissipates ≈ 1.3 W at 1 A |
| BQ25185 | linear, power path | 1 A | $1.75, 309 | thin stock |
| MCP73871 | linear, power path | ≈ 1.5 A | $2.18 | older |
| TP4056 + TPS2116 (v1) | linear + separate path | ≈ 0.5 A | — | chosen for hand soldering only |

Why the ETA6003: up to 95 % efficient, so it stays cool inside a closed case on top of the dock (a linear charger turns ≈ 1.3 W into heat at 1 A); cheapest; the two charge currents replace v1's switched R_PROG.

**Battery care:** the firmware stops charging at ≈ 80 % with ENB while docked; the pad runs from the dock's 5 V through the power path, so the cell isn't held at 4.2 V for weeks.

**To check in the schematic:** the ETA6003's IN is 4.4–5.5 V operating, 6 V absolute. The dock's switched 5 V is 5.16 V; the pad's SMAJ5.0A clamps at ≈ 9 V, so consider an input overvoltage stage.

## 4. Protection and level

DW01A (C351410) + FS8205 (C32254), both JLCPCB Basic: the 50E has no built-in protection. Battery level: 100 k / 100 k divider into an ESP32-S3 ADC pin (fuel gauge optional, e.g. MAX17048).

Sources: [Trendyol 50E](https://www.trendyol.com/12mens/samsung-inr21700-50e-3-7v-5000-mah-li-ion-sarjli-pil-10a-2c-p-978281021), [Robolink 50E](https://www.robolinkmarket.com/samsung-inr21700-50e-li-ion-sarjli-pil-37v-5000mah), [Pilmak 50E](https://www.pilmak.com/samsung-inr21700-50e---5000-mah-li-ion-sarjli-pil---10a---2c-618), [50E specification](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/INR21700_2D00_50E-Cell-Specification_5F00_V1.0_5F00_180711.pdf), [LCSC ETA6003](https://www.lcsc.com/product-detail/C5455585.html), [ETA6003 datasheet](https://www.waveshare.com/w/upload/3/3f/ETA6003.pdf), [LCSC BQ24072](https://www.lcsc.com/product-detail/C140288.html), [LCSC BQ24074](https://www.lcsc.com/product-detail/C54313.html), [LCSC BQ25185](https://www.lcsc.com/product-detail/C19725033.html), [JLCPCB DW01A](https://jlcpcb.com/partdetail/PUOLOP-DW01A/C351410), [JLCPCB FS8205](https://jlcpcb.com/partdetail/FortuneSemicon-FS8205/C32254), [LCSC BH-21700-B1BJ001](https://www.lcsc.com/product-detail/C20606791.html), [Motorobit 21700 holder](https://www.motorobit.com/21700-single-battery-holder).

## 5. 3.3 V rail (decided 2026-10-04): TLV75733P LDO

**TLV75733PDBVR (LCSC C485517, $0.20, 1 A, SOT-23-5 with EN)** from VSYS. Loads: ESP32-S3 (≥ 500 mA supply asked; BLE TX 189 mA at 0 dBm, 340 mA at full power; module runs 3.0–3.6 V), display logic and backlight, pull-ups. VSYS is 3.6–4.5 V on the dock and follows the cell (4.2 → ≈ 3.0 V) on battery; below ≈ 3.3 V the LDO passes VSYS through minus its dropout, which the ESP32 tolerates down to 3.0 V. The capacity below ≈ 3.25 V that the LDO gives up is estimated at 10–15 % (not measured); acceptable for a pad that lives on the dock. Firmware low-battery cutoff ≈ 3.3 V (DW01A hard cutoff ≈ 2.4 V is the backstop).

Rejected: buck-boost TPS63802 (C2845237, $0.57) / TPS63020 ($0.65): full range but inductor, switching noise near the antenna, more parts. Cheaper LDOs: TLV75533P (500 mA, C404027), ME6211C33 (C82942, larger dropout at high current).

Sources: [ESP32-S3-MINI-1 datasheet](https://documentation.espressif.com/esp32-s3-mini-1_mini-1u_datasheet_en.html), [ESP-IDF current measurement](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/current-consumption-measurement-modules.html), [LCSC TLV75733PDBVR](https://www.lcsc.com/product-detail/C485517.html), [LCSC TPS63802](https://www.lcsc.com/product-detail/C2845237.html).

## 6. Voltage levels along the chain (2026-10-04)

| Point | Min | Typical | Max | From |
|---|---|---|---|---|
| Dock USB-C input (PD 9 V contract) | 8.55 V | 9.0 V | 9.45 V | USB PD fixed supply ± 5 %; 5 V before negotiation or with a non-PD charger |
| Dock 5 V rail (TPS54331, 12 k / 2.2 k) | 4.98 V (4.90 V with 1 % resistors) | 5.16 V | 5.34 V (5.44 V) | reference 0.772 / 0.800 / 0.828 V (datasheet) × 6.4545 |
| At the pad's pogo input | ≈ 4.7 V at ≈ 1 A | ≈ 5.1 V | 5.44 V | rail minus SY6280, cable and contact drops (estimate) |
| ETA6003 input: allowed | 4.4 V | | 5.5 V operating, **6 V absolute** | datasheet; reduces its current when the input sags to 4.5 V |
| Pad VSYS, docked | 3.6 V | | 4.5 V | ETA6003 |
| Pad VSYS, on battery | ≈ 3.3 V (firmware cutoff) | | 4.2 V | follows the cell (50 mΩ path) |
| Cell | 2.4 V (DW01A cutoff, approx.) / 3.3 V (firmware) | ≈ 4.0–4.1 V docked with the 80 % limit (estimate) | 4.20 V (4.16–4.24) | ETA6003 CV |
| 3.3 V rail | ≈ 3.0 V near empty | 3.3 V | | TLV75733P |
| 5 V LED rail | | ≈ 5.05 V | | TPS61023 (v1 divider) |

In normal operation the pad's input never exceeds 5.44 V (inside the ETA6003's 5.5 V operating limit). More can only arrive from a dock fault (TPS54331 switch shorted: 9 V on the 5 V rail). The SMAJ5.0A alone does not protect against that (it clamps at ≈ 9.2 V, above the 6 V limit).

## 7. Overvoltage switch (decided 2026-10-04): WS3222D

**WS3222D (LCSC C239703, $0.33, DFN2x2-8):** input up to 28 V, 45 mΩ, 3 A, OVLO = 1.2 V × (1 + R1/R2) with a 1.17–1.23 V reference. R1 = 51 k + 5.1 k, R2 = 15 k → **5.69 V** (≈ 5.5–5.9 V with tolerances): above the dock's 5.44 V maximum, below the ETA6003's 6 V limit. The TVS in front of it is an **SMBJ15A** (as on the dock), not the SMAJ5.0A of v1: a 5 V TVS would conduct continuously if the dock put 9 V on the contacts.

Rejected: NCP360 (fixed 5.675 V, but only 600 mA and 20 V). Not checked further: BQ24314 (170 mΩ would drop ≈ 0.2 V at 1.2 A).

Protection FET: **FS8205A in TSSOP-8 (C14212)** with the symbol already verified in v1, instead of the SOT-23-6 FS8205 named in §4.

NTC network for a 10 k B3950 thermistor on the cell: 10 k ∥ 33 k from IN to NTC, 100 k from NTC to GND → charging allowed ≈ 0–45 °C (ETA6003 thresholds 76.5 % / 35 % of VIN). Charge current: ISET1 1 k → 1.0 A, ISET2 2.2 k → 0.45 A (USB_DET high).

Sources: [LCSC WS3222D](https://www.lcsc.com/product-detail/Power-Distribution-Switches_WILLSEMI-Will-Semicon-WS3222D-8-TR_C239703.html), [WS3222D datasheet](http://www.sinotimes-tech.com/product/20180824110159443.pdf), [NCP360 datasheet](https://www.onsemi.com/pdf/datasheet/ncp360-d.pdf), [XL-2020RGBC-WS2812B datasheet](https://www.lcsc.com/datasheet/C5349955.pdf).
