# Dock v2: MCU support circuit and chip-to-chip links (research)

**Decisions (2026-09-29):**
- Crystal: **ABM8-272-T3** (C20625731) on both RP2354A, with RPi's 15 pF + 1 kΩ circuit. The v2 plan's X322512MSB4SI is dropped.
- **A→B SWD link included** (A can reflash and recover B).
- Buttons: **BOOTSEL A, BOOTSEL B, RESET A** (3 × TS-1187A, Basic).

Date: 2026-09-29. Sources: Raspberry Pi *Hardware design with RP2350* (release 3, 2026-08) and its **RP2350A Minimal KiCad design** (netlist read directly), RP2350 datasheet, ESP32-C3-MINI-1 datasheet v2.2, JLCPCB parts search. "Ext" = Extended ($3.07 feeder fee per unique part), "Basic" = no fee.

```text
                         ┌───────────── UART0 (1 Mbaud+) ─────────────┐
 PC1 USB ═══ RP2354A **A** ◄──── RUN, BOOTSEL, SWD (A can reset/flash B) ──► RP2354A **B** ═══ PC2 USB
 keyboard ═ (PIO-USB)  │  └── UART1 + EN + GPIO9 ──► ESP32-C3-MINI-1 (BLE to pad)
                       ├── I2C ── CH224A          ├── ADC ×4 (KBD CC1/CC2, KBD_VBUS, POGO_5V)
                       └── pogo: DET, POGO_OFF, PIO UART
```

## 1. Each RP2354A: parts around the chip

Copied from Raspberry Pi's Minimal design (the RP2354A is the RP2350A with 2 MB flash inside, so the external flash U3 and its resistors are left out):

