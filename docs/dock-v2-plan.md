# Dock v2: chips on the board, JLCPCB assembly (study)

Status: **study only**, nothing in the v1 dock design changes. Prices and stock checked on 2026-09-28 through JLCPCB's parts search (the same data as jlcpcb.com/parts), at the 10+ price tier. Quantity for the order: **5 boards, all 5 assembled**, Economic PCBA.

## 1. What changes from v1

| | v1 (now) | v2 (this plan) |
|---|---|---|
| Keyboard host + BLE | Pico 2 W module | RP2354A **A** (PIO-USB host) + ESP32-C3-MINI-1 module (BLE) |
| PC1 endpoint | Pico 2 module | RP2354A **A**, native USB (A does host *and* PC1) |
| PC2 endpoint | Pico 2 module | RP2354A **B**, native USB |
| Power | from the PCs' VBUS (TPS2116 mux) | **own USB-C PD input**: 9 V or 12 V, buck to 5 V, LDO to 3.3 V. The PC ports only *sense* VBUS |
| Assembly | hand-soldered modules and SMD | JLCPCB machine assembly |

Note: v1's rule "no external power adapter for the dock" goes away. The dock then needs a USB-C charger on the desk.

## 2. Choices and why

**USB: 2 × RP2354A.** No cheap chip has three USB controllers; the best have two (CH32V305, APM32F405, CH32V208, CH582). So the minimum is two chips. The RP2354A (RP2350 with 2 MB flash inside, QFN-60) reuses the v1 firmware almost as is: TinyUSB device + Pico-PIO-USB host, which already handles keyboards with built-in hubs. Each chip flashes as a UF2 drive over its own PC's USB port, so no special programmer is needed.

- The cheaper option is CH32V203 (host + PC1) + CH32X035 (PC2). It saves about $2 per board, only about $7 per order after the extra feeder fee, but TinyUSB's CH32 host driver has no hub support yet and needs the WCH toolchain and a WCH-LinkE. Not worth it for 5 boards.
- CH9350L + 2 × CH9329 (the chip set in cheap KVMs): no NKRO, no raw reports, limited media keys, most expensive ($5.5). Ruled out.
- Ground: the two PCs share GND through the dock, exactly as in v1 (and every KVM). Never join the two PCs' VBUS; enable each port's D+ pull-up only while that PC's VBUS is present.

**BLE: ESP32-C3-MINI-1-H4X module.** It is the cheapest pre-certified module with a PCB antenna, so there is no RF tuning. It runs a small NimBLE central and forwards packets to RP2354A **A** over UART. The dock is the central, the pad (Pico 2 W) the peripheral, with a 7.5–15 ms connection interval. Antenna at a board edge with Espressif's copper keep-out. (The WCH CH582/CH592 chips are about $1 and have BLE + USB, but need your own antenna layout and a closed, thinly documented BLE library.)

**Power: CH224A → TPS54331 → AMS1117.**
- The CH224K is discontinued; the **CH224A** is its drop-in replacement. One resistor picks the voltage: 6.8k = 9 V, 24k = 12 V.
- **Ask for 9 V, not 12 V.** 12 V is optional in USB PD. Many chargers (Apple 20 W, most 30–65 W) only give 5/9/15/20 V, and those would drop the dock back to 5 V. 9 V × 2 A is available on every PD charger of 18 W or more.
- **TPS54331** (SOIC-8, no thermal pad, "preferred" part, so no feeder fee): 3 A buck to 5.08 V. On a plain 5 V charger it runs at 100 % duty and passes the input through: about 4.75 V at 2.4 A, still inside USB's limit for the keyboard. At 12 V → 5 V × 2.5 A the IC runs about 47 °C above ambient and the SS54 diode loses about 0.6 W: give both copper.
- The CH224A's **PG** pin goes to an MCU input. If PG says 5 V only, the firmware limits the pad's charging current.
- **AMS1117-3.3** for 3.3 V (two RP2354 + ESP32-C3, radio peaks around 350 mA): about 0.6 W at peak in SOT-223, fine with a copper pad.

