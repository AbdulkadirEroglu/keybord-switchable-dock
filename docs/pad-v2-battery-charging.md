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
