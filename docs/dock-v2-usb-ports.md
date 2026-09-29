# Dock v2: USB ports (research)

**Decisions (2026-09-29):**
- **All four ports are USB-C** (same connector); the keyboard uses a USB-C cable.
- **22 Ω** USB series resistors (Basic).
- Keyboard VBUS bulk: **one 220 µF 16 V through-hole electrolytic, hand-soldered** (Koshin PKRJ-016V221ME070-T/A5.0 from Özdisan), plus a 10 µF + 1 µF ceramic placed by JLCPCB. Meets the USB 2.0 **120 µF** rule even at −20 % tolerance (176 µF).
- Keyboard port current limit stays at **≈ 1 A**. The current keyboard is rated 200 mA (≈ 100–150 mA in use); the headroom is for a brighter keyboard later.

Date: 2026-09-29. Prices: JLCPCB parts search, 10+ tier. "Ext" = Extended ($3.07 feeder fee per unique part), "Basic" = no fee.

```text
                 ┌──────────────── dock ────────────────┐
 charger ══ C ═══╪═ J1 POWER  CH224A (docs/dock-v2-power-input.md)       sink
 Personal PC ═ C ╪═ J2 PC1    RP2354A A, native USB (device)            sink (Rd)
 Work PC ═════ C ╪═ J3 PC2    RP2354A B, native USB (device)            sink (Rd)
 keyboard ════ C ╪═ J4 KBD    RP2354A A, PIO-USB (host), 5 V via SY6280  SOURCE (Rp)
                 └──────────────────────────────────────┘
```

## 1. Connector: one part for all four

**TYPE-C-31-M-12** (C165948, 16P USB 2.0, SMD pins + through-hole shell pegs), $0.15, Ext, 443 k in stock.
- Rated **20 V / 5 A**, so it can be the 9 V power input as well. The cheaper 16P clones (C2765186, C393939) are rated 5 V or 3 A; not for J1.
- 4 per dock, **one feeder fee**. The USB-A part (and its hand-soldering) is gone.
- JLCPCB counts the shell pegs as through-hole joints (a small THT fee).

## 2. ESD protection: one part for all four ports

**TPD4E1U06** (4 channels, 0.8 pF, SOT-23-6), one per port, **all four channels used on every port: D+, D−, CC1, CC2**. (On J1 the CH224A uses D+/D− for QC/BC1.2.)

- **Why not the USBLC6-2SC6** from the v2 plan: the USBLC6 has a VBUS pin its diodes clamp to. On a PC port that pin sits on the PC's VBUS. If that PC is off while the dock is on, the RP2354A's D+ pull-up (3.3 V) forward-biases the internal diode and **back-feeds the powered-down PC**. The TPD4E1U06 clamps to GND only, with no VBUS pin. (v1 chose it for the same reason.)
- One part type on all four ports = one feeder fee.
- LCSC: TI original **C124691** ($0.30) or pin-compatible C19829453 ($0.07). Take the TI part for the first build (+$0.92/dock).
- Place each right at its connector, before the series resistors.

## 3. PC ports (J2, J3): USB device (sink)

Per port, same on both:

| Signal | Connection |
|---|---|
| CC1, CC2 | **5.1 kΩ to GND each** (Rd, Basic C25905). Without Rd a USB-C PC (C-to-C cable) never turns VBUS on |
| D+, D− | ESD → **22 Ω** (Basic C25092) → RP2354A USB_DP/USB_DM |
| VBUS | **sense only**: 22 kΩ / 33 kΩ divider (Basic C25779 for 33 k) → RP2354A GPIO (5.25 V → 3.15 V). Not connected to any dock rail |
| Shield | GND (optionally 1 MΩ ∥ 4.7 nF; decide at layout) |

- No CC voltage sensing any more: the dock doesn't draw power from the PCs, so it doesn't matter what current they advertise.
- **Firmware rule kept:** each RP2354A enables its D+ pull-up only while its VBUS-sense GPIO is high.
- GND: both PCs, the charger and the dock share GND (as in v1 and every KVM). USB chargers are isolated, so no mains ground loop.

## 4. Keyboard port (J4): USB-C **source** (host)

A USB-C host port has two jobs a USB-A port didn't have:

1. **Rp pull-ups on CC1 and CC2**: they tell the keyboard "I am a source" and how much current it may draw.
2. **Cold socket**: VBUS must stay **off** until a sink (Rd) is detected on CC, and go off again on unplug. This also makes the port safe if someone plugs a charger or PC into it by mistake: a source shows Rp, not Rd, so the dock never turns VBUS on against it.

### 4.1 How: firmware with two ADC pins (no extra chip)