| Function | Parts (per chip) | JLCPCB | Notes |
|---|---|---|---|
| Core regulator (1.1 V, on-chip switcher) | L1 **3.3 µH AOTA-B201610S3R3-101-T** (0806); C6 4.7 µF on VREG_VIN; C7 4.7 µF on the 1.1 V output | L1 C42411119 Ext $0.28; 4.7 µF 0402 **C23733 Basic** | RPi: *"if you choose not to use our example, you do so at your own risk"*. The inductor has a polarity dot and must face the right way. **Copy their layout from the Minimal KiCad files** (downloaded, same QFN-60) |
| VREG_AVDD filter | 33 Ω + 4.7 µF | Basic (C25105, C23733) | the regulator's analogue supply is noise-sensitive |
| DVDD (1.1 V) pins 6, 23, 39 | 100 nF each | Basic C1525 | |
| IOVDD ×6, ADC_AVDD, USB_OTP_VDD, QSPI_IOVDD | 100 nF each (pins 53/54 share one in RPi's layout) + 10 µF bulk | Basic | all on 3.3 V |
| Crystal | **ABM8-272-T3** 12 MHz, 10 pF, 50 Ω; 15 pF ×2 to GND; **1 kΩ** in series on XOUT | ABM8 **C20625731 Ext $0.62**, 15 pF C1548 Basic, 1 k Basic | see §2 |
| RUN | nothing required: RUN has an internal pull-up | — | chip B's RUN goes to chip A (§3) |
| BOOTSEL | button from QSPI_SS **through 1 kΩ** to GND | TS-1187A (C318884) Basic | the 1 k lets QSPI_SS overdrive it while booting |
| USB | 22 Ω series ×2, close to the chip | Basic | decided in the USB doc (RPi's reference uses 27 Ω) |

Per chip: ≈ 11 × 100 nF, 3 × 4.7 µF, 1 × 10 µF, 33 Ω, 1 k ×2, 15 pF ×2, crystal, inductor, button. All Basic except the **inductor** and the **crystal**.

## 2. Crystal: change from the v2 plan

The v2 plan listed **X322512MSB4SI** (C9002, Basic, $0.09). It doesn't match what Raspberry Pi designed the oscillator for:

| | RPi-recommended ABM8-272-T3 | X322512MSB4SI (v2 plan) |
|---|---|---|
| Load capacitance | **10 pF** (15 pF ×2 + ≈ 3 pF stray ≈ 10.5 pF) | 20 pF (needs ≈ 33 pF caps) |
| Max ESR | **50 Ω** | 80 Ω |
| JLCPCB | C20625731, Ext, $0.62, 15 k in stock | C9002, Basic, $0.09 |

RPi's guide: the 1 kΩ damping resistor and 15 pF caps are tuned for *that* crystal at 3.3 V, and *"any deviation … will require extensive testing to ensure that the crystal oscillates under all conditions."* An 80 Ω crystal behind a 1 kΩ resistor has less start-up margin. USB itself would tolerate the frequency error; the risk is a crystal that sometimes fails to start.

**Recommendation: ABM8-272-T3.** Cost: one feeder fee + ≈ $1.06 per dock (2 crystals).

## 3. Chip A ↔ chip B

| Signal | A side | B side | Why |
|---|---|---|---|
| UART0 TX/RX | hardware UART0 | hardware UART0 | HID reports, 1 Mbaud or faster (v1 framing: SOF/TYPE/SEQ/LEN/PAYLOAD/CRC) |
| B_RUN | GPIO, open-drain | RUN + **10 k pull-up** | A can reset B. The external pull-up beats A's reset-state pull-down; without it B could stay in reset whenever A restarts |
| B_BOOTSEL | GPIO, open-drain, via 1 kΩ, **10 k pull-up** | QSPI_SS | A holds it low while pulsing B_RUN → B restarts in **BOOTSEL** mode and shows up as a UF2 drive on the Work PC |
| B_SWCLK / B_SWDIO | 2 GPIOs (PIO) | SWD pins | **A can reflash B over SWD** (Raspberry Pi's debugprobe firmware does this on an RP2040/RP2350). Updating everything from the Personal PC then becomes possible, and it's the recovery path if B's firmware is broken |

Flashing summary:
- **A:** BOOTSEL button (or firmware "reboot to BOOTSEL") → UF2 drive on the **Personal PC**.
- **B:** its own BOOTSEL button → UF2 on the **Work PC**; or from A: BOOTSEL via B_BOOTSEL/B_RUN, or directly over SWD.
- SWD test pads for both A and B on the board as well (3 pads each: SWCLK, SWDIO, GND), for a Debug Probe during development.

## 4. ESP32-C3-MINI-1 (BLE)

| Pin | Connection | Why (datasheet) |
|---|---|---|
| 3V3 | 3.3 V + 10 µF + 100 nF | BLE TX peaks: 170 mA at 0 dBm, 340 mA at +20 dBm |
| EN | 10 kΩ to 3.3 V + 1 µF to GND, **and** chip A GPIO (open-drain) | Espressif's recommended RC delay; A can reset the C3. "Do not leave EN floating" |
| GPIO9 (BOOT) | chip A GPIO (open-drain) + **10 k pull-up** | low at reset = download mode. A can put the C3 into download mode; the pull-up stops A's reset-state pull-down doing it by accident |
| GPIO8 | 10 kΩ pull-up | must be 1 for UART download mode |
| GPIO2 | 10 kΩ pull-up | Espressif recommends it high (glitches) |
| TXD0/RXD0 (GPIO21/20) | chip A UART1 | normal data link **and** the download port |
| GPIO18/19 (USB D−/D+) | test pads | direct USB flashing during development (C3 built-in USB-Serial/JTAG) |

- **Flashing the C3 through A:** A drives EN and GPIO9 and passes esptool's serial traffic from the Personal PC (USB CDC) to UART0. That's the same thing a USB-serial adapter does, so no extra connector is needed. The GPIO18/19 pads are the fallback.
- **Antenna:** module at a **board edge**, antenna end outward (ideally the antenna part hangs just past the edge), **no copper on any layer** and no parts under or near the antenna area, per Espressif's *Hardware Design Guidelines, General Principles of PCB Layout for Modules*. Keep the pogo magnets and any metal enclosure parts away from that end.
- The ESP32-C3-MINI-1 is MSL 3: JLCPCB handles it (it's one of the parts they must place anyway).

## 5. Chip A pin budget (RP2354A: GPIO0–29, ADC on 26–29 only)

**Final pin maps (GPIO numbers, pins, nets) for A and B: [hardware/dock-v2/DOCK_CONNECTIONS.md](../hardware/dock-v2/DOCK_CONNECTIONS.md) §5–6.** Added there: 10 k pull-ups on B_RUN, B_BOOTSEL and the ESP32's GPIO9, and a second 2N7002 for POGO_OFF, because A's pins default to weak pull-downs at reset.

| Function | GPIOs |
|---|---|
| PIO-USB host (keyboard D+/D−, adjacent) | 2 |
| UART0 ↔ B | 2 |
| UART1 ↔ ESP32-C3 | 2 |
| C3 EN, C3 GPIO9 | 2 |
| B RUN, B BOOTSEL, B SWCLK, B SWDIO | 4 |
| CH224A I2C SDA/SCL, CH224A PG | 3 |
| Keyboard VBUS EN | 1 |
| ADC: KBD CC1, KBD CC2, KBD_VBUS, POGO_5V | 4 (GPIO26–29) |
| Pogo DET, POGO_OFF, pogo UART TX/RX (PIO) | 4 |
| PC1 VBUS sense | 1 |
| Status LED | 1 |
| **Total** | **26 of 30** (4 spare) |

- PIO use: PIO-USB (1 block), pogo UART (2 state machines), SWD to B (1 state machine). RP2354A has 3 blocks × 4 state machines: fits.
- PIO-USB needs a system clock that is a multiple of 12 MHz (120, 144, 240 MHz).
- The exact GPIO numbers come at schematic time: hardware UART TX/RX only exist on certain pins (e.g. UART0 TX on GPIO0/12/16/28…, UART1 TX on GPIO4/8/20/24…).

Chip B: native USB, UART0 ↔ A (2), PC2 VBUS sense (1), status LED (1). Everything else is free.

## 6. 3.3 V budget (AMS1117, see power doc)

2 × RP2354A ≈ 2 × 30–40 mA + ESP32-C3 BLE peak 170 mA (0 dBm; 340 mA only at +20 dBm) + LEDs ≈ **0.25–0.45 A peak**: inside the AMS1117's 1 A and the 0.4 A the power budget assumed. Firmware should keep the C3 at ≤ +9 dBm (190 mA): the pad sits right next to the dock.

## 7. Feeder-fee summary for this block

| Part | Type | Qty/dock |
|---|---|---|
| RP2354A (C41378174) | Ext | 2 |
| AOTA-B201610S3R3-101-T (C42411119) | Ext | 2 |
| ABM8-272-T3 (C20625731) | Ext | 2 |
| ESP32-C3-MINI-1-H4X (C41349510) | Ext | 1 |
| Everything else (100 nF, 4.7 µF, 10 µF, 15 pF, 33 Ω, 1 k, 10 k, buttons) | Basic | — |

## 8. Decided

1. Crystal: ABM8-272-T3.
2. A→B SWD link: included.
3. Buttons: BOOTSEL A, BOOTSEL B, RESET A.

## 9. Not verified

- Current draw of the RP2354A at 240 MHz with PIO-USB running (datasheet typical ≈ 30–40 mA at 150 MHz).
- Exact antenna keep-out dimensions: take them from Espressif's hardware design guidelines when placing the module.

Sources: [Hardware design with RP2350](https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf), [RP2350A Minimal KiCad design](https://datasheets.raspberrypi.com/rp2350/Minimal-KiCAD.zip), [RP2350 datasheet](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf), [ESP32-C3-MINI-1 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf), [Raspberry Pi debugprobe](https://github.com/raspberrypi/debugprobe), JLCPCB parts search.
