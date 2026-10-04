# Pad v2: display (research)

**Decision (2026-10-04): 1.69" 240×280 ST7789V3 IPS module from Meon Otomasyon ($5 + VAT, ≈ 272 TL), mounted to the case behind its window, 9-pin JST-PH cable (8 signals + second GND) to the main PCB. Power switched by an AO3401 P-MOSFET (JLC Basic). Backlight dimmed by PWM straight into the module's BLK pin (the module has its own backlight transistor).**

Date: 2026-10-04.

## 1. Options

| Option | Size | Turkey | Notes |
|---|---|---|---|
| **1.69" 240×280 ST7789V3 module** | Waveshare's equivalent: 31.5 × 39.0 mm board, 27.97 × 32.63 mm active area | **Meon Otomasyon $5 + VAT (≈ 272 TL)**; SAMM 9.64 € (out of stock) | SPI, 8-pin header, 3.3/5 V, Waveshare's ≤ 90 mA at 3.3 V |
| 1.9" 170×320 ST7789 | — | Hepsiburada (import only) | narrower |
| 2.0" 240×320 IPS | ~ 34 × 48 mm | Robotistan (Waveshare) 700 TL, out of stock; Motorobit | too wide for the ≈ 100 mm top row |
| Bare 1.69" FPC panel on the main PCB | panel only | BuyDisplay $3.74, AliExpress (import) | needs FPC connector + backlight driver; sits at PCB height, not flush with the case window |

## 2. The module (photo of the back, "1.69"TFT V1.1, IC: ST7789V3")

- Header order: **BLK CS DC RES SDA SCL VCC GND**; four corner mounting holes.
- **U6 (SOT-89)**: regulator for VCC (hence "3.3 V / 5 V").
- **U5 (SOT-23)**: backlight switch between the BLK pin and the panel's LED (the FPC's A/K pins); BLK is a logic input. Check on delivery: with the backlight on, BLK should draw ≪ 1 mA (a direct LED feed would draw ≈ 20 mA).

## 3. Circuit

- VCC from the 3.3 V rail through an **AO3401** high-side switch (gate pull-up, GPIO pulls it low to switch on): the module draws nothing while the pad sleeps. Uses one of the three spare GPIOs (two left).
- **Firmware rule:** drive SCL/SDA/CS/DC/RES/BLK low before switching VCC off, so the outputs don't back-feed the unpowered module through its input clamps.
- BLK: ESP32-S3 LEDC PWM directly; no MOSFET on the main PCB.

Sources: [Meon Otomasyon 1.69" ST7789V3](https://www.meonotomasyon.com/urun/tft-lcd-1-69-inc-240x280-st7789-v3-spi-display-modulu), [SAMM 1.69"](https://market.samm.com/169-lcd-ekran-modulu-240x280), [Waveshare 1.69inch LCD wiki](https://www.waveshare.com/wiki/1.69inch_LCD_Module), [Robotistan 2"](https://www.robotistan.com/2-inc-lcd-display-module), [BuyDisplay FPC panel](https://www.buydisplay.com/1-69-inch-240x280-round-rectangle-ips-tft-lcd-screen-soldering-fpc).
