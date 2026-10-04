# Dock v2: pogo interface to the pad (research)

**Decisions (2026-09-29):**
- **Hardware DET enable kept:** pad 5 V turns on from DET alone; firmware can only veto.
- **7-pin connector (2026-09-29, replaces the 6-pin): `GND | +5V | DET | RX | TX | +5V | GND`** (2026-10-01: +5V moved to both ends, see §1). Contacts are rated 1 A each, so +5V and GND on two contacts give 2 A. Limit raised to **R_SET 4.7 kΩ → 1.45 A** (1.09–1.81 A, below the 2 A of the two contacts). The earlier requirement to dim the pad's LEDs while docked (≤ 0.85 A) is **dropped**.

Date: 2026-09-29. Prices: JLCPCB parts search. "Ext" = Extended ($3.07 feeder fee per unique part), "Basic" = no fee.

The pad side does not change (pogo board with SMAJ5.0A + TPD4E1U06, DET tied to GND; DESIGN.md §15). This doc is the dock side only.

## 1. What carries over from v1

- **Connector (changed 2026-10-04, pad docks on top of the dock):** the contacts are the **straight** Motorobit 7-pin 2.54 mm magnetic pogo set (≈ 200 TL), on a small **lid pogo board** in the dock's top cover: flat contacts on the dock, spring pins on the pad's underside. The dock board carries **J601 = JST-XH 7-pin vertical header B7B-XH-A (LCSC C144398, 3 A/contact)**, wired **1:1** (pin n to pin n) to the lid board. Hand-soldered. (v1 and the first v2 plan used a right-angle pogo at the front edge.)
- **Lid board = the pad's pogo board design:** two identical boards facing each other meet pin 1 to pin 7, which is exactly the mirrored order below; only the contact half (flat vs spring) and the signal names differ. The housing of J601 overhangs the PCB edge by 0.5 mm (the pins stay on the original row to keep the routing); allow for it in the case.
- **Contact order:** `GND | +5V | DET | RX | TX | +5V | GND` (dock side; pad pin 1 meets dock pin 7; pad side `GND | +5V | TX | RX | DET | +5V | GND`). Because +5V (pins 2, 6) and GND (pins 1, 7) are mirror-symmetric, a pad fitted the wrong way round still gets +5V on +5V and GND on GND: it is powered and charges normally. Only the UART lines cross (dock TX → pad DET, pad TX → dock DET, RX ↔ RX), all through 1 kΩ, so nothing is damaged; the pogo UART just doesn't work that way round.
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
                                             └── drain Q602 2N7002, gate ◄── RP2354A A GPIO  POGO_OFF (100 k to GND)

+5V ──► SY6280AAC ──► POGO_5V ── 10 µF + 1 µF ── pogo +5V
          ISET ── 4.7 kΩ  (1.45 A typ, 1.09–1.81 A; the same 4.7 k as the CH224A I2C pull-ups)
