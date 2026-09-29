# Dock v2: MCU selection (research)

**Decision (2026-09-29): option 1, 2 × RP2354A + ESP32-C3-MINI-1.** CH32H417 set aside for now (unfamiliar WCH toolchain).

Date: 2026-09-29. Prices: JLCPCB parts search, 10+ tier, checked today. "Ext" = Extended part, $3.07 feeder fee per unique part.

## 0. What the dock actually needs

Three USB ports, but not three hosts:

| Port | Role | Speed needed |
|---|---|---|
| Keyboard | **host** (dock powers and reads the keyboard) | low/full speed; must handle keyboards with a built-in hub |
| Personal PC | **device** (dock looks like a keyboard) | full speed |
| Work PC | **device** | full speed |

So we need **three separate USB controllers, at least two of them able to act as a device**. A USB hub chip can't help here: a hub gives more host ports, never a second device port. Two PCs means two separate device controllers.

## 1. Single chips with three USB controllers

Searched: WCH, Espressif, Raspberry Pi, ST, NXP, Nordic, Renesas, Artery, GigaDevice, Microchip.

| Chip | USB controllers | Usable for the dock? | BLE | JLCPCB price | Turkey |
|---|---|---|---|---|---|
| **WCH CH32H417** | USB-FS OTG + USB-HS (480M, host/device) + **USB3 SuperSpeed** (host/device) | **No, only 2 usable.** The USB3 controller has only the SuperSpeed PHY (SSTX/SSRX); it doesn't fall back to USB 2.0. A PC on a USB 2.0 port or a USB-2-only USB-C cable would never see it. | no | $2.82 (QFN-68) – $4.58 (QFN-88) | no seller found |
| **Raspberry Pi RP2350 / RP2354** | 1 native (host/device) + PIO-USB software ports | **Not today.** Pico-PIO-USB has a single PIO port engine (`pio_port[1]` in `pio_usb.c`): one PIO port runs as host *or* device, not both. One chip = native device + PIO host (that's v2's chip A). A third port would need a rewrite of the library. | no | RP2354A $1.27 | RP2350A: Robotistan 66.83 TL incl. VAT (out of stock today); RP2354: not found |
| ESP32-P4 | USB-HS OTG + USB-FS OTG + USB-Serial/JTAG | No: Serial/JTAG is fixed-function (can't be a HID device). 2 usable. | no (needs a companion radio) | not stocked at JLCPCB | — |
| ESP32-S31 (new, 2026) | USB-HS OTG + USB-Serial/JTAG | 1 usable | BLE 5.4 | sampling | — |
| STM32 F4/F7/H7, GD32F4, AT32F4, NXP RT10xx/RT11xx/LPC55/MCX-N, Renesas RA6/RA8, CH32V305/307 | 2 × OTG (one HS, one FS) | 2 usable | no | CH32V305 $1.61–1.88 | CH32V307 dev board on direnc.net |

**Conclusion: no practical single chip has three USB 2.0 controllers.** The best chips have two. That is why every option below uses two chips.

(Linux application processors such as RK3588 have several USB OTG controllers, but they need DDR memory, a PMIC and an OS. That's far outside this project.)

## 2. Two-chip combinations

Chip **A** runs the keyboard host + Personal PC device (+ BLE if it has it). Chip **B** runs the Work PC device only. A and B talk over UART, like v1.

Parts with two USB controllers **and BLE** on one chip exist, and they are cheap:

| Chip | USB | BLE | RAM | JLCPCB | Stock | Notes |
|---|---|---|---|---|---|---|
| **CH32V208** (WBU6 QFN-68 / CBU6 QFN-48 / GBU6 QFN-28) | USBD (device only, PA11/12) + USBFS (host/device, PB6/7) | 5.3 | 64 KB | $1.10–1.57 | 523 / 697 / 40 | WCH says "a CH32V203 with the CH582's BLE". WCH's USB host example (`HOST_KM`) **includes hub support** (`usb_host_hub.c`). |
| **CH582F** (QFN-28) / CH582M (QFN-48) | 2 × USB-FS host/device (both pinned out even on QFN-28) | 5.3 | 32 KB | $0.95 | 1851 / 0 | WCH's CH58x host library has **no hub support**; keyboards with a hub inside would need our own driver. Widely used in wireless keyboards; QMK port exists. |
| **CH585M** (QFN-48) | USB-HS (480M) + USB-FS, both host/device | 5.4 | 128 KB | $0.81 | 498 | Newest, cheapest, most RAM. Least community code. |

All three WCH radios need their own antenna: a PCB or chip antenna with a matching network, copied from WCH's reference design. There's no pre-certified module on JLCPCB (CH582F modules show 0 stock). They also need a 32 MHz crystal (plus 32.768 kHz for low power; optional here).

### Candidate combinations

Per-dock chip cost and feeder-fee count for the MCU/BLE parts only (support parts are similar across options).

| # | Chip A (host + PC1) | Chip B (PC2) | BLE | Chips $/dock | Unique Ext parts | Firmware | Risk |
|---|---|---|---|---|---|---|---|
| **1** | RP2354A | RP2354A | ESP32-C3-MINI-1 module (UART to A) | 1.27×2 + 2.58 = **5.13** | 3 (RP2354A, ESP32-C3, 3.3 µH core inductor) | TinyUSB + Pico-PIO-USB (hub support, used by v1 plan), NimBLE on the C3. UF2 flashing over each PC's USB, no programmer. Three firmware images. | **Lowest.** Pre-certified radio, best-documented USB stack. |
| **2** | CH32V208 | CH32V208 (BLE unused) | integrated in A | 1.25×2 = **2.50** | 1 | WCH EVT: USBFS host with hub + USBD device + BLE HID/GATT examples. One chip type. Flashing: WCH-LinkE ($5–8) or the built-in USB ISP bootloader (BOOT0 + `wchisp`). | Medium: own antenna layout, WCH toolchain, host stack from WCH examples (not TinyUSB). |
| 3 | CH32V208 | CH32X035 | integrated in A | 1.25 + 0.42 = **1.67** | 2 | As #2; X035 is a cheap USB device chip (TinyUSB device driver, partial). | As #2, plus a second toolchain target. At 2 boards, #2 is cheaper (one feeder fee less: 2×0.83 < $3.07). |
| 4 | CH582F | CH582F | integrated in A | 0.95×2 = **1.90** | 1 | WCH CH58x SDK. | Medium-high: **no hub support** in the host library, 32 KB RAM. |
| 5 | CH585M | CH585M or CH32X035 | integrated in A | 0.81×2 = **1.62** | 1 | WCH CH585 SDK (new). | High: newest chip, thinnest community support. |
| 6 | ESP32-S3 module (OTG host + BLE) | 2 × CH32X035 or 2 × RP2354A | integrated in A | 4.14 + 0.84 = **~5.0** | 2–3 | ESP-IDF USB host (hubs supported), TinyUSB on the device chips. **Three chips again**, like v1. | Low, but no cheaper than #1 and the S3 only does the host. |
| — | CH32H417 | any 1 more USB device chip | separate module | 2.82 + … | 3+ | USBFS host + USBHS device; the USB3 port is wasted. | Not worth it: expensive, needs a 1.2 V rail, no BLE. |

What each saving is worth (2 assembled boards, like v2 plan §4b): #2 vs #1 is about (5.13 − 2.50) × 2 + 2 feeder fees ≈ **$11.40 before tax, ≈ $18 landed**. It also removes the ESP32 module (13 × 17 mm) and one UART link.

## 3. Availability in Turkey (bonus)

| Part family | Turkish seller found | Status 2026-09-29 |
|---|---|---|
| RP2350A chip | Robotistan (55.69 TL + VAT) | listed, out of stock |
| RP2354A/B chip | none (The Pi Hut UK has it) | — |
| Espressif modules | **Empa Elektronik** (İstanbul, official Espressif distributor; sells to individuals): ESP32-C3-MINI-1-N4 $2.40 + VAT. **Özdisan**: ESP32-S3-WROOM-1 modules | C3 out of stock at Empa |
| WCH (CH32V208, CH582, CH585, CH32X035) | none; direnc.net has only a CH32V307 dev board | LCSC / JLCPCB / AliExpress only |
| Nordic nRF52840 | Özdisan (dev kits) | — |

Since the chips will be placed by JLCPCB anyway, local stock only matters for spares and dev boards.

## 4. Recommendation

- **Keep option 1 (2 × RP2354A + ESP32-C3-MINI-1) as the baseline.** It's the lowest-risk path: pre-certified radio, TinyUSB + PIO-USB with hub support, UF2 flashing with no programmer.
- **Option 2 (2 × CH32V208) is the one worth a prototype if integrated BLE matters.** It is the only cheap BLE chip whose vendor host stack already handles hubs. It saves ≈ $18 per 2-dock order and one module, at the cost of an antenna layout, the WCH toolchain and a WCH-LinkE.
- Suggested de-risking before committing to #2: buy a CH32V208 dev board (AliExpress, ≈ $5–8). Check (a) the `HOST_KM` example with your actual keyboard, (b) USBD as a HID device on a PC, (c) BLE link to the pad, all at once.
- Options 4 and 5 are cheaper on paper, but CH582 has no hub support and CH585 is too new. Revisit only if #2 fails.

## 5. Not verified

- CH32V208: running BLE + USBFS host + USBD device all at once (RAM and CPU are shared; WCH has no example that combines all three).
- NKRO / large keyboard reports through the WCH host example (it's written for boot-protocol keyboards and mice).
- Whether the pad (Pico 2 W today) should change too: if the dock uses WCH BLE, the pad side is unaffected, since BLE is BLE.

Sources: [CH32H417 datasheet](https://ch32-riscv-ug.github.io/CH32H417/datasheet_en/CH32H417DS0.PDF), [CNX on CH32H417](https://www.cnx-software.com/2026/01/03/wch-ch32h417-dual-core-risc-v-mcu-offers-usb-3-0-500mb-s-uhsif-and-fast-ethernet-interfaces/), [CH32V208 datasheet](https://static.chipdip.ru/lib/423/DOC050423417.pdf), [CH582 datasheet (LCSC)](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2403131113_WCH-Jiangsu-Qin-Heng-CH582F_C3001175.pdf), [openwch/ch585](https://github.com/openwch/ch585), [openwch/ch32v20x EVT](https://github.com/openwch/ch32v20x), [openwch/ch583 EVT](https://github.com/openwch/ch583), [Pico-PIO-USB](https://github.com/sekigon-gonnoc/Pico-PIO-USB), [TinyUSB supported MCUs](https://github.com/hathach/tinyusb), [Espressif USB overview](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_overview.html), [ESP32-P4 USB host](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/peripherals/usb_host.html), [ESP32-S31](https://www.cnx-software.com/2026/03/24/esp32-s31-dual-core-risc-v-mcu-offers-gigabit-ethernet-wifi-bluetooth-and-802-15-4-connectivity/), [Robotistan RP2350A](https://www.robotistan.com/raspberry-pi-rp2350a-microcontroller-en), [Empa ESP32-C3-MINI-1](https://empa.com/wi-fi-ble-module-esp32-c3-mini-1-n4-espressif-en), [Özdisan](https://www.ozdisan.com/en/ps/wifi-modules-652).
