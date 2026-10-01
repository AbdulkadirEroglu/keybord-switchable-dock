"""Dock v2 connection model: net -> [REF.PIN]. Single source for DOCK_CONNECTIONS.md."""

def usbc(j, vbus, cc1, cc2, dp, dn):
    return {vbus: [f'{j}.A4', f'{j}.A9', f'{j}.B4', f'{j}.B9'],
            cc1: [f'{j}.A5'], cc2: [f'{j}.B5'],
            dp: [f'{j}.A6', f'{j}.B6'], dn: [f'{j}.A7', f'{j}.B7'],
            'GND': [f'{j}.A1', f'{j}.A12', f'{j}.B1', f'{j}.B12', f'{j}.SH']}

def tpd(u, d1p, d1n, d2p, d2n):
    """TPD4E1U06: 1 D1+, 6 D1-, 3 D2+, 4 D2-, 2 GND, 5 NC."""
    n = {'GND': [f'{u}.2']}
    for pin, net in (('1', d1p), ('6', d1n), ('3', d2p), ('4', d2n)):
        if net:
            n.setdefault(net, []).append(f'{u}.{pin}')
    return n

NETS = {}
NC = []          # pins deliberately left unconnected (put a no-connect flag)

def add(d):
    for k, v in d.items():
        NETS.setdefault(k, []).extend(v)

def two(ref, a, b):          # 2-pin part: pin 1 -> a, pin 2 -> b
    add({a: [f'{ref}.1'], b: [f'{ref}.2']})

# ---------------------------------------------------------------- 1 POWER
add(usbc('J101', 'VBUS_IN', 'PD_CC1', 'PD_CC2', 'PD_DP', 'PD_DM'))
NC += ['J101.A8', 'J101.B8']
add(tpd('U101', 'PD_DP', 'PD_DM', 'PD_CC1', 'PD_CC2')); NC += ['U101.5']
add({'VBUS_IN': ['D101.1'], 'GND': ['D101.2']})          # D_TVS: 1 = K, 2 = A
add({'VBUS_IN': ['U102.1', 'U102.8'], 'PD_SCL': ['U102.2'], 'PD_SDA': ['U102.3'], 'PD_DP': ['U102.4'],
     'PD_DM': ['U102.5'], 'PD_CC2': ['U102.6'], 'PD_CC1': ['U102.7'], 'PD_CFG1': ['U102.9'],
     'PD_PG': ['U102.10'], 'GND': ['U102.11']})
two('C101', 'VBUS_IN', 'GND')
two('R101', 'PD_CFG1', 'GND')
two('R102', '+3V3', 'PD_PG')
two('R103', '+3V3', 'PD_SCL')
two('R104', '+3V3', 'PD_SDA')
# buck: 1 BOOT, 2 VIN, 3 EN, 4 SS, 5 VSENSE, 6 COMP, 7 GND, 8 PH
add({'BUCK_BOOT': ['U103.1'], 'VBUS_IN': ['U103.2'], 'BUCK_SS': ['U103.4'], 'BUCK_FB': ['U103.5'],
     'BUCK_COMP': ['U103.6'], 'GND': ['U103.7'], 'BUCK_SW': ['U103.8']})
NC += ['U103.3']
two('C102', 'VBUS_IN', 'GND'); two('C103', 'VBUS_IN', 'GND')
two('C104', 'BUCK_BOOT', 'BUCK_SW')
two('C105', 'BUCK_SS', 'GND')
two('R105', 'BUCK_COMP', 'BUCK_COMP_RC'); two('C106', 'BUCK_COMP_RC', 'GND'); two('C107', 'BUCK_COMP', 'GND')
two('R106', '+5V', 'BUCK_FB'); two('R107', 'BUCK_FB', 'GND')
add({'BUCK_SW': ['D102.1'], 'GND': ['D102.2']})           # D_Schottky: 1 = K, 2 = A
two('L101', 'BUCK_SW', '+5V')
for c in ('C108', 'C109', 'C110'): two(c, '+5V', 'GND')
add({'GND': ['U104.1'], '+3V3': ['U104.2'], '+5V': ['U104.3']})   # AMS1117: 1 GND, 2 VO, 3 VI
two('C111', '+5V', 'GND'); two('C112', '+3V3', 'GND')
# H101-H104 mounting holes: no pins

