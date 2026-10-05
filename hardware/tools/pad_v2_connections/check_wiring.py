"""Compare the wired pad-v2 schematic with the connection model (PAD_WIRING.md).

    python3 hardware/tools/pad_v2_connections/check_wiring.py            (exports the netlist itself)
    python3 hardware/tools/pad_v2_connections/check_wiring.py my.net     (use a netlist you exported)

What is checked is which pins are joined; net *names* may differ from the guide.
Interchangeable pins are accepted:
  - non-polarised resistors, capacitors, push buttons and crystals may be drawn either way round;
  - the four TPD4E1U06 ESD channels (pins 1, 3, 4, 6) may carry the four signals in any order;
  - inductors may be drawn either way round;
  - the two mounting-hole symbols and FS8205A's doubled pins are checked as drawn.
Reported:
  - MISSING: a part in the guide is not in the schematic (or renamed)
  - UNWIRED: none of the net's pins is connected yet
  - SPLIT:   pins the guide puts on one net are on several nets in the schematic
  - MERGED:  one schematic net contains pins of more than one guide net
  - NC:      a pin the guide leaves unconnected is wired to something
Exit code 0 when everything matches.
"""
import os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pad_nets import NETS, NC

net_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), 'pad_v2_check.net')
if len(sys.argv) == 1:
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', net_file,
                    os.path.join(HERE, '..', '..', 'pad-v2', 'pad-v2.kicad_sch')], check=True, capture_output=True)
s = open(net_file).read()
parts = dict(re.findall(r'\(comp\s*\(ref "([^"]+)"\).*?\(libsource\s*\(lib "[^"]*"\)\s*\(part "([^"]+)"', s, re.S))
actual = {}                                   # pin -> schematic net name
nets_block = s[s.index('(nets'):]
for m in re.finditer(r'\(net\s*\(code "?\d+"?\)\s*\(name "([^"]*)"\)(.*?)(?=\n\t\t\(net\s|\Z)', nets_block, re.S):
    pins = re.findall(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', m.group(2))
    if len(pins) > 1:                         # single-pin nets are unconnected pins
        for r, p in pins:
            actual[f'{r}.{p}'] = m.group(1)

owner = {p: n for n, pins in NETS.items() for p in pins}
refs_model = {p.split('.')[0] for p in list(owner) + NC}
problems, notes = 0, []

missing = sorted(r for r in refs_model if r not in parts)
if missing:
    problems += 1
    print('MISSING parts (not in the schematic, or renamed): ' + ', '.join(missing))

SWAP2 = {'R', 'C', 'SW_Push', 'L'}            # two interchangeable pins 1/2
XTAL = {'Crystal_GND24'}                      # pins 1/3 interchangeable
TPD = {'TPD4E1U06DBV'}                        # channel pins 1, 3, 4, 6 interchangeable
groups = {}
for r, part in parts.items():
    if r not in refs_model:
        continue
    if part in SWAP2:
        groups[r] = ['1', '2']
    elif part in XTAL:
        groups[r] = ['1', '3']
    elif part in TPD:
        groups[r] = ['1', '3', '4', '6']
flex = {f'{r}.{p}' for r, ps in groups.items() for p in ps}

amap = {}                                     # schematic net -> guide nets seen on fixed pins
def learn(pairs):
    for a, g in pairs:
        if a and g:
            amap.setdefault(a, set()).add(g)
learn((actual.get(p), g) for p, g in owner.items() if p not in flex)

oriented = {}
for rnd in range(8):
    for r, ps in groups.items():
        if r in oriented:
            continue
        want = [owner.get(f'{r}.{p}') for p in ps]
        have = [actual.get(f'{r}.{p}') for p in ps]
        known = [next(iter(amap[a])) if a in amap and len(amap[a]) == 1 else None for a in have]
        if all(k is None for k in known) and rnd < 7:
            continue                          # wait until a neighbour tells us the orientation
        perm, used = {}, set()
        for i, g in enumerate(want):
            if g is None:
                continue
            j = next((j for j, k in enumerate(known) if k == g and j not in used), None)
            if j is not None:
                perm[i] = j; used.add(j)
        for i in range(len(ps)):
            if i not in perm:
                j = i if i not in used else next(j for j in range(len(ps)) if j not in used)
                perm[i] = j; used.add(j)
        oriented[r] = {f'{r}.{ps[i]}': f'{r}.{ps[j]}' for i, j in perm.items()}
        if any(i != j for i, j in perm.items()):
            if r in ('L301', 'L401'):
                notes.append(f'WARNING {r}: pins 1/2 swapped. Pin 1 (polarity dot) must be the 1.1 V side for RPi\'s layout: swap it in the schematic.')
            elif parts[r] in XTAL:
                notes.append(f'note {r}: crystal pins 1/3 swapped (works electrically; RPi\'s layout has pin 1 on XIN).')
        learn((actual.get(ap), owner.get(mp)) for mp, ap in oriented[r].items())

view = {p: a for p, a in actual.items() if p not in flex}
for r, m in oriented.items():
    for mp, ap in m.items():
        if ap in actual:
            view[mp] = actual[ap]

for net, pins in sorted(NETS.items()):
    pins = [p for p in pins if p.split('.')[0] in parts]
    if not pins:
        continue
    got = {view.get(p, '(unconnected)') for p in pins}
    if got == {'(unconnected)'}:
        problems += 1
        print(f'UNWIRED {net}: {", ".join(pins)}')
    elif len(got) > 1:
        problems += 1
        detail = {g: [p for p in pins if view.get(p, '(unconnected)') == g] for g in got}
        print(f'SPLIT  {net}: ' + '; '.join(f'{g}: {", ".join(v)}' for g, v in sorted(detail.items())))
seen = {}
for p, a in view.items():
    if p.split('.')[0] in refs_model:
        seen.setdefault(a, set()).add(owner.get(p, 'NC:' + p))
for a, guide in sorted(seen.items()):
    if len(guide) > 1:
        problems += 1
        print(f'MERGED schematic net {a} joins guide nets: {", ".join(sorted(guide))}')
for p in NC:
    if p in view:
        problems += 1
        print(f'NC     {p} should be unconnected, is on {view[p]}')
extra = sorted(r for r in parts if r not in refs_model and not r.startswith('#'))
if extra:
    print('note: parts not in the guide (renamed or added?): ' + ', '.join(extra))
for n in notes:
    print(n)
print('OK: wiring matches the guide' if not problems else f'{problems} problem(s)')
sys.exit(1 if problems else 0)
