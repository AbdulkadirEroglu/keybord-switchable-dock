"""Compare the wired dock-v2 schematic with the connection model (DOCK_CONNECTIONS.md).

    python3 hardware/tools/dock_v2_connections/check_wiring.py            (exports the netlist itself)
    python3 hardware/tools/dock_v2_connections/check_wiring.py my.net     (use a netlist you exported)

Net *names* may differ from the guide; what is checked is which pins are joined:
  - UNWIRED: none of the net's pins is connected yet
  - SPLIT:   pins the guide puts on one net are on several nets in the schematic
  - MERGED:  one schematic net contains pins of more than one guide net
  - NC:      a pin the guide leaves unconnected is wired to something
Exit code 0 when everything matches.
"""
import os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dock_nets import NETS, NC

net_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), 'dock_v2_check.net')
if len(sys.argv) == 1:
  subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', net_file,
                os.path.join(HERE, '..', '..', 'dock-v2', 'dock-v2.kicad_sch')], check=True, capture_output=True)
s = open(net_file).read()
actual = {}                                   # pin -> schematic net name
nets_block = s[s.index('(nets'):]
for m in re.finditer(r'\(net\s*\(code "?\d+"?\)\s*\(name "([^"]*)"\)(.*?)(?=\n\t\t\(net\s|\Z)', nets_block, re.S):
    pins = re.findall(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', m.group(2))
    if len(pins) > 1:                         # single-pin nets are unconnected pins
        for r, p in pins:
            actual[f'{r}.{p}'] = m.group(1)

problems = 0
owner = {p: n for n, pins in NETS.items() for p in pins}
for net, pins in sorted(NETS.items()):
    got = {actual.get(p, '(unconnected)') for p in pins}
    if got == {'(unconnected)'}:
        problems += 1
        print(f'UNWIRED {net}: {", ".join(pins)}')
    elif len(got) > 1:
        problems += 1
        detail = {g: [p for p in pins if actual.get(p, '(unconnected)') == g] for g in got}
        print(f'SPLIT  {net}: ' + '; '.join(f'{g}: {", ".join(v)}' for g, v in detail.items()))
seen = {}
for p, a in actual.items():
    seen.setdefault(a, set()).add(owner.get(p, 'NC:' + p))
for a, guide in sorted(seen.items()):
    if len(guide) > 1:
        problems += 1
        print(f'MERGED schematic net {a} joins guide nets: {", ".join(sorted(guide))}')
for p in NC:
    if p in actual:
        problems += 1
        print(f'NC     {p} should be unconnected, is on {actual[p]}')
print('OK: wiring matches DOCK_CONNECTIONS.md' if not problems else f'{problems} problem(s)')
sys.exit(1 if problems else 0)
