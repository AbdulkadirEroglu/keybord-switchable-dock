#!/usr/bin/env python3
"""Pad v2: project files, custom symbols, and all parts placed (unwired) on five sheets."""
import re, uuid, os, math, json
HW = '/home/ae/Work/dock-pad/hardware'
PRJ = f'{HW}/pad-v2'
STD = '/usr/share/kicad/symbols'
CUSTOM = f'{PRJ}/pad_v2_custom.kicad_sym'
src = open('/home/ae/.claude/jobs/e7adcb65/tmp/place_parts.py').read()
helpers = src[src.index('# ------------------------------------------------------------------ symbol library access'):src.index('def main():')]
helpers = helpers.replace("lib == 'dock_v2_custom'", "lib == 'pad_v2_custom'")
exec(helpers)

# ---------------------------------------------------------------- custom symbol library
EFF = '(effects\n\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t)\n\t\t\t\t\t)'
def prop(k, v, y=0, hide=True):
    h = '\n\t\t\t(hide yes)' if hide else ''
    return f'\t\t(property "{k}" "{v}"\n\t\t\t(at 0 {y} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no){h}\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
def ic(name, fp, ds, desc, left, right, w=10.16):
    n = max(len(left), len(right)); top = 2.54 * (n - 1) / 2; top = round(top / 2.54) * 2.54 if n % 2 else top
    h = top + 2.54
    pins = []
    for side, lst in ((-1, left), (1, right)):
        for i, p in enumerate(lst):
            if p is None: continue
            num, nm, typ = p
            y = top - 2.54 * i
            pins.append(f'\t\t\t(pin {typ} line\n\t\t\t\t(at {side * (w + 2.54):g} {y:g} {0 if side < 0 else 180})\n\t\t\t\t(length 2.54)\n\t\t\t\t(name "{nm}"\n\t\t\t\t\t{EFF}\n\t\t\t\t)\n\t\t\t\t(number "{num}"\n\t\t\t\t\t{EFF}\n\t\t\t\t)\n\t\t\t)')
    return (f'\t(symbol "{name}"\n\t\t(pin_names\n\t\t\t(offset 1.016)\n\t\t)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(duplicate_pin_numbers_are_jumpers no)\n'
            + prop('Reference', 'U', h + 1.27, False) + '\n' + prop('Value', name, -h - 1.27, False) + '\n' + prop('Footprint', fp) + '\n' + prop('Datasheet', ds) + '\n' + prop('Description', desc) + '\n'
            + f'\t\t(symbol "{name}_0_1"\n\t\t\t(rectangle\n\t\t\t\t(start {-w:g} {h:g})\n\t\t\t\t(end {w:g} {-h:g})\n\t\t\t\t(stroke\n\t\t\t\t\t(width 0.254)\n\t\t\t\t\t(type default)\n\t\t\t\t)\n\t\t\t\t(fill\n\t\t\t\t\t(type background)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
            + f'\t\t(symbol "{name}_1_1"\n' + '\n'.join(pins) + '\n\t\t)\n\t\t(embedded_fonts no)\n\t)')
dockc = open(f'{HW}/dock-v2/dock_v2_custom.kicad_sym').read()
padc = open(f'{HW}/pad/pad_custom.kicad_sym').read()
head = dockc[:dockc.index('\t(symbol "')]
syms = ['\t' + block(dockc, 'TPD4E1U06DBV'), '\t' + block(padc, 'TPS61023DRL'), '\t' + block(padc, 'FS8205A'),
  ic('ETA6003', 'Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm', 'https://www.lcsc.com/datasheet/C5455585.pdf',
     '2.5 A 3 MHz switching Li-ion charger with dynamic power path. IN 4.4-5.5 V (6 V abs). Icharge = 1000/RISET (A). ENB low = charge. QFN3x3-16',
     [('2', 'IN', 'power_in'), ('6', '~{ENB}', 'input'), ('13', 'USB_DET', 'input'), ('11', 'ISET1', 'passive'), ('12', 'ISET2', 'passive'), ('7', 'NTC', 'input'), ('8', 'ENPPB', 'input'), ('9', 'STAT', 'open_collector')],
     [('3', 'SW', 'power_out'), ('4', 'SW', 'passive'), ('1', 'SYS', 'power_out'), ('15', 'SYS', 'passive'), ('14', 'BATT', 'bidirectional'), ('16', 'BATT', 'passive'), ('5', 'PGND', 'power_in'), ('10', 'GND', 'power_in'), ('17', 'EP', 'passive')], w=12.7),
  ic('WS3222D', 'Package_DFN_QFN:DFN-8-1EP_2x2mm_P0.5mm_EP0.9x1.7mm', 'https://www.lcsc.com/datasheet/C239703.pdf',
     'Overvoltage protection load switch, IN up to 28 V (29 V abs), 45 mOhm, 3 A. OVLO = 1.2 V x (1 + R1/R2), reference 1.17-1.23 V. DFN2x2-8',
     [('6', 'IN', 'power_in'), ('7', 'IN', 'passive'), ('8', 'IN', 'passive'), ('5', 'OVLO', 'input')],
     [('1', 'OUT', 'power_out'), ('2', 'OUT', 'passive'), ('3', 'OUT', 'passive'), ('4', 'GND', 'power_in'), ('9', 'EP', 'passive')])]