POGO_5V ── 10 k / 15 k ──► RP2354A A ADC (4th ADC pin; 5.1 V → 3.06 V)
```

- **Undocked:** DET is pulled up → Q1 on → EN low → contacts dead.
- **Docked:** pad grounds DET → Q1 off → EN pulled high → 5 V on, **with no firmware involved.** The pad charges even when the dock's firmware is blank, crashed or being flashed (matches the pad's rule that its TP4056 charges by default).
- **Firmware can still veto:** POGO_OFF drives a second 2N7002 (Q602) that pulls EN low, for example after an overload. Q602's gate has a 100 k pull-down, so MCU A's reset-state pull-down means "no veto". (Connecting the GPIO straight to EN would drag it to ≈ 1.1 V against the 100 k pull-up and stop pad charging whenever MCU A has no firmware; found while making the pin map, DOCK_CONNECTIONS.md §8.)
- **No FAULT pin on the SY6280:** POGO_5V goes to the last free ADC pin instead. Firmware sees the pad's load (voltage sag in current limit) and a short (collapse). This uses **all 4 ADC pins** of RP2354A A: KBD CC1, KBD CC2, KBD_VBUS, POGO_5V.
- Output discharge (150 Ω) pulls the contact voltage down quickly when the pad leaves.
- Hot-plug: the pad's input capacitors charge through the SY6280's current limit; the pad's SMAJ5.0A catches ringing.

## 3. Current limit: 1.45 A (7-pin connector)

The pad draws from the pogo 5 V while docked:

| Pad load | Current at 5 V |
|---|---|
| Charging (TP4056 fast) | 0.51 A |
| Pico 2 W + BLE + display + inputs | ≈ 0.15 A |
| 36 RGB LEDs, full white (worst case) | 0.54 A |
| **Total, worst case** | **≈ 1.2 A** |
| Total, normal (charging, LEDs at moderate brightness) | ≈ 0.7–0.8 A |

- **Limit 1.45 A (R_SET 4.7 kΩ):** covers the pad's worst case (≈ 1.2 A: fast charging with every LED full white), so **no LED dimming is needed**. On a switch at the low end of its tolerance (1.09 A) that one corner is capped: POGO_5V sags and the pad's TPS2116 moves to battery. Nothing is damaged.
- The highest possible limit (1.81 A) stays below the 2 A of the two +5V contacts.
- 5 V budget: keyboard 1.0 A + pogo 1.45 A + 3.3 V 0.4 A ≈ 2.85 A at the nominal limits, inside the TPS54331's 3 A; realistic use is ≈ 1 A (power doc §1).
- History: with the 6-pin connector (one +5V contact) the limit was 1.0 A and the pad had to dim its LEDs while docked (≤ 0.85 A). Replaced by the 7-pin connector on 2026-09-29.

## 4. Pogo UART

- RP2354A A's two hardware UARTs are taken (UART to RP2354A B, UART to the ESP32-C3), so the pogo UART is a **PIO UART**, as in v1.
- PIO blocks: PIO-USB uses one, the pogo UART one more; RP2354A has three.
- Dock RX idles high with the internal pull-up, so a floating contact (undocked) doesn't produce garbage.
- If the dock is unpowered and the pad docked, the pad's TX feeds the dock's RX pin through 2 × 1 kΩ: ≤ 1.6 mA, harmless.

## 5. Parts (dock side, per dock)

| Part | Qty | Feeder |
|---|---|---|
| JST-XH 7-pin vertical header B7B-XH-A (C144398), THT | 1 | hand-soldered |
| Straight 7-pin magnetic pogo set (Motorobit), on the lid board | 1 | hand-soldered (lid board) |
| SY6280AAC (C55136) | 1 | shared with the keyboard switch |
| TPD4E1U06 (C124691) | 1 (DET, TX, RX; 1 spare) | shared with the USB ports |
| 2N7002 (C8545) | 1 | Basic |
| 1 kΩ ×3, 10 kΩ ×2, 15 kΩ, 100 kΩ ×2, 4.7 kΩ | 9 | Basic |
| 2N7002 (Q602, POGO_OFF veto) | 1 | Basic |
| 10 µF 0805 (C15850), 1 µF ×2 | 3 | Basic |

**No new Extended part** for this block.

## 6. Answered

1. Contact rating: **1 A** per pin (Motorobit). Solved by the 7-pin connector: two contacts each for +5V and GND.
2. Hardware DET enable: **kept**. The firmware veto is a second 2N7002 (Q602), see DOCK_CONNECTIONS.md §8.

## 7. Not verified

- The pogo set's current and cycle rating (not on the Motorobit listing).
- The straight pogo set's footprint on the lid/pad pogo board: check against the delivered part.

Sources: [SY6280 datasheet (Silergy)](https://www.olimex.com/Products/Components/IC/SY6280/resources/SY6280AAC.PDF), [Motorobit 7-pin 90° magnetic pogo set](https://www.motorobit.com/7-pin-254mm-90c-pogo-pin-magnetic-connector-set-with-ear), DESIGN.md §10, §12, §15 (pad loads and pad-side pogo board), JLCPCB parts search.
