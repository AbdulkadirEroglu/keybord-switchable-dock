# Dock v2: pogo interface to the pad (research)

**Decisions (2026-09-29):**
- **Hardware DET enable kept:** pad 5 V turns on from DET alone; firmware can only veto.
- **Contacts are rated 1 A** (Motorobit listing). Limit stays at R_SET 6.8 kΩ (1.0 A typ). The pad firmware **must** keep its docked draw ≤ ≈ 0.85 A (cap LED brightness while docked), so the contacts run below their rating in normal use; the limiter only acts on faults.

Date: 2026-09-29. Prices: JLCPCB parts search. "Ext" = Extended ($3.07 feeder fee per unique part), "Basic" = no fee.

The pad side does not change (pogo board with SMAJ5.0A + TPD4E1U06, DET tied to GND; DESIGN.md §15). This doc is the dock side only.

## 1. What carries over from v1

- **Connector:** the same 6-pin 2.54 mm magnetic pogo set (Motorobit, "6-Pin 2.54mm 90° Pogo Pin Magnetic Connector Set – With Ear"), footprint `dock:Pogo-6`. Through-hole: **hand-soldered**.
- **Contact order:** `GND | +5V | DET | RX | TX | GND` (dock side; pad pin 1 meets dock pin 6).
- **+5 V is off while undocked:** the contacts are exposed, so they are dead until a pad pulls DET low.
- **BLE is the normal data link;** the pogo UART is for diagnostics/recovery only.
- **1 kΩ series resistors** on TX, RX and DET, **TPD4E1U06** ESD right at the contacts (same part as the USB ports: no new feeder fee).

## 2. What changes: the 5 V switch

v1 used a TPS2552 whose active-low EN was driven straight by DET. v2 uses the **SY6280AAC** (already on the board for the keyboard: no new feeder fee), and its EN is **active high**, so DET needs inverting:

```text
3V3 ── 10 kΩ ──┬── 1 kΩ ── ESD ── pogo DET          (pad ties DET to GND)
               ├──────────────► RP2354A A GPIO  POGO_DET (low = docked)
               └── gate  Q1 2N7002 (Basic C8545)
                         drain ─┬── SY6280 EN ── 100 kΩ ── 3V3
                         source ┴ GND        │
                                             └──── RP2354A A GPIO  POGO_OFF (open-drain, pulls EN low)

+5V ──► SY6280AAC ──► POGO_5V ── 10 µF + 1 µF ── pogo +5V
          ISET ── 6.8 kΩ  (1.0 A typ, 0.75–1.25 A; same value as the keyboard port)
POGO_5V ── 10 k / 15 k ──► RP2354A A ADC (4th ADC pin; 5.1 V → 3.06 V)
```

- **Undocked:** DET is pulled up → Q1 on → EN low → contacts dead.
- **Docked:** pad grounds DET → Q1 off → EN pulled high → 5 V on, **with no firmware involved.** The pad charges even when the dock's firmware is blank, crashed or being flashed (matches the pad's rule that its TP4056 charges by default).
- **Firmware can still veto:** POGO_OFF (a GPIO in open-drain mode, left floating at reset) pulls EN low, for example after an overload.
- **No FAULT pin on the SY6280:** POGO_5V goes to the last free ADC pin instead. Firmware sees the pad's load (voltage sag in current limit) and a short (collapse). This uses **all 4 ADC pins** of RP2354A A: KBD CC1, KBD CC2, KBD_VBUS, POGO_5V.
- Output discharge (150 Ω) pulls the contact voltage down quickly when the pad leaves.
- Hot-plug: the pad's input capacitors charge through the SY6280's current limit; the pad's SMAJ5.0A catches ringing.

## 3. Current limit: 1 A

The pad draws from the pogo 5 V while docked:

| Pad load | Current at 5 V |
|---|---|
| Charging (TP4056 fast) | 0.51 A |
| Pico 2 W + BLE + display + inputs | ≈ 0.15 A |
| 36 RGB LEDs, full white (worst case) | 0.54 A |
| **Total, worst case** | **≈ 1.2 A** |
| Total, normal (charging, LEDs at moderate brightness) | ≈ 0.7–0.8 A |

- **Limit at 1.0 A (R_SET 6.8 kΩ, same as the keyboard)**, as in v1. The one case that exceeds it is fast charging with every LED full white. For that, the pad caps its LED brightness while docked (required, see §6). If it isn't capped, the SY6280 holds the current, POGO_5V sags, and the pad's TPS2116 moves to battery below ≈ 4.0 V. It degrades gracefully, with nothing damaged.
- Why not raise it: the contact rating of the Motorobit set isn't published (similar 2.54 mm magnetic pogo sets are listed at 1–2 A per pin). With one +5 V pin, 1 A is the safe choice until the rating is known.
- 5 V budget: keyboard 1 A + pogo 1 A + 3.3 V rail 0.4 A = 2.4 A worst case, inside the TPS54331's 3 A (see power doc).

## 4. Pogo UART

- RP2354A A's two hardware UARTs are taken (UART to RP2354A B, UART to the ESP32-C3), so the pogo UART is a **PIO UART**, as in v1.
- PIO blocks: PIO-USB uses one, the pogo UART one more; RP2354A has three.
- Dock RX idles high with the internal pull-up, so a floating contact (undocked) doesn't produce garbage.
- If the dock is unpowered and the pad docked, the pad's TX feeds the dock's RX pin through 2 × 1 kΩ: ≤ 1.6 mA, harmless.

## 5. Parts (dock side, per dock)

| Part | Qty | Feeder |
|---|---|---|
| 6-pin magnetic pogo (Motorobit), THT | 1 | hand-soldered |
| SY6280AAC (C55136) | 1 | shared with the keyboard switch |
| TPD4E1U06 (C124691) | 1 (DET, TX, RX; 1 spare) | shared with the USB ports |
| 2N7002 (C8545) | 1 | Basic |
| 1 kΩ ×3, 10 kΩ ×2, 15 kΩ, 100 kΩ, 6.8 kΩ | 8 | Basic |
| 10 µF 0805 (C15850), 1 µF ×2 | 3 | Basic |

**No new Extended part** for this block.

## 6. Answered

1. Contact rating: **1 A** per pin (Motorobit). Normal pad load (0.7–0.8 A) is under it. The SY6280's 0.75–1.25 A limit spread means a faulty pad could push ≈ 1.25 A through the +5 V contact until the SY6280's thermal cut-out or the firmware veto (POGO_5V sag on the ADC) acts; acceptable for a fault. For a strict ≤ 1 A ceiling instead: R_SET 8.2 kΩ (0.62–1.04 A), at the cost of hitting the limit during normal fast charging on a low-tolerance part.
2. Hardware DET enable: **kept**.

## 7. Not verified

- The pogo set's current and cycle rating (not on the Motorobit listing).
- **Pad firmware requirement:** cap LED brightness while docked so the total docked draw stays ≤ ≈ 0.85 A (charging 0.51 A + electronics 0.15 A leaves ≈ 0.2 A for LEDs, ≈ 13 LEDs full white or all 36 at ≈ 35 %).

Sources: [SY6280 datasheet (Silergy)](https://www.olimex.com/Products/Components/IC/SY6280/resources/SY6280AAC.PDF), [Motorobit 6-pin magnetic pogo set](https://www.motorobit.com/6-pin-254mm-90c-pogo-pin-magnetic-connector-set-with-ear), DESIGN.md §10, §12, §15 (pad loads and pad-side pogo board), JLCPCB parts search.
