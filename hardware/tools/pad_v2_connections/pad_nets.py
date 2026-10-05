"""Pad v2 connection model: every net and the pins on it. Source for PAD_WIRING.md and check_wiring.py."""
NETS, NC = {}, []
def add(d):
    for k, v in d.items(): NETS.setdefault(k, []).extend(v)
def two(ref, a, b): add({a: [f'{ref}.1'], b: [f'{ref}.2']})

# ---------------------------------------------------------------- ESP32-S3-MINI-1 pin map (GPIO -> module pin, net)
ESP_PIN = {0: 4, 1: 5, 2: 6, 3: 7, 4: 8, 5: 9, 6: 10, 7: 11, 8: 12, 9: 13, 10: 14, 11: 15, 12: 16, 13: 17, 14: 18, 15: 19,
           16: 20, 17: 21, 18: 22, 19: 23, 20: 24, 21: 25, 26: 26, 47: 27, 33: 28, 34: 29, 48: 30, 35: 31, 36: 32, 37: 33,
           38: 34, 39: 35, 40: 36, 41: 37, 42: 38, 43: 39, 44: 40, 45: 41, 46: 44}
# side of the module as placed (rotation 90, antenna at the left board edge)
ESP_SIDE = {**{g: 'front edge row (via under the module)' for g in range(0, 12)},
            **{g: 'right row, south of USB (pocket: via, bottom layer)' for g in range(12, 19)},
            19: 'right row', 20: 'right row', 21: 'right row, north of USB', 26: 'right row, north of USB',
            47: 'right row, north', 33: 'right row, north', 34: 'right row, north', 48: 'right row, north',
            35: 'back row, east end', 36: 'back row, east end', 37: 'back row, east end',
            38: 'back row', 39: 'back row', 40: 'back row', 41: 'back row', 42: 'back row',
            43: 'back row (via, bottom layer)', 44: 'back row (via, bottom layer)', 45: 'back row, west', 46: 'back row, west'}
GPIO = {0: 'BOOT', 1: 'KEY2', 2: 'KEY6', 3: 'KEY10', 4: 'KEY3', 5: 'KEY7', 6: 'KEY11', 7: 'KEY4', 8: 'KEY8', 9: 'KEY12',
        10: 'VBAT_SENSE', 11: 'VIN_SENSE',
        12: 'TGL_WORK', 13: 'TGL_PERSONAL', 14: 'CHG_STAT', 15: 'CHG_EN_N', 16: 'ENC2_SW', 17: 'ENC2_B', 18: 'ENC2_A',
        19: 'USB_DN', 20: 'USB_DP', 21: 'CHG_ISEL', 26: 'RGB_EN',
        47: 'DISP_EN_N', 33: 'DISP_SCL', 34: 'DISP_SDA', 48: 'DISP_RES', 35: 'DISP_DC', 36: 'DISP_CS', 37: 'DISP_BLK',
        38: 'KEY9', 39: 'KEY5', 40: 'KEY1', 41: 'ENC1_B', 42: 'ENC1_A', 43: 'PAD_TX', 44: 'PAD_RX', 45: 'ENC1_SW', 46: 'RGB_DATA'}
GOES = {'BOOT': 'SW202 (BOOT button); strapping pin, internal pull-up',
        'VBAT_SENSE': 'R117/R118 divider (ADC1_CH9)', 'VIN_SENSE': 'R106/R107 divider: dock 5 V present (ADC2_CH0 or digital)',
        'TGL_WORK': 'J301 pin 3', 'TGL_PERSONAL': 'J301 pin 1', 'CHG_STAT': 'ETA6003 STAT (open drain, R114 pull-up)',
        'CHG_EN_N': 'ETA6003 ENB: low = charge (R113 pull-down)', 'CHG_ISEL': 'ETA6003 USB_DET: low = 1.0 A, high = 0.45 A',
        'ENC2_SW': 'SW314 push switch', 'ENC2_A': 'SW314 A through R307/C303', 'ENC2_B': 'SW314 B through R308/C304',
        'ENC1_SW': 'SW313 push switch (strapping pin IO45: no external pull-up)', 'ENC1_A': 'SW313 A through R303/C301', 'ENC1_B': 'SW313 B through R304/C302',
        'USB_DN': 'J201 D- (fixed pin)', 'USB_DP': 'J201 D+ (fixed pin)', 'RGB_EN': 'TPS61023 EN (R403 pull-down)',
        'RGB_DATA': 'U402 input (strapping pin IO46: low at reset)', 'DISP_EN_N': 'Q501 gate: low = display on (R501 pull-up)',
        'DISP_SCL': 'J501 pin 6', 'DISP_SDA': 'J501 pin 5', 'DISP_RES': 'J501 pin 4', 'DISP_DC': 'J501 pin 3', 'DISP_CS': 'J501 pin 2',
        'DISP_BLK': 'J501 pin 1 (backlight PWM)', 'PAD_TX': 'R102 -> pogo pin 4 (UART0 TX, also the ROM bootloader)', 'PAD_RX': 'R101 <- pogo pin 3 (UART0 RX)'}
