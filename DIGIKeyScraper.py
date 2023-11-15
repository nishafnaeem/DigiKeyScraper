import json
import os
import re
import threading
import traceback
from typing import List, Dict

import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from db.models import *


class DIGIKeyScraper:
    def __init__(self):
        self.NUMBER_OF_THREADS = os.environ.get('number_of_threads', 1)
        self.BASE_URL = "https://www.digikey.com"
        self.PRODUCTS_URL = "{base_url}/products/en?keywords={mpn_no}"
        self.MPN_RECORDS = self.get_mpn_records()
        self.final_results = list()

    @staticmethod
    def get_mpn_records() -> List:
        """
            Get all MPN Records.
        """
        return ['UCR100-120-T72-SV-C', 'BZX84C4V7', 'CC0603JRNPO9BN220', 'CC0603KRX7R9BB104', 'CD4060BPW',
                'CL21B225KAFNNNE', 'GH CS8PM1.24-3T1U-1', 'LBC807-25LT1G', 'LBC817-25LT1G', 'LF XTAL003000',
                'LUW CR7P-LRLT-HPHR-1', 'PIC10F204T-I/OT', 'PMEG3030EP', 'RC0603FR-0715KL', 'RC0603FR-071KL',
                'RC0603FR-077M32L', 'RC0603FRF10300KL', 'RC1206FR-071K5L', 'RC1206FR-071RL', 'RC1206JR-070RL',
                'SIA459EDJ-T1-GE3', 'VLCF4028T-1R2N2R7-2', 'VLS5045EX-4R7M', 'W-PCB-00795', '476591002', '484090003',
                '1051330001', '5022505191', '20708-050EC', '20709-050EC', '24LC256T-I/SN', '5PB1104CMGI',
                'ADG5408BRUZ-REEL7', 'ADXL345BCCZ-RL', 'AL5809-15P1-7', 'AO3414', 'APDS-9306-065',
                'B2B-PH-SM4-TB(LF)(SN)', 'BM04B-SRSS-TB(LF)(SN)', 'CDBC560-G', 'CS4344-CZZR', 'ECS-240-20-30B-TR',
                'EEE-1HA101UAP', 'FSMRA4JH', 'FXL6408UMX', 'ICM-20948', 'ITG-3050', 'LM25010MH/NOPB', 'LT8611EUDD#PBF',
                'MA40H1S-R', 'MAX16053AUT+T', 'MAX232IDWR', 'MAX3218CAP+', 'NE555DR', 'NZ2520SB-32.768KHZ-NSA3536C',
                'PCA9306DCTR', 'PGA460TPWR', 'PIC32MX795F512L-80I/PT', 'SEAM-50-02.0-S-08-2-A-K-TR', 'SFV15R-1STE1HLF',
                'SFV26R-1STE1HLF', 'SFV6R-1STE1HLF', 'SFW10S-2STME1LF', 'SN74HCT00D', 'SPH0645LM4H-B', 'TL3305AF160QG',
                'TLE5206-2G', 'TLV1117LV12DCYR', 'TLV1117LV18DCYT', 'TLV1117LV28DCYR', 'TMC5130A-TA-T', 'TPA3118D2DAPR',
                'TPS2561DRCR', 'TPS54361DPRT', 'TPS61187RTJR', 'TPS62087RLTR', 'TPS74801RGWR', 'TUSB8041ARGCT',
                'TXB0108PWR', 'ZLDO1117G33TA', '6.93E+11', '18-038/RSGHBHC1-S03/2T', '2450AT07A0100',
                'ABM10-165-38.400MHZ-T3', 'AH086M555003-T', 'B3U-1000P', 'BG301-02-A-0540-L-B', 'BG95', 'BLM21PG220SN1',
                'BQ24040DSQx', 'BRC2012T1R5MD', 'CDBQR43', 'CMT-5023S-SMT-TR', 'CRF0805-FZ-R020ELF',
                'DFE201612E-2R2M=P2', 'DTC143EET1G', 'DW1000-I', 'ESD9L5.0ST5G', 'ESD9X12ST5G', 'FSA2567UMX',
                'FT7521L6X', 'GRM0335C1E150FA01D', 'GRM188R60J476ME15D', 'HHM1595A1', 'HK100515NJ-T', 'IS25WP016D-JKLE',
                'Keystone 5176', 'L403035', 'LBMF1608T100K', 'LP5018RSMR', 'LPS22HHTR', 'LQG15HN22NG02#',
                'LQP15MN3N9B02D', 'LQW18AS3N3G00#', 'LQW18AS6N8G00#', 'LSM6DSOXTR', 'MAX17055ETB+', 'Molex 202410-0002',
                'nRF52840-QIAA', 'NTA4001NT1G', 'NTA4151PT1G', 'Q24FA20H0019600', 'RX8900CE UB', 'SKY66112-11',
                'TPS22917DBVR', 'TPS62840DLC', 'TPS63031DSKR', 'TPSB107K006R0250', 'TXB0101DRLR', 'TXB0104RUTR',
                'U.FL-R-SMT-1(01)', 'W3796', 'Z30C1T8460001', 'ZRB15XR61A475KE01D', '574', '1645', '1646', '1992',
                '2223', '3289', '5011', '10770', '25260', '25260', '40340', '139163', '320559', '332255', '1000007',
                '22232021', '22232051', '22284030', '191600039', '430450812', '451320801', '479480001', '676433910',
                '878311241', '901200765', '1052630001', '1053001100', '1053002100', '1053071205', '1053071206',
                '1053091105', '1053091206', '1053091207', '1053131105', '1053131306', '1461750001', '0191600042\u200e',
                '04025A0R5BAT2A', '04025A101JAT2A', '04025A220JAT2A', '0402YC103KAT2A', '0402YC223KAT2A',
                '0402YD104KAT2A', '06035C104JAT2A', '08055C104MAT2A', '10118194-0001LF', '103AT-4-70316', '1283N23',
                '1376164-1', '1430-18-19T-0', '1430-18-19T-2', '1430-20-19T-0', '1430-20-19T-2', '1430-20-19T-3',
                '1430-20-19T-4', '1430-20-19T-6', '1430-20-19T-9', '1430-22-19T-0', '1430-22-19T-2', '1430-22-19T-5',
                '1430-22-19T-6', '1922T28', '1959T39', '1IC03419121401', '1IC03420021001', '1N4148WS-E3-08',
                '1N4148WT-7', '202-00001', '202-00014', '203-00017', '203-00018', '203-00021', '203-00029', '204-00003',
                '2051T48', '206-00001', '206-00003', '208-00001', '208-00002', '208-00003', '208-00004', '208-00005',
                '208-00006', '208-00007', '208-00008', '208-00009', '208-00010', '208-00011', '208-00012', '209-00003',
                '22-28-4360', '22005515-02', '22204515-02', '22304211-01', '22304515-01', '22304515-02', '22304515-03',
                '2779K15 Green', '2779K203', '2779K801', '2779K802', '282837-2', '3-644540-4', '30-00683', '3000TR',
                '30W Solar Panel', '3133T12', '3259T31', '3310T513', '3313J-1-502E', '35SVPF39M', '3DP-FDM', '4061T12',
                '47948-0001', '5-146278-6', '5062C', '5151003F', '5308T142', '5322K18', '5322K241', '5787834-1',
                '640456-2', '640456-4', '6609006-7', '6844N12', '69885K79', '6PCV-03-006', '7-1437651-0', '70215K66',
                '7108k81', '7130K52', '7310K12', '75145K32', '75935A14', '75935A28', '7602A58', '7609K3', '76455a16',
                '77311-118-02LF', '8-2176092-8', '8(3C18/4C20)-BH', '80005K52', '87035K81', '8709K78', '8904T2',
                '8904T4', '90031A179', '90054A146', '90107A030', '904-00001', '90576A117', '91249A144', '91249A537',
                '91257A566', '91310A332', '91525A114', '91771A541', '92000A103', '92000a114', '92000A222', '92000A318',
                '92005A069', '92010A544', '92141A029', '92146A029', '92148A180', '92323A516', '92323A523', '92620A563',
                '92865A593', '93075A244', '93298A108', '93298A110', '93365a162', '93475A250', '93627A519', '93655A091',
                '94000A037', '94180a307', '9452k14', '9452K311', '9452K329', '94863A206', '94895A805', '95345A095',
                '95345A110', '95462A030', '95526A175', '95836a107', '9774015151R', '9774020151R', '9774020951R',
                '9774140360R', '98055A223', '98090A165', '98676A500', '9983k16', 'A1069-ND', 'ACPDQC3V3T-HF',
                'AD2410-4045', 'AD5141BCPZ10-RL7', 'ADM803RAKSZ-REEL7', 'ADS1015IDGSR', 'AK500-OE-5-1', 'AMN33111',
                'AMN43121', 'AP.17E.07.0064A', 'APT1608LZGCK', 'APTF1616LSEEZGKQBKC', 'AT24C128C-MAHM-T',
                'B0035 w 12mm LensIR', 'B0035 w 16mm LensIR', 'B1L110_BLUE_BOTTOM', 'B2B-PH-K-S(LF)(SN)',
                'B3B-XH-A(LF)(SN)', 'B57221V2103J060', 'BAT54XV2T1G', 'BBUA999BS', 'BGM13P22F512GA-V2R',
                'BLM15AG121SN1D', 'BQ24650RVAT', 'BSS138', 'BSS84-7-F', 'Bulksim-Tri-A', 'BZX84C4V7-7-F', 'C-0203-N',
                'C1005X5R1C474M050BC', 'C1005X5R1V105K050BC', 'C1005X7R1H104K050BB', 'C1206C102KGRACTU',
                'C1210X225K1RACAUTO', 'C1608X5R1V475M080AC', 'C3216X5R1E476M160AC', 'C3216X7S0J336M160AC',
                'CAT24C128YI-GT3', 'CC0402JRNP09BN220', 'CC0402KRX7R7BB102', 'CC0603CRNPO9BN2R2', 'CDBQR0130L-HF',
                'CHS-01TA', 'CL-1-2008-0120-I', 'CL05A225MA5NUNC', 'CL05A334KP5NNNC', 'CL05A474KA5NNNC',
                'CL05A475KP5NRNC', 'CL05B102KB5NNNC', 'CL05B224KO5NNNC', 'CL10A105KB8NNNC', 'CL10A106MQ8NNNC',
                'CL10B474KA8NFNC', 'CL10B474KA8NNWC', 'CL21C122JBFNNNE', 'CL31A226KAHNNNE', 'CL31B106KBHNNNE',
                'CL31B475KBHNNNE', 'CL32A107MPVNNNE', 'CL32B106KBJNNWE', 'CQUSBA-LEFT', 'CQUSBMICRO-OTG-5PIN',
                'CR0402-FX-1002GLF', 'CRCW040229K4FKED', 'CRCW04026K65FKED', 'CRCW06035K10FKEA', 'CRCW12060000Z0EAHP',
                'CRCW25122R00JNEG', 'CRGP0805F12R', 'CSD17577Q5A', 'CSD18511Q5A', 'CSD18543Q3A', 'CSI-SAFE-200-UFFR',
                'CSR0805FKR250', 'CWT-9003', 'Cylinder - Hose Clamp Rubber Protector', 'DB2G42900L1', 'DD5G60-AIWA',
                'DDZ5V1B-7', 'DF2B36FU,H3F', 'DF40C-100DP-0.4V(51)', 'DF40C-100DS-0.4V(51)', 'DLW21SN900SQ2',
                'DMG1012T-7', 'DS3231SN#T&R', 'ECE80US24', 'ECPU1C154MA5', 'EEHZA1H101P', 'EMK105BJ105KV-F',
                'ERA-2AEB2872X', 'ERA-2AEB4991X', 'ERA-2AEB9532X', 'ERA-3AEB2802V', 'ERA3AEB912V', 'ERJ-2RKF1372X',
                'ERJ-2RKF2000X', 'ERJ-2RKF2943X', 'ERJ-2RKF6802X', 'ESD7C5.0DT5G', 'ESDA14V2L', 'ESQT-106-02-F-D-785',
                'ESR03EZPJ102', 'EUV-026S024PS', 'FBMH3216HM221NT', 'FBMJ2125HS250NT', 'FDV301N', 'FGI-P-BEZELADH',
                'FGI-P-WINDOWADH', 'FLS5-15P-L5-20R', 'FLS5-15P-L5-20R-25FT', 'FLS5-15P-L5-20R-50FT',
                'FLSHARNBLKOVMOLD', 'FLSYSPLITTERCORD', 'FTSH-105-01-L-DV-K-TR', 'FXMAR2104UMX', 'FXUB63.07.0150C',
                'G0727', 'GCJ188R71H104KA12D', 'GG0402050R3C2P', 'GMK316BJ106KL-T', 'Gorilla Clear Grip, 4 Pack',
                'GRM1555C1H470FA01D', 'GRM155R61A104KA01D', 'GRM155R61C105KE01D', 'GRM155R61H104KE19D',
                'GRM155R71E104KE14J', 'GRM155R71E473KA88J', 'GRM155R71H103KA88J', 'GRM155R71H223KA12J',
                'GRM155R71H472KA01J', 'GRM1885C1H222JA01J', 'GRM188R61A475ME15D', 'GRM188R6YA225KA12D',
                'GRM216R61E105KA12D', 'GRM21B5C1H223JA01L', 'GRM21BR61C106KE15L', 'GRM21BR61E106KA73L',
                'GRT31CR61H106ME01L', 'GX16-2C-M', 'H4CFC2DMS', 'HCJ1206ZT0R00', 'HTS221TR', 'IHLP3232DZER100M01',
                'ILHB0805ER601V', 'ILHB1206ER121V', 'INA219AIDR', 'IPG-222135-G', 'ITB-632', 'IUTB -M4', 'IUTB-M3',
                'K-LD2-RFB-00H-02', 'K450010LL0', 'K450020LL0', 'KDZVTR27B', 'KRL1220E-M-R015-F-T5',
                'KRL3216T4A-M-R003-F-T1', 'L1I0-0850060000000', 'LCMC0603S2N2GTAR', 'LIS3MDLTR', 'LM-GX16-2P100',
                'LM-GX16-2P20', 'LM-MC4-2P', 'LM25118MH/NOPB', 'LM3405XMK/NOPB', 'LM73606RNPT', 'LMZ14203HTZX/NOPB',
                'LMZM23600V5SILR', 'LS-12020', 'LSM6DS3HTR', 'LSP10120S', 'LTC4015IUHF', 'LTL-12.7ODX7.11ID',
                'LTST-C190GKT', 'LTST-C190YKT', 'LV-UN3481', 'LVK24R020DER', 'M1270-3005-AL', 'M50-3530242',
                'M9528010 BK001', 'MCP1700T-3002E/TT', 'MCP23017T-E/SO', 'MCR01MZPJ331', 'MDR-60-24', 'MF52C1103F3380',
                'MIC803-26D2VM3-TR', 'MIC94040YFL TR', 'ML-621S/ZTN', 'MMSZ5246B-7-F', 'MPB16L-CBRE-06-JR-3V',
                'MPZ1005S121C', 'N/A', 'NC7WV16P6X', 'NCP718ASN330T1G', 'NJR4266F3D1', 'NL-SW-LTE-S7588-T-C',
                'NL-SW-LTE-S7588-V-B', 'NL-SW-LTE-S7618RD', 'NL-SW-LTE-S7648', 'NL-SW-LTE-WM14-C', 'NPPN101BFCN-RC',
                'NPPN101BFLC-RC', 'NRVTS245ESFT1G', 'NSR0620P2T5G', 'P15.4KDCTR-ND', 'PA4341.103NLT', 'PCR1J101MCL1GS',
                'PCV1V121MCL2GS', 'PDS1040-13', 'PHD-SFS01', 'PHD-SFS02', 'PK-121', 'PMR100HZPFU10L0', 'PP-M30WB-CH7',
                'Printed Vinyl Flag - 2.5? x 3.5?', 'PRT-09914', 'PTS810 SJK 250 SMTR LFS', 'Q2M9-T6S9-window rev01.0',
                'Q5-3X-1/2-01-QB48IN-5', 'QC-DB-M10004', 'QC-DL-M10032', 'RAM-108BU', 'RAM-118BU', 'RAM-231Z-2U',
                'RAM-B-108BU', 'RAM-B-201U-A', 'RAM-B-202-339U', 'RAP-200-1U', 'RAP-201U-B', 'RAP-293U',
                'RAP-379U-252037', 'RAP-B-379U-252025', 'Raspberry Pi 3 Model A+', 'Raspberry Pi 4 4GB',
                'Raspberry Pi Zero W', 'RC0402FR-07100KL', 'RC0402FR-07100RL', 'RC0402FR-07133KL', 'RC0402FR-07150KL',
                'RC0402FR-0716K5L', 'RC0402FR-071K82L', 'RC0402FR-071KL', 'RC0402FR-071ML', 'RC0402FR-0730KL',
                'RC0402FR-0731K6L', 'RC0402FR-07330KL', 'RC0402FR-0734KL', 'RC0402FR-0736KL', 'RC0402FR-073K92L',
                'RC0402FR-07475KL', 'RC0402FR-07499KL', 'RC0402FR-0749K9L', 'RC0402FR-07510KL', 'RC0402FR-075K23L',
                'RC0402FR-07910KL', 'RC0402JR-070RL', 'RC0402JR-07100KL', 'RC0402JR-07100RL', 'RC0402JR-0710KL',
                'RC0402JR-071KL', 'RC0402JR-07330RL', 'RC0402JR-07470RL', 'RC0402JR-074K7L', 'RC0402JR-07750RL',
                'RC0603FR-07249KL', 'RC0603JR-070RL', 'RC0805FR-071K91L', 'RC0805JR-070RL', 'RC1005F3323CS',
                'RC1206FR-0710RP', 'RG1005P-4022-B-T5', 'RL1220S-R20-F', 'RMCF0402FT2K20', 'RMCF0402FT301K',
                'RMCF0402ZT0R00', 'RMCF0603ZT0R00', 'RMCF0805JT100K', 'RMCF0805JT10K0', 'RMCF0805JT1K00',
                'RMCF0805JT24K0', 'RMCF0805JT510K', 'RMCF0805JT75K0', 'RMCF0805JT910K', 'RMCF1206ZT0R00',
                'RMCF2512JT2R00', 'RNCP0603FTD10K0', 'RNF-100-3/32-BK-SP', 'RNG-CNCT-MC4Y', 'RT0402BRD0715KL',
                'RT0402BRD076K81L', 'RUM002N02T2L', 'S-PM4*10/8SUSBK', 'SB021', 'SBRT5A50SA-13', 'SER1360-272KLB',
                'SER2918H-223KL', 'SFW15R-2STE1LF', 'SI3134K-TP', 'SI7288DP-T1-GE3', 'SIM', 'SK-17', 'SK-6',
                'SKM50B-05', 'SKM50B-12', 'SLF6028T-6R8M1R5-PF', 'SMA6F28A', 'SMF24A', 'SML-LX0402SUGC-TR',
                'SN74AUP1T86DCKR', 'SN74LVC1G08DCKR', 'SN74LVC1G3157DCKR', 'SN74LVC2G74DCTR', 'SP1', 'SP3-14',
                'SP3012-04UTG', 'SP7', 'SQD19P06-60L_GE3', 'SRP1265A-4R7M', 'SRU5018-6R8Y', 'SS13', 'SSM3J328R',
                'ST715MR', 'ST730MR', 'SUD50P06-15-GE3', 'T68236300', 'TC7USB40MU', 'TCA9509DGKR', 'TCS34725FN',
                'TF-2309TX', 'TLV75533PDBVR', 'TPD2EUSB30DRTR', 'TPS27081ADDCR', 'TPS71501DCKR', 'TR3D107K010C0065',
                'TSL25911FN', 'TW-06-01-F-D-120-090', 'TXS0102DCUR', 'U.FL-R-SMT-1(10)', 'UCLAMP3311P.TCT',
                'UHE1E101MED', 'V2016B', 'VCUT0714A-HD1-GS08', 'WH-06K-01', 'WH-08-02', 'WQ-50', 'WQ-50P-01',
                'WSL2010R2000FEA', 'WSLP1206R0150FEA', 'X.FL-PR-SMT1-2(80)', 'YB12014000', 'ZZZ260R060',
                'MCCPM-MCPV-3421S-RLS', '0402X106M6R3CT', '0402X475M6R3CT', '0603X475K250CT', '19-337/R6GHBHC-M02/2T',
                '1N4148WS', '5YAA24000202KF60Q2', '5YAA37400161KF60Q1', '6027SC2P2.8+MT', '8.07A0.008200',
                '9UNA32768122TF65CT', 'AO3401A', 'AO3418', 'AP6255', 'AT8563S', 'BL9165-120BARN', 'BL9165-180BARN',
                'BL9165-280BARN', 'BLM15EG221SN1D', 'BLM18EG601SN1D', 'BLM18PG181SH1D', 'CC0402JRNPO9120',
                'CL05A105KP5NNNC', 'CL05C102KB5NNNC', 'CL10A106KP8NNNC', 'CL10A226MP8NUNE', 'CL10B225KO8NNNC',
                'CL21A106KPFNNNE', 'D2516ECMDXGJD', 'DMC3400SDW-7', 'EMMC04G-M627', 'ESD5451N-2/TR', 'ESDA6V8UL-3/TR',
                'GRM1555C1H101JA01D', 'GRM1555C1H220JA01D', 'GRM1555C1H470JA01D', 'GRM155R61E104KA87D',
                'GRM155R71H471KA01D', 'HNRF3015-3R3M-N', 'ITR9608', 'LBAT54XV2T1G', 'MCF12102G900-T',
                'MHCD252010A-1R0M-A8S', 'MMBT3904LT1G', 'NAU85L40YGB', 'NR6045T470M', 'NS4150B', 'PAM2804AAB010',
                'PBY160808T-301Y-N', 'PET-PB00004-OP', 'RK805-2', 'RTT02000JTH', 'RTT021000FTH', 'RTT021001FTH',
                'RTT021003FTH', 'RTT02103JTH', 'RTT021300FTH', 'RTT021330FTH', 'RTT02151JTH', 'RTT02153JTH',
                'RTT021803FTH', 'RTT022001FTH', 'RTT02203JTH', 'RTT02220JTH', 'RTT02222JTH', 'RTT022400FTH',
                'RTT023002FTH', 'RTT02331JTH', 'RTT0233R0FTH', 'RTT02393JTH', 'RTT024701FTH', 'RTT024702FTH',
                'RTT0249R9FTH', 'RTT025103FTH', 'RTT02513JTH', 'RTT025602FTH', 'RTT031R0JTP', 'RTX2521R250JKTE',
                'RV1108A', 'SFH3711', 'SM3R3703T01U', 'SPH4012H4R7MT', 'TAJB107K010RNJ', 'WS3205D61-8/TR',
                'YFC05L-241GS-2A25', 'YFE127S1GN-207-PMR', 'YFE127S1GN-210-PMR', 'YWMX125VS1-02-CR-JD', 'YX-OR1W-850',
                '54', '1825027-8', '815-ABMM-25-B2-T', 'AC0402FR-0710KL', 'AC0402FR-0749K9L', 'AP9211SA-AE-HAC-7',
                'BLM21PG331SN1D', 'C0402C270J5GACTU', 'C1005X7S2A103K050BB', 'CAT24C256WI-GT3', 'CC0402KRX5R5BB105',
                'CC0402KRX7R7BB682', 'CL05C8R2DB5NNNC', 'CL05C8R2DB5NNNC', 'CRCW0402330RFKEDHP', 'CRGP0402F27K',
                'DO1608C-102MLC', 'EMK105B7224MVHF', 'ENC424J600-I/ML', 'ERJ-2RKF2432X', 'ERJ-PA3F3301V',
                'ERJ-PA3F9101V', 'FA2924-AL', 'FDMA8051L', 'GCM155R72A102KA37D', 'GRM155R60J106ME15D',
                'GRM155R62A104KE14D', 'GRM155R71A474KE01D', 'GRM188R61A106KE69D', 'GRM32ER61A107ME20L',
                'HMK325B7225MM-P', 'KDV06FR620ET', 'LP5521YQ/NOPB', 'LTC4040EUFD#PBF', 'LVT12R0100FER', 'MSL0104RGBU1',
                'NTCS0402E3103JLT', 'RC0402FR-070RL', 'RC0402FR-07100RL', 'RC0402FR-07121KL', 'RC0402FR-071KP',
                'RC0402FR-07324KL', 'RC0402FR-07357KL', 'RC0402FR-07392KL', 'RC0402FR-0744K2L', 'RC0402FR-0788K7L',
                'RC0402JR-07100KL', 'RC0402JR-07180RL', 'RC0402JR-0747KL', 'RCS04022K70FKED', 'RCS040275R0FKED',
                'RK73H1JTTD6R80F', 'RMCF0402FT12K4', 'RMCF0402FT1M69', 'RS1B', 'SI-52003-F', 'SI3406-A-GM',
                'SR0402FR-7T10RL', 'TPD4E02B04DQAR', 'TPS2121RUXR', 'TPS62142RGTR', 'TSW-123-17-L-D', 'ULT2D120MNL1GS',
                'USB4085-GF-A', 'UUD1A221MCL1GS', 'XAL5030-222MEC', 'XB24CZ7PIS-004', 'ZM5304AE-CME3R', '15912045',
                '528923033', '175-00001', '74LVC1G08SE-7', 'ATMEGA328P-AUR', 'BSH105,215', 'C1608X5R1C105K080AA',
                'C1608X7R1E104K080AA', 'CC0603KRX5R6BB225', 'CL21A476MQCLRNC', 'CL21B105KOFNNNE', 'CNF7130-1000BG772-G',
                'CPFBZ-A2C5-32.768KD6', 'CTURA1', 'M20-8760342', 'MAX4410EUD+', 'NRC10J620TRF', 'OP999', 'PCH_175',
                'PKLCS1212E40A1-R1', 'RMCF0603JT10K0', 'RMCF0603JT47K0', 'Shift Labs 830-00002', 'TPS60313DGSR',
                '202684-MC03', 'ANT016008LCS2442MA2', 'AP7350-27CF4-7', 'AP7350D-18CF4-7', 'BLM15HG601SN1D',
                'C1005X5R1A475K050BC', 'C1005X5R1C225K050BC', 'CL05A106MP5NUNC', 'CL10A226MP8NUNE',
                'CT DELSS1.12-AABA-36-44G4', 'DFE201610E-4R7MP2', 'DMN3110LCP3-7', 'EM9304V01CS25B',
                'GJM0335C1E1R4BB01D', 'GJM0335C1E4R0BB01E', 'GRM0335C1E220FA01D', 'GRM0335C1H1R6BA01D',
                'GRM0335C1H2R7BA01D', 'GRM033R61C104ME84D', 'GRM033R71A103KA01D', 'GRM033R71E101KA01D',
                'GRM033R71E102KA01D', 'GRM155R61A105KE15D', 'GRM155R61A474KE15D', 'ILCX19-IH5F8', 'LIS2DW12TR',
                'LQM18PN4R7MFRL', 'LQP03TN2N0B02D', 'MBKK1608T2R2M', 'MLG0603P2N3BT000', 'PCap04-BQFM-24',
                'RC0201FR-07100RL', 'RC0201FR-0710KL', 'RC0201FR-0722RL', 'RC0201FR-0747KL', 'RC0201FR-074K7L',
                'RC0201FR-075M1L', 'RC0201FR-07750KL', 'SDM02M30LP3-7B', 'SN74LVC1T45YZPR', 'TS5A3166YZPR',
                'VEMD5080X01', '---OR---',
                "10TB Seagate ST10000NM0016 Exos Enterprise Capacity 3.5'' HDD 10TB (Helium) 7200 RPM SATA 6Gb/s",
                '12 x 32GB PC4-23400 2933MHz DDR4 ECC Registered DIMM', '2 x CBL-SAST-0616 Mini-SAS-HD to 4 SATA 50cm',
                '2 x CBL-SAST-0699 MINI SAS HD-4 SATA,12G,INT,75/75/90/90CM',
                '2 x Enterpr2 e Drives greater than 800GB (imaging software expects to find a device roughly 1TB in size)',
                '2 x Xeon Gold 6230 (Cascade Lake)', '4 x NVIDIA Tesla V100 PCIe 16GB HBM2',
                '4U/Tower GPU Server - Redundant Power Supply',
                '6 x 10TB SATA 6.0Gb/s 7200RPM Enterprise Drives - 3.5“',
                '960GB Intel SSD D3-S4510 Series 2.5" SATA 6.0Gb/s Solid State Drive',
                'GPU Fan Kit: MCP-320-74702-0N-KIT', 'Internal SAS/SATA Cables for RAID Card',
                'Network Interface Card: Mellanox ConnectX-5 VPI MCX556A-ECAT', 'PCIe RAID Card (LSI SAS3108)',
                'RAID 1 (mirror) (PRIMARY BOOT DEVICE, UEFI)', 'RAID 6 (4+2)', 'X11DPG-QT', '04023A3R3CAT2A',
                '0ZCF0100AF2A', '101X43W474MV4E', '202R18W102KV4E', '39501-1002', '5.0SMDJ15A', '500075-1517',
                '597-7717-507F', '625L3C050M00000', '74ALVT16373DGG,118', '74LVC1G08SE-7', '77313-818-14LF', '88E6341',
                '8Z-12.000MAHQ-T', 'ABM10AIG-25.000MHZ-4Z-T3', 'AC0201FR-0747KL', 'AC0402FR-0727KL', 'AD9363BBCZ',
                'ADP1755ACPZ-R7', 'ADUM1201ARZ-RL7', 'AP3418KTR-G1', 'AT24C64D-XHM-B', 'BLM18PG330SN1D',
                'C0402C101K3RAC7867', 'C0402C103K4PACTU', 'C0402C182J3GACTU', 'C0402C220J3GACTU', 'C0402C330J4RACAUTO',
                'C1005X7R1E104K050BB', 'CAT24C64WI-GT3', 'CC0201KRX5R8BB103', 'CC0402KRX5R8BB105', 'CC0402KRX7R7BB103',
                'CC0402KRX7R7BB222', 'CC0402KRX7R8BB102', 'CC0402KRX7R8BB332', 'CC0805KKX7RABB103',
                'CNF7130-1000BG772-G', 'CRCW0402100KFKED', 'CRCW060375R0JNEA', 'CRGCQ0402F180K', 'CRT0402-FZ-3002GLF',
                'CSD17556Q5B', 'DAC8571IDGKR', 'DMC2038LVT-7', 'ECS-MPI2520R0-4R7-R', 'EEE-FK1A221XP',
                'EMMC16G-M525-B53', 'EMVE250ADA470MF55G', 'ERA-2AEB361X', 'ERJ-1GNF1501C', 'ERJ-1GNF3651C',
                'ERJ-1GNF4322C', 'ERJ-1GNF4532C', 'ERJ-1GNF6491C', 'ERJ-2GE0R00X', 'ERJ-2RKF6341X', 'ERJ-2RKF7681X',
                'ERJP08J105V', 'EXB-38V104JV', 'FBMH1608HM600-T', 'FSM4JSMATR', 'FT230XQ-R', 'GRM033R61C104KE84D',
                'GRM033R61E104ME14D', 'GRM1555C1H200JA01D', 'GRM1555C1H270JA01D', 'GRM155C81E105KE11D',
                'GRM155R61E225ME15D', 'GRM188C81C106MA73D', 'GRM188R61A226ME15D', 'GRM31CR60J107ME39L',
                'GRT155R61E474ME01D', 'IS43TR16256AL-15HBLI', 'LM25066APSQE/NOPB', 'LM73606RNPR', 'LP3943ISQ/NOPB',
                'LQH2HPZ6R8MJRL', 'LQH32PN100MN0L', 'LTST-C190KGKT', 'LTST-C190KRKT', 'LTST-C190TBKT', 'M55-6102042R',
                'MCP1316MT-29KE/OT', 'MDMK4040T1R5MF', 'MLC1260-401MLC', 'MLK1005SR10JT000', 'MMBT3904LT1G',
                'MMBT3904LT3G', 'MPZ1005S121CT000', 'MT28EW01GABA1HJS-0SIT TR', 'PESD3V3X1BL,315', 'PFR05S-153-FNH',
                'PI6C557-03BLE', 'RB751S40T5G', 'RC0201JR-074K7L', 'RC0402FR-07100KL', 'RC0402FR-07100RL',
                'RC0402FR-0710KL', 'RC0402FR-0714K3L', 'RC0402FR-0714KL', 'RC0402FR-0717K4L', 'RC0402FR-07187KL',
                'RC0402FR-071KL', 'RC0402FR-071RL', 'RC0402FR-0720KL', 'RC0402FR-07240RL', 'RC0402FR-0724K9L',
                'RC0402FR-0727R4L', 'RC0402FR-072K37L', 'RC0402FR-0736RL', 'RC0402FR-0737R4L', 'RC0402FR-0743KL',
                'RC0402FR-07475RL', 'RC0402FR-0749R9L', 'RC0402FR-074K99L', 'RC0402FR-0768KL', 'RC0402JR-070RL',
                'RC0402JR-07100KL', 'RC0402JR-0710KL', 'RC0402JR-071KL', 'RC0402JR-07200KL', 'RC0402JR-0722RL',
                'RC0402JR-07300RL', 'RC0402JR-07330RL', 'RC0402JR-0733RL', 'RC0402JR-074K7L', 'RC0402JR-07560RL',
                'RC0805FR-072R05L', 'RC2512JK-070RL', 'RCL12250000Z0EG', 'RK73H1ETTP1500F', 'RMCF0201FT10K0',
                'RMCF0402FT3K01', 'RMCF0402FT8K45', 'RMCF0805JT120R', 'SMBJ16CA', 'SN74CBTD3861PWR', 'SN74LVC1G08DCKR',
                'SN74LVC1G17QDCKRQ1', 'SPM6550T-2R2M-HZ', 'SRP5030TA-1R5M', 'TCM1-63AX+', 'TL1105JAF160Q',
                'TMK325ABJ476MM-P', 'TMP464AIRGTR', 'TPS51200DRCR', 'TPS53353DQPT', 'TPS54319RTET', 'TPS54519RTET',
                'TPSE687K006R0045', 'TXB0101DBVR', 'U.FL-R-SMT-1(10)', 'U7769LF', 'WSL12064L000FEA']

    @staticmethod
    def get_headers() -> Dict:
        return {
            "Accept-Language": "en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }

    def get_content(self, url: str, timeout: int = 60) -> (str, str):
        """
            Returns the content of the HTTP Request and the URL.
        """
        data = requests.get(url, headers=self.get_headers(), timeout=timeout)
        assert data.status_code == 200
        return data.text, data.url

    @staticmethod
    def extract_general_part_data(soup: BeautifulSoup) -> Dict:
        """
            Extract the General Part Data Info.
            This Function extracts the following information
                1) DIGI Key Part No.
                2) Manufacturer
                3) MPN
                4) Description & Detailed Description
        """
        results = dict()
        product_overview = soup.find('div', attrs={'class': 'product-overview-wrapper product-details-section'})
        if not product_overview:
            product_overview = soup.find('div', attrs={'data-evg': 'product-details-overview'})
            product_overview = product_overview.find('tbody') if product_overview else product_overview

        if product_overview:
            all_rows = product_overview.find_all('tr')
            for row in all_rows:
                if row.find_all('td')[0].text.strip().lower() == 'digi-key part number':
                    part_no = row.find_all('td')[1].text.strip()
                    results['Digi-Key Part Number'] = part_no.split(" ")[0]
                if row.find_all('td')[0].text.strip().lower() == 'manufacturer':
                    results['Manufacturer'] = row.find_all('td')[1].text.strip()
                if row.find_all('td')[0].text.strip().lower() == 'manufacturer part number' \
                        or row.find_all('td')[0].text.strip().lower() == 'manufacturer product number':
                    results['MPN'] = row.find_all('td')[1].text.strip()
                if row.find_all('td')[0].text.strip().lower() == 'description':
                    results['Description'] = row.find_all('td')[1].text.strip()
                if row.find_all('td')[0].text.strip().lower() == 'detailed description':
                    results['Detailed Description'] = row.find_all('td')[1].text.strip()

        return results

    @staticmethod
    def extract_documents_and_media(soup: BeautifulSoup) -> Dict:
        """
            Extract Documents and Media. Following three Documents are scraped.
                1) DataSheets
                2) EDA/CAD Models
                3) Online Catalog

        """
        results = {
            'Datasheets': list(),
            'EDA / CAD Models': list(),
            'Online Catalog': list()
        }
        document_section = soup.find(
            'div',
            attrs={'class': 'product-details-documents-media product-details-section'}
        )
        if not document_section:
            document_section = soup.find('div', attrs={'data-evg': 'product-details-docs-n-media'})
            document_section = document_section.find('tbody') if document_section else document_section

        if document_section:
            for row in document_section.find_all('tr'):
                if row.find('td').text.strip() in results.keys():
                    output = {
                        "name": row.find_all('td')[1].find('a').text.strip(),
                        "value": [i.find('a').get('href')
                                  for i in row.find_all('td')[1].find_all('div', attrs={'class': 'jss84'})]
                    }
                    if not output['value']:
                        output['value'] = [row.find_all('td')[1].find('a').get('href')]
                    results[row.find('td').text.strip()] = json.dumps(output['value'])

        return results

    @staticmethod
    def extract_product_attributes(soup: BeautifulSoup) -> Dict:
        """
            Extract the Product Specifications from the HTML Content.
            Product Specs like "Category", "Mfr", "Series", "Package", "Part Status",
            "Tolerance", "Dissipation Factor" etc are being extracted.
        """
        results = dict()
        product_attributes = soup.find(
            'div',
            attrs={'class': 'product-details-product-attributes product-details-section'}
        )
        if not product_attributes:
            product_attributes = soup.find(
                'div',
                attrs={'data-evg': 'product-details-product-attributes'}
            )

            product_attributes = product_attributes.find('tbody') if product_attributes else product_attributes

        if product_attributes:
            product_attributes = product_attributes.find_all('tr')
            for row in product_attributes:
                row_value = row.find_all('td')[1].find('div')
                value = ' '.join([i.text.strip() for i in row_value.find_all('div')])
                value = row_value.text.strip() if not value else value
                results[row.find_all('td')[0].text.strip()] = value

            environment_attributes = soup.find('table', attrs={'class': 'env-and-export-table'})
            if not environment_attributes:
                environment_attributes = soup.find(
                    'div',
                    attrs={
                        'data-evg': 'product-details-environmental'
                    }
                )
                environment_attributes = environment_attributes.find('tbody')
            for row in environment_attributes.find_all('tr'):
                row_value = row.find_all('td')[1].find('div')
                value = ' '.join([i.text.strip() for i in row_value.find_all('div')]) \
                    if row_value else row.find_all('td')[1].text.strip()
                value = row_value.text.strip() if not value else value
                results[row.find_all('td')[0].text.strip()] = value

        return results

    def extract_images_links(self, soup: BeautifulSoup) -> List:
        """
            Extract the Image Links from the HTML Content.
        """
        image_links = list()
        images = soup.find('div', attrs={'class': 'product-photo-carousel'})
        if not images:
            images = soup.find('div', attrs={'data-testid': 'carousel-container'})
        if images:
            images = images.find_all('img')
            for image in images:
                image_url = image.get('href')
                if not image_url:
                    image_url = image.get('src')

                image_links.append(f"{self.BASE_URL}{image_url}")

        return image_links

    def extract_elements(self, mpn: str, soup: BeautifulSoup, url: str) -> None:
        """
            Check if the WebPage gives us the /products/filter/ page.
            This means the WebPage has shown us possible products against our keyword.
            So we select the first product, get its HTML content and scrape that product.

            If the WebPage is redirected to /products/details page that means it has been
            redirected to the product detail page so we directly scrape the content.

            If the WebPage shows any other content, we simply ignore that
        """
        result = dict()
        table_data = soup.find('tbody', attrs={'id': 'lnkPart'})
        if not table_data:
            table_data = soup.find('table', attrs={'id': 'data-table-0'})
            table_data = table_data.find('tbody') if table_data else table_data

        zero_results = soup.find('span', attrs={'data-testid': 'zero-results-header'})
        zero_results = soup.find('div', attrs={'id': 'noResults'}) if not zero_results else zero_results
        if zero_results or 'products/result' in url:
            print(f"{threading.current_thread().name}: No Results found for {mpn}..")
            return
        if table_data:
            all_rows = table_data.find_all('tr')
            row = all_rows[0]
            digi_key_part_no = row.find('td', attrs={'class': 'tr-dkPartNumber'})
            if not digi_key_part_no:
                digi_key_part_no = row.find('td', attrs={'data-atag': 'tr-product'})

            part_link = digi_key_part_no.find_all('a')
            part_link = part_link[1].get('href') \
                if '.pdf' in part_link[0].get('href') else part_link[0].get('href')
            data, url = self.get_content(f"{self.BASE_URL}{part_link}")
            soup = BeautifulSoup(data)

        result["General Part Data"] = self.extract_general_part_data(soup)
        if len(result['General Part Data'].keys()) == 0:
            raise Exception(f"{threading.current_thread().name}: Content Not Loaded. Trying again for {mpn}...")
        result["Documents & Media"] = self.extract_documents_and_media(soup)
        result["Product Attributes"] = self.extract_product_attributes(soup)
        result['Images'] = self.extract_images_links(soup)
        price = soup.find('div', attrs={'data-testid': 'total-selected-price'})
        # result['Price and Procurement'] = self.extract_price_and_procurement(soup)
        result['Price'] = re.search("\\d*,*\\d+\\.*\\d+", price.text.strip()).group(0) if price else ''
        result['URL'] = url
        print(f"{threading.current_thread().name}: Found result for {mpn}")
        self.final_results.append(result)

    def extract_price_and_procurement(self, soup):
        result = {}
        price_info = soup.find('div', attrs={'data-evg': 'priced-in'})
        if not price_info:
            price_info = soup.find('div', attrs={'data-testid': 'pricing-table-container'})

        if price_info:
            for table in price_info.find_all('table'):
                header = table.previous_sibling.text.strip()
                if not header:
                    continue

                headers = [header.text.strip() for header in soup.find('thead').find('th')]
                table_rows = soup.find('tbody').find('tr')
                for row in table_rows:
                    result[header] = dict()
                    for key, value in zip(headers, row):
                        result[header][key] = value

        return result

    def run(self) -> None:
        """
            Main Thread Function. This function does the following things.
                1) Get the record from MPN_RECORDS object
                2) Get the HTML Content against the URL created from that record.
                3) Scrape and Extract the Elements from it.
                4) if there is any exception while scraping. Retry until the retry_max_value is reached.
        """
        while len(self.MPN_RECORDS) > 0:
            retry_count = 0
            mpn = self.MPN_RECORDS.pop(0)
            print(f"{threading.current_thread().name}: Iterating over {mpn}")
            while True:
                try:
                    data, url = self.get_content(self.PRODUCTS_URL.format(base_url=self.BASE_URL, mpn_no=mpn), timeout=60)
                    print(
                        f"{threading.current_thread().name}: "
                        f"{self.PRODUCTS_URL.format(base_url=self.BASE_URL, mpn_no=mpn)}")
                    if 'products/category' in url:
                        #Example: https://www.digikey.com/en/products/category/discrete-semiconductor-products/19?s=N4IgTCBcDaIEIC0AaAOALAYTQNQOwgF0BfIA
                        print("We are not currently scraping the category page!!")
                        break
                    soup = BeautifulSoup(data)
                    self.extract_elements(mpn, soup, url)
                    break
                except Exception as e:
                    print(f"{threading.current_thread().name}: Error with {url}\nException: {str(e)}")

                    if retry_count >= 3:
                        break
                    retry_count += 1
                    continue

    def insert_records_in_db(self) -> None:
        """
            Inserts data in the Database.
            For each result
                1) Create the GenericPart object if not exists. If already exists
                    get that record.
                2) Create the Specific object if not exists. If already exists
                    update that record.
                3) For each Product Specification, Create the PartSpecifications object if not exists.
                    If already exists update that record and add it to the Specific Part.
                4) Create the DocumentsMedia object if not exists. If already exists
                    update that record.
                5) Create the GenericPart object if not exists. If already exists
                    update that record.
                6) For each Image, Create the PartImage object if not exists. If already exists
                    update that record.
        """
        for result in self.final_results:
            generic_part_obj, _ = GenericPart.objects.get_or_create(
                part_type=result["Product Attributes"]['Category']
            )
            specific_part, _ = SpecificPart.objects.update_or_create(
                generic_part=generic_part_obj,
                defaults={
                    'digi_key_part_no': result["General Part Data"].get('Digi-Key Part Number', ''),
                    'manufacturer': result["General Part Data"].get('Manufacturer', ''),
                    'mpn': result["General Part Data"].get('MPN', ''),
                    'description': result["General Part Data"].get('Description', ''),
                    'detailed_description': result["General Part Data"].get('Detailed Description', ''),
                    'digikey_link': result['URL'],
                    'price': result['Price']
                }
            )
            for key, value in result["Product Attributes"].items():
                spec, _ = PartSpecifications.objects.update_or_create(
                    spec_name=key,
                    defaults={'spec_value': value}
                )
                specific_part.specifications.add(spec)

            DocumentsMedia.objects.update_or_create(
                specific_part=specific_part,
                defaults={
                    'data_sheets': result['Documents & Media']['Datasheets'],
                    'eda_cad_models': result['Documents & Media']['EDA / CAD Models'],
                    'online_catalog': result['Documents & Media']['Online Catalog']
                }
            )
            for image_link in result['Images']:
                PartImages.objects.update_or_create(
                    specific_part=specific_part, image_link=image_link
                )

    def start_scraper(self):
        """
            Execute the DIGI Key Scraper in Multiple threads.
        """
        print("Starting Scraping...")
        thread_names = []
        for _ in range(self.NUMBER_OF_THREADS):
            t = threading.Thread(target=self.run)
            t.start()
            thread_names.append(t)

        for thread in thread_names:
            thread.join()

        self.insert_records_in_db()
        print("Completed Scraping...")


if __name__ == "__main__":
    DIGIKeyScraper().start_scraper()