# ---------------------------------------------------------------- 2 USB PORTS
add(usbc('J201', 'KBD_VBUS', 'KBD_CC1', 'KBD_CC2', 'KBD_USBJ_D_P', 'KBD_USBJ_D_N')); NC += ['J201.A8', 'J201.B8']
add(tpd('U201', 'KBD_USBJ_D_P', 'KBD_USBJ_D_N', 'KBD_CC1', 'KBD_CC2')); NC += ['U201.5']
two('R201', '+3V3', 'KBD_CC1'); two('R202', '+3V3', 'KBD_CC2')
two('R203', 'KBD_USBJ_D_P', 'GND'); two('R204', 'KBD_USBJ_D_N', 'GND')
two('R205', 'KBD_USBJ_D_P', 'KBD_USB_D_P'); two('R206', 'KBD_USBJ_D_N', 'KBD_USB_D_N')
# SY6280: 1 OUT, 2 GND, 3 ISET, 4 EN, 5 IN
add({'KBD_VBUS': ['U202.1'], 'GND': ['U202.2'], 'KBD_ISET': ['U202.3'], 'KBD_VBUS_EN': ['U202.4'], '+5V': ['U202.5']})
two('R207', 'KBD_ISET', 'GND'); two('R208', 'KBD_VBUS_EN', 'GND')
two('C201', 'KBD_VBUS', 'GND')                              # C_Polarized: 1 = +
two('C202', 'KBD_VBUS', 'GND'); two('C203', 'KBD_VBUS', 'GND'); two('C204', '+5V', 'GND')
two('R209', 'KBD_VBUS', 'KBD_VBUS_SENSE'); two('R210', 'KBD_VBUS_SENSE', 'GND')
for j, u, r, pc in (('J202', 'U203', 211, 'PC1'), ('J203', 'U204', 217, 'PC2')):
    add(usbc(j, f'{pc}_VBUS', f'{pc}_CC1', f'{pc}_CC2', f'{pc}_USBJ_D_P', f'{pc}_USBJ_D_N')); NC += [f'{j}.A8', f'{j}.B8']
    add(tpd(u, f'{pc}_USBJ_D_P', f'{pc}_USBJ_D_N', f'{pc}_CC1', f'{pc}_CC2')); NC += [f'{u}.5']
    two(f'R{r}', f'{pc}_CC1', 'GND'); two(f'R{r+1}', f'{pc}_CC2', 'GND')
    two(f'R{r+2}', f'{pc}_VBUS', f'{pc}_VBUS_DET'); two(f'R{r+3}', f'{pc}_VBUS_DET', 'GND')
    two(f'R{r+4}', f'{pc}_USBJ_D_P', f'{pc}_USB_D_P'); two(f'R{r+5}', f'{pc}_USBJ_D_N', f'{pc}_USB_D_N')

# ---------------------------------------------------------------- 3/4 MCUs
RP_3V3 = ['1', '11', '20', '30', '38', '45', '44', '49', '53', '54']     # IOVDD x6, ADC_AVDD, VREG_VIN, USB_OTP, QSPI_IOVDD
QSPI_DATA = ['55', '56', '57', '58', '59']
GPIO_PIN = {0: 2, 1: 3, 2: 4, 3: 5, 4: 7, 5: 8, 6: 9, 7: 10, 8: 12, 9: 13, 10: 14, 11: 15, 12: 16, 13: 17, 14: 18,
            15: 19, 16: 27, 17: 28, 18: 29, 19: 31, 20: 32, 21: 33, 22: 34, 23: 35, 24: 36, 25: 37,
            26: 40, 27: 41, 28: 42, 29: 43}

