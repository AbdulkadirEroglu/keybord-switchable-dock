"""Regenerate hardware/dock-v2/DOCK_CONNECTIONS.md from dock_nets.py + template.md (needs kicad-cli)."""
import json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dock_nets import NETS, NC, LOCAL_PREFIX, A_GPIO, B_GPIO, GPIO_PIN

NETFILE = os.path.join(tempfile.gettempdir(), 'dock_v2_placed.net')
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', NETFILE,
                os.path.join(HERE, '..', '..', 'dock-v2', 'dock-v2.kicad_sch')], check=True, capture_output=True)
s = open(NETFILE).read()
COMP = {}
for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)(.*?)\n\t\t\)', s, re.S):
    b = m.group(2)
    f = dict(re.findall(r'\(field\s*\(name "([^"]+)"\)\s*(?:\(value "([^"]*)"\)|"([^"]*)")', b)) if False else {}
    for fm in re.finditer(r'\(field\s*\(name "([^"]+)"\)\s*"((?:[^"\\]|\\.)*)"', b):
        f[fm.group(1)] = fm.group(2)
    COMP[m.group(1)] = dict(value=re.search(r'\(value "([^"]*)"\)', b).group(1),
                            fp=(re.search(r'\(footprint "([^"]*)"\)', b) or [None, ''])[1],
                            part=re.search(r'\(part "([^"]+)"\)', b).group(1),
                            lcsc=f.get('LCSC', ''), note=f.get('Note', ''))
# parts in the connection model / groups but not (or no longer) in the schematic
_model_refs = {p.split('.')[0] for p in [q for v in NETS.values() for q in v] + NC}
_model_refs |= {r for g in json.load(open(os.path.join(HERE, 'groups.json'))).values() for _, rs in g for r in rs}
for _r in _model_refs:
    COMP.setdefault(_r, dict(value='(not in the schematic)', fp='', part='', lcsc='', note='not in the schematic'))
PINNAME = {}
for m in re.finditer(r'\(libpart\s*\(lib "[^"]*"\)\s*\(part "([^"]+)"\)(.*?)\n\t\t\)', s, re.S):
    PINNAME[m.group(1)] = dict(re.findall(r'\(pin\s*\(num "([^"]+)"\)\s*\(name "([^"]*)"', m.group(2)))

where = {}
for net, pins in NETS.items():
    for p in pins:
        where[p] = net
ncset = set(NC)

def pn(ref, pin):
    n = PINNAME.get(COMP[ref]['part'], {}).get(pin, '')
    return n.replace('~{', '').replace('}', '') if n and n != pin else ''

def bold(net):
    return net if net.startswith(LOCAL_PREFIX) or net in ('KBD_ISET', 'POGO_ISET', 'POGO_EN', 'POGO_DET_J', 'POGO_RX_J', 'POGO_TX_J', 'BLE_GPIO2', 'BLE_GPIO8') or '_USBJ_' in net else f'**{net}**'

def fp_short(fp):
    return fp.split(':')[-1] if fp else '— (choose)'

def parts_table(refs):
    out = ['| Ref | Value | Footprint | LCSC | Job |', '|---|---|---|---|---|']
    for r in refs:
        c = COMP[r]
        out.append(f"| {r} | {c['value']} | `{fp_short(c['fp'])}` | {c['lcsc'] or '—'} | {c['note'].replace('|', chr(92) + '|')} |")
    return '\n'.join(out)

def others(net, me, limit=8):
    o = [p for p in NETS[net] if not p.startswith(me + '.')]
    if net in ('GND', '+3V3', '+5V') and len(o) > limit:
        return f'{len(o)} other pins'
    return ', '.join(o[:limit]) + (' …' if len(o) > limit else '')

def ic_table(ref):
    pins = sorted({p.split('.', 1)[1] for p in list(where) + NC if p.split('.', 1)[0] == ref},
                  key=lambda x: (len(x), x))
    pins = sorted(pins, key=lambda x: (re.sub(r'\d', '', x), int(re.sub(r'\D', '', x) or 0)))
    out = [f'| {ref} pin | Name | Net | Also on this net |', '|---|---|---|---|']
    for p in pins:
        key = f'{ref}.{p}'
        if key in ncset:
            out.append(f'| {p} | {pn(ref, p)} | no-connect flag | |')
        else:
            n = where[key]
            out.append(f'| {p} | {pn(ref, p)} | {bold(n)} | {others(n, ref)} |')
    return '\n'.join(out)