## 3. Parts, count and price (5 boards)

Unit price = JLCPCB 10+ tier. "Ext" = Extended part: JLCPCB charges a $3.07 feeder fee per unique Extended part (Economic PCBA). "Preferred" Extended parts are exempt.

| Group | Part | Job | LCSC | Type | Qty/board | Unit $ | $/board | $ for 5 |
|---|---|---|---|---|---|---|---|---|
| USB / MCU | RP2354A (QFN-60, 2 MB flash inside) | MCU A: keyboard host (PIO-USB) + PC1 device; MCU B: PC2 device | C41378174 | Ext | 2 | 1.2732 | 2.546 | 12.73 |
| USB / MCU | X322512MSB4SI | 12 MHz crystal | C9002 | Basic | 2 | 0.0947 | 0.189 | 0.95 |
| USB / MCU | 0402 15 pF C0G | crystal load caps | C1548 | Basic | 4 | 0.0038 | 0.015 | 0.08 |
| USB / MCU | 0402 1 kΩ | crystal series R | C11702 | Basic | 2 | 0.0019 | 0.004 | 0.02 |
| USB / MCU | AOTA-B201610S3R3-101-T | 3.3 µH core-regulator inductor | C42411119 | Ext | 2 | 0.2826 | 0.565 | 2.83 |
| USB / MCU | 0402 100 nF | decoupling | C1525 | Basic | 20 | 0.0045 | 0.090 | 0.45 |
| USB / MCU | 0603 4.7 µF | regulator in/out | C19666 | Basic | 6 | 0.0294 | 0.176 | 0.88 |
| USB / MCU | 0402 22 Ω | USB D+/D− series (3 ports × 2) | C25092 | Basic | 6 | 0.0027 | 0.016 | 0.08 |
| USB / MCU | 0402 10 kΩ | VBUS-sense dividers, pull-ups | C25744 | Basic | 8 | 0.0034 | 0.027 | 0.14 |
| USB / MCU | 0402 5.1 kΩ | CC Rd on the 2 PC ports + power input | C25905 | Basic | 6 | 0.0024 | 0.014 | 0.07 |
| USB / MCU | TS-1187A-B-A-B | BOOTSEL buttons (one per RP2354) | C318884 | Basic | 2 | 0.0205 | 0.041 | 0.21 |
| USB / MCU | USBLC6-2SC6 | ESD, one per USB port | C7519 | Ext | 3 | 0.1765 | 0.529 | 2.65 |
| Connectors | TYPE-C-31-M-12 | USB-C 16P: PC1, PC2, power input | C165948 | Ext | 3 | 0.1855 | 0.556 | 2.78 |
| Connectors | BX-TYPE-A-MCC4P | USB-A female for the keyboard (THT) | C18077685 | Ext | 1 | 0.1452 | 0.145 | 0.73 |
| Switches | SY6280AAC | current-limited switch: keyboard VBUS, pogo 5 V | C55136 | Ext | 2 | 0.0921 | 0.184 | 0.92 |
| BLE | ESP32-C3-MINI-1-H4X | BLE module, PCB antenna, pre-certified | C41349510 | Ext | 1 | 2.5837 | 2.584 | 12.92 |
| BLE | 0603 10 µF | 3V3 bulk | C19702 | Basic | 1 | 0.0319 | 0.032 | 0.16 |
| BLE | 0402 1 µF | EN RC delay | C52923 | Basic | 1 | 0.0099 | 0.010 | 0.05 |
| Power | CH224A | USB-PD sink, CFG resistor picks 9 V or 12 V | C42459160 | Ext | 1 | 0.3573 | 0.357 | 1.79 |
| Power | SMBJ15A | VBUS TVS | C113988 | Ext | 1 | 0.0582 | 0.058 | 0.29 |
| Power | TPS54331DR | 3 A buck → 5 V (SOIC-8, no exposed pad) | C9865 | Ext (preferred) | 1 | 0.3385 | 0.339 | 1.69 |
| Power | SS54 | buck catch diode | C22452 | Basic | 1 | 0.0442 | 0.044 | 0.22 |
| Power | SMDRH105R-6R8NT | 6.8 µH buck inductor | C10167 | Ext | 1 | 0.1829 | 0.183 | 0.91 |
| Power | 1206 22 µF 25 V | buck output | C12891 | Basic | 3 | 0.1755 | 0.526 | 2.63 |
| Power | AMS1117-3.3 | 3.3 V LDO | C6186 | Basic | 1 | 0.2071 | 0.207 | 1.04 |
| Power | 0805 10 µF 25 V | buck input (2) + LDO in/out (2) | C15850 | Basic | 4 | 0.0788 | 0.315 | 1.58 |
| Power | 0603 1 µF | CH224A VHV | C15849 | Basic | 1 | 0.0166 | 0.017 | 0.08 |
| Power | small caps/resistors | buck boot/soft-start/compensation, feedback, CFG, PG | various | Basic | 11 | 0.0050 | 0.055 | 0.28 |
| | | | | | | **per board** | **9.83** | **49.14** |