def mcu_core(p, X):
    u = f'U{p}01'
    add({'+3V3': [f'{u}.{n}' for n in RP_3V3], f'{X}_1V1': [f'{u}.{n}' for n in ('6', '23', '39', '50')],
         f'{X}_VREG_AVDD': [f'{u}.46'], 'GND': [f'{u}.47', f'{u}.61'], f'{X}_VREG_LX': [f'{u}.48'],
         f'{X}_XIN': [f'{u}.21'], f'{X}_XOUT': [f'{u}.22'], f'{X}_QSPI_SS': [f'{u}.60']})
    NC.extend(f'{u}.{n}' for n in QSPI_DATA)
    two(f'L{p}01', f'{X}_1V1', f'{X}_VREG_LX')                 # pin 1 = dot = 1.1 V
    two(f'C{p}01', '+3V3', 'GND')                              # at VREG_VIN (pin 49)
    two(f'C{p}02', f'{X}_1V1', 'GND')
    two(f'C{p}03', f'{X}_VREG_AVDD', 'GND')
    two(f'R{p}01', '+3V3', f'{X}_VREG_AVDD')
    for i in range(4, 7): two(f'C{p}{i:02d}', f'{X}_1V1', 'GND')
    for i in range(7, 15): two(f'C{p}{i:02d}', '+3V3', 'GND')
    add({f'{X}_XIN': [f'Y{p}01.1'], f'{X}_XOUT_R': [f'Y{p}01.3'], 'GND': [f'Y{p}01.2', f'Y{p}01.4']})
    two(f'C{p}15', f'{X}_XIN', 'GND'); two(f'C{p}16', f'{X}_XOUT_R', 'GND')
    two(f'R{p}02', f'{X}_XOUT', f'{X}_XOUT_R')
    two(f'R{p}03', f'{X}_QSPI_SS', f'{X}_BOOTSEL_BTN'); two(f'SW{p}01', f'{X}_BOOTSEL_BTN', 'GND')
    add({'GND': [f'TP{p}03.1']})
    two(f'R{p}05', f'{X}_LED', f'{X}_LED_R')
    add({f'{X}_LED_R': [f'D{p}01.2'], 'GND': [f'D{p}01.1']})   # Device:LED: 1 = K, 2 = A

A_GPIO = {0: 'PC1_VBUS_DET', 1: None, 2: 'A_LED', 3: None, 4: None, 5: 'KBD_VBUS_EN',
          6: 'KBD_USB_D_P', 7: 'KBD_USB_D_N', 8: 'BLE_TX', 9: 'BLE_RX', 10: 'BLE_EN', 11: 'BLE_BOOT',
          12: 'POGO_TX', 13: 'POGO_RX', 14: 'POGO_DET', 15: 'POGO_OFF', 16: 'B_LINK_TX', 17: 'B_LINK_RX',
          18: 'B_RUN', 19: 'B_BOOTSEL', 20: 'PD_SDA', 21: 'PD_SCL', 22: 'PD_PG', 23: 'B_SWCLK',
          24: 'B_SWDIO', 25: None, 26: 'KBD_CC1', 27: 'KBD_CC2', 28: 'KBD_VBUS_SENSE', 29: 'POGO_5V_SENSE'}
B_GPIO = {0: 'B_LINK_RX', 1: 'B_LINK_TX', 2: 'PC2_VBUS_DET', 3: 'B_LED'}

mcu_core(3, 'A')
for g, net in A_GPIO.items():
    (add({net: [f'U301.{GPIO_PIN[g]}']}) if net else NC.append(f'U301.{GPIO_PIN[g]}'))
add({'PC1_USB_D_P': ['U301.52'], 'PC1_USB_D_N': ['U301.51'], 'A_RUN': ['U301.26'],
     'A_SWCLK': ['U301.24', 'TP301.1'], 'A_SWDIO': ['U301.25', 'TP302.1']})
two('SW302', 'A_RUN', 'GND')

mcu_core(4, 'B')
for g in range(30):
    net = B_GPIO.get(g)
    (add({net: [f'U401.{GPIO_PIN[g]}']}) if net else NC.append(f'U401.{GPIO_PIN[g]}'))
add({'PC2_USB_D_P': ['U401.52'], 'PC2_USB_D_N': ['U401.51'], 'B_RUN': ['U401.26'],
     'B_SWCLK': ['U401.24', 'TP401.1'], 'B_SWDIO': ['U401.25', 'TP402.1']})