for g, net in GPIO.items(): add({net: [f'U201.{ESP_PIN[g]}']})
add({'+3V3': ['U201.3'], 'ESP_EN': ['U201.45'], 'GND': [f'U201.{n}' for n in (1, 2, 42, 43, *range(46, 66))]})

# ---------------------------------------------------------------- POWER
add({'GND': ['J101.1', 'J101.5', 'J101.7', 'D101.2', 'U101.2', 'U102.4', 'U102.9'],
     'POGO_5V': ['J101.2', 'J101.6', 'D101.1', 'U102.6', 'U102.7', 'U102.8'],
     'PAD_RX_J': ['J101.3', 'U101.1'], 'PAD_TX_J': ['J101.4', 'U101.3'],
     'VIN_PROT': ['U102.1', 'U102.2', 'U102.3', 'U103.2'], 'OVLO': ['U102.5']})
NC.extend(['U101.4', 'U101.5', 'U101.6'])
two('R101', 'PAD_RX_J', 'PAD_RX'); two('R102', 'PAD_TX_J', 'PAD_TX')
two('C101', 'POGO_5V', 'GND'); two('R103', 'POGO_5V', 'OVLO_TOP'); two('R104', 'OVLO_TOP', 'OVLO'); two('R105', 'OVLO', 'GND')
two('R106', 'VIN_PROT', 'VIN_SENSE'); two('R107', 'VIN_SENSE', 'GND')
add({'CHG_SW': ['U103.3', 'U103.4'], 'VSYS': ['U103.1', 'U103.15'], 'VBAT': ['U103.14', 'U103.16', 'J102.1'],
     'GND': ['U103.5', 'U103.10', 'U103.17', 'U103.8'], 'CHG_EN_N': ['U103.6'], 'CHG_ISEL': ['U103.13'], 'CHG_STAT': ['U103.9'],
     'CHG_ISET1': ['U103.11'], 'CHG_ISET2': ['U103.12'], 'CHG_NTC': ['U103.7', 'J103.1'], 'GND ': []})
NETS.pop('GND ')
add({'GND': ['J103.2']})
two('C102', 'VIN_PROT', 'GND'); two('C103', 'VIN_PROT', 'GND'); two('L101', 'CHG_SW', 'VSYS')
two('C104', 'VSYS', 'GND'); two('C105', 'VSYS', 'GND'); two('C106', 'VBAT', 'GND')
two('R108', 'CHG_ISET1', 'GND'); two('R109', 'CHG_ISET2', 'GND')
two('R110', 'VIN_PROT', 'CHG_NTC'); two('R111', 'VIN_PROT', 'CHG_NTC'); two('R112', 'CHG_NTC', 'GND')
two('R113', 'CHG_EN_N', 'GND'); two('R114', 'CHG_STAT', '+3V3')
add({'BAT_N': ['J102.2', 'U104.6', 'Q101.2', 'Q101.3'], 'DW_VCC': ['U104.5'], 'DW_OD': ['U104.1', 'Q101.4'], 'DW_OC': ['U104.3', 'Q101.5'],
     'DW_CS': ['U104.2'], 'FET_D': ['Q101.1', 'Q101.8'], 'GND': ['Q101.6', 'Q101.7']})
NC.append('U104.4')
two('R115', 'VBAT', 'DW_VCC'); two('C107', 'DW_VCC', 'BAT_N'); two('R116', 'DW_CS', 'GND')
two('R117', 'VBAT', 'VBAT_SENSE'); two('R118', 'VBAT_SENSE', 'GND'); two('C108', 'VBAT_SENSE', 'GND')
add({'VSYS': ['U105.1', 'U105.3'], 'GND': ['U105.2'], '+3V3': ['U105.5']}); NC.append('U105.4')
two('C109', 'VSYS', 'GND'); two('C110', '+3V3', 'GND')

# ---------------------------------------------------------------- MCU
two('C201', '+3V3', 'GND'); two('C202', '+3V3', 'GND'); two('R201', '+3V3', 'ESP_EN'); two('C203', 'ESP_EN', 'GND')
two('SW201', 'ESP_EN', 'GND'); two('SW202', 'BOOT', 'GND')
add({'GND': ['J201.A1', 'J201.A12', 'J201.B1', 'J201.B12', 'J201.SH', 'U202.2'],
     'USB_VBUS': ['J201.A4', 'J201.A9', 'J201.B4', 'J201.B9'],
     'USB_DP': ['J201.A6', 'J201.B6', 'U202.1'], 'USB_DN': ['J201.A7', 'J201.B7', 'U202.3'],
     'USB_CC1': ['J201.A5'], 'USB_CC2': ['J201.B5']})
