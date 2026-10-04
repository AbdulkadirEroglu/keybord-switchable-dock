# Pad v2: inputs and RGB (research)

**Decisions (2026-10-04):**

- **Inputs:** every key, encoder signal and the toggle on its own ESP32-S3 GPIO (no matrix, no expander). MX switch footprint taking 3- and 5-pin switches; **Kailh CPG151101S11 hot-swap sockets, hand-soldered** (LCSC/JLC out of stock). Switches: the user's choice, open (any MX-compatible switch fits). Encoders: **Bourns PEC11R-4220F-S0024** (THT, hand-soldered) with Bourns' RC filter on A/B (10 k + 10 nF). Toggle: panel-mounted ON-OFF-ON on the case, 3-pin header.
- **RGB:** 12 × **SK6812MINI-E** (reverse mount, bottom side, **hand-soldered by the user**) under the keys, 2 × 12 × **XL-2020RGBC-WS2812B** (top side, JLC) for the encoder rings, one chain. 5 V from a **TPS61023** boost (true disconnect in shutdown, so the LEDs' ≈ 1 mA/LED idle current is cut), 1 µH ≥ 4.5 A inductor, **SN74AHCT1G125** level shifter on the data line.

Date: 2026-10-04. LCSC/JLC 1-piece prices.

## 1. GPIO budget (ESP32-S3-MINI-1-N8: 39 GPIO + UART0 = 41)

USB D−/D+ 2 (GPIO19/20) · BOOT 1 (GPIO0) · keys 12 · encoders 6 · toggle 2 · RGB data + LED 5 V enable 2 (enable on GPIO46: low at reset) · display SCLK/MOSI/CS/DC/RST/backlight 6 · charger ENB/USB_DET/STAT 3 · battery + dock-5V sense 2 · pogo UART 2 (GPIO43/44 = UART0, so the dock can also reach the ROM bootloader) → **38, 3 spare**. Exact pins at schematic time, chosen for routing.

## 2. Keys, sockets, encoders, toggle

| Part | Source | Price | Note |
|---|---|---|---|
| Razer Yellow (v1 choice) | not sold loose in Turkey; ≈ $25 / 36 abroad | — | user picks switches later |
| Gateron Milky Yellow Pro V2 / Akko linear | Amazon.com.tr | 933 TL / 90; 719–1,109 TL / 45 | local alternatives |
| Kailh CPG151101S11 socket | LCSC C2803348 "not available", -16 variant out of stock; AliExpress ≈ $0.02–0.11; buet.com.tr listing | — | hand-solder (designed for it) |
| PEC11R-4220F-S0024 | e-komponent.com.tr 197.95 TL + VAT incl. customs (DigiKey stock, 7–10 days) | | ALPS EC11K0924404 (LCSC C470743) has 20 detents |
| ON-OFF-ON toggle | Robotistan IC145; generic MTS-103 | | case-mounted |

## 3. RGB

SK6812MINI-E datasheet (rev 04): VDD 3.7–5.5 V (typ 5.2), DIN VIH = 0.7 VDD, 12 mA per channel (≈ 36 mA per LED white), ≈ 1 mA static per LED. Hence a 5 V boost (the 50E sits below 3.7 V most of its discharge), a 5 V-powered level shifter, and a supply cut when the LEDs are off.

| Part | LCSC/JLC | Price, stock |
|---|---|---|
| SK6812MINI-E | C5149201 | $0.081, 90,810 |
| XL-2020RGBC-WS2812B | C5349955 | $0.10, 125,144 (JLC) |
| WS2812B-2020 | C965555 | $0.092, ≈ 10 in stock |
| TPS61023DRLR | C919459 | $0.25, 54,600 |
| XRNR4030-1uH/N (Isat 5.26 A) | C5289359 | JLC |
| SN74AHCT1G125DBVR | C7484 | $0.10 |

All 36 LEDs white ≈ 1.3 A at 5 V. The pad gets ≤ 1.45 A from the dock, so the firmware caps the LEDs at ≈ 0.5 A and selects the ETA6003's lower charge current (0.5 A) while the LEDs are bright.

Key LEDs hand-soldered (≈ 300–330 °C, 2–3 s per leg, moisture-sensitive: keep sealed) instead of JLC double-sided assembly (+$25.56 setup, +$8.21 stencil).

Sources: [LCSC SK6812MINI-E](https://www.lcsc.com/product-detail/C5149201.html), [SK6812MINI-E datasheet](https://akizukidenshi.com/goodsaffix/sk6812mini-e.pdf), [JLCPCB XL-2020RGBC-WS2812B](https://jlcpcb.com/partdetail/Xinglight-XL_2020RGBCWS2812B/C5349955), [WS2812B-2020 datasheet](https://cdn-shop.adafruit.com/product-files/4684/4684_WS2812B-2020_V1.3_EN.pdf), [TPS61023 datasheet](https://www.ti.com/lit/ds/symlink/tps61023.pdf), [LCSC TPS61023](https://www.lcsc.com/product-detail/C919459.html), [JLCPCB XRNR4030-1uH](https://jlcpcb.com/partdetail/XR-XRNR4030_1uHN/C5289359), [LCSC SN74AHCT1G125](https://www.lcsc.com/product-detail/C7484.html), [JLCPCB assembly pricing](https://jlcpcb.com/help/article/pcb-assembly-price), [LCSC CPG151101S11](https://lcsc.com/product-detail/mechanical-keyboard-shaft_kailh-cpg151101s11_C2803348.html), [e-komponent PEC11R](https://www.e-komponent.com/rotary-encoder-mechanical-pec11r-4220f-s0024), [Robotistan IC145](https://www.robotistan.com/ic145-6-feet-toggle-switch-on-off-on), [Amazon.com.tr linear switches](https://www.amazon.com.tr/linear-switch/s?k=linear+switch).