two('R404', 'B_BOOTSEL', 'B_QSPI_SS')
two('R406', '+3V3', 'B_RUN'); two('R407', '+3V3', 'B_BOOTSEL')

# ---------------------------------------------------------------- 5 BLE
ESP_GND = ['1', '2', '11', '14'] + [str(n) for n in range(36, 54)]
ESP_NC = ['4', '7', '9', '10', '15', '17', '24', '25', '28', '29', '32', '33', '34', '35']
ESP_UNUSED = ['6', '12', '13', '16', '18', '19', '20', '21']       # GPIO3, 0, 1, 10, 4, 5, 6, 7
add({'GND': [f'U501.{n}' for n in ESP_GND], '+3V3': ['U501.3'], 'BLE_EN': ['U501.8'],
     'BLE_GPIO2': ['U501.5'], 'BLE_GPIO8': ['U501.22'], 'BLE_BOOT': ['U501.23'],
     'BLE_TX': ['U501.30', 'TP504.1'], 'BLE_RX': ['U501.31', 'TP503.1'], 'GND ': []})
NETS.pop('GND ')
NC += [f'U501.{n}' for n in ESP_NC + ESP_UNUSED + ['26', '27']]   # GPIO18/19 (USB): test pads dropped 2026-10-01
two('C502', '+3V3', 'GND'); two('C503', '+3V3', 'GND')
two('R501', '+3V3', 'BLE_EN'); two('C501', 'BLE_EN', 'GND')
two('R502', '+3V3', 'BLE_GPIO8'); two('R503', '+3V3', 'BLE_GPIO2'); two('R504', '+3V3', 'BLE_BOOT')
add({'GND': ['TP505.1']})

# ---------------------------------------------------------------- 6 POGO
# dock side: GND | +5V | DET | RX | TX | +5V | GND  (+5V and GND at both ends: two 1 A contacts each;
# a reversed pad lands +5V on +5V and leaves DET open, so the dock never switches 5 V on)
add({'GND': ['J601.1', 'J601.7'], 'POGO_5V': ['J601.2', 'J601.6'], 'POGO_DET_J': ['J601.3'],
     'POGO_RX_J': ['J601.4'], 'POGO_TX_J': ['J601.5']})
# ESD channels as wired: D2- (4) DET, D2+ (3) RX, D1- (6) TX, D1+ (1) spare
add({'GND': ['U601.2'], 'POGO_DET_J': ['U601.4'], 'POGO_RX_J': ['U601.3'], 'POGO_TX_J': ['U601.6']})
NC += ['U601.1', 'U601.5']
two('R601', 'POGO_TX', 'POGO_TX_J'); two('R602', 'POGO_RX_J', 'POGO_RX'); two('R603', 'POGO_DET_J', 'POGO_DET')
add({'POGO_5V': ['U602.1'], 'GND': ['U602.2'], 'POGO_ISET': ['U602.3'], 'POGO_EN': ['U602.4'], '+5V': ['U602.5']})
add({'POGO_DET': ['Q601.1'], 'GND': ['Q601.2'], 'POGO_EN': ['Q601.3']})   # 2N7002: 1 G, 2 S, 3 D
add({'POGO_OFF': ['Q602.1'], 'GND': ['Q602.2'], 'POGO_EN': ['Q602.3']})
two('R604', '+3V3', 'POGO_DET'); two('R605', '+3V3', 'POGO_EN'); two('R609', 'POGO_OFF', 'GND')
two('R606', 'POGO_ISET', 'GND')
two('C601', '+5V', 'GND'); two('C602', 'POGO_5V', 'GND'); two('C603', 'POGO_5V', 'GND')
two('R607', 'POGO_5V', 'POGO_5V_SENSE'); two('R608', 'POGO_5V_SENSE', 'GND')

# sheet-local nets (local labels); everything else crossing sheets is a global label
LOCAL_PREFIX = ('A_', 'B_1V1', 'B_VREG', 'B_XIN', 'B_XOUT', 'B_QSPI', 'B_BOOTSEL_BTN', 'B_LED', 'BUCK_', 'PD_CFG1')
