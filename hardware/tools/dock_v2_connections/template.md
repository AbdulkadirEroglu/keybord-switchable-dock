# Dock v2 — Connection & Placement Guide

Use this to understand the v2 dock circuit, sheet by sheet (sketches, reasons, placement). **To wire the schematic, use the component-by-component list [DOCK_WIRING.md](DOCK_WIRING.md)**: every part, every pin, what it connects to and which label to draw.
All parts are already on their sheets (`hardware/dock-v2/`, placed, not wired) with the references used here.
Why each part was chosen is in `docs/dock-v2-*.md`; where it goes on the board is in [PCB_PLACEMENT.md](PCB_PLACEMENT.md).

The tables are generated from one connection model and checked against the placed schematic: {{STATS}}. Every pin of every part is listed once, either on a net or as a no-connect.

How to read the tables:

- **Parts**: what is on the sheet (value, footprint and LCSC number are already filled in).
- **Wiring**: each row is one pin and the net it belongs to. Everything with the same net name is wired together.
  Nets in **bold** leave the sheet: use a **global label** with exactly that name. The rest are **local labels** (or plain wires) inside the sheet.
- **Placement**: what has to sit next to what on the PCB, and why.

Net names used everywhere:

| Net | What it is |
|---|---|
| **GND** | Board ground (also the two PCs' and the charger's ground) |
| **VBUS_IN** | Charger input after J101: 9 V with a PD charger, 5 V without |
| **+5V** | Buck output, 5.16 V (≈ 4.7 V pass-through on a 5 V-only charger) |
| **+3V3** | AMS1117 output: both RP2354A, the ESP32-C3, all pull-ups |
| **KBD_VBUS** | Keyboard 5 V after the SY6280 switch (off until a keyboard is detected) |
| **POGO_5V** | Pad 5 V after the pogo SY6280 switch (on while the pad is docked); two contacts, limit ≈ 1.45 A |
| A_1V1, B_1V1 | Each RP2354A's own 1.1 V core rail. **Local labels, never a `+1V1` power symbol**: a power symbol is global and would join A's and B's regulators |
| PC1_VBUS, PC2_VBUS | The PCs' VBUS: **sense only**, never joined to a dock rail |

## Contents

