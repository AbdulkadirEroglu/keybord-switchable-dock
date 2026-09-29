"""Generate hardware/dock-v2/DOCK_WIRING.md: a component-by-component wiring list (needs kicad-cli).

For every part, in the order of the groups on its sheet: every pin and exactly what it connects to,
plus which kind of label to draw. Built from dock_nets.py (the same model as DOCK_CONNECTIONS.md).
"""
import json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dock_nets import NETS, NC

NETFILE = os.path.join(tempfile.gettempdir(), 'dock_v2_wiring.net')
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', NETFILE,
                os.path.join(HERE, '..', '..', 'dock-v2', 'dock-v2.kicad_sch')], check=True, capture_output=True)
s = open(NETFILE).read()
COMP = {}
for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)(.*?)\n\t\t\)', s, re.S):
    b = m.group(2)
    f = {fm.group(1): fm.group(2) for fm in re.finditer(r'\(field\s*\(name "([^"]+)"\)\s*"((?:[^"\\]|\\.)*)"', b)}
    COMP[m.group(1)] = dict(value=re.search(r'\(value "([^"]*)"\)', b).group(1),
                            part=re.search(r'\(part "([^"]+)"\)', b).group(1), note=f.get('Note', ''))
PINNAME = {}
for m in re.finditer(r'\(libpart\s*\(lib "[^"]*"\)\s*\(part "([^"]+)"\)(.*?)\n\t\t\)', s, re.S):
    PINNAME[m.group(1)] = dict(re.findall(r'\(pin\s*\(num "([^"]+)"\)\s*\(name "([^"]*)"', m.group(2)))
GROUPS = json.load(open(os.path.join(HERE, 'groups.json')))

SHEET = {'1': 'POWER', '2': 'USB_PORTS', '3': 'MCU_A', '4': 'MCU_B', '5': 'BLE', '6': 'POGO'}
FILE = {'POWER': 'power.kicad_sch', 'USB_PORTS': 'usb_ports.kicad_sch', 'MCU_A': 'mcu_a.kicad_sch',
        'MCU_B': 'mcu_b.kicad_sch', 'BLE': 'ble.kicad_sch', 'POGO': 'pogo.kicad_sch'}
POWER_SYMBOLS = {'GND', '+3V3', '+5V'}
PWR_FLAGS = {'VBUS_IN': 'POWER', '+5V': 'POWER', 'A_1V1': 'MCU_A', 'A_VREG_AVDD': 'MCU_A',
             'B_1V1': 'MCU_B', 'B_VREG_AVDD': 'MCU_B'}
ZONE = {
    'USB-C power input': 'right edge, y ≈ 48 (J101 mouth on the edge; ESD and TVS within 5 mm)',
    'PD sink CH224A': 'right edge, next to J101',
    '5 V buck TPS54331': 'front-right corner (keep the hot loop tiny)',
    '3.3 V LDO': 'centre of the board, ≈ (45, 38)',
    'Mounting holes': '(4, 4), (86, 4), (86, 66), (20, 66)',
    'Keyboard port J201': 'left edge, y ≈ 18 (22 Ω resistors near MCU A)',
    'Keyboard VBUS switch': 'between J201 and the +5V trunk; C201 (THT) at J201',
    'Personal PC port J202': 'back edge, left, above MCU A (22 Ω near MCU A)',
    'Work PC port J203': 'back edge, right, above MCU B (22 Ω near MCU B)',
    'RP2354A A': 'back-left, ≈ (24, 22); regulator/USB side towards J202',
    'RP2354A B': 'back-right, ≈ (64, 22); regulator/USB side towards J203',
    'Core regulator': 'around the MCU exactly as Raspberry Pi (placed by copy_rpi_core_layout.py)',
    'Decoupling': 'one capacitor on each power pin (placed by copy_rpi_core_layout.py)',
    'Crystal': 'next to XIN/XOUT (placed by copy_rpi_core_layout.py)',
    'Buttons, SWD pads, LED': 'near the MCU, buttons reachable from above',
    'ESP32-C3-MINI-1': 'left edge, front half, antenna end on the edge, keep-out clear',
    'Reset / boot straps': 'at the module\'s EN (8), GPIO8/9 (22/23), GPIO2 (5) pins',
    'Test pads': 'near the module, reachable with a probe',
    'Pogo connector': 'front edge, centre (hand-soldered); ESD right at the pins',
    'Pogo 5 V switch': 'behind J601',
}

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

out = ['# Dock v2 — Wiring List (component by component)', '',
       'Open a sheet, go through its parts in the order below (same order as the dashed group boxes on the sheet), and for each pin draw what the **Draw** column says.',
       'Generated from the same checked connection model as [DOCK_CONNECTIONS.md](DOCK_CONNECTIONS.md) (the sketches and reasons are there). After wiring, `python3 hardware/tools/dock_v2_connections/check_wiring.py` compares the schematic with this list.',
       '', 'How to draw each kind of connection:', '',
       '- **power symbol** `GND`, `+3V3`, `+5V`: the KiCad power symbols (they connect across all sheets by themselves).',
       '- **global label**: the net continues on another sheet. Use a global label with exactly this name on every sheet where it appears.',
       '- **wire (or local label)**: the net stays on this sheet. Draw a wire to the listed pins, or put the same local label on each pin if the parts are far apart.',
       '- **no-connect flag**: the pin is deliberately unused: put an X on it.',
       '- The same net is listed at every pin that belongs to it, so each connection appears twice (once from each end). Draw it once.',
       '- `A_*` and `B_*` nets are each MCU\'s own (for example A_1V1 and B_1V1): use local labels, never power symbols, or the two chips\' rails would be joined.',
       '', '## Contents', '']
for sheet in ['POWER', 'USB_PORTS', 'MCU_A', 'MCU_B', 'BLE', 'POGO']:
    out.append(f'- [{sheet}](#sheet-{sheet.lower().replace("_", "_")})')
out.append('')

for sheet in ['POWER', 'USB_PORTS', 'MCU_A', 'MCU_B', 'BLE', 'POGO']:
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
open(os.path.join(HERE, '..', '..', 'dock-v2', 'DOCK_WIRING.md'), 'w').write('\n'.join(out).replace('\n\n\n', '\n\n'))
print('written', len(out), 'blocks')