def two_table(refs):
    out = ['| Part | Pin 1 | Pin 2 |', '|---|---|---|']
    for r in refs:
        a, b = where.get(f'{r}.1', 'no-connect'), where.get(f'{r}.2', 'no-connect')
        note = {'D_Schottky': ' (1 = K, 2 = A)', 'LED': ' (1 = K, 2 = A)', 'D_TVS': ' (1 = cathode band)',
                'C_Polarized': ' (1 = +)', 'L': ''}.get(COMP[r]['part'], '')
        out.append(f'| {r}{note} | {bold(a)} | {bold(b)} |')
    return '\n'.join(out)

def three(refs):
    out = ['| Part | Gate (1) | Source (2) | Drain (3) |', '|---|---|---|---|']
    for r in refs:
        out.append(f"| {r} | {bold(where[r + '.1'])} | {bold(where[r + '.2'])} | {bold(where[r + '.3'])} |")
    return '\n'.join(out)

def single(refs):
    return ', '.join(f"{r} → {bold(where[r + '.1'])}" for r in refs)

T = open(os.path.join(HERE, 'template.md')).read()
def repl(m):
    kind, arg = m.group(1), m.group(2)
    refs = [x.strip() for x in arg.split(',') if x.strip()]
    return {'PARTS': parts_table, 'IC': lambda r: ic_table(r[0]), 'TWO': two_table, 'FET': three,
            'ONE': single}[kind](refs)
doc = re.sub(r'\{\{(PARTS|IC|TWO|FET|ONE):([^}]*)\}\}', repl, T)

# GPIO numbers in the text come from the pin maps in dock_nets.py
AG = {n: g for g, n in A_GPIO.items() if n}
BG = {n: g for g, n in B_GPIO.items() if n}
doc = re.sub(r'\{\{A:(\w+)\}\}', lambda m: str(AG[m.group(1)]), doc)
doc = re.sub(r'\{\{B:(\w+)\}\}', lambda m: str(BG[m.group(1)]), doc)
doc = re.sub(r'\{\{ADC:(\w+)\}\}', lambda m: str(AG[m.group(1)] - 26), doc)

# A pin map
rows = ['| GPIO | Pin | Net | Goes to |', '|---|---|---|---|']
goes = {'PC1_VBUS_DET': 'J202 VBUS divider (R213/R214)', 'A_LED': 'R305 → D301', 'KBD_VBUS_EN': 'U202 EN (R208 pull-down)',
        'KBD_USB_D_P': 'PIO-USB D+ → R205 → J201', 'KBD_USB_D_N': 'PIO-USB D− → R206 → J201 (D− = D+ − 1: PIO_USB_PINOUT_DMDP)',
        'BLE_TX': 'UART0 TX → ESP32 RXD0 (U501.30)', 'BLE_RX': 'UART0 RX ← ESP32 TXD0 (U501.31)',
        'BLE_EN': 'ESP32 EN, open-drain', 'BLE_BOOT': 'ESP32 GPIO9, open-drain', 'POGO_TX': 'PIO UART TX → R601 → pogo pin 5',
        'POGO_RX': 'PIO UART RX ← R602 ← pogo pin 4', 'POGO_DET': 'pogo DET (low = docked), also Q601 gate',
        'POGO_OFF': 'Q602 gate: high = pogo 5 V off', 'B_LINK_TX': f'UART1 TX → B GPIO{BG["B_LINK_TX"]} (RX)', 'B_LINK_RX': f'UART1 RX (F11 aux) ← B GPIO{BG["B_LINK_RX"]} (TX)',
        'B_RUN': 'B RUN, open-drain (R406 pull-up)', 'B_BOOTSEL': 'R404 → B QSPI_SS, open-drain (R407 pull-up)',
        'PD_SDA': 'I2C1 SDA → CH224A CFG3/SDA', 'PD_SCL': 'I2C1 SCL → CH224A CFG2/SCL', 'PD_PG': 'CH224A PG (R102 pull-up)',
        'B_SWCLK': 'B SWCLK (PIO SWD probe)', 'B_SWDIO': 'B SWDIO', 'KBD_CC1': f'ADC{AG["KBD_CC1"]-26}: J201 CC1 (Rp R201)',
        'KBD_CC2': f'ADC{AG["KBD_CC2"]-26}: J201 CC2 (Rp R202)', 'KBD_VBUS_SENSE': f'ADC{AG["KBD_VBUS_SENSE"]-26}: R209/R210 divider',
        'POGO_5V_SENSE': f'ADC{AG["POGO_5V_SENSE"]-26}: R607/R608 divider'}
