# Dock v2: power input (research)

**Decision (2026-09-29): option C, no PC-power fallback.** CH224A (9 V, I2C to RP2354A A) → TPS54331 → 5 V → AMS1117 → 3.3 V. The dock runs from a 30 W USB-C PD charger (9 V × 3 A = 27 W available). The charger only goes off in a power cut, when the PCs are off too, so a fallback adds nothing.

Date: 2026-09-29. Prices: JLCPCB parts search, 10+ tier. "Ext" = Extended part ($3.07 feeder fee each), "Pref" = Preferred Extended (no fee), "Basic" = no fee.

## 1. Power budget (5 V rail)

| Load | Typical | Worst case | Notes |
|---|---|---|---|
| Keyboard (USB-C, via current-limited switch) | 0.1–0.15 A | 1.0 A | current keyboard is rated 200 mA; the 1 A limit leaves room for a brighter keyboard later |
| Pogo → pad (TP4056 charging + pad system while docked) | 0.6 A | 1.0 A | pad fast charge 510 mA + Pico/BLE/display + RGB; dock switch limits at ≈ 1 A |
| 3.3 V rail via LDO (2 × RP2354A + ESP32-C3) | 0.15 A | 0.4 A | ESP32-C3 radio peaks ≈ 350 mA |
| **Total** | **≈ 0.9 A (4.5 W)** | **≈ 2.4 A (12 W)** | |

So the dock needs **≈ 12 W worst case**. From a 9 V input through a ≈ 90 % buck that is ≈ 1.5 A at 9 V, which any 18 W or larger PD charger gives.

## 2. Ways to power the dock

| | Option | What it takes | Good | Bad |
|---|---|---|---|---|
| A | **From the PCs** (v1) | TPS2116 mux of the two PCs' VBUS | no charger, one cable less | a USB-A PC port gives 0.5 A (USB 2) / 0.9 A (USB 3): not enough for keyboard + pad charging; must read each port's CC advertisement and throttle |
| B | **USB-C 5 V only, no PD** | power USB-C + 2 × 5.1 kΩ Rd, CC read by ADC | cheapest, no negotiation chip | 5 V/3 A only if the charger advertises it (many do, not guaranteed; a USB-A-to-C cable gives "default", i.e. unknown). No regulation: at 2.4 A the cable drop leaves ≈ 4.5–4.7 V, then the keyboard switch drops more |
| C | **USB-PD 9 V + buck to 5 V** (v2 plan) | CH224A + TPS54331 + LDO | regulated 5.0 V to the keyboard and pad no matter the cable; low current in the cable | needs a PD charger (≥ 18 W) for full function; ≈ $1.3 of parts |
| D | C **plus** fallback to PC power | C + a power mux (TPS2116) from the PCs | works with no charger at all | more parts and more cases to test; back-feed rules from v1 come back |

### Why 9 V is the right request

The USB PD spec's power rules make **9 V mandatory on every PD source above 15 W** (sources above 27 W must add 15 V, above 45 W also 20 V). **12 V is optional** and many chargers skip it (Apple 20 W, most 30–65 W laptop chargers). A 9 V request therefore works with every PD charger of 18 W or more.

### What happens on a charger without PD

- The CH224A stays at 5 V (PD handshake fails, or it gets 5 V via BC1.2).
- **TPS54331 keeps working below its set point:** its datasheet (§7.3.3) says it runs at **100 % duty** while the boot capacitor stays charged, so it passes the 5 V input through (≈ 4.7 V after the high-side FET and inductor at 2 A). Most synchronous SOT-23 bucks (TPS563201, SY8120…) can't do this; they top out around 80–90 % duty and would give ≈ 4 V. This is the main reason to keep the TPS54331 even though it needs a diode.
- Firmware sees 5 V (via I2C or PG, below) and limits pad charging to the slow 146 mA setting.

## 3. PD sink chip choice

| Chip | Package | Config | Talks to MCU | JLCPCB $ | Stock | Type |
|---|---|---|---|---|---|---|
| **CH224A** | ESSOP-10 (exposed pad) | 1 resistor (6.8 k = 9 V) or I/O pins or **I2C** | **I2C (0x22/0x23):** protocol status (PD/QC/BC), requested voltage, max current of the current PD profile; PG pin | 0.36 | 18 394 | Ext |
| HUSB238 | DFN-10 3×3 | resistors or I2C | I2C | 0.47 | 8 650 | Ext |
| CYPD3177 | QFN-24 | resistors | none (Infineon EZ-PD BCR) | 1.10 | 659 | Ext |
| STUSB4500 | QFN-24 | NVM (programmed over I2C) | I2C | 2.27 | 5 892 | Ext |
| AP33772S | QFN-24 | I2C only (PPS/AVS) | I2C | 3.26 | 31 | Ext |
| IP2721 | TSSOP-16 | pins | none | 0.63 | 5 | Ext, no stock |
| CH224K / CH224Q | — | — | — | — | 0 | CH224K discontinued; CH224Q not stocked |

**CH224A stays.** It's the cheapest, it's well stocked, and its I2C mode gives the firmware more than a yes/no:

- CFG1 → 6.8 kΩ to GND (asks for 9 V on its own at power-up, no firmware needed).
- CFG2/SCL and CFG3/SDA → RP2354A **A** I2C pins with 4.7 kΩ pull-ups to 3.3 V. Firmware reads register `0x09` (which protocol won) and `0x50` (max current at this voltage, 50 mA units), and can re-request 5 V via `0x0A` if needed.
- PG (open drain) → an RP2354A input with pull-up, as a backup to I2C.
- The CH224A has the CC pull-downs built in (no external 5.1 kΩ on the power port).