NC.extend(['J201.A8', 'J201.B8', 'U202.4', 'U202.5', 'U202.6'])
two('R202', 'USB_CC1', 'GND'); two('R203', 'USB_CC2', 'GND')

# ---------------------------------------------------------------- INPUTS
for k in range(1, 13): two(f'SW3{k:02d}', f'KEY{k}', 'GND')
for e, ref, r0, c0 in ((1, 'SW313', 301, 301), (2, 'SW314', 305, 303)):
    add({f'ENC{e}_A_RAW': [f'{ref}.A'], f'ENC{e}_B_RAW': [f'{ref}.B'], 'GND': [f'{ref}.C', f'{ref}.MP', f'{ref}.S2'], f'ENC{e}_SW': [f'{ref}.S1']})
    two(f'R{r0}', f'ENC{e}_A_RAW', '+3V3'); two(f'R{r0 + 1}', f'ENC{e}_B_RAW', '+3V3')
    two(f'R{r0 + 2}', f'ENC{e}_A_RAW', f'ENC{e}_A'); two(f'R{r0 + 3}', f'ENC{e}_B_RAW', f'ENC{e}_B')
    two(f'C{c0}', f'ENC{e}_A', 'GND'); two(f'C{c0 + 1}', f'ENC{e}_B', 'GND')
add({'TGL_PERSONAL': ['J301.1'], 'GND': ['J301.2'], 'TGL_WORK': ['J301.3']})

# ---------------------------------------------------------------- RGB
add({'BOOST_FB': ['U401.1'], 'RGB_EN': ['U401.2'], 'VSYS': ['U401.3'], 'GND': ['U401.4'], 'BOOST_SW': ['U401.5'], '5V_RGB': ['U401.6']})
two('L401', 'VSYS', 'BOOST_SW'); two('C401', 'VSYS', 'GND'); two('C402', '5V_RGB', 'GND'); two('C403', '5V_RGB', 'GND')
two('R401', '5V_RGB', 'BOOST_FB'); two('R402', 'BOOST_FB', 'GND'); two('R403', 'RGB_EN', 'GND')
add({'GND': ['U402.1', 'U402.3'], 'RGB_DATA': ['U402.2'], 'RGB_DATA_5V': ['U402.4'], '5V_RGB': ['U402.5']})
two('C404', '5V_RGB', 'GND'); two('R404', 'RGB_DATA_5V', 'LED_D0')
# chain order: (kind, where); kind K = SK6812MINI-E key LED (bottom), R = XL-2020 ring LED (top)
CHAIN = ([('K', f'key {k}') for k in (9, 10, 11, 12, 8, 7, 6, 5, 1, 2, 3, 4)]
         + [('R', f"ring 2, {h} o'clock") for h in (7, 6, 5, 4, 3, 2, 1, 12, 11, 10, 9, 8)]
         + [('R', f"ring 1, {h} o'clock") for h in (4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5)])
LEDPINS = {'K': dict(vss=1, din=2, vdd=3, dout=4), 'R': dict(dout=1, vss=2, din=3, vdd=4)}
for i, (kind, where) in enumerate(CHAIN):
    ref, p = f'D4{i + 1:02d}', LEDPINS[kind]
    add({f'LED_D{i}': [f'{ref}.{p["din"]}'], '5V_RGB': [f'{ref}.{p["vdd"]}'], 'GND': [f'{ref}.{p["vss"]}']})
    if i < len(CHAIN) - 1: add({f'LED_D{i + 1}': [f'{ref}.{p["dout"]}']})
    else: NC.append(f'{ref}.{p["dout"]}')
    two(f'C4{i + 5:02d}', '5V_RGB', 'GND')

# ---------------------------------------------------------------- DISPLAY
add({'DISP_BLK': ['J501.1'], 'DISP_CS': ['J501.2'], 'DISP_DC': ['J501.3'], 'DISP_RES': ['J501.4'], 'DISP_SDA': ['J501.5'],
     'DISP_SCL': ['J501.6'], 'DISP_VCC': ['J501.7', 'Q501.3'], 'GND': ['J501.8', 'J501.9'], 'DISP_EN_N': ['Q501.1'], '+3V3': ['Q501.2']})
two('C501', 'DISP_VCC', 'GND'); two('R501', 'DISP_EN_N', '+3V3')