Not included: the pogo contacts (same part as v1, hand-soldered), the pogo board and the case.

## 4. JLCPCB order total (5 boards, Economic PCBA)

JLCPCB's assembly fees below are from their price page (updated 2026-09-09). PCB fabrication price and shipping to Turkey could not be read from the quote tool: they are estimates. Check them in the real quote.

| Line | How it is counted | $ |
|---|---|---|
| Parts | table above | 49.14 |
| Parts attrition / minimum-quantity buffer | estimate, JLCPCB adds spare parts | ~3.00 |
| PCBA setup | Economic, one side | 8.18 |
| Stencil (inside PCBA) | Economic | 1.53 |
| SMT joints | ≈ 454 per board × 5 × $0.0016 | 3.63 |
| Feeder fee, Extended parts | 10 unique × $3.07 | 30.70 |
| Through-hole soldering | $3.58 + 18 joints × 5 × $0.0164 (USB-C shell pegs, USB-A) | 5.06 |
| PCB, 4-layer, 100 × 80 mm, 5 pcs | not verified (sources say $2–7) | ~7.00 |
| Shipping to Turkey | not verified; your 2-layer dock quote was $17.52 with e-post | ~15.00 |
| **Order total** | | **≈ 123** |
| Monthly $9 SMT coupon (if your account has it) | | −9 |
| **Order total with coupon** | | **≈ 114** |
| **Landed in Turkey** | 60 % flat import tax on non-EU parcels since Feb 2026 (Presidential Decision 10813, €30 exemption removed) | **≈ 180–195** |
| **Per board, landed** | | **≈ $36–39** |

A separate stencil for hand assembly (only if you solder yourself) is "from $3".

### 4b. Cheapest useful order: 5 PCBs, 2 assembled, only the hard parts placed

- JLCPCB assembles **at least 2 boards**, so "1 assembled" isn't possible.
- Leaving out *all* Extended parts doesn't work either: the RP2354A (QFN-60), ESP32-C3-MINI-1 (pads underneath), CH224A (exposed pad), the 0806 core inductor and the USB-C receptacles can't be soldered with an iron. That order would come to about $31–37 before tax, but it would be missing every chip.
- So let JLCPCB place those **5 Extended parts** (plus all Basic parts and the TPS54331, which is Preferred and free), and hand-solder the easy ones: USBLC6 and SY6280 (SOT-23), SMBJ15A, the 10 mm inductor, the USB-A port. Order those from LCSC in the same shipment.