for g in range(30):
    n = A_GPIO[g]
    rows.append(f"| GPIO{g} | {GPIO_PIN[g]} | {bold(n) if n else 'spare (no-connect flag)'} | {goes.get(n, '')} |")
doc = doc.replace('{{APINMAP}}', '\n'.join(rows))
rows = ['| GPIO | Pin | Net | Goes to |', '|---|---|---|---|']
gb = {'B_LINK_RX': f'UART1 TX (F11 aux) → A GPIO{AG["B_LINK_RX"]}', 'B_LINK_TX': f'UART1 RX ← A GPIO{AG["B_LINK_TX"]}', 'PC2_VBUS_DET': 'J203 VBUS divider (R219/R220)', 'B_LED': 'R405 → D401'}
for g in sorted(B_GPIO):
    rows.append(f"| GPIO{g} | {GPIO_PIN[g]} | {bold(B_GPIO[g])} | {gb[B_GPIO[g]]} |")
rows.append('| all other GPIOs | … | spare (no-connect flags) | |')
doc = doc.replace('{{BPINMAP}}', '\n'.join(rows))

# crossing nets
sheet_of = lambda ref: {'1': 'POWER', '2': 'USB_PORTS', '3': 'MCU_A', '4': 'MCU_B', '5': 'BLE', '6': 'POGO'}[re.sub(r'\D', '', ref)[0]]
rows = ['| Net | Sheets | Pins |', '|---|---|---|']
for n in sorted(NETS):
    sh = sorted({sheet_of(p.split('.')[0]) for p in NETS[n]})
    if len(sh) > 1 and n not in ('GND', '+3V3', '+5V'):
        rows.append(f"| {n} | {', '.join(sh)} | {', '.join(NETS[n])} |")
doc = doc.replace('{{CROSS}}', '\n'.join(rows))

# appendix
rows = ['| Net | Pins (ref.pin name) |', '|---|---|']
for n in sorted(NETS, key=lambda x: (x != 'GND', x)):
    pins = NETS[n]
    if n == 'GND':
        rows.append(f'| GND | {len(pins)} pins (every GND pin, shield and exposed pad) |')
        continue
    txt = ', '.join(f"{p}" + (f" ({pn(*p.split('.', 1))})" if pn(*p.split('.', 1)) else '') for p in pins)
    rows.append(f'| {n} | {txt} |')
doc = doc.replace('{{APPENDIX}}', '\n'.join(rows))
nc_by = {}
for p in NC:
    r, q = p.split('.', 1); nc_by.setdefault(r, []).append(q + (f" ({pn(r, q)})" if pn(r, q) else ''))
doc = doc.replace('{{NCLIST}}', '\n'.join(f"- **{r}**: {', '.join(v)}" for r, v in nc_by.items()))
doc = doc.replace('{{STATS}}', f"{len(COMP)} parts, {sum(len(v) for v in NETS.values())} connected pins on {len(NETS)} nets, {len(NC)} no-connect pins")
open(os.path.join(HERE, '..', '..', 'dock-v2', 'DOCK_CONNECTIONS.md'), 'w').write(doc)
left = re.findall(r'\{\{[^}]*\}\}', doc)
print('written', len(doc), 'chars; unreplaced:', left)