os.makedirs(PRJ, exist_ok=True)
open(CUSTOM, 'w').write(head + '\n'.join(syms) + '\n)\n')

# ---------------------------------------------------------------- parts
R0402 = 'Resistor_SMD:R_0402_1005Metric'; C0402 = 'Capacitor_SMD:C_0402_1005Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'; C0805 = 'Capacitor_SMD:C_0805_2012Metric'
def R(v, lcsc, fp=R0402): return ('Device:R', v, fp, lcsc)
def C(v, lcsc, fp=C0402): return ('Device:C', v, fp, lcsc)
L = dict(r1k='C11702', r2k2='C25879', r5k1='C25905', r6k8='C25917', r10k='C25744', r15k='C25756', r33k='C25779', r51k='C25794',
         r100k='C25741', r33='C25105', c10n='C15195', c100n='C1525', c1u='C52923', c1u50_0603='C15849', c10u='C15850', c22u='C45783')
TPD = ('pad_v2_custom:TPD4E1U06DBV', 'TPD4E1U06DBVR', 'Package_TO_SOT_SMD:SOT-23-6', 'C124691')
BTN = ('Switch:SW_Push', 'SW_Push', 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A', 'C318884')
HOLE = ('Mechanical:MountingHole', 'M3', 'MountingHole:MountingHole_3.2mm_M3', '')
RING = ('LED:WS2812B-2020', 'XL-2020RGBC-WS2812B', 'pad_v2:LED_XL-2020RGBC_2.0x2.0mm', 'C5349955')
KLED = ('LED:SK6812MINI-E', 'SK6812MINI-E', 'LED_SMD:LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount', 'C5149201')
MX = ('Switch:SW_Push', 'MX switch (hot-swap socket)', 'dock:SW_MX_Hotswap_Kailh', '')
ENC = ('Device:RotaryEncoder_Switch_MP', 'PEC11R-4220F-S0024', 'dock:RotaryEncoder_Bourns_PEC11R-4xxxF-S_Vertical', '')

def led_groups():
    order = [('Ring 1 (ENC1), clockwise from 6 o\'clock', RING, [f'ring 1, {h} o\'clock' for h in (6,7,8,9,10,11,12,1,2,3,4,5)]),
             ('Key LEDs, keys 1-4', KLED, [f'key {k} (bottom side, HAND-SOLDER)' for k in (1,2,3,4)]),
             ('Ring 2 (ENC2), clockwise from 7 o\'clock', RING, [f'ring 2, {h} o\'clock' for h in (7,8,9,10,11,12,1,2,3,4,5,6)]),
             ('Key LEDs, keys 8, 7, 6, 5', KLED, [f'key {k} (bottom side, HAND-SOLDER)' for k in (8,7,6,5)]),
             ('Key LEDs, keys 9-12', KLED, [f'key {k} (bottom side, HAND-SOLDER)' for k in (9,10,11,12)])]
    out, n = [], 1
    for name, part, notes in order:
        g = []
        for note in notes:
            g.append((f'D4{n:02d}', *part, f'chain index {n - 1}: {note}'))
            g.append((f'C4{n + 4:02d}', *C('100nF', L['c100n']), f'at D4{n:02d} VDD (top side)'))
            n += 1
        out.append((name, g))
    return out

SHEETS = {
 'power.kicad_sch': ('POWER', [
  ('Pogo input (front strip)', [
    ('J101', 'Connector_Generic:Conn_01x07', 'Pogo cable (to floor board)', 'Connector_JST:JST_XH_S7B-XH-A_1x07_P2.50mm_Horizontal', '', 'HAND-SOLDER, bottom. 1 GND, 2 +5V, 3 PAD_RX (dock TX), 4 PAD_TX (dock RX), 5 DET -> GND, 6 +5V, 7 GND'),
    ('D101', 'Device:D_TVS', 'SMBJ15A', 'Diode_SMD:D_SMB', 'C113988', 'TVS on the pogo +5V (before the OVP switch)'),
    ('U101', *TPD, 'ESD on PAD_RX and PAD_TX at J101'),
    ('R101', *R('1k', L['r1k']), 'PAD_RX series (to ESP RXD0)'),
    ('R102', *R('1k', L['r1k']), 'PAD_TX series (from ESP TXD0)'),
  ]),
  ('Overvoltage switch WS3222D (5.69 V)', [
    ('U102', 'pad_v2_custom:WS3222D', 'WS3222D', 'Package_DFN_QFN:DFN-8-1EP_2x2mm_P0.5mm_EP0.9x1.7mm', 'C239703', 'pogo +5V -> VIN_PROT (charger input); EP to GND'),
    ('C101', *C('1uF 50V', L['c1u50_0603'], C0603), 'U102 IN'),
    ('R103', *R('51k', L['r51k']), 'OVLO top, part 1 (IN to R104)'),
    ('R104', *R('5.1k', L['r5k1']), 'OVLO top, part 2 (R103 to OVLO): 56.1k total'),
    ('R105', *R('15k', L['r15k']), 'OVLO bottom: 1.2 x (1 + 56.1/15) = 5.69 V'),
    ('R106', *R('10k', L['r10k']), 'dock-5V sense top (VIN_PROT -> ADC)'),
    ('R107', *R('15k', L['r15k']), 'dock-5V sense bottom'),
  ]),
  ('Charger ETA6003 (1 A / 0.45 A, power path)', [
    ('U103', 'pad_v2_custom:ETA6003', 'ETA6003', 'Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm', 'C5455585', 'ENPPB to GND; ENB low = charge; USB_DET high = ISET2; EP to GND'),
    ('C102', *C('10uF', L['c10u'], C0805), 'IN (pin 2) to PGND (pin 5), closest to the IC'),
    ('C103', *C('10uF', L['c10u'], C0805), 'IN to GND (pin 10)'),
    ('L101', 'Device:L', '2.2uH', 'Inductor_SMD:L_APV_ANR4030', '', 'SW to SYS. Isat >= 3.5 A, 4x4 mm (LCSC number at BOM time)'),
    ('C104', *C('22uF', L['c22u'], C0805), 'SYS output'),
    ('C105', *C('22uF', L['c22u'], C0805), 'SYS output'),
    ('C106', *C('10uF', L['c10u'], C0805), 'BATT'),
    ('R108', *R('1k', L['r1k']), 'ISET1: 1.0 A (USB_DET low)'),
    ('R109', *R('2.2k', L['r2k2']), 'ISET2: 0.45 A (USB_DET high)'),
    ('R110', *R('10k', L['r10k']), 'NTC top a (IN to NTC), parallel with R111'),
    ('R111', *R('33k', L['r33k']), 'NTC top b: 10k || 33k = 7.67k'),
    ('R112', *R('100k', L['r100k']), 'NTC to GND (parallel with the 10k B3950 NTC): charge window 0-45 C'),
    ('R113', *R('100k', L['r100k']), 'ENB pull-down: charging on without firmware'),
    ('R114', *R('10k', L['r10k']), 'STAT pull-up to 3V3'),
  ]),
  ('Battery protection and sense', [
    ('J102', 'Connector_Generic:Conn_01x04', 'Battery 1x 21700 + NTC', 'Connector_JST:JST_XH_S4B-XH-A_1x04_P2.50mm_Horizontal', '', 'HAND-SOLDER, bottom. 1 B+, 2 B-, 3 NTC, 4 NTC return (GND)'),
    ('U104', 'Battery_Management:DW01A', 'DW01A', 'Package_TO_SOT_SMD:SOT-23-6', 'C351410', 'cell protection'),
    ('Q101', 'pad_v2_custom:FS8205A', 'FS8205A', 'Package_SO:TSSOP-8_4.4x3mm_P0.65mm', 'C14212', 'dual N-FET between B- and GND'),
    ('R115', *R('100', ''), 'DW01A VCC series (100 ohm; LCSC number at BOM time)'),
    ('C107', *C('100nF', L['c100n']), 'DW01A VCC'),
    ('R116', *R('1k', L['r1k']), 'DW01A CS'),
    ('R117', *R('100k', L['r100k']), 'battery sense top (BATT -> ADC)'),
    ('R118', *R('100k', L['r100k']), 'battery sense bottom'),
    ('C108', *C('100nF', L['c100n']), 'battery sense filter'),
  ]),
  ('3.3 V LDO (left strip, near the ESP32)', [
    ('U105', 'Regulator_Linear:TLV75733PDBV', 'TLV75733PDBV', 'Package_TO_SOT_SMD:SOT-23-5', 'C485517', 'VSYS -> 3V3, EN tied to IN'),
    ('C109', *C('1uF', L['c1u']), 'LDO input'),
    ('C110', *C('1uF', L['c1u']), 'LDO output'),
  ]),
  ('Mounting holes (M3)', [(f'H10{i}', *HOLE, n) for i, n in enumerate(['(4.5, 38)', '(95.5, 38)', '(4.5, 66)', '(95.5, 80)', '(60, 93)'], 1)]),
 ]),
 'mcu.kicad_sch': ('MCU', [
  ('ESP32-S3-MINI-1 (front-left, antenna at the left edge)', [
    ('U201', 'RF_Module:ESP32-S3-MINI-1', 'ESP32-S3-MINI-1-N8', 'pad_v2:ESP32-S3-MINI-1', 'C2913206', 'position (9.50, 92.30), rotation 90'),
    ('C201', *C('10uF', L['c10u'], C0805), '3V3 at the module'),
    ('C202', *C('100nF', L['c100n']), '3V3 at the module'),
  ]),
  ('Reset and boot', [
    ('R201', *R('10k', L['r10k']), 'EN pull-up'),
    ('C203', *C('1uF', L['c1u']), 'EN to GND (RC delay)'),
    ('SW201', *BTN, 'RESET: EN to GND'),
    ('SW202', *BTN, 'BOOT: GPIO0 to GND'),
  ]),
  ('USB-C (flashing / debug only, left edge)', [
    ('J201', 'Connector:USB_C_Receptacle_USB2.0_16P', 'TYPE-C-31-M-12', 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'C165948', 'D+/D- to GPIO20/GPIO19; VBUS not used'),
    ('U202', *TPD, 'ESD on D+, D-'),
    ('R202', *R('5.1k', L['r5k1']), 'CC1 Rd'),
    ('R203', *R('5.1k', L['r5k1']), 'CC2 Rd'),
  ]),
 ]),
 'inputs.kicad_sch': ('INPUTS', [
  ('Keys 1-12 (one GPIO each, other side to GND)', [(f'SW3{k:02d}', *MX, f'key {k}; socket HAND-SOLDER, bottom') for k in range(1, 13)]),
  ('Encoder 1: volume (left)', [
    ('SW313', *ENC, 'HAND-SOLDER. C and MP (lugs) to GND; A, B through the RC filter; switch to a GPIO'),
    ('R301', *R('10k', L['r10k']), 'A pull-up to 3V3'), ('R302', *R('10k', L['r10k']), 'B pull-up to 3V3'),
    ('R303', *R('10k', L['r10k']), 'A series'), ('R304', *R('10k', L['r10k']), 'B series'),
    ('C301', *C('10nF', L['c10n']), 'A filter, GPIO side'), ('C302', *C('10nF', L['c10n']), 'B filter, GPIO side'),
  ]),
  ('Encoder 2: mic / call (right)', [
    ('SW314', *ENC, 'HAND-SOLDER'),
    ('R305', *R('10k', L['r10k']), 'A pull-up to 3V3'), ('R306', *R('10k', L['r10k']), 'B pull-up to 3V3'),
    ('R307', *R('10k', L['r10k']), 'A series'), ('R308', *R('10k', L['r10k']), 'B series'),
    ('C303', *C('10nF', L['c10n']), 'A filter, GPIO side'), ('C304', *C('10nF', L['c10n']), 'B filter, GPIO side'),
  ]),
  ('Selector toggle (on the case)', [
    ('J301', 'Connector_Generic:Conn_01x03', 'Toggle PERSONAL-OFF-WORK', 'Connector_JST:JST_XH_S3B-XH-A_1x03_P2.50mm_Horizontal', '', 'HAND-SOLDER, bottom. 1 PERSONAL, 2 GND (common), 3 WORK'),
  ]),
 ]),
 'rgb.kicad_sch': ('RGB', [
  ('5 V boost TPS61023 (power strip)', [
    ('U401', 'pad_v2_custom:TPS61023DRL', 'TPS61023DRLR', 'Package_TO_SOT_SMD:SOT-563', 'C919459', 'VSYS -> 5V_RGB; EN from a GPIO (true disconnect when low)'),
    ('L401', 'Device:L', '1uH', 'Inductor_SMD:L_APV_ANR4030', 'C5289359', 'XRNR4030-1uH/N, Isat 5.26 A'),
    ('C401', *C('10uF', L['c10u'], C0805), 'boost input'),
    ('C402', *C('22uF', L['c22u'], C0805), '5V_RGB output'),
    ('C403', *C('22uF', L['c22u'], C0805), '5V_RGB output'),
    ('R401', *R('51k', L['r51k']), 'FB top: 0.595 x (1 + 51/6.8) = 5.06 V'),
    ('R402', *R('6.8k', L['r6k8']), 'FB bottom'),
    ('R403', *R('100k', L['r100k']), 'EN pull-down (LEDs off at reset)'),
  ]),
  ('Data level shifter', [
    ('U402', '74xGxx:74AHCT1G125', 'SN74AHCT1G125DBVR', 'Package_TO_SOT_SMD:SOT-23-5', 'C7484', 'powered from 5V_RGB; OE to GND'),
    ('C404', *C('100nF', L['c100n']), 'U402 VCC'),
    ('R404', *R('33', L['r33']), 'series, U402 output to D401 DIN'),
  ]),
 ] + led_groups()),
 'display.kicad_sch': ('DISPLAY', [
  ('Display connector (back strip, bottom side)', [
    ('J501', 'Connector_Generic:Conn_01x09', 'Display 1.69in ST7789V3', 'Connector_JST:JST_PH_S9B-PH-K_1x09_P2.00mm_Horizontal', '', 'HAND-SOLDER. 1 BLK, 2 CS, 3 DC, 4 RES, 5 SDA, 6 SCL, 7 VCC, 8 GND, 9 GND'),
    ('C501', *C('1uF', L['c1u']), 'DISP_VCC at J501'),
  ]),
  ('Display power switch', [
    ('Q501', 'Transistor_FET:AO3401A', 'AO3401A', 'Package_TO_SOT_SMD:SOT-23', 'C15127', 'source 3V3, drain DISP_VCC, gate to a GPIO (low = on)'),
    ('R501', *R('100k', L['r100k']), 'gate pull-up to 3V3 (off at reset)'),
  ]),
 ]),
}

# ---------------------------------------------------------------- root sheet, project
U = lambda: str(uuid.uuid4())
keep = f'{PRJ}/.uuids.json'
ids = json.load(open(keep)) if os.path.exists(keep) else {'root': U(), **{f: [U(), U()] for f in SHEETS}}
json.dump(ids, open(keep, 'w'))
ROOT = ids['root']

def sheet_block(i, fname, name):
    x, y = 20 + (i % 3) * 70, 50 + (i // 3) * 45
    def p(k, v, yy, j): return f'\t\t(property "{k}" "{v}"\n\t\t\t(at {x} {yy:g} 0)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left {j})\n\t\t\t)\n\t\t)'
    return (f'\t(sheet\n\t\t(at {x} {y})\n\t\t(size 50.8 25.4)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(stroke\n\t\t\t(width 0.1524)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill\n\t\t\t(color 0 0 0 0)\n\t\t)\n\t\t(uuid "{ids[fname][1]}")\n'
            + p('Sheetname', name, y - 0.9, 'bottom') + '\n' + p('Sheetfile', fname, y + 26.3, 'top')
            + f'\n\t\t(instances\n\t\t\t(project "pad-v2"\n\t\t\t\t(path "/{ROOT}"\n\t\t\t\t\t(page "{i + 2}")\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)')
root = f'''(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "{ROOT}")
	(paper "A4")
	(title_block
		(title "Pad v2 - top level")
		(date "2026-10-04")
		(rev "v2.0")
		(comment 1 "ESP32-S3-MINI-1, 1x 21700 + ETA6003, sits on top of the dock, JLCPCB assembly (top side)")
		(comment 2 "Decisions: docs/pad-v2-*.md; placement: hardware/pad-v2/PCB_PLACEMENT.md")
	)
	(lib_symbols)
{chr(10).join(sheet_block(i, f, n) for i, (f, (n, _)) in enumerate(SHEETS.items()))}
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)
'''
open(f'{PRJ}/pad-v2.kicad_sch', 'w').write(root)

pro = json.load(open(f'{HW}/dock-v2/dock-v2.kicad_pro'))
pro['meta']['filename'] = 'pad-v2.kicad_pro'
pro['sheets'] = [[ROOT, 'pad-v2']] + [[ids[f][1], n] for f, (n, _) in SHEETS.items()]
if 'top_level_sheets' in pro.get('schematic', {}): pro['schematic']['top_level_sheets'] = [{'filename': 'pad-v2.kicad_sch', 'name': 'pad-v2', 'uuid': ROOT}]
pro['net_settings']['netclass_patterns'] = [{'netclass': 'Power', 'pattern': p} for p in ('GND', 'POGO_5V', 'VIN_PROT', 'VSYS', 'VBAT', 'BAT_N', '3V3*', '+3V3', '5V_RGB', 'DISP_VCC')] + [{'netclass': 'USB', 'pattern': p} for p in ('USB_DP', 'USB_DN', 'USB_D_P', 'USB_D_N')]
pro['net_settings']['netclass_assignments'] = None
json.dump(pro, open(f'{PRJ}/pad-v2.kicad_pro', 'w'), indent=2)
open(f'{PRJ}/sym-lib-table', 'w').write('(sym_lib_table\n\t(version 7)\n\t(lib (name "pad_v2_custom") (type "KiCad") (uri "${KIPRJMOD}/pad_v2_custom.kicad_sym") (options "") (descr "Pad v2 project symbols"))\n)\n')
open(f'{PRJ}/fp-lib-table', 'w').write('(fp_lib_table\n\t(version 7)\n\t(lib (name "dock") (type "KiCad") (uri "${KIPRJMOD}/../libraries/dock.pretty") (options "") (descr "Shared footprints: MX hot-swap, PEC11R, pogo"))\n\t(lib (name "pad_v2") (type "KiCad") (uri "${KIPRJMOD}/../libraries/pad_v2.pretty") (options "") (descr "Pad v2 footprints: ESP32-S3-MINI-1, XL-2020 LED"))\n)\n')

# ---------------------------------------------------------------- sheets
main_src = src[src.index('def main():'):src.index('\nmain()')]
body = main_src[main_src.index("        libsyms, placed, graphics = {}, [], []"):main_src.index("        open(path, 'w').write(out)")]
body = body.replace('(project "dock-v2"', '(project "pad-v2"').replace('{root_uuid}/{sheet_uuid[fname]}', '{ROOT}/{ids[fname][1]}')
body = body.replace('W, H = 420.0, 297.0', 'W, H = (841.0, 594.0) if fname == "rgb.kicad_sch" else (420.0, 297.0)').replace('(paper "A3")', '(paper "{"A1" if fname == "rgb.kicad_sch" else "A3"}")')
body = body.replace('(date "2026-09-29")', '(date "2026-10-04")').replace('Values/LCSC from docs/dock-v2-*.md', 'Values from docs/pad-v2-*.md')
code = "for fname, (title_, groups) in SHEETS.items():\n    if True:\n        path = f'{PRJ}/{fname}'; own_uuid = ids[fname][0]; title = 'Pad v2 - ' + title_\n" + body + "        open(path, 'w').write(out)\n        print(f'{fname}: {len(placed)} parts, rows end at y={rowy + rowh:.0f} mm')\n"
exec(code)
