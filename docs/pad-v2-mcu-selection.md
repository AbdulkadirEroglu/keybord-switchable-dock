# Pad v2: MCU and BLE selection (research)

**Decision (2026-10-04): ESP32-S3-MINI-1-N8, assembled by JLCPCB.** The socketed Pico 2 WH of the v1 plan and the TCA9555 expander are dropped.

Date: 2026-10-04. Prices: LCSC, 1-piece tier, checked today. Turkish prices include VAT.

## 0. What changed since v1

The v1 pad was planned around hand soldering (socketed Pico 2 WH, no QFN parts). The dock moved to JLCPCB assembly in v2; doing the same for the pad removes the package limits and the socket.

## 1. What the pad needs

About 30 GPIO: 12 keys, 2 encoders with push switches, the PERSONAL/OFF/WORK toggle, RGB data, display SPI + backlight, charger control/status, battery measurement, pogo UART and DET. BLE peripheral to the dock's ESP32-C3 (central).

## 2. Options

| Option | Free GPIO | LCSC (1 pc) | Turkey | Notes |
|---|---|---|---|---|
| **ESP32-S3-MINI-1-N8** | ~36 | $4.76, 6,222 in stock | bare module: not found; dev boards: Robotistan 539 TL, Direnc 610 TL | all signals direct, no expander; native USB; same Espressif BLE stack and toolchain as the dock's ESP32-C3 |
| ESP32-C3-MINI-1 (the dock's chip) | ~15 | ~$3.7 | Özdisan 182 TL (373 in stock), Robotistan, Direnc | needs the TCA9555 back |
| ESP32-C6-MINI-1-N4 | ~22 | $3.92, 326 in stock | not found | needs an expander; thin stock |
| nRF52840 module (MS88SF2, Ebyte E73) | ~20 (MS88SF2 datasheet) | ≈ $3–6 at JLCPCB (Extended) | XIAO nRF52840 boards only (Robotistan, Direnc) | best battery life; new toolchain (Zephyr / nRF Connect); needs an expander |
| Raspberry Pi Pico 2 W (v1 plan) | 26 | — | Robotistan 461 TL | hand-solderable; CYW43 BLE stack least mature; needs the expander |

## 3. Power

Measured light sleep (Qoitech): ESP32-S3 0.69 mA, C3 0.19 mA, C6 0.22 mA; nRF52840 far lower. Estimated S3 idle with the BLE link kept: 5–10 mA. Since the pad sits on the dock and charges most of the time, this is acceptable (see pad-v2-battery-charging.md).

Sources: [LCSC ESP32-S3-MINI-1-N8](https://www.lcsc.com/product-detail/C2913206.html), [LCSC ESP32-C6-MINI-1-N4](https://www.lcsc.com/product-detail/C5736265.html), [Özdisan ESP32-C3-MINI-1-N4](https://www.ozdisan.com/en/p/wifi-modules-652/espressif-systems-esp32-c3-mini-1-n4-1077480), [Robotistan ESP32-S3 Mini](https://www.robotistan.com/esp32-s3-mini-wifi-and-bluetooth-development-board-en), [Robotistan Pico 2 W](https://www.robotistan.com/raspberry-pi-pico-2wifi), [JLCPCB MS88SF2](https://jlcpcb.com/partdetail/Minew-MS88SF2nRF52840/C20616655), [Minew MS88SF2 datasheet](https://en.minewsemi.com/file/MS88SF2-nRF52840_Datasheet_K_EN.pdf), [Qoitech sleep measurements](https://www.qoitech.com/blog/esp32-s3-c3-c6-sleep-power-consumption/).
