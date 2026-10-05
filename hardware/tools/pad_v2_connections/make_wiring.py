"""Generate hardware/pad-v2/PAD_WIRING.md: a component-by-component wiring list (needs kicad-cli).

For every part, in the order of the groups on its sheet: every pin and exactly what it connects to,
plus which kind of label to draw. Built from pad_nets.py.
"""
import json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pad_nets import NETS, NC, GPIO, ESP_PIN, ESP_SIDE, GOES, CHAIN

NETFILE = os.path.join(tempfile.gettempdir(), 'pad_v2_wiring.net')
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', NETFILE,
                os.path.join(HERE, '..', '..', 'pad-v2', 'pad-v2.kicad_sch')], check=True, capture_output=True)
s = open(NETFILE).read()
COMP = {}
for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)(.*?)\n\t\t\)', s, re.S):
    b = m.group(2)
    f = {fm.group(1): fm.group(2) for fm in re.finditer(r'\(field\s*\(name "([^"]+)"\)\s*"((?:[^"\\]|\\.)*)"', b)}
    COMP[m.group(1)] = dict(value=re.search(r'\(value "([^"]*)"\)', b).group(1),
                            part=re.search(r'\(part "([^"]+)"\)', b).group(1), note=f.get('Note', ''))
# parts in the connection model / groups but not (or no longer) in the schematic
_model_refs = {p.split('.')[0] for p in [q for v in NETS.values() for q in v] + NC}
_model_refs |= {r for g in json.load(open(os.path.join(HERE, 'groups.json'))).values() for _, rs in g for r in rs}
for _r in _model_refs:
    COMP.setdefault(_r, dict(value='(not in the schematic)', fp='', part='', lcsc='', note='not in the schematic'))
PINNAME = {}
for m in re.finditer(r'\(libpart\s*\(lib "[^"]*"\)\s*\(part "([^"]+)"\)(.*?)\n\t\t\)', s, re.S):
    PINNAME[m.group(1)] = dict(re.findall(r'\(pin\s*\(num "([^"]+)"\)\s*\(name "([^"]*)"', m.group(2)))
GROUPS = json.load(open(os.path.join(HERE, 'groups.json')))

SHEET = {'1': 'POWER', '2': 'MCU', '3': 'INPUTS', '4': 'RGB', '5': 'DISPLAY'}
FILE = {'POWER': 'power.kicad_sch', 'MCU': 'mcu.kicad_sch', 'INPUTS': 'inputs.kicad_sch', 'RGB': 'rgb.kicad_sch', 'DISPLAY': 'display.kicad_sch'}
POWER_SYMBOLS = {'GND', '+3V3'}
PWR_FLAGS = {'POGO_5V': 'POWER', 'VIN_PROT': 'POWER', 'VSYS': 'POWER', 'VBAT': 'POWER', 'BAT_N': 'POWER', '+3V3': 'POWER', 'GND': 'POWER', '5V_RGB': 'RGB', 'DISP_VCC': 'DISPLAY'}
ZONE = {}

where = {p: n for n, pins in NETS.items() for p in pins}
ncset = set(NC)
sheet_of = lambda ref: SHEET[re.sub(r'\D', '', ref)[0]]

def pname(ref, pin):
    n = PINNAME.get(COMP[ref]['part'], {}).get(pin, '')
    n = n.replace('~{', '').replace('}', '')
    return n if n and n != pin and n != '~' else ''

def pinref(p):
    r, q = p.split('.', 1)
    n = pname(r, q)
    return f'{r}.{q}' + (f' ({n})' if n else '')

def net_sheets(net):
    return {sheet_of(p.split('.')[0]) for p in NETS[net]}

def draw(net, sheet):
    if net in POWER_SYMBOLS:
        return f'power symbol `{net}`'
    if len(net_sheets(net)) > 1:
        return f'**global label `{net}`**'
    return f'wire (or local label `{net}`)'

def partners(net, me, sheet):
    if net in POWER_SYMBOLS:
        return ''
    others = [p for p in NETS[net] if p.split('.')[0] != me]
    if len(others) > 12:
        return f'{len(others)} other pins: use the label'
    here = [pinref(p) for p in others if sheet_of(p.split('.')[0]) == sheet]
    away = {}
    for p in others:
        sh = sheet_of(p.split('.')[0])
        if sh != sheet:
            away.setdefault(sh, []).append(pinref(p))
    txt = ', '.join(here) if here else ''
    for sh, lst in away.items():
        txt += ('; ' if txt else '') + f'{sh} sheet: ' + ', '.join(lst)
    return txt or '(only this part)'

def pins_of(ref):
    ps = [p.split('.', 1)[1] for p in list(where) + NC if p.split('.', 1)[0] == ref]
    return sorted(set(ps), key=lambda x: (re.sub(r'\d', '', x), int(re.sub(r'\D', '', x) or 0)))

def component(ref, sheet):
    c = COMP[ref]
    head = f'#### {ref} · {c["value"]}' + (f' · {c["note"]}' if c['note'] else '')
    pins = pins_of(ref)
    if not pins:
        return head + '\n\nNo pins (mechanical only).\n'
    rows = ['| Pin | Net | Connects to | Draw |', '|---|---|---|---|']
    for q in pins:
        key = f'{ref}.{q}'
        n = pname(ref, q)
        pin = f'{q}' + (f' {n}' if n else '')
        if key in ncset:
            rows.append(f'| {pin} | — | nothing | no-connect flag (X) |')
        else:
            net = where[key]
            rows.append(f'| {pin} | {net} | {partners(net, ref, sheet)} | {draw(net, sheet)} |')
    return head + '\n\n' + '\n'.join(rows) + '\n'