```text
3V3 ── 33 kΩ ──┬── J4 CC1 ── ESD      CC1_SENSE → RP2354A A ADC (GPIO26–29)
3V3 ── 33 kΩ ──┬── J4 CC2 ── ESD      CC2_SENSE → RP2354A A ADC
+5V ──► SY6280AAC ──► KBD_VBUS ──► J4 VBUS ── 220 µF THT + 10 µF + 1 µF
          EN ◄── RP2354A A GPIO (100 kΩ pull-down: off at reset)
          ISET ── 6.8 kΩ (1.0 A typ)
KBD_VBUS ── 10 k / 15 k ──► RP2354A A ADC (5.1 V → 3.06 V)
J4 D+/D− ── ESD ── 22 Ω ──► RP2354A A, two adjacent GPIOs (PIO-USB), 15 kΩ to GND on each
```

- **Rp = 33 kΩ to 3.3 V (Basic C25779)** advertises "Default USB power". The spec value for a 3.3 V pull-up is 36 kΩ ± 20 % (28.8–43.2 kΩ). 36 kΩ is Ext at JLCPCB; 33 kΩ is Basic and inside the range. Default is right here: the port is limited to ≈ 1 A anyway, and USB 2.0 keyboards draw ≤ 500 mA.
- What the ADC sees on each CC pin:

| Attached | CC voltage | Firmware |
|---|---|---|
| nothing | 3.3 V | VBUS off |
| keyboard (Rd 5.1 kΩ) | **≈ 0.44 V** | turn VBUS on |
| e-marked cable only (Ra ≈ 1 kΩ) | ≈ 0.10 V | ignore (cable, no device) |
| a source plugged in by mistake (its Rp) | ≥ 3.3 V | VBUS stays off |

  Spec thresholds (Type-C spec, "Source CC voltage thresholds", default Rp): Ra ≲ 0.2 V, Rd up to ≈ 1.6 V, open above that; our three cases (0.10 / 0.44 / 3.3 V) sit well inside their windows. Check the exact table values when writing the firmware. Attach = one CC in the Rd window for > 100 ms (debounce, per spec tCCDebounce); detach = both CC above 1.6 V. VBUS off within the spec's 650 ms after detach is trivial in firmware.
- **ADC pins:** RP2354A has 4 (GPIO26–29). This port takes 3 (CC1, CC2, KBD_VBUS), leaving one spare.
- **VCONN not needed**: it only powers e-marker chips, which USB 2.0 keyboard cables don't have (and a keyboard works without it).
- Why not a dedicated CC controller chip (WUSB3801Q $0.38, TUSB320L $0.78, FUSB302 $0.86, TPS25810 $0.70): each adds a feeder fee and a tiny QFN, for a job three Basic resistors and ~40 lines of firmware do. The RP2354A is already there and must control VBUS anyway.

### 4.2 Power switch: SY6280AAC (C55136, $0.07, Ext)