| Line | $ |
|---|---|
| Parts placed by JLCPCB, 2 boards (≈ $8.73 each) | 17.5 |
| Hand-solder parts from LCSC (2 boards + spares) | ~3 |
| Setup + stencil | 9.71 |
| Feeder fee: 5 × $3.07 | 15.35 |
| SMT joints (≈ 2 × 440 × $0.0016) | 1.4 |
| PCB, 5 pcs (2-layer ≈ $2, 4-layer ≈ $7, not verified) | 2–7 |
| Shipping (not verified) | ~15 |
| **Total** | **≈ $64–69** |
| **Landed in Turkey (× 1.6)** | **≈ $105–115**, about $55 per working dock, plus 3 bare PCBs |

For comparison, the v1 dock BOM (hardware/dock/BOM.xlsx) is 3500 TL ≈ $72 for one dock.

### 4c. No assembly: PCBs + stencil from JLCPCB, all parts from LCSC, you solder

LCSC prices checked on 2026-09-29 with LCSC's minimum-buy quantities (0402/0603 passives come in 100s or 20s–50s), and one spare for each fine-pitch chip.

| Line | 2 docks | 5 docks |
|---|---|---|
| Parts from LCSC | 35.4 | 64.0 |
| Small compensation/feedback values not in the table | ~2 | ~2 |
| PCB, 5 pcs (2-layer ≈ $2, 4-layer ≈ $7, not verified) | 2–7 | 2–7 |
| Stencil, frameless (JLCPCB "from $3", often ≈ $7) | ~7 | ~7 |
| JLCPCB shipping (not verified) | ~15 | ~15 |
| LCSC shipping, a second parcel (not verified) | ~15 | ~15 |
| **Total before tax** | **≈ $76–81** | **≈ $105–110** |
| **Landed in Turkey (× 1.6)** | **≈ $120–130**, ≈ $62 per dock | **≈ $170–176**, ≈ $35 per dock |

- Not cheaper than 4b: LCSC charges a bit more for the ESP32 module ($2.94 vs $2.58), the minimum-buy lots add up, and the parts come in a second parcel with its own shipping and 60 % tax.
- You need a reflow method for the RP2354A (QFN-60), the ESP32 module and the CH224A: a hot plate or hot air, plus solder paste. Neither is in the totals.
- For hand assembly, switch the passives from 0402 to 0603 or 0805.
- LCSC shows 0 stock today for C11702 (1 k 0402), C52923 (1 µF 0402), C12891 (22 µF 1206) and C15849 (1 µF 0603). Any equivalent part works; the price is about the same.

## 5. Ways to lower it

1. **Feeder fees are the biggest lever** ($30.70). Every Extended part you remove or swap for a Basic/Preferred one saves $3.07. Candidates:
   - Hand-solder the USB-A (through-hole): saves the $3.07 feeder fee and some through-hole fee.
   - Find Basic replacements for the TVS and the 6.8 µH inductor.
2. Assemble 2 of the 5 boards: the fees barely change (about $2 less), but the parts cost drops to 2/5.
3. 2-layer instead of 4-layer: saves a few dollars; the RP2354A QFN-60 and three USB pairs route more easily on 4 layers.

## 6. Not verified

- PCB fab price (2-layer vs 4-layer, HASL vs ENIG) and shipping cost to Turkey: check at cart.jlcpcb.com/quote.
- What the CH224A does when the charger lacks the requested voltage (community sources say it stays at 5 V with PG high): test on the bench.
- Whether the monthly coupon is on your account.
- Crystal load capacitors: check against the RP2350 hardware design guide.

Sources: JLCPCB parts search API; jlcpcb.com/help/article/pcb-assembly-price; jlcpcb.com/capabilities/pcb-assembly-capabilities; LCSC product pages for every part number above; WCH CH224A datasheet; TI TPS54331 datasheet; TinyUSB and Pico-PIO-USB repositories; webrazzi.com / hurriyet.com.tr (Turkey customs, Jan 2026).