1. [Power input and PD (J101, CH224A)](#1-power-input-and-pd-j101-ch224a)
2. [5 V buck and 3.3 V LDO](#2-5-v-buck-and-33-v-ldo)
3. [Keyboard port (J201, USB-C source)](#3-keyboard-port-j201-usb-c-source)
4. [PC ports (J202 Personal, J203 Work)](#4-pc-ports-j202-personal-j203-work)
5. [MCU A (RP2354A)](#5-mcu-a-rp2354a)
6. [MCU B (RP2354A)](#6-mcu-b-rp2354a)
7. [BLE (ESP32-C3-MINI-1)](#7-ble-esp32-c3-mini-1)
8. [Pogo interface](#8-pogo-interface)
9. [Signals that cross between sheets](#9-signals-that-cross-between-sheets)
10. [Board-wide rules, PWR_FLAGs and no-connects](#10-board-wide-rules-pwr_flags-and-no-connects)
11. [Appendix: full net index](#appendix--full-net-index-generated)

## The whole dock at a glance

```text
 charger ═ J101 ─ VBUS_IN ─┬─ CH224A (asks 9 V) ── I2C, PG ──────────────────────────┐
                           └─ TPS54331 ── +5V ─┬─ AMS1117 ── +3V3 ──► A, B, ESP32      │
                                               ├─ SY6280 ── KBD_VBUS ──► J201 keyboard │
                                               └─ SY6280 ── POGO_5V ───► J601 pogo     │
                                                                                       ▼
 keyboard ═ J201 ── PIO-USB (GPIO{{A:KBD_USB_D_N}}/{{A:KBD_USB_D_P}}) ──►┌────────────┐── UART1 ──►┌────────────┐
                    CC1/CC2 → ADC        │ RP2354A  A │◄─ RUN, BOOTSEL, SWD ─│ RP2354A  B │══ J203 ═ Work PC
 Personal PC ═ J202 ══ native USB ═══════│  (U301)    │            │  (U401)    │
                                         └─────┬──────┘            └────────────┘
                              UART0, EN, BOOT  │  PIO UART, DET, OFF, ADC
                                  ESP32-C3 ◄───┴───► pogo J601 ═ pad
```

Each sketch below is only a reading aid: `●` is a junction, `─` a wire, `→`/`←` show which way a signal goes. The tables under each sketch are the exact reference.

---

## 1. Power input and PD (J101, CH224A)

Sheet `power.kicad_sch`.

```text
 J101 VBUS (A4, A9, B4, B9) ──●── VBUS_IN ──► buck VIN (section 2)
                              ├── D101 SMBJ15A cathode (pin 1); anode (pin 2) ── GND
                              ├── C101 1 µF 50 V ── GND
                              └── U102 pin 1 VHV and pin 8 VBUS (tied together, datasheet)
 J101 CC1 (A5) ──●── PD_CC1 ── U102 pin 7        J101 D+ (A6, B6) ──●── PD_DP ── U102 pin 4
                 └── U101 pin 3 (ESD)                               └── U101 pin 1
 J101 CC2 (B5) ──●── PD_CC2 ── U102 pin 6        J101 D− (A7, B7) ──●── PD_DM ── U102 pin 5
                 └── U101 pin 4                                     └── U101 pin 6
 U102 pin 9 CFG1 ── PD_CFG1 ── R101 6.8 k ── GND            (requests 9 V on its own)
 U102 pin 2 CFG2/SCL ──●── PD_SCL ──► MCU A GPIO{{A:PD_SCL}}      (R103 4.7 k to +3V3)
 U102 pin 3 CFG3/SDA ──●── PD_SDA ◄─► MCU A GPIO{{A:PD_SDA}}      (R104 4.7 k to +3V3)
 U102 pin 10 PG ───────●── PD_PG ───► MCU A GPIO{{A:PD_PG}}      (R102 10 k to +3V3)
 U102 pin 11 (exposed pad) ── GND;  J101 A1, A12, B1, B12, SH ── GND;  SBU A8/B8: no-connect
```

**Parts**

{{PARTS:J101, U101, D101, U102, C101, R101, R102, R103, R104}}

**Wiring — J101 (USB-C, power input)**

{{IC:J101}}

**Wiring — U101 (ESD) and U102 (CH224A)**

{{IC:U101}}

{{IC:U102}}

{{TWO:D101, C101, R101, R102, R103, R104}}

Notes:
- D101 uses KiCad's `D_TVS` symbol, drawn bidirectional (pins A1/A2). The SMBJ15A is **unidirectional**: pin 1 (A1) is the footprint's **cathode-band** pad, so pin 1 goes to VBUS_IN.
- Not verified: the level of the CH224A's internal CFG2/CFG3 pull-ups. Measure SCL/SDA idle voltage on the first board before connecting the I2C lines to MCU A (both are rated 6.5 V; the RP2354A pins are 3.3 V).

**Placement**

- J101 on the right edge. U101 within 5 mm of J101, signals pass its pads first. D101 right at J101's VBUS pads.
- U102 next to J101: short CC and D± runs. C101 at U102 pin 1. R101 at pin 9.
- VBUS_IN is a Power-class net (0.6 mm).

---

## 2. 5 V buck and 3.3 V LDO

Sheet `power.kicad_sch`. Values from TI's TPS54331 Table 7-1 (5 V design), on JLCPCB Basic parts: see `docs/dock-v2-power-input.md` §4b.

```text
 VBUS_IN ──●── U103 pin 2 VIN                    U103 pin 8 PH ──●── BUCK_SW ──●── L101 6.8 µH ──●── +5V
           ├── C102 10 µF ── GND                                 │             └── D102 SS54 cathode; anode ── GND
           └── C103 10 µF ── GND                                 └── C104 100 nF ── U103 pin 1 BOOT
 U103 pin 3 EN: no-connect (internal pull-up; a UVLO divider would stop the 5 V pass-through)
 U103 pin 4 SS ── BUCK_SS ── C105 10 nF ── GND                       (≈ 4 ms soft start)
 U103 pin 6 COMP ──●── BUCK_COMP ── R105 51 k ── BUCK_COMP_RC ── C106 4.7 nF ── GND
                   └── C107 47 pF ── GND
 +5V ── R106 12 k ──●── BUCK_FB ── U103 pin 5 VSENSE            (0.8 V × (1 + 12/2.2) = 5.16 V)
                    └── R107 2.2 k ── GND
 +5V ──●── C108, C109, C110 22 µF ── GND
       └── U104 pin 3 VI (AMS1117)   U104 pin 2 VO ──●── +3V3     U104 pin 1 GND
           C111 10 µF at VI                          └── C112 10 µF ── GND
```

**Parts**

{{PARTS:U103, C102, C103, C104, C105, R105, C106, C107, R106, R107, D102, L101, C108, C109, C110, U104, C111, C112, H101, H102, H103, H104}}

**Wiring — U103 (TPS54331) and U104 (AMS1117)**

{{IC:U103}}

{{IC:U104}}

{{TWO:C102, C103, C104, C105, R105, C106, C107, R106, R107, D102, L101, C108, C109, C110, C111, C112}}

H101–H104 (M3 holes) have no pins.

**Placement**

- Front-right corner. The **hot loop**: C102/C103 → U103 VIN/GND → PH → D102 → GND. Keep it tiny, on the top layer, over the In1 ground plane.
- L101 next to the PH pin; C108–C110 between L101 and the +5V trunk. Copper pour around U103 GND and D102 for heat.
- R106/R107 at U103 pin 5, fed from the +5V side of C108–C110; keep BUCK_FB away from BUCK_SW, L101 and D102.
- C104 right at pins 1 and 8. C105, R105/C106/C107 right at pins 4 and 6.
- U104 in the centre of the board (it feeds A, B and the ESP32); tab on a copper area. C111/C112 at its pins.
- L101 = Sunltech **SLO0630H6R8MTT** (C207841): 6.8 µH, saturation 8 A (above the TPS54331's 5.8 A maximum current limit, so it can't saturate in an overload), 45 mΩ, 7.1 × 6.6 × 3.0 mm, footprint `Inductor_SMD:L_TechFuse_SL0630` (same body and pad gap as Sunltech's land pattern). Extended part: JLCPCB has no Basic power inductor.

---

## 3. Keyboard port (J201, USB-C source)

Sheet `usb_ports.kicad_sch`. The dock is the **source** here: Rp pull-ups on CC, 5 V only after the firmware sees a keyboard (docs/dock-v2-usb-ports.md §4).

```text
 +5V ──●── U202 pin 5 IN (SY6280)        U202 pin 1 OUT ──●── KBD_VBUS ──► J201 VBUS (A4, A9, B4, B9)
       └── C204 1 µF ── GND                               ├── C201 220 µF THT (+ = pin 1), hand-soldered
 U202 pin 4 EN ──●── KBD_VBUS_EN ◄── MCU A GPIO{{A:KBD_VBUS_EN}}          ├── C202 10 µF, C203 1 µF ── GND
                 └── R208 100 k ── GND  (off at reset)    └── R209 10 k ──●── KBD_VBUS_SENSE ──► MCU A GPIO{{A:KBD_VBUS_SENSE}} (ADC{{ADC:KBD_VBUS_SENSE}})
 U202 pin 3 ISET ── R207 6.8 k ── GND  (1.0 A)                             └── R210 15 k ── GND
 +3V3 ── R201 33 k ──●── KBD_CC1 ── J201 CC1 (A5) ──► MCU A GPIO{{A:KBD_CC1}} (ADC{{ADC:KBD_CC1}});  U201 pin 3
 +3V3 ── R202 33 k ──●── KBD_CC2 ── J201 CC2 (B5) ──► MCU A GPIO{{A:KBD_CC2}} (ADC{{ADC:KBD_CC2}});  U201 pin 4
 J201 D+ (A6, B6) ──●── KBD_USBJ_D_P ── R205 22 Ω ── KBD_USB_D_P ──► MCU A GPIO{{A:KBD_USB_D_P}} (PIO-USB D+)
                    ├── U201 pin 1;  R203 15 k ── GND
 J201 D− (A7, B7) ──●── KBD_USBJ_D_N ── R206 22 Ω ── KBD_USB_D_N ──► MCU A GPIO{{A:KBD_USB_D_N}} (PIO-USB D−)
                    ├── U201 pin 6;  R204 15 k ── GND
 J201 A1, A12, B1, B12, SH ── GND;  SBU A8/B8: no-connect
```

**Parts**

{{PARTS:J201, U201, R201, R202, R203, R204, R205, R206, U202, R207, R208, C201, C202, C203, C204, R209, R210}}

**Wiring**

{{IC:J201}}

{{IC:U201}}

{{IC:U202}}

{{TWO:R201, R202, R203, R204, R205, R206, R207, R208, C201, C202, C203, C204, R209, R210}}

**Placement**

- J201 on the left edge. U201 within 5 mm. R201/R202 near J201.
- U202 between the +5V trunk and J201; R207 short to U202 pin 3. C201 (Ø 6.3 mm, THT) and C202/C203 at J201's VBUS pads.
- R205/R206 **near MCU A** (series termination at the driver); R203/R204 anywhere on the pair, near J201 is fine.
- KBD_USB pair as a 90 Ω differential pair; GPIO{{A:KBD_USB_D_N}}/GPIO{{A:KBD_USB_D_P}} are on MCU A's left side, facing J201.
- KBD_VBUS is Power class.

---

## 4. PC ports (J202 Personal, J203 Work)

Sheet `usb_ports.kicad_sch`. The dock is a **sink** (Rd) but draws no power: VBUS is only sensed.

```text
 J202 (Personal PC, back edge)                               J203 (Work PC) is the same with R217–R222, U204,
 J202 VBUS ── PC1_VBUS ── R213 22 k ──●── PC1_VBUS_DET ──► MCU A GPIO{{A:PC1_VBUS_DET}}     PC2_* nets, MCU B GPIO{{B:PC2_VBUS_DET}} and B's USB pins
                                      └── R214 33 k ── GND
 J202 CC1 (A5) ──●── PC1_CC1 ── R211 5.1 k ── GND;  U203 pin 3
 J202 CC2 (B5) ──●── PC1_CC2 ── R212 5.1 k ── GND;  U203 pin 4
 J202 D+ (A6, B6) ──●── PC1_USBJ_D_P ── R215 22 Ω ── PC1_USB_D_P ──► MCU A pin 52 USB_DP
                    └── U203 pin 1
 J202 D− (A7, B7) ──●── PC1_USBJ_D_N ── R216 22 Ω ── PC1_USB_D_N ──► MCU A pin 51 USB_DM
                    └── U203 pin 6
 J202 A1, A12, B1, B12, SH ── GND;  SBU A8/B8: no-connect
```

**Parts**

{{PARTS:J202, U203, R211, R212, R213, R214, R215, R216, J203, U204, R217, R218, R219, R220, R221, R222}}

**Wiring — J202 / U203 (Personal)**

{{IC:J202}}

{{IC:U203}}

{{TWO:R211, R212, R213, R214, R215, R216}}

**Wiring — J203 / U204 (Work)**

{{IC:J203}}

{{IC:U204}}

{{TWO:R217, R218, R219, R220, R221, R222}}

**Placement**

- J202 back edge, left (towards MCU A); J203 back edge, right (towards MCU B). ESD within 5 mm of each.
- R215/R216 near MCU A's USB pins, R221/R222 near MCU B's.
- PCx_VBUS is **never** connected to +5V or any dock rail. Firmware connects each MCU's USB (D+ pull-up) only while its PCx_VBUS_DET is high, so a switched-off PC is never back-fed.

---

## 5. MCU A (RP2354A)

Sheet `mcu_a.kicad_sch`. Core circuit = Raspberry Pi's Minimal design (`hardware/reference/rpi-rp2350a-minimal`); after F8, `hardware/tools/copy_rpi_core_layout.py … U301` copies RPi's layout.

```text
 +3V3 ──●── U301 IOVDD (1, 11, 20, 30, 38, 45), ADC_AVDD (44), USB_OTP_VDD (53), QSPI_IOVDD (54)
        ├── U301 pin 49 VREG_VIN ── C301 4.7 µF ── GND
        └── R301 33 Ω ──●── A_VREG_AVDD ── U301 pin 46;  C303 4.7 µF ── GND
 U301 pin 48 VREG_LX ── A_VREG_LX ── L301 pin 2      L301 pin 1 (dot) ──●── A_1V1
 A_1V1 ── U301 DVDD (6, 23, 39) and VREG_FB (50);  C302 4.7 µF, C304–C306 100 nF ── GND
 +3V3 ── C307–C313 100 nF, C314 10 µF ── GND          U301 pin 47 VREG_PGND, pin 61 pad ── GND
 U301 pin 21 XIN ──●── A_XIN ── Y301 pin 1;  C315 15 pF ── GND
 U301 pin 22 XOUT ── A_XOUT ── R302 1 k ── A_XOUT_R ──●── Y301 pin 3;  C316 15 pF ── GND
 Y301 pins 2, 4 ── GND
 U301 pin 60 QSPI_SS ── A_QSPI_SS ── R303 1 k ── A_BOOTSEL_BTN ── SW301 ── GND      (BOOTSEL A)
 U301 pin 26 RUN ── A_RUN ── SW302 ── GND                                            (RESET A)
 U301 pins 24/25 SWCLK/SWDIO ── J401 pins 3/2 (1x3 2.54 mm SWD header; pin 1 = GND)
 U301 GPIO{{A:A_LED}} ── A_LED ── R305 1 k ── A_LED_R ── D301 anode (2); cathode (1) ── GND
 QSPI_SD0–3, QSPI_SCLK (55–59): no-connect (the 2 MB flash inside uses them)
```

**Parts**

{{PARTS:U301, L301, C301, C302, C303, R301, C304, C305, C306, C307, C308, C309, C310, C311, C312, C313, C314, Y301, C315, C316, R302, SW301, R303, SW302, D301, R305, J401}}

**Pin map — MCU A GPIOs**

{{APINMAP}}

Why these pins (chosen to keep the routing on 2 layers with as few crossings as possible): hardware UART0 TX/RX exist on GPIO 0/1, 2/3, 12/13, 14/15, 16/17, 18/19, 28/29 (TX even, RX odd); UART1 on 4/5, 6/7, 8/9, 10/11, 20/21, 22/23, 24/25, 26/27 (any TX with any RX of the same UART); I2C1 SDA/SCL on 18/19 (and 2/3, 6/7, 10/11, 14/15, 22/23); the ADC only on 26–29; PIO-USB needs two adjacent GPIOs — here D− = D+ − 1, so the firmware uses `PIO_USB_PINOUT_DMDP` with `pin_dp = {{A:KBD_USB_D_P}}`. The ESP32 is on UART0 and the B link on UART1; the CH224A is on I2C1. Sides of the QFN-60 (top view, pin 1 top-left, counter-clockwise): left = GPIO0–11 (faces J201), bottom = GPIO12–18 (faces the ESP32 and the pogo), right = GPIO19–29 (faces MCU B; the CH224A lines run under B), top = regulator and USB (faces J202).

**Wiring — U301**

{{IC:U301}}

{{TWO:L301, C301, C302, C303, R301, C304, C305, C306, C307, C308, C309, C310, C311, C312, C313, C314, C315, C316, R302, R303, SW301, SW302, R305, D301}}

Crystal: {{ONE:Y301}} is 4 pins — 1 = A_XIN, 3 = A_XOUT_R, 2 and 4 = GND.

**Placement**

- U301 back-left; top side (regulator, USB pins) towards J202, left side towards J201.
- Run `copy_rpi_core_layout.py … U301`: it places L301, C301–C313, R301, Y301, C315, C316, R302 exactly as RPi does (inductor dot towards A_1V1) and copies the pours and tracks.
- C314 (10 µF) near U104's +3V3 feed into this chip. SW301/SW302 reachable from above.

---

## 6. MCU B (RP2354A)

Sheet `mcu_b.kicad_sch`. Same core as MCU A (B_ nets, U401 …). What differs: B has no reset button (A resets it), and A controls B's RUN, BOOTSEL and SWD.

```text
 (core: as MCU A, with U401, L401, C401–C416, R401, R402, Y401, B_* local nets)
 U401 pin 26 RUN ── B_RUN ◄── MCU A GPIO{{A:B_RUN}} (open-drain);  R406 10 k to +3V3
 U401 pin 60 QSPI_SS ──●── B_QSPI_SS ── R403 1 k ── B_BOOTSEL_BTN ── SW401 ── GND     (BOOTSEL B)
                       └── R404 1 k ── B_BOOTSEL ◄── MCU A GPIO{{A:B_BOOTSEL}} (open-drain);  R407 10 k to +3V3
 U401 pins 24/25 SWCLK/SWDIO ──●── B_SWCLK / B_SWDIO ◄── MCU A GPIO{{A:B_SWCLK}} / GPIO{{A:B_SWDIO}}
                               └── J501 pins 3/2 (1x3 SWD header; pin 1 = GND)
 U401 GPIO{{B:B_LINK_RX}} (UART1 TX) ── B_LINK_RX ──► MCU A GPIO{{A:B_LINK_RX}} (UART1 RX)
 U401 GPIO{{B:B_LINK_TX}} (UART1 RX) ◄── B_LINK_TX ◄── MCU A GPIO{{A:B_LINK_TX}} (UART1 TX)
 U401 GPIO{{B:PC2_VBUS_DET}} ◄── PC2_VBUS_DET;   U401 GPIO{{B:B_LED}} ── B_LED ── R405 1 k ── D401 ── GND
 U401 pins 52/51 USB_DP/DM ── PC2_USB_D_P / PC2_USB_D_N (from R221/R222)
```

R406/R407 matter: at reset and in BOOTSEL mode, MCU A's pins are inputs with weak pull-downs. Without the 10 k pull-ups, B_RUN and B_BOOTSEL would sit at mid-level against B's weak internal pull-ups, and B could stay in reset or boot into BOOTSEL whenever A restarts.

**Parts**

{{PARTS:U401, L401, C401, C402, C403, R401, C404, C405, C406, C407, C408, C409, C410, C411, C412, C413, C414, Y401, C415, C416, R402, SW401, R403, R404, R406, R407, D401, R405, J501}}

**Pin map — MCU B GPIOs**

{{BPINMAP}}

**Wiring — U401**

{{IC:U401}}

{{TWO:L401, C401, C402, C403, R401, C404, C405, C406, C407, C408, C409, C410, C411, C412, C413, C414, C415, C416, R402, R403, R404, R406, R407, SW401, R405, D401}}

Crystal: {{ONE:Y401}} (1 = B_XIN, 3 = B_XOUT_R, 2 and 4 = GND).

**Placement**

- U401 back-right; top side towards J203. Its left side (link, LED) faces MCU A; PC2_VBUS_DET is on the top-right pin towards J203.
- `copy_rpi_core_layout.py … U401` for the core.
- R406/R407 near U401 (RUN pin 26, QSPI_SS pin 60); R404 at QSPI_SS.

---

## 7. BLE (ESP32-C3-MINI-1)

Sheet `ble.kicad_sch`.

```text
 +3V3 ──●── U501 pin 3 3V3;  C502 10 µF, C503 100 nF ── GND (at pin 3)
        ├── R501 10 k ──●── BLE_EN ── U501 pin 8 EN;  C501 1 µF ── GND;  ◄── MCU A GPIO{{A:BLE_EN}} (open-drain)
        ├── R504 10 k ──●── BLE_BOOT ── U501 pin 23 GPIO9 ◄── MCU A GPIO{{A:BLE_BOOT}} (open-drain; low at reset = download mode)
        ├── R502 10 k ──── BLE_GPIO8 ── U501 pin 22 GPIO8   (must be high for UART download)
        └── R503 10 k ──── BLE_GPIO2 ── U501 pin 5 GPIO2    (Espressif: keep high)
 U501 pin 30 RXD0 ◄── BLE_TX ◄── MCU A GPIO{{A:BLE_TX}} (UART0 TX);  TP504
 U501 pin 31 TXD0 ──► BLE_RX ──► MCU A GPIO{{A:BLE_RX}} (UART0 RX);  TP503
 U501 pins 26/27 GPIO18/19 (native USB): no-connect (USB test pads dropped);  TP505 ── GND
 GND pins 1, 2, 11, 14, 36–53 ── GND;  NC and unused GPIOs: no-connect flags
```

R504 is needed for the same reason as R406/R407: the ESP32's GPIO9 pull-up is weak, and A's reset-state pull-down could drag it low and start the ESP32 in download mode.

**Parts**

{{PARTS:U501, C502, C503, R501, C501, R502, R503, R504, TP503, TP504, TP505}}

**Wiring — U501**

{{IC:U501}}

{{TWO:C502, C503, R501, C501, R502, R503, R504}}

Test pads: {{ONE:TP503, TP504, TP505}}.

**Placement**

- Left edge, front half, **antenna end on the board edge**. The footprint's keep-out: no copper on any layer, no parts under or in front of the antenna. Keep pogo magnets and screws ≥ 15 mm away.
- C502/C503 at pin 3; R501/C501 at pin 8. Test pads where a probe or USB lead can reach.

---

## 8. Pogo interface

Sheet `pogo.kicad_sch`. **7 contacts**, dock side: `GND | +5V | DET | RX | TX | +5V | GND`; pad pin 1 meets dock pin 7 (the pad's pogo board is the mirror: `GND | +5V | TX | RX | DET | +5V | GND`). +5V and GND sit at both ends, two contacts each: the contacts are rated 1 A, so the pad can draw up to ≈ 1.45 A (the switch limit) with no LED dimming. Because +5V (pins 2, 6) and GND (pins 1, 7) are mirror-symmetric, a pad fitted the wrong way round still gets +5V on +5V and GND on GND: it is powered and charges normally. Only the UART lines cross (dock TX → pad DET, pad TX → dock DET, RX ↔ RX), all through 1 kΩ, so nothing is damaged; the pogo UART just doesn't work that way round.

```text
 J601 pin 1, pin 7 ── GND
 J601 pins 2 and 6 (+5V, both ends) ──●── POGO_5V ◄── U602 pin 1 OUT (SY6280)
                    ├── C602 10 µF, C603 1 µF ── GND
                    └── R607 10 k ──●── POGO_5V_SENSE ──► MCU A GPIO{{A:POGO_5V_SENSE}} (ADC{{ADC:POGO_5V_SENSE}})
                                    └── R608 15 k ── GND
 +5V ──●── U602 pin 5 IN;  C601 1 µF ── GND        U602 pin 3 ISET ── R606 4.7 k ── GND (1.45 A)
 U602 pin 4 EN ──●── POGO_EN ── R605 100 k ── +3V3
                 ├── Q601 drain   (Q601 gate = POGO_DET, source = GND)
                 └── Q602 drain   (Q602 gate = POGO_OFF ◄── MCU A GPIO{{A:POGO_OFF}}, R609 100 k to GND; source = GND)
 J601 pin 3 (DET) ──●── POGO_DET_J ── R603 1 k ──●── POGO_DET ──► MCU A GPIO{{A:POGO_DET}}, Q601 gate
                    └── U601 pin 4 (ESD)         └── R604 10 k ── +3V3
 J601 pin 4 (RX)  ──●── POGO_RX_J ── R602 1 k ── POGO_RX ──► MCU A GPIO{{A:POGO_RX}} (PIO UART RX)
                    └── U601 pin 3
 J601 pin 5 (TX)  ──●── POGO_TX_J ── R601 1 k ── POGO_TX ◄── MCU A GPIO{{A:POGO_TX}} (PIO UART TX)
                    └── U601 pin 6
 U601 pin 2 ── GND;  pins 1, 5: no-connect
```

How the enable works: undocked, DET is pulled up → Q601 on → EN low → contacts dead. Docked, the pad grounds DET → Q601 off → R605 pulls EN high → 5 V on, **with no firmware**. MCU A can veto by driving POGO_OFF high (Q602 on). Q602 exists so that A's reset-state pull-down on GPIO{{A:POGO_OFF}} means "no veto": a direct connection to EN would drag it to ≈ 1.1 V and stop pad charging whenever A has no firmware.

**Parts**

{{PARTS:J601, U601, R601, R602, R603, U602, Q601, Q602, R604, R605, R606, R609, C601, C602, C603, R607, R608}}

**Wiring**

{{IC:J601}}

{{IC:U601}}

{{IC:U602}}

{{FET:Q601, Q602}}

{{TWO:R601, R602, R603, R604, R605, R606, R609, C601, C602, C603, R607, R608}}

**Placement**

- J601 at the front edge, centre: **JST-XH 7-pin vertical header (B7B-XH-A)**, cable 1:1 to the lid pogo board (straight Motorobit 7-pin magnetic contacts; the pad docks on top). Hand-soldered.
- U601 right at J601; R601–R603 between U601 and the MCU A traces.
- U602, Q601, Q602 and their resistors behind J601; C602/C603 near J601. POGO_5V goes to **both** +5V pins of the header (pins 2 and 6): run it as a wide Power-class trace or pour to both pins so the two contacts share the current. Same for GND (pins 1 and 7).
- POGO_5V is Power class. Mark pin 1 on the silkscreen.

---

## 9. Signals that cross between sheets

Use a **global label** with exactly these names (the power nets GND, +3V3 and +5V are power symbols).

{{CROSS}}

---

## 10. Board-wide rules, PWR_FLAGs and no-connects

- **Power symbols** (`power:` library) only for GND, +3V3, +5V. VBUS_IN, KBD_VBUS and POGO_5V are global labels (Power net class by name).
- **PWR_FLAG** (so ERC knows these nets are supplied): VBUS_IN (J101 is a passive connector), +5V (comes out of an inductor), A_1V1 and B_1V1 (out of an inductor), A_VREG_AVDD and B_VREG_AVDD (through a resistor). +3V3, KBD_VBUS and POGO_5V are driven by power-output pins.
- **Local vs global**: A_* and B_* core nets (1V1, VREG_LX, VREG_AVDD, XIN, XOUT, XOUT_R, QSPI_SS, BOOTSEL_BTN, LED, LED_R, RUN, SWCLK/SWDIO of A), BUCK_*, PD_CFG1, KBD_ISET, POGO_ISET, POGO_EN, POGO_*_J and the *_USBJ_* connector-side pairs stay on their sheet.
- Net classes (project file): Power = VBUS_IN, +5V, +3V3, KBD_VBUS, POGO_5V, GND (0.6 mm); USB = `*USB*_D_P` / `*USB*_D_N` (both the connector side `*_USBJ_*` and the MCU side); everything else Default. Clearance 0.15 mm everywhere (RPi core layout).
- 4 layers: L1 parts + signals, **L2 solid GND**, L3 +3V3 / +5V pours, L4 signals. All SMD on top; only C201 and J601 are through-hole (hand-soldered).
- BUCK_SW is the noisiest net on the board: short, wide, away from BUCK_FB, crystals and the antenna.

**No-connect flags** (put an X on each):

{{NCLIST}}

---

## Appendix — full net index (generated)

Generated from the connection model that the tables above come from; checked against the placed schematic (every pin exactly once).

<details>
<summary>Show the full net index</summary>

{{APPENDIX}}

</details>