## 4. Rails after the PD chip

| Rail | Part | JLCPCB | Why |
|---|---|---|---|
| VBUS_IN protection | SMBJ15A TVS (C113988) | $0.06, Ext | 15 V stand-off > 9 V (and > 12 V if ever re-configured); TPS54331 is rated to 28 V |
| 5 V, 3 A | **TPS54331DR** (C9865), SS54 diode, 6.8 µH **SLO0630H6R8MTT** (C207841) | $0.27, **Pref** (no fee); inductor $0.11, Ext | 100 % duty pass-through on 5 V chargers (above); SOIC-8 without a thermal pad; free to place |
| 3.3 V | AMS1117-3.3 (C6186) | $0.16, **Basic** | 5 → 3.3 V at ≤ 0.4 A = ≤ 0.7 W peak in SOT-223 with a copper pad; still regulates from the ≈ 4.7 V pass-through |
| Keyboard VBUS | SY6280AAC (C55136) | $0.07, Ext | current-limited switch, limit set by resistor |
| Pogo 5 V | SY6280AAC (same part) | — | one feeder fee covers both |

**Inductor (decided 2026-09-29): Sunltech SLO0630H6R8MTT, C207841.** JLCPCB has no Basic power inductor at all (only mA-rated chip inductors), so any choice costs one feeder fee. The TPS54331's current limit is 3.5–5.8 A, so the inductor must not saturate below 5.8 A: this one saturates at 8 A (typ), is rated 4.5 A, 45 mΩ typ (≈ 0.26 W at the 2.4 A worst case), 7.1 × 6.6 × 3.0 mm, $0.11, 7.9 k in stock. The earlier SMDRH105R-6R8NT (7 A, 10 × 10 mm) is bigger, pricier and has 881 in stock; the 6 × 6 mm parts (SWPA6045 etc.) saturate at 3.9–4.3 A, below the current limit.

## 4b. 5 V buck component values

From TI's datasheet Table 7-1 (typical design 12 V → 5 V, 570 kHz, 6.8 µH, ceramic output), adjusted to JLCPCB Basic parts (no feeder fees):

| Part | TI Table 7-1 | Dock v2 | Why |
|---|---|---|---|
| Feedback (RO1 / RO2) | 10 k / 1.91 k → 4.99 V | **12 k / 2.2 k → 5.16 V** | Basic values; 5.16 V leaves room for the switch and cable drops to the keyboard and pad |
| Compensation R3 | 49.9 k | **51 k** | Basic |
| Compensation C1 (series) | 4.7 nF | **4.7 nF** | |
| Compensation C2 (to GND) | 39 pF | **47 pF** | Basic; pole moves from ≈ 80 to ≈ 66 kHz, still far above the ≈ 25 kHz crossover |
| Output | 2 × 33 µF ceramic | **3 × 22 µF 25 V 1206** | ≈ same effective capacitance after DC bias at 5 V |
| Soft start | — | **10 nF** | T_SS = 10 nF × 0.8 V / 2 µA = 4 ms (datasheet: 1–10 ms) |
| Boot | 0.1 µF | **100 nF** | |
| EN | UVLO divider suggested | **left open** (internal pull-up) | a UVLO divider would stop the 5 V pass-through on a 5 V-only charger |

Check the loop on the first board (load step on +5V). TI WEBENCH can confirm the values for 9 V in.

## 5. Recommendation

- **Option C: CH224A (9 V, I2C to RP2354A A) → TPS54331 → 5 V → AMS1117 → 3.3 V**, as in the v2 plan, with one upgrade: wire the CH224A's I2C, not just PG.
- The dock needs a **≥ 18 W USB-C PD charger** for full-speed pad charging. On any plain 5 V USB-C supply it still runs (pass-through), with slow pad charging.

## 6. PC-power fallback (option D): dropped

Considered and dropped (2026-09-29). It would have kept the keyboard alive with the charger unplugged, at the cost of a TPS2116 mux, a feeder fee and v1's VBUS back-feed rules. In this setup the charger is off only during a power cut, when the PCs are off anyway.

Firmware consequence: the PC ports are **sense only**. Each RP2354A still reads its PC's VBUS and connects its D+ pull-up only while that PC is on (no back-feeding a PC that is off).

## 7. Not verified

- CH224A behaviour when the charger has no 9 V (datasheet doesn't say; expected: stays at 5 V). Bench test.
- The level of the CH224A's internal CFG2/CFG3 pull-ups (datasheet: "supports 3.3 V or 5 V level input"). Confirm the I2C lines never exceed the RP2354A's 3.3 V rating before wiring them directly.
- TPS54331 pass-through voltage at 2 A on a real 5 V charger (boot-refresh pulses lower it slightly).

Sources: [CH224A/Q datasheet V2.0](https://done.land/assets/files/ch224aq_datasheet.pdf), [TI TPS54331 datasheet](https://www.ti.com/lit/ds/symlink/tps54331.pdf), [done.land CH224 family](https://done.land/components/power/powersupplies/usb/usbtriggers/ch224/), [Renesas: USB PD basics](https://www.renesas.com/en/support/engineer-school/usb-power-delivery-02), [GRL: USB PD 3.2 AVS rule](https://www.grlps.com/en-us/technical-blog/new-avs-requirement-for-usb-c-chargers-above-27w), JLCPCB parts search (prices and stock).
