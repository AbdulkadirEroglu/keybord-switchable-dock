#!/usr/bin/python3
"""Copy Raspberry Pi's RP2350A core layout (regulator, crystal, decoupling) onto one MCU of a board.

Source: hardware/reference/rpi-rp2350a-minimal (Raspberry Pi RP2350A Minimal design, MIT license).

What it does, for one target MCU (e.g. U301):
  1. Maps each Raspberry Pi net to your net through the MCU's pads (U1 pad n <-> U301 pad n).
  2. Finds your support parts on the same schematic sheet as the MCU, matched by value and nets
     (L1 3.3u, C6/C7/C9 4.7u, R3 33, C8/C10/C11 100n on 1.1 V, C12-C18 100n on 3.3 V,
     X1 12 MHz, C3/C4 15p, R2 1k), and places them at Raspberry Pi's positions around your MCU,
     rotated with it.
  3. Copies the copper pours, tracks and vias of those nets around the chip, with your net names.

Run with KiCad's Python (KiCad closed, board saved), after "Update PCB from Schematic" (F8)
and after placing the MCU itself where you want it:

    /usr/bin/python3 hardware/tools/copy_rpi_core_layout.py hardware/dock-v2/dock-v2.kicad_pcb U301
    /usr/bin/python3 hardware/tools/copy_rpi_core_layout.py hardware/dock-v2/dock-v2.kicad_pcb U401

Options: --dry-run (report only), --no-copper (place parts only).
A backup <board>.before-<REF>.kicad_pcb is written first.
"""
import argparse
import math
import os
import re
import shutil
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
REF_BOARD = os.path.join(HERE, '..', 'reference', 'rpi-rp2350a-minimal', 'RPI-RP2350A-MINIMAL_R4-S1.kicad_pcb')
REF_MCU = 'U1'
# Raspberry Pi parts that belong to the MCU core (placed around the chip).
CORE_PARTS = ['L1', 'C6', 'C7', 'C9', 'R3', 'C8', 'C10', 'C11',
              'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'X1', 'C3', 'C4', 'R2']
# Raspberry Pi nets whose copper around the chip is copied.
CORE_NETS = {'+3V3', 'GND', '+1V1', '/VREG_LX', '/VREG_AVDD', '/XIN', '/XOUT', 'Net-(C4-Pad1)'}
# Copper is copied only inside this box around the reference MCU (mm, reference coordinates).
REF_CENTRE = (100.0, 100.0)
BOX = (-12.0, -12.0, 12.0, 15.0)    # dx_min, dy_min, dx_max, dy_max
BOARD_WIDE = 20.0                   # zones larger than this (mm) are board-wide pours: skipped


# ----------------------------------------------------------------------------- reference file
def _blocks(s, tag):
    """Top-level (tag ...) blocks of a board file."""
    out, k = [], 0
    while True:
        i = s.find('\n\t(' + tag, k)
        if i < 0:
            return out
        d, j = 0, i + 1
        while True:
            c = s[j]
            if c == '"':
                j += 1
                while s[j] != '"':
                    j += 2 if s[j] == '\\' else 1
            elif c == '(':
                d += 1
            elif c == ')':
                d -= 1
                if d == 0:
                    break
            j += 1
        out.append(s[i + 1:j + 1])
        k = j


def _net(b):
    return re.search(r'\(net "?([^")]*)"?\)', b).group(1)


def read_reference():
    s = open(REF_BOARD).read()
    segs, vias, zones = [], [], []
    for b in _blocks(s, 'segment'):
        (x1, y1), (x2, y2) = [tuple(map(float, re.search(r'\(%s ([-\d.]+) ([-\d.]+)\)' % k, b).groups()))
                              for k in ('start', 'end')]
        segs.append(dict(a=(x1, y1), b=(x2, y2), w=float(re.search(r'\(width ([\d.]+)\)', b).group(1)),
                         layer=re.search(r'\(layer "([^"]+)"\)', b).group(1), net=_net(b)))
    for b in _blocks(s, 'via'):
        at = tuple(map(float, re.search(r'\(at ([-\d.]+) ([-\d.]+)\)', b).groups()))
        vias.append(dict(at=at, size=float(re.search(r'\(size ([\d.]+)\)', b).group(1)),
                         drill=float(re.search(r'\(drill ([\d.]+)\)', b).group(1)), net=_net(b)))
    for b in _blocks(s, 'zone'):
        if '(keepout' in b:
            continue
        poly = b[b.index('(polygon'):]
        if '(filled_polygon' in poly:
            poly = poly[:poly.index('(filled_polygon')]
        pts = [tuple(map(float, p)) for p in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', poly)]
        num = lambda pat, dflt: float(re.search(pat, b).group(1)) if re.search(pat, b) else dflt
        zones.append(dict(net=_net(b), layer=re.search(r'\(layers? "([^"]+)"', b).group(1), pts=pts,
                          prio=int(num(r'\(priority (\d+)\)', 0)),
                          clearance=num(r'\(connect_pads[^()]*\s*\(clearance ([\d.]+)\)', 0.2),
                          min_thickness=num(r'\(min_thickness ([\d.]+)\)', 0.2),
                          solid='(connect_pads yes' in b,
                          thermal_gap=num(r'\(thermal_gap ([\d.]+)\)', 0.5),
                          thermal_width=num(r'\(thermal_bridge_width ([\d.]+)\)', 0.5)))
    return segs, vias, zones


# ----------------------------------------------------------------------------- helpers
def mm(v):
    return pcbnew.ToMM(v)


def iu(v):
    return pcbnew.FromMM(v)


def norm_value(v):
    v = v.strip().lower().replace('µ', 'u').replace('ω', '').replace('ohm', '').replace(' ', '')
    v = re.sub(r'(?<=\d)f$', '', v)           # 100nf -> 100n, 15pf -> 15p
    v = re.sub(r'(?<=\d)h$', '', v)           # 3.3uh -> 3.3u
    v = re.sub(r'(?<=\d)hz$', '', v)          # 12mhz -> 12m
    v = re.sub(r'^(\d+)r(\d*)$', r'\1', v)    # 33r -> 33
    v = v.replace('12m', '12mhz')
    return v


def in_box(p):
    dx, dy = p[0] - REF_CENTRE[0], p[1] - REF_CENTRE[1]
    return BOX[0] <= dx <= BOX[2] and BOX[1] <= dy <= BOX[3]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('mcu', help='reference of your RP2354A, e.g. U301')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-copper', action='store_true')
    a = ap.parse_args()

    ref = pcbnew.LoadBoard(REF_BOARD)
    rfp = {f.GetReference(): f for f in ref.GetFootprints()}
    brd = pcbnew.LoadBoard(a.board)
    tfp = {f.GetReference(): f for f in brd.GetFootprints()}
    if a.mcu not in tfp:
        sys.exit(f'{a.mcu} not found on {a.board}. Run Update PCB from Schematic (F8) first.')
    rmcu, tmcu = rfp[REF_MCU], tfp[a.mcu]
    if tmcu.IsFlipped():
        sys.exit(f'{a.mcu} is on the back side; this script only handles the front side.')

    # 1. net map through the MCU pads
    netmap = {}
    rp = {p.GetNumber(): p.GetNetname() for p in rmcu.Pads()}
    for p in tmcu.Pads():
        rn, tn = rp.get(p.GetNumber()), p.GetNetname()
        if rn and tn:
            netmap.setdefault(rn, tn)
    missing = [n for n in CORE_NETS if n not in netmap and n not in ('/XOUT', 'Net-(C4-Pad1)')]
    if missing:
        print('warning: no net on', a.mcu, 'for', missing)

    # transform: reference frame (U1 at REF_CENTRE, 0 deg) -> target MCU frame
    tpos = tmcu.GetPosition()
    tx, ty, rot = mm(tpos.x), mm(tpos.y), tmcu.GetOrientationDegrees() - rmcu.GetOrientationDegrees()
    c, s_ = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))   # KiCad: y down, angles CCW

    def T(p):
        dx, dy = p[0] - REF_CENTRE[0], p[1] - REF_CENTRE[1]
        return (tx + dx * c - dy * s_, ty + dx * s_ + dy * c)

    # 2. match support parts on the same sheet
    def sheet(f):
        return f.GetPath().AsString().rsplit('/', 1)[0]
    tsheet = sheet(tmcu)
    pool = [f for r, f in tfp.items() if r != a.mcu and sheet(f) == tsheet]
    placed = {}
    # nets of each ref part through the net map; XOUT/C4 net come from the chain X1-R2-C4
    for rr in CORE_PARTS:
        if rr not in rfp:
            continue
        rf = rfp[rr]
        want_val = norm_value(rf.GetValue())
        rnets = sorted({pd.GetNetname() for pd in rf.Pads() if pd.GetNetname()})
        want = sorted({netmap.get(n) for n in rnets if n in netmap})
        best = None
        for f in pool:
            if f in placed.values() or norm_value(f.GetValue()) != want_val:
                continue
            fn = {pd.GetNetname() for pd in f.Pads() if pd.GetNetname()}
            if set(want) <= fn:
                best = f
                break
        if best is None:
            print(f'  {rr:4} {rf.GetValue():6} nets {rnets}: no matching part on the sheet, skipped')
            continue
        placed[rr] = best
        # learn nets that only the support parts know (XOUT side of R2, C4-X1 node)
        for rpd in rf.Pads():
            n = rpd.GetNetname()
            if n and n not in netmap:
                for tpd in best.Pads():
                    if tpd.GetNumber() == rpd.GetNumber() and tpd.GetNetname():
                        netmap[n] = tpd.GetNetname()

    print(f'{a.mcu}: at ({tx:.3f}, {ty:.3f}) mm, {rot:.1f} deg; {len(placed)} of {len(CORE_PARTS)} core parts matched')
    for rr, f in placed.items():
        rf = rfp[rr]
        p = T((mm(rf.GetPosition().x), mm(rf.GetPosition().y)))
        print(f'  {rr:4} -> {f.GetReference():6} {f.GetValue():8} at ({p[0]:.3f}, {p[1]:.3f}) '
              f'rot {rf.GetOrientationDegrees() + rot:.1f}')
    if a.dry_run:
        print('net map:', {k: v for k, v in netmap.items() if k in CORE_NETS or k.startswith('Net-(C4')})

    # pad-by-pad check: does each pad carry the net RPi has on the same pad number?
    extra = {}
    for rr, f in placed.items():
        rnet = {pd.GetNumber(): netmap.get(pd.GetNetname()) for pd in rfp[rr].Pads()}
        tnet = {pd.GetNumber(): pd.GetNetname() for pd in f.Pads()}
        if all(rnet[n] is None or rnet[n] == tnet.get(n) for n in rnet):
            continue
        if len(rnet) == 2 and not rr.startswith(('L', 'X')) and \
                rnet.get('1') == tnet.get('2') and rnet.get('2') == tnet.get('1'):
            extra[rr] = 180          # non-polar part drawn the other way round: turn it
            print(f'  {rr} -> {f.GetReference()}: pins swapped in your schematic, turned 180 deg (fine for R/C)')
        else:
            print(f'  WARNING {rr} -> {f.GetReference()}: pad nets differ from RPi '
                  f'(RPi {rnet}, yours {tnet}). For the inductor, pin 1 (dot) must be the 1.1 V side. '
                  f'Fix the schematic; placed as RPi, check it in the PCB.')
    if a.dry_run:
        return

    shutil.copyfile(a.board, re.sub(r'\.kicad_pcb$', f'.before-{a.mcu}.kicad_pcb', a.board))
    for rr, f in placed.items():
        rf = rfp[rr]
        p = T((mm(rf.GetPosition().x), mm(rf.GetPosition().y)))
        if f.IsFlipped():
            f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(rf.GetOrientationDegrees() + rot + extra.get(rr, 0))
        f.SetPosition(pcbnew.VECTOR2I(iu(p[0]), iu(p[1])))

    if not a.no_copper:
        segs, vias, zones = read_reference()
        nets = brd.GetNetsByName()
        layer = {n: brd.GetLayerID(n) for n in ('F.Cu', 'B.Cu')}
        added = [0, 0, 0]

        def tnet(rn):
            n = netmap.get(rn)
            return nets[n] if n and nets.has_key(n) else None
        for sg in segs:
            n = tnet(sg['net'])
            if sg['net'] in CORE_NETS | {'Net-(C4-Pad1)'} and n and in_box(sg['a']) and in_box(sg['b']):
                t = pcbnew.PCB_TRACK(brd)
                t.SetStart(pcbnew.VECTOR2I(*map(iu, T(sg['a']))))
                t.SetEnd(pcbnew.VECTOR2I(*map(iu, T(sg['b']))))
                t.SetWidth(iu(sg['w'])); t.SetLayer(layer[sg['layer']]); t.SetNet(n)
                brd.Add(t); added[0] += 1
        for v in vias:
            n = tnet(v['net'])
            if v['net'] in CORE_NETS and n and in_box(v['at']):
                t = pcbnew.PCB_VIA(brd)
                t.SetPosition(pcbnew.VECTOR2I(*map(iu, T(v['at']))))
                t.SetWidth(iu(v['size'])); t.SetDrill(iu(v['drill'])); t.SetNet(n)
                t.SetViaType(pcbnew.VIATYPE_THROUGH); t.SetLayerPair(layer['F.Cu'], layer['B.Cu'])
                brd.Add(t); added[1] += 1
        for z in zones:
            xs = [p[0] for p in z['pts']]; ys = [p[1] for p in z['pts']]
            if max(xs) - min(xs) > BOARD_WIDE or max(ys) - min(ys) > BOARD_WIDE:
                continue
            n = tnet(z['net'])
            if z['net'] not in CORE_NETS or not n or not all(in_box(p) for p in z['pts']):
                continue
            zn = pcbnew.ZONE(brd)
            zn.SetLayer(layer[z['layer']]); zn.SetNet(n)
            zn.SetAssignedPriority(z['prio'])
            zn.SetLocalClearance(iu(z['clearance']))
            zn.SetMinThickness(iu(z['min_thickness']))
            zn.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if z['solid'] else pcbnew.ZONE_CONNECTION_THERMAL)
            zn.SetThermalReliefGap(iu(z['thermal_gap']))
            zn.SetThermalReliefSpokeWidth(iu(z['thermal_width']))
            ol = zn.Outline(); ol.NewOutline()
            for p in z['pts']:
                q = T(p); ol.Append(iu(q[0]), iu(q[1]))
            brd.Add(zn); added[2] += 1
        pcbnew.ZONE_FILLER(brd).Fill(brd.Zones())
        print(f'copied {added[0]} tracks, {added[1]} vias, {added[2]} pours')
    pcbnew.SaveBoard(a.board, brd)
    print('saved', a.board)


if __name__ == '__main__':
    main()
