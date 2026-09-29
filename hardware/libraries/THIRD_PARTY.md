# Third-party library content

| What | Where | Source | Licence |
|---|---|---|---|
| `RP2350A_QFN-60_RPi_Vias`, `L_Abracon_AOTA-B201610S3R3_0806`, `C_0402_RPi_Wide` | `dock_v2.pretty/` | Raspberry Pi *RP2350A Minimal* KiCad design (`RPI-RP2350A-MINIMAL_R4-S1`), footprints extracted unchanged except: RPi-internal part properties removed, 3D models pointed at KiCad stock models (the QFN-60 uses KiCad's QFN-56 7 × 7 mm 0.4 mm model as a stand-in; KiCad has no QFN-60 model) | MIT, © 2026 Raspberry Pi Ltd (`../reference/rpi-rp2350a-minimal/LICENSE.txt`) |
| Whole RP2350A Minimal design | `../reference/rpi-rp2350a-minimal/` | https://datasheets.raspberrypi.com/rp2350/Minimal-KiCAD.zip | MIT, © 2026 Raspberry Pi Ltd |
| `ESP32-C3-MINI-1` footprint | `dock_v2.pretty/` | https://github.com/espressif/kicad-libraries (3D model path changed to `dock_v2.3dshapes`) | CC-BY-SA 4.0 with the KiCad library exception (designs using it are not affected) |
| `ESP32-C3-MINI-1.step` | `dock_v2.3dshapes/` | same repository | same |
| `ESP32-C3-MINI-1` symbol | `../dock-v2/dock_v2_custom.kicad_sym` | same repository (footprint link changed to `dock_v2:`) | same |
| `CH224A` symbol | `../dock-v2/dock_v2_custom.kicad_sym` | KiCad `Interface_USB:CH224K`, renamed, pin names per the CH224A datasheet | CC-BY-SA 4.0 with the KiCad library exception |
| `RP2354A_RPiFP` symbol | `../dock-v2/dock_v2_custom.kicad_sym` | KiCad `MCU_RaspberryPi:RP2350A` (base of KiCad's RP2354A), renamed, footprint set to `dock_v2:RP2350A_QFN-60_RPi_Vias` | CC-BY-SA 4.0 with the KiCad library exception |