- 80 mΩ, 2.4–5.5 V, **I_LIM = 6800 / R_SET**: 6.8 kΩ → 1.0 A typ (0.75–1.25 A).
- Thermal shutdown with auto-retry, reverse blocking, 150 Ω output discharge when off (helps VBUS fall fast on unplug), 120 µs turn-on.
- EN ≥ 2.4 V high at 5 V in: a 3.3 V GPIO drives it. **100 kΩ pull-down** so VBUS is off during reset/boot (cold socket even with blank firmware).
- **No FAULT pin** (v1's TPS2553 had one). The KBD_VBUS ADC divider replaces it: an overload shows up as VBUS collapsing.
- Same part switches the pogo 5 V: one shared feeder fee.
- Checked alternative: WCH **CH217** (70 mΩ, has a FLAG# fault pin). CH217K is out of stock at JLCPCB; CH217A is stocked but not in the datasheet (unknown pinout). Not worth the risk.

### 4.3 VBUS bulk capacitance: 220 µF through-hole, hand-soldered

USB 2.0 asks for ≥ 120 µF on a host port's VBUS.

**Chosen: Koshin PKRJ-016V221ME070-T/A5.0** from Özdisan: 220 µF, 16 V, ±20 %, 105 °C / 1000 h, Ø6.3 × 7 mm, radial, 5.0 mm lead pitch (formed leads, per the listing). **40 919 in stock**, 1.46 TL each, minimum 5 (buy 5: spares).

- Electrolytics keep their capacitance under DC voltage: worst case 220 × 0.8 = **176 µF**, no derating sums needed. 16 V on a 5 V rail is plenty of margin.
- It is a general-purpose part (ripple rating 126 mA), not low-ESR. That's fine here: VBUS carries no switching ripple, and the fast edges are handled by the **10 µF 0805 (Basic C15850) + 1 µF** ceramics next to the connector, placed by JLCPCB.
- Footprint: CP_Radial_D6.3mm, **P5.00 mm** (check the lead spacing on the delivered parts before ordering PCBs; the straight-lead version of this series is 2.5 mm). Leave room for the 6.3 mm body next to J4; 7 mm tall.
- Easier to solder than any 0805: two big through-hole pins, from the top or the back.

Considered and not taken:
- **Panasonic FR/FC 220 µF 16 V** (low-ESR, EEUFR1C221 / EEUFC1C221): listed at Özdisan but **out of stock, 22–23 weeks**. Koshin KLH 220 µF 16 V (low-ESR): out of stock, 5–6 weeks. Any of them drops into the same footprint if it comes back.
- **0805 ceramics:** a 47 µF 0805 6.3 V keeps only ≈ 20–30 % at 5 V, so you'd need 8 or more.
- **4–5 × 100 µF 1206 ceramics** (previous plan, Samsung curve ≈ −64 % at 5 V → ≈ 36 µF each): works, but needs the derating sums and still misses 120 µF at the −20 % corner with 4 parts.
- Basic tantalum 100 µF 6.3 V (C16133): 5 V is 79 % of its rating; too close on a supply rail.

Inrush: the SY6280 limits it to ≈ 1 A; charging 220–260 µF to 5 V takes ≈ 1.3 ms. Harmless for the 3 A buck.

### 4.4 Data lines

- PIO-USB: **two adjacent GPIOs**, no external pull-up in host mode.
- **15 kΩ to GND on D+ and D−** (Basic C25756): host pull-downs per USB 2.0. PIO-USB also enables the internal ones; the external ones make it correct regardless of firmware.
- **RP2350 erratum E9** (pad leakage fighting pull-downs, hit PIO-USB on the A2 stepping) is **fixed in A4**, and every RP2354A is A4.
- 22 Ω series, as on the PC ports.

## 5. Parts for this block (per dock)

| Part | Qty | Feeder |
|---|---|---|
| TYPE-C-31-M-12 (C165948) | 4 | 1 Ext |
| TPD4E1U06 (C124691) | 4 | 1 Ext |
| SY6280AAC (C55136) | 1 (+1 pogo) | 1 Ext (shared) |
| 220 µF 16 V THT electrolytic (Özdisan, Koshin PKRJ-016V221ME070-T/A5.0) | 1 | hand-soldered |
| 10 µF 0805 25 V (C15850) + 1 µF | 1 + 1 | Basic |
| 5.1 k ×4, 33 k ×2 (Rp) + dividers, 22 Ω ×6, 15 k ×2, 100 k, 6.8 k, 10 k/15 k | ≈ 22 | Basic |

Compared with the v2 plan: USBLC6 → TPD4E1U06 (swap), USB-A removed (one fewer part type), one more USB-C, two Rp resistors, two ADC pins.

## 6. Layout notes (for later)

- D+/D− as 90 Ω differential pairs, short, no stubs; series resistors near the RP2354A, ESD at the connector.
- The 220 µF and the 10 µF + 1 µF sit next to J4, between the SY6280 and the connector.
- The CC traces are slow signals, any routing is fine; keep the 33 k Rp near the connector.

## 7. Not verified

- 22 Ω instead of Raspberry Pi's 27 Ω: common on RP2040/RP2350 boards; check enumeration on the first board. 27 Ω later = one feeder fee.
- Current keyboard: 200 mA rated, so Default Rp and the 1 A limit are ample. A future keyboard that needs more than 1 A (rare): Rp = 12 kΩ (1.5 A advertisement) and a smaller R_SET are the only changes.
- The CH217A's pinout, if a fault pin ever becomes worth a second look.

Sources: [Özdisan: Koshin PKRJ-016V221ME070-T/A5.0](https://ozdisan.com/passive-components/capacitors/aluminum-capacitors/PKRJ-016V221ME070-TA5-0/354618), [Özdisan: Panasonic EEUFR1C221](https://www.ozdisan.com/pasif-komponentler/kapasitorler/aluminyum-kapasitorler/EEUFR1C221/1094765), [SY6280 datasheet (Silergy)](https://www.olimex.com/Products/Components/IC/SY6280/resources/SY6280AAC.PDF), [CH217 datasheet (WCH)](https://akizukidenshi.com/goodsaffix/CH217.pdf), [Samsung CL31A107MQHNNN characteristics](https://datasheet.octopart.com/CL31A107MQHNNNE-Samsung-datasheet-12514918.pdf), [Espressif USB Type-C hardware guide](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html), [TI TPD4E1U06](https://www.ti.com/product/TPD4E1U06), [Pico-PIO-USB](https://github.com/sekigon-gonnoc/Pico-PIO-USB), [RP2350 A4 fixes E9 (CNX)](https://www.cnx-software.com/2025/07/29/raspberry-pi-rp2350-a4-stepping-fixes-e9-gpio-erratum-9-glitching-bugs-introduces-2mb-flash-variants/), JLCPCB parts search (prices, stock, Basic/Extended).