out = ['# Pad v2 — Wiring List (component by component)', '',
       'Open a sheet, go through its parts in the order below (same order as the dashed group boxes), and for each pin draw what the **Draw** column says. After wiring, `python3 hardware/tools/pad_v2_connections/check_wiring.py` compares the schematic with this list (it checks which pins are joined; net names may differ).',
       '', 'How to draw each kind of connection:', '',
       '- **power symbol** `GND`, `+3V3`: KiCad power symbols (they connect across all sheets).',
       '- **global label**: the net continues on another sheet. Same name on every sheet where it appears.',
       '- **wire (or local label)**: the net stays on this sheet.',
       '- **no-connect flag**: the pin is deliberately unused: put an X on it.',
       '- Each connection appears at both of its ends. Draw it once.',
       '- Resistors, capacitors, inductors and push switches may be drawn either way round. The four ESD channels of a TPD4E1U06 (pins 1, 3, 4, 6) are interchangeable.',
       '', '## 1. Power chain', '', '```text',
       ' pogo +5V (J101 2, 6) ─ D101 TVS ─ U102 WS3222D (cuts off at 5.69 V) ─ VIN_PROT ─ U103 ETA6003 ─┬─ VSYS ─┬─ U105 LDO ─ +3V3 ─ ESP32, display, pull-ups',
       '                                                                                │        └─ U401 boost ─ 5V_RGB ─ 36 LEDs, U402',
       '                                                                                └─ VBAT ─ J102 battery + ;  battery − = BAT_N ─ Q101 ─ GND',
       '```', '',
       '- `BAT_N` (battery minus) is **not** GND: it reaches GND only through Q101 (the protection FETs). Only J102 pin 2, U104 GND, C107 and Q101 S1 are on BAT_N.',
       '- Put a PWR_FLAG on: ' + ', '.join(f'`{n}`' for n in PWR_FLAGS) + ' (ERC needs one on every supply net that no power-output pin drives).',
       '', '## 2. ESP32-S3 pin map', '',
       'Chosen for the placement in PCB_PLACEMENT.md (module at the front-left, rotation 90°): each signal leaves the module on the side facing its destination. All 39 GPIOs are used.', '',
       '| GPIO | Module pin | Net | Leaves the module at | Goes to |', '|---|---|---|---|---|']
for g in sorted(GPIO, key=lambda g: ESP_PIN[g]):
    n = GPIO[g]
    goes = GOES.get(n) or (f'SW3{int(n[3:]):02d} (key {n[3:]})' if n.startswith('KEY') else '')
    out.append(f'| {"TXD0 (IO43)" if g == 43 else "RXD0 (IO44)" if g == 44 else "IO" + str(g)} | {ESP_PIN[g]} | {n} | {ESP_SIDE[g]} | {goes} |')
out += ['', 'Notes:', '',
        '- **Strapping pins:** IO0 = BOOT button. IO45 must not be pulled high at reset (it carries only the encoder switch to GND). IO46 is low at reset (RGB data idles low). IO3 is a key to GND (harmless).',
        '- The display, encoder and key pins can be swapped among themselves in firmware (GPIO matrix); USB (IO19/20), UART0 (TXD0/RXD0) and the ADC pin IO10 are fixed.',
        '- Firmware: enable the internal pull-ups on the key, encoder-switch, toggle and BOOT pins.',
        '', '## 3. LED chain (firmware index = reference − 401)', '',
        '| Index | LED | Where |', '|---|---|---|']
for i, (k, w) in enumerate(CHAIN):
    out.append(f'| {i} | D4{i + 1:02d} | {w}{" (SK6812MINI-E, bottom)" if k == "K" else " (XL-2020, top)"} |')
out += ['', '## Sheets', '']
for sheet in ['POWER', 'MCU', 'INPUTS', 'RGB', 'DISPLAY']:
    f = FILE[sheet]
    refs = [r for g, rs in GROUPS[f] for r in rs]
    nets_here = {where[f'{r}.{q}'] for r in refs for q in pins_of(r) if f'{r}.{q}' in where}
    glob = sorted(n for n in nets_here if n not in POWER_SYMBOLS and len(net_sheets(n)) > 1)
    pwr = sorted(n for n in nets_here if n in POWER_SYMBOLS)
    flags = sorted(n for n, sh in PWR_FLAGS.items() if sh == sheet)
    ncs = sum(1 for p in NC if p.split('.')[0] in refs)
    out += ['---', '', f'## Sheet {sheet}', '',
            f'File `{f}` · {len(refs)} parts', '',
            f'- Power symbols: {", ".join("`" + n + "`" for n in pwr)}',
            f'- Global labels on this sheet: ' + (', '.join('`' + n + '`' for n in glob) if glob else 'none'),
            f'- PWR_FLAG on: ' + (', '.join('`' + n + '`' for n in flags) if flags else 'none'),
            f'- No-connect flags: {ncs}', '']
    for g, rs in GROUPS[f]:
        z = next((v for k, v in ZONE.items() if g.startswith(k)), '')
        out += [f'### {g}', '', f'On the PCB: {z}' if z else '', '']
        for r in rs:
            out.append(component(r, sheet))
open(os.path.join(HERE, '..', '..', 'pad-v2', 'PAD_WIRING.md'), 'w').write('\n'.join(out).replace('\n\n\n', '\n\n'))
print('written', len(out), 'blocks')
