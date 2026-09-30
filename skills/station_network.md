# station_network — which station sits where along the rivers
Reconstructed station topology for the thaiwater telemetry network (the API has **no** explicit station-to-station link table).
- Snapshot: `waterlevel_load` readings of 2026-09-30 12:00 (retrieved 2026-09-30 07:34 BKK), 806 stations with coordinates.
- Method: group by `river_name`, then walk a greedy nearest-neighbour chain starting from the northern-most station of the group (Thai rivers in this payload flow roughly S / SW). Leg distances are great-circle, not river km — use them to rank order, not as exact river distances.
- Cross-check: the RID main-stem numbering itself runs downstream (C.2 → C.13 → C.3 → C.7A → C.12) and agrees with the reconstructed order.
- Station families share sites: RID `C.*/P.*/N.*/Y.*/W.*/S.*/T.*`, HII `CPY*/PIN*/NAN*/YOM*/WAN*/PAS*/THA*/TCP*/BKC*/CHM*`, EGAT `BBD*/SKD*/MKVKD*/RAJ*`. A site usually has one gauge per family, a few metres apart — that is what the co-located table below lists.

## 1. Chao Phraya main stem (ordered downstream)
```
## แม่น้ำเจ้าพระยา  (20 stations, chain length 250 km)
    start  CPY001    สะพานเดชาติวงศ์                  15.6885,100.1238 HII  msl=23.52 sit=4 ต่ำกว่าตลิ่ง (ม.)
   2.52 km  C.2       ค่ายจิรประวัติ                   15.6706,100.1094 RID  msl=23.77 sit=4 ต่ำกว่าตลิ่ง (ม.)
  27.27 km  CPY002    พยุหะคีรี                        15.4266,100.1347 HII  msl=19.86 sit=4 ต่ำกว่าตลิ่ง (ม.)
  11.33 km  CPY003    ปตร.มโนรมย์                      15.3277,100.1091 HII  msl=16.25 sit=3 ต่ำกว่าตลิ่ง (ม.)
   9.04 km  CPY004    สะพานธรรมจักร(วัดธรรมามูล)       15.2503,100.0835 HII  msl=18.61 sit=5 ล้นตลิ่ง (ม.)
  14.77 km  C.13      ท้ายเขื่อนเจ้าพระยา              15.1638,100.1879 RID  msl=15.22 sit=4 ต่ำกว่าตลิ่ง (ม.)
  10.52 km  CPY005    สรรพยา                           15.1091,100.2678 HII  msl=14.44 sit=4 ต่ำกว่าตลิ่ง (ม.)
  13.31 km  CPY006    อินทร์บุรี                       15.0060,100.3309 HII  msl=13.29 sit=4 ต่ำกว่าตลิ่ง (ม.)
  14.16 km  C.3       บ้านบางพุทรา                     14.8987,100.4019 RID  msl=11.74 sit=4 ต่ำกว่าตลิ่ง (ม.)
  13.13 km  CPY007    พรหมบุรี                         14.7909,100.4518 HII  msl=10.11 sit=4 ต่ำกว่าตลิ่ง (ม.)
  22.29 km  C.7A      บ้านบางแก้ว                      14.5904,100.4533 RID  msl=8.25 sit=4 ต่ำกว่าตลิ่ง (ม.)
   1.63 km  CPY008    เมืองอ่างทอง                     14.5765,100.4485 HII  msl=7.96 sit=4 ต่ำกว่าตลิ่ง (ม.)
  24.62 km  CPY011    พระนครศรีอยุธยา                  14.3691,100.5286 HII  msl=4.46 sit=4 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  C.35      บ้านป้อม                         14.3691,100.5287 RID  msl=4.94 sit=5 ล้นตลิ่ง (ม.)
   8.25 km  CPY012    บางปะอิน                         14.3046,100.5665 HII  msl=3.07 sit=5 ล้นตลิ่ง (ม.)
  39.85 km  CPY014    สะพานนวลฉวี                      13.9475,100.5351 HII  msl=2.35 sit=4 ต่ำกว่าตลิ่ง (ม.)
  17.94 km  C.12      กรมชลประทานสามเสน                13.7881,100.5091 RID  msl=1.75 sit=4 ต่ำกว่าตลิ่ง (ม.)
   9.93 km  CPY015    สะพานกรุงเทพ                     13.7003,100.4928 HII  msl=0.86 sit=4 ต่ำกว่าตลิ่ง (ม.)
   7.05 km  BKC003    ปตร. คลองลัดบางยอ 1              13.6762,100.5531 HII  msl=1.14 sit=4 ต่ำกว่าตลิ่ง (ม.)
   2.28 km  BKC004    ปตร. คลองลัดบางยอ 2              13.6610,100.5673 HII  msl=0.54 sit=4 ต่ำกว่าตลิ่ง (ม.)
```
**Answer to "what is above C.13?"** — C.13 (ท้ายเขื่อนเจ้าพระยา) sits at the Chao Phraya Dam tailrace in Chai Nat. Above it, in order: `CPY004` สะพานธรรมจักร (วัดธรรมามูล, 14.8 km) on the dam headpond → `CPY003` ปตร.มโนรมย์ (9.0 km) → `CPY002` พยุหะคีรี (11.3 km) → `C.2` ค่ายจิรประวัติ (27.3 km) → `CPY001` สะพานเดชาติวงศ์ (2.5 km) at the Ping–Nan confluence (Pak Nam Pho, Nakhon Sawan).
Below C.13: `CPY005` สรรพยา → `CPY006` อินทร์บุรี → `C.3` บ้านบางพุทรา → `CPY007` พรหมบุรี → `C.7A` บ้านบางแก้ว → `CPY008` เมืองอ่างทอง → `CPY011`/`C.35` พระนครศรีอยุธยา → `CPY012` บางปะอิน → `CPY014` สะพานนวลฉวี (Pathum Thani) → `C.12` สามเสน → `CPY015` สะพานกรุงเทพ → `BKC003`/`BKC004`.

## 2. Feeder rivers above C.2 (ordered downstream)
```
## แม่น้ำปิง  (20 stations, chain length 452 km)
    start  CHM004    เชียงดาว                         19.3673,98.9688 HII  msl=379.24 sit=3 ต่ำกว่าตลิ่ง (ม.)
  39.76 km  P.67      บ้านแม่แต                        19.0099,98.9597 RID  msl=316.41 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  CHM001    สันทราย                          19.0098,98.9597 HII  msl=315.35 sit=2 ต่ำกว่าตลิ่ง (ม.)
  16.05 km  P.103     สะพานวงแหวนรอบ 3                 18.8665,98.9782 RID  msl=304.02 sit=3 ต่ำกว่าตลิ่ง (ม.)
   9.29 km  P.1       สะพานนวรัฐ                       18.7870,99.0051 RID  msl=302.04 sit=3 ต่ำกว่าตลิ่ง (ม.)
  66.77 km  P.73      บ้านสบสอย                        18.2913,98.6476 RID  msl=265.07 sit=4 ต่ำกว่าตลิ่ง (ม.)
   4.26 km  P.73A     บ้านสบแปะ                        18.2534,98.6414 RID  msl=260.94 sit=3 ต่ำกว่าตลิ่ง (ม.)
   8.40 km  CHM002    ฮอด                              18.1786,98.6302 HII  msl=257.51 sit=3 ต่ำกว่าตลิ่ง (ม.)
  112.67 km  P.12C     บ้านย่านรี                       17.2382,99.0263 RID  msl=128.03 sit=1 ต่ำกว่าตลิ่ง (ม.)
  22.37 km  PIN001    บ้านตาก                          17.0407,99.0663 HII  msl=118.96 sit=3 ต่ำกว่าตลิ่ง (ม.)
  21.53 km  P.2A      บ้านท่าแค                        16.8553,99.1245 RID  msl=105.25 sit=3 ต่ำกว่าตลิ่ง (ม.)
   9.92 km  PIN002    เมืองตาก                         16.7866,99.1840 HII  msl=100.29 sit=3 ต่ำกว่าตลิ่ง (ม.)
  31.80 km  PIN003    สะพานลานดอกไม้                   16.6282,99.4326 HII  msl=81.93 sit=3 ต่ำกว่าตลิ่ง (ม.)
  19.04 km  PIN006    เมืองกำแพงเพชร (P7A)             16.4782,99.5187 HII  msl=74.14 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.09 km  P.7A      ต.ในเมือง                        16.4777,99.5179 RID  msl=74.45 sit=3 ต่ำกว่าตลิ่ง (ม.)
  36.53 km  P.15      หน้าวัดศรีภิรมย์                 16.2141,99.7223 RID  msl=56.53 sit=4 ต่ำกว่าตลิ่ง (ม.)
  22.21 km  P.16      บ้านแสนตอ                        16.0647,99.8602 RID  msl=45.56 sit=4 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  PIN004    ขาณุวรลักษบุรี                   16.0648,99.8603 HII  msl=45.37 sit=5 ล้นตลิ่ง (ม.)
  18.98 km  P.17      บ้านท่างิ้ว                      15.9354,99.9761 RID  msl=38.33 sit=5 ล้นตลิ่ง (ม.)
  12.45 km  PIN005    เก้าเลี้ยว                       15.8505,100.0521 HII  msl=31.87 sit=5 ล้นตลิ่ง (ม.)
```
```
## แม่น้ำวัง  (15 stations, chain length 241 km)
    start  MOU323    สะพานน้ำวัง                      19.2325,99.6325 FOP  msl=442.87 sit=2 ต่ำกว่าตลิ่ง (ม.)
  26.89 km  W.25      บ้านร่องเคาะ                     18.9909,99.6211 RID  msl=382.48 sit=2 ต่ำกว่าตลิ่ง (ม.)
  22.90 km  W.16A     บ้านไฮ                           18.7852,99.6304 RID  msl=305.32 sit=3 ต่ำกว่าตลิ่ง (ม.)
  29.62 km  W.10B     บ้านแลง                          18.5188,99.6300 RID  msl=259.37 sit=3 ต่ำกว่าตลิ่ง (ม.)
  21.86 km  W.21      บ้านท่าเดื่อ                     18.3430,99.5372 RID  msl=232.66 sit=2 ต่ำกว่าตลิ่ง (ม.)
   5.54 km  W.1C      สะพานเสตุวารี                    18.2997,99.5112 RID  msl=229.65 sit=3 ต่ำกว่าตลิ่ง (ม.)
  17.05 km  W.5A      บ้านเกาะคา                       18.1915,99.3969 RID  msl=217.15 sit=3 ต่ำกว่าตลิ่ง (ม.)
   3.85 km  WAN004    เกาะคา                           18.1592,99.3841 HII  msl=211.50 sit=3 ต่ำกว่าตลิ่ง (ม.)
  48.13 km  WAN003    เถิน                             17.7517,99.2306 HII  msl=172.24 sit=3 ต่ำกว่าตลิ่ง (ม.)
  12.26 km  W.3A      บ้านดอนชัย                       17.6415,99.2320 RID  msl=161.35 sit=3 ต่ำกว่าตลิ่ง (ม.)
  24.41 km  WAN002    แม่พริก                          17.4452,99.1290 HII  msl=148.92 sit=3 ต่ำกว่าตลิ่ง (ม.)
   8.90 km  W.23      บ้านแม่เชียงราย                  17.3666,99.1130 RID  msl=144.86 sit=3 ต่ำกว่าตลิ่ง (ม.)
   6.28 km  W.24      บ้านท่าไผ่                       17.3217,99.0772 RID  msl=140.62 sit=3 ต่ำกว่าตลิ่ง (ม.)
   6.80 km  WAN001    สามเงา                           17.2605,99.0780 HII  msl=135.21 sit=3 ต่ำกว่าตลิ่ง (ม.)
   6.54 km  W.4A      บ้านวังหมัน                      17.2050,99.0981 RID  msl=134.24 sit=3 ต่ำกว่าตลิ่ง (ม.)
```
```
## แม่น้ำยม  (24 stations, chain length 383 km)
    start  Y.31      บ้านทุ่งหนอง                     18.9463,100.2589 RID  msl=259.09 sit=3 ต่ำกว่าตลิ่ง (ม.)
  40.22 km  YOM013    ศาลเจ้าพ่อพญาอ้น                 18.5997,100.1496 HII  msl=183.88 sit=3 ต่ำกว่าตลิ่ง (ม.)
   1.52 km  Y.20      บ้านห้วยสัก                      18.5861,100.1513 RID  msl=183.00 sit=3 ต่ำกว่าตลิ่ง (ม.)
  13.36 km  YOM014    สะพานหนองจันทร์                  18.4660,100.1517 HII  msl=171.69 sit=2 ต่ำกว่าตลิ่ง (ม.)
  22.41 km  YOM003    หนองม่วงไข่                      18.2659,100.1771 HII  msl=154.21 sit=2 ต่ำกว่าตลิ่ง (ม.)
  15.69 km  Y.1C      บ้านน้ำโค้ง                      18.1339,100.1246 RID  msl=145.50 sit=2 ต่ำกว่าตลิ่ง (ม.)
   0.03 km  YOM010    เมืองแพร่                        18.1337,100.1246 HII  msl=145.34 sit=3 ต่ำกว่าตลิ่ง (ม.)
  14.35 km  YOM004    เด่นชัย                          18.0208,100.0588 HII  msl=139.69 sit=3 ต่ำกว่าตลิ่ง (ม.)
  49.74 km  Y.37      บ้านวังชิ้น                      17.9012,99.6057 RID  msl=96.46 sit=3 ต่ำกว่าตลิ่ง (ม.)
  45.68 km  YOM005    ศรีสัชนาลัย                      17.5172,99.7588 HII  msl=62.30 sit=2 ต่ำกว่าตลิ่ง (ม.)
  25.06 km  Y.3A      บ้านวังขอนไม้                    17.3024,99.8303 RID  msl=55.66 sit=3 ต่ำกว่าตลิ่ง (ม.)
  11.73 km  YOM006    สวรรคโลก                         17.2019,99.8639 HII  msl=53.11 sit=3 ต่ำกว่าตลิ่ง (ม.)
   3.68 km  Y.33      บ้านคลองตาล                      17.1689,99.8610 RID  msl=52.22 sit=3 ต่ำกว่าตลิ่ง (ม.)
  16.99 km  YOM012    เมืองสุโขทัย                     17.0213,99.8197 HII  msl=48.70 sit=3 ต่ำกว่าตลิ่ง (ม.)
   1.68 km  Y.4       ต.ธานี                           17.0064,99.8221 RID  msl=48.82 sit=4 ต่ำกว่าตลิ่ง (ม.)
  17.04 km  YOM007    กงไกรลาศ                         16.9273,99.9593 HII  msl=42.44 sit=4 ต่ำกว่าตลิ่ง (ม.)
   0.02 km  Y.15      บ้านกง                           16.9274,99.9594 RID  msl=42.73 sit=4 ต่ำกว่าตลิ่ง (ม.)
  13.13 km  VLGE13    ชุมแสงสงคราม                     16.8586,100.0597 HII  msl=40.94 sit=5 ล้นตลิ่ง (ม.)
  12.57 km  Y.64      บางระกำ                          16.7621,100.1212 RID  msl=38.94 sit=5 ล้นตลิ่ง (ม.)
   0.76 km  Y.16      บางระกำ                          16.7579,100.1156 RID  msl=38.97 sit=5 ล้นตลิ่ง (ม.)
   8.15 km  YOM008    บางระกำ                          16.7082,100.1718 HII  msl=33.35 sit=3 ต่ำกว่าตลิ่ง (ม.)
  22.58 km  Y.17      สามง่าม                          16.5074,100.2041 RID  msl=36.16 sit=4 ต่ำกว่าตลิ่ง (ม.)
  23.03 km  YOM009    โพธิ์ประทับช้าง                  16.3108,100.2717 HII  msl=32.58 sit=4 ต่ำกว่าตลิ่ง (ม.)
  24.05 km  Y.5       หน้าอำเภอโพทะเล                  16.0948,100.2599 RID  msl=29.27 sit=4 ต่ำกว่าตลิ่ง (ม.)
```
```
## แม่น้ำน่าน  (26 stations, chain length 411 km)
    start  NAN001    ท่าวังผา                         19.0961,100.8026 HII  msl=218.41 sit=2 ต่ำกว่าตลิ่ง (ม.)
   9.29 km  SKU02     อ.ท่าวังผา (N.64)                19.0153,100.7802 EGAT msl=212.46 sit=2 ต่ำกว่าตลิ่ง (ม.)
   0.02 km  N.64      บ้านผาขวาง                       19.0152,100.7802 RID  msl=212.52 sit=2 ต่ำกว่าตลิ่ง (ม.)
  17.72 km  NAN002    ภูเพียง                          18.8597,100.8171 HII  msl=197.36 sit=2 ต่ำกว่าตลิ่ง (ม.)
  10.22 km  N.1       หน้าสำนักงานป่าไม้               18.7749,100.7797 RID  msl=193.30 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  SKU03     อ.เมืองน่าน (N.1)                18.7749,100.7797 EGAT msl=193.27 sit=2 ต่ำกว่าตลิ่ง (ม.)
   4.80 km  NAN003    เมืองน่าน                        18.7380,100.7561 HII  msl=190.78 sit=3 ต่ำกว่าตลิ่ง (ม.)
  20.91 km  SKU04     อ.เวียงสา (N.13A) น้ำน่าน        18.5500,100.7606 EGAT msl=178.76 sit=2 ต่ำกว่าตลิ่ง (ม.)
   0.09 km  NAN009    เวียงสา                          18.5499,100.7615 HII  msl=179.96 sit=3 ต่ำกว่าตลิ่ง (ม.)
  93.61 km  N.12A     บ้านหาดไผ่                       17.7369,100.5316 RID  msl=70.47 sit=2 ต่ำกว่าตลิ่ง (ม.)
  34.48 km  SKD02     บ้านผาจุก                        17.6682,100.2141 EGAT msl=55.80 sit=2 ต่ำกว่าตลิ่ง (ม.)
  13.76 km  N.2B      ต.ในเมือง                        17.6099,100.0996 RID  msl=52.77 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.03 km  NAN011    เมืองอุตรดิตถ์                   17.6101,100.0994 HII  msl=52.83 sit=3 ต่ำกว่าตลิ่ง (ม.)
  21.56 km  SKD04     บ้านหาดสองแคว (N.60)             17.4185,100.1308 EGAT msl=49.51 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.02 km  NAN014    ตรอน                             17.4183,100.1308 HII  msl=49.19 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.02 km  N.60      บ้านเด่นสำโรง                    17.4183,100.1309 RID  msl=49.66 sit=3 ต่ำกว่าตลิ่ง (ม.)
  14.70 km  NAN004    พิชัย                            17.2943,100.0828 HII  msl=47.84 sit=3 ต่ำกว่าตลิ่ง (ม.)
  31.47 km  N.27A     ท้ายเขื่อนนเรศวร                 17.0336,100.1980 RID  msl=40.61 sit=3 ต่ำกว่าตลิ่ง (ม.)
  19.43 km  NAN012    เมืองพิษณุโลก                    16.8647,100.2448 HII  msl=38.27 sit=3 ต่ำกว่าตลิ่ง (ม.)
   6.52 km  N.5A      สะพานสุพรรณกัลยา                 16.8061,100.2458 RID  msl=37.73 sit=3 ต่ำกว่าตลิ่ง (ม.)
  14.95 km  DIV004    คลองผันน้ำยม-น่าน4               16.6717,100.2458 HII  msl=37.84 sit=3 ต่ำกว่าตลิ่ง (ม.)
  10.17 km  NAN006    บางกระทุ่ม                       16.5805,100.2386 HII  msl=34.05 sit=3 ต่ำกว่าตลิ่ง (ม.)
  15.78 km  N.7A      บ้านราชช้างขวัญ                  16.4695,100.3309 RID  msl=32.94 sit=4 ต่ำกว่าตลิ่ง (ม.)
  23.85 km  NAN007    ตะพานหิน                         16.2703,100.4140 HII  msl=31.53 sit=4 ต่ำกว่าตลิ่ง (ม.)
  47.36 km  NAN008    ชุมแสง                           15.8692,100.2648 HII  msl=25.74 sit=4 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  N.67      วัดเกยไชยเหนือ                   15.8692,100.2647 RID  msl=26.28 sit=4 ต่ำกว่าตลิ่ง (ม.)
```

## 3. Branches and distributaries (ordered downstream)
```
## แม่น้ำป่าสัก  (15 stations, chain length 336 km)
    start  S.33      ต.ตาดกลอย                        17.0041,101.3529 RID  msl=193.55 sit=3 ต่ำกว่าตลิ่ง (ม.)
  27.20 km  S.3       ต.ตาลเดี่ยว                      16.7816,101.2467 RID  msl=142.52 sit=3 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  PAS001    หล่มสัก                          16.7815,101.2467 HII  msl=142.10 sit=3 ต่ำกว่าตลิ่ง (ม.)
  37.99 km  PAS002    เมืองเพชรบูรณ์                   16.4479,101.1702 HII  msl=115.68 sit=4 ต่ำกว่าตลิ่ง (ม.)
   2.87 km  S.4B      ต.ในเมือง                        16.4232,101.1621 RID  msl=114.71 sit=4 ต่ำกว่าตลิ่ง (ม.)
  34.97 km  PAS003    หนองไผ่                          16.1150,101.0971 HII  msl=93.95 sit=5 ล้นตลิ่ง (ม.)
  59.68 km  S.42      บ้านบ่อวัง                       15.5783,101.0886 RID  msl=63.26 sit=5 ล้นตลิ่ง (ม.)
  30.89 km  S.43      บ้านพูลทรัพย์                    15.3274,101.2124 RID  msl=48.03 sit=4 ต่ำกว่าตลิ่ง (ม.)
  56.50 km  S.28      ท้ายเขื่อนป่าสักชลสิทธิ์         14.8346,101.0843 RID  msl=19.68 sit=2 ต่ำกว่าตลิ่ง (ม.)
  24.05 km  S.9       บ้านป่า                          14.6292,101.0144 RID  msl=11.14 sit=3 ต่ำกว่าตลิ่ง (ม.)
  12.56 km  S.32      สถานีแพดับเพลิง                  14.5575,100.9242 RID  msl=8.63 sit=3 ต่ำกว่าตลิ่ง (ม.)
  21.99 km  S.26      ท้ายเขื่อนพระรามหก               14.5601,100.7199 RID  msl=6.76 sit=4 ต่ำกว่าตลิ่ง (ม.)
   0.01 km  PAS008    ท่าเรือ                          14.5601,100.7199 HII  msl=6.41 sit=5 ล้นตลิ่ง (ม.)
  22.65 km  PAS009    นครหลวง                          14.4027,100.5864 HII  msl=3.66 sit=4 ต่ำกว่าตลิ่ง (ม.)
   4.93 km  S.5       สะพานปรีดี-ธำรง                  14.3587,100.5805 RID  msl=3.76 sit=4 ต่ำกว่าตลิ่ง (ม.)
```
```
## แม่น้ำท่าจีน  (10 stations, chain length 184 km)
    start  THA001    สะพานคง-ศุข ศรีสวัสดิ์           15.2250,100.0782 HII  msl=17.71 sit=4 ต่ำกว่าตลิ่ง (ม.)
  52.70 km  THA004    สามชุก                           14.7514,100.0959 HII  msl=8.02 sit=5 ล้นตลิ่ง (ม.)
  66.18 km  T.13      บ้านบางการ้อง                    14.1570,100.1279 RID  msl=3.35 sit=5 ล้นตลิ่ง (ม.)
   0.07 km  THA006    วัดท่าเจดีย์ (TTC06)             14.1566,100.1274 HII  msl=3.19 sit=5 ล้นตลิ่ง (ม.)
  12.69 km  T.15      วัดบางไผ่นารถ                    14.0522,100.1751 RID  msl=2.58 sit=5 ล้นตลิ่ง (ม.)
   4.02 km  THA007    บางเลน                           14.0164,100.1798 HII  msl=2.80 sit=5 ล้นตลิ่ง (ม.)
  23.97 km  T.1       ที่ว่าการอ.นครชัยศรี             13.8010,100.1880 RID  msl=2.32 sit=5 ล้นตลิ่ง (ม.)
   1.47 km  THA008    สะพานนครชัยศรี                   13.7922,100.1982 HII  msl=2.13 sit=5 ล้นตลิ่ง (ม.)
   7.80 km  T.14      ร.ร.บ้านสามพราน                  13.7241,100.2157 RID  msl=1.75 sit=5 ล้นตลิ่ง (ม.)
  15.44 km  THA009    เมืองสมุทรสาคร                   13.5860,100.2305 HII  msl=0.21 sit=4 ต่ำกว่าตลิ่ง (ม.)
```
```
## แม่น้ำน้อย  (6 stations, chain length 22 km)
    start  TCP005    ปตร.บางแก้ว (ทุ่งผักไห่)         14.4366,100.3715 HII  msl=3.47 sit=3 ต่ำกว่าตลิ่ง (ม.)
   4.18 km  TCP006    ปตร กุฎิ (ทุ่งป่าโมก)            14.4124,100.4012 HII  msl=5.77 sit=4 ต่ำกว่าตลิ่ง (ม.)
   4.28 km  CPY009    คลองบางหลวง                      14.4158,100.4407 HII  msl=6.12 sit=5 ล้นตลิ่ง (ม.)
   0.01 km  C.36      บ้านบางหลวงโดด                   14.4159,100.4408 RID  msl=6.16 sit=5 ล้นตลิ่ง (ม.)
  10.51 km  TCP012    เสนา (ทุ่งบางบาล-บ้านแพน)        14.3278,100.4055 HII  msl=1.91 sit=3 ต่ำกว่าตลิ่ง (ม.)
   2.93 km  CPY017    เสนา                             14.3198,100.3795 HII  msl=2.72 sit=4 ต่ำกว่าตลิ่ง (ม.)
```
```
## คลองบางบาล  (2 stations, chain length 7 km)
    start  CPY010    คลองบางบาล                       14.4230,100.4819 HII  msl=7.02 sit=5 ล้นตลิ่ง (ม.)
   6.66 km  C.37      บ้านบางบาล                       14.3632,100.4848 RID  msl=4.16 sit=5 ล้นตลิ่ง (ม.)
```
`คลองพระยาบรรลือ` has a single station in the payload: `CPY016` (14.1648, 100.3073, 2.99 m MSL, below bank) — it is the west-bank channel parallel to the main stem in the Ayutthaya → Pathum Thani reach. The Noi / Bang Ban / Phraya Banlue system takes Chao Phraya water off on the west bank around Ang Thong–Ayutthaya (nearest main-stem stations: `CPY008`, `C.7A`, `CPY011`) and the data next picks the main stem up at `CPY012` (Bang Pa-in) and `CPY014` (Pathum Thani).

## 4. Junction check — nearest gauge on each side
| junction | river A gauge | river B gauge | separating distance |
|---|---|---|---|
| Yom → Nan | `Y.5` หน้าอำเภอโพทะเล | `N.67` วัดเกยไชยเหนือ | 25.1 km |
| Ping+Wang → (Bhumibol Dam site) | `WAN001` สามเงา | `P.12C` บ้านย่านรี | 6.0 km |
| Ping+Nan → Chao Phraya (Pak Nam Pho) | `PIN005` เก้าเลี้ยว | `N.67` วัดเกยไชยเหนือ | 22.8 km |
| Pasak → Chao Phraya (Ayutthaya) | `S.5` สะพานปรีดี-ธำรง | `C.35` บ้านป้อม | 5.7 km |
| Tha Chin take-off from Chao Phraya | `THA001` สะพานคง-ศุข ศรีสวัสดิ์ | `CPY004` สะพานธรรมจักร(วัดธรรมามูล) | 2.9 km |

## 5. Co-located cross-family station pairs
74 pairs within 0.5 km across different code families (first 20 shown; regenerate the full list with the tool below).
| dist | station A | station B | families | river |
|---|---|---|---|---|
| 1 m | `SLA002` คลองหอยโข่ง | `X.90` บ้านบางศาลา | HII/RID | คลองอู่ตะเภา |
| 1 m | `STU003` มะนัง | `X.150` บ้านวังพระเคียน | HII/RID | คลองละงู |
| 3 m | `X.236` บ้านย่านตาขาว | `TNG004` ปะเหลียน | RID/HII | คลองปะเหลียน |
| 4 m | `MOU385` สะพานคลองท่าสะแก | `N.55` บ้านท่าสะแก | FOP/RID | น้ำภาค |
| 4 m | `MUN002` เฉลิมพระเกียรติ | `M.2A` บ้านด่านกะตา | HII/RID | แม่น้ำมูล |
| 5 m | `CHN001` เมืองจันทบุรี | `Z.57` สะพานวัดจันทนาราม | HII/RID | คลองจันทบุรี |
| 5 m | `N.75` สะพานท่าลี่ | `SKU07` อ.เวียงสา (N.75)  น้ำว้า | RID/EGAT | แม่น้ำน้ำว้า |
| 5 m | `W.3A` บ้านดอนชัย | `BBD09` แม่น้ำวังที่ อ.เถิน (W.3A) | RID/EGAT | แม่น้ำวัง |
| 6 m | `SKU03` อ.เมืองน่าน (N.1) | `N.1` หน้าสำนักงานป่าไม้ | EGAT/RID | แม่น้ำน่าน |
| 6 m | `I.17` บ้านเจดีย์งาม | `PYO005` สะพานข้ามน้ำอิง (I.17) | RID/HII | ร่องค้าน |
| 7 m | `CHI005` ชนบท | `E.9` บ้านท่านางเลื่อน | HII/RID | แม่น้ำชี |
| 7 m | `M.9` ชุมชนสะพานขาว | `MUN010` เมืองศรีสะเกษ | RID/HII | ห้วยสำราญ |
| 7 m | `CHM001` สันทราย | `P.67` บ้านแม่แต | HII/RID | แม่น้ำปิง |
| 7 m | `Kh.89` บ้านหัวสะพาน | `CHR003` แม่จัน | RID/HII | น้ำแม่จัน |
| 7 m | `PAS001` หล่มสัก | `S.3` ต.ตาลเดี่ยว | HII/RID | แม่น้ำป่าสัก |
| 7 m | `PRN001` ปราณบุรี | `Pr.1` บ้านเขาน้อย | HII/RID | แม่น้ำปราณบุรี |
| 8 m | `K.62` บ้านหนองไผ่ | `MKVKD09` วัดหินแท่น (K.62) | RID/EGAT | ลำภาชี |
| 8 m | `KRN004` ลิ่นถิ่น | `MKVKD03` บ้านลิ่นถิ่น (K.54) | HII/EGAT | แม่น้ำแควน้อย |
| 8 m | `S.26` ท้ายเขื่อนพระรามหก | `PAS008` ท่าเรือ | RID/HII | แม่น้ำป่าสัก |
| 8 m | `X.37A` บ้านย่านดินแดง | `RPBD11` สะพานอิปัน อ.พระแสง (X.37A | RID/EGAT | แม่น้ำตาปี |

## 6. Regenerate
```sh
# snapshot (no key needed)
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load" -o wl.json
python3 tools/station_chain.py wl.json            # all rivers, chains + co-located pairs
python3 tools/station_chain.py wl.json เจ้าพระยา     # one river only
```
Cross-family datum caution (2026-09-30): at Nakhon Sawan `CPY001` (HII, 13:00) read 23.52 m while `C.2` (RID, 12:00) read 23.77 m only 2.5 km downstream — a flowing river cannot rise downstream, so the two families do not reconcile on absolute MSL there (site, section or datum offset). Compare a reading only against its own family history, and prefer same-family pairs when chaining levels.

Caveats: greedy ordering can zigzag on rivers with big bends or parallel channels — always sanity-check a chain before quoting it. Headpond stations can read over-bank against a low bank datum without meaning floodplain flooding (2026-09-30: `CPY004` headpond showed 1.07 m over bank while the reach below the dam was 1.12 m below bank). River-kilometre positions and exact junction points can only be pinned with the river-network geometry layer or the RID lower-Chao-Phraya water-management plan (water.rid.go.th/flood/plan_new/planlow.html) — this file is built from telemetry coordinates only.

## 7. Cross-check vs the two official chart pages (2026-09-30)

Sources

- brief: `https://waterchart.thaiwater.net/basin/chaophraya` — Next.js app that renders `assets/svg/chaophraya/chaophraya.svg`
  (1028 x 1578 Illustrator schematic) and feeds it live values from `public/waterlevel_load?basin_code=6..26`,
  `public/watergate_load?basin_id=6..26`, `analyst/dam` and `analyst/cctv`. Note: the TLS handshake fails from this VM
  (`curl` needs `-k`), and nothing on the page exposes station-to-station links either — the topology is in the drawing.
- full: `https://tiwrm.hii.or.th/DATA/REPORT/php/chart/chaopraya/2013/chaopraya.php` — 2013 legacy chart page, 297 numbered
  nodes over a 3073 x 7196 background PNG (`20241004_chaopraya_chart_edit.png`), with per-node values inside the HTML.

Cross-check method: on the SVG every node owns a leader line `id="<CODE>-line"` running from its value box to the river;
its far endpoint is the node's position on the drawn network. Snapping those points to the drawn `River_line` polylines and
ordering by arc length reproduces the chart's own sequence. The legacy page's node order was read from its markup order.

Agreements

| segment | chart | telemetry-derived | verdict |
|---|---|---|---|
| main stem, Nakhon Sawan → Bangkok | `CPY001 -> C2 -> C13 -> CPY005 -> CPY008 -> CPY013 -> CPY014 -> CPY015` (strictly descending its x≈425 vertical line) | `CPY001 -> C.2 -> CPY002/003/004 -> C.13 -> CPY005 -> ... -> CPY008 -> ... -> CPY013/CPY014 -> C.12 -> CPY015` | same order; the chart simply omits the RID `C.*` and `CPY002/003/004/006/007` nodes |
| legacy chart markup order | `CPY001, C2, CPY002, ..., CPY004, C13, CPY005, CPY006, CPY007, C7A, CPY008, C35, CPY011, CPY012, C29A, CPY013, CPY014, C22, C12, C4, CPY015` | same sequence | independent confirmation, including the nodes the new SVG drops |
| Ping | separate line `CHM001 -> ... -> PIN005` | `CHM004 ... PIN005` | same |
| Wang → Ping | Wang line ends on the Ping line at the Bhumibol Dam reach | `W.4A` <-> `P.12C` 6 km, Bhumibol site | same junction |
| Yom → Nan | Yom line ends at `YOM009`, on the Nan line just above `NAN008` | last Yom gauge `Y.5`, 25 km above `N.67`/`NAN008` (Chum Saeng) | same junction |
| Tha Chin | line branches off the main stem at y≈737 (i.e. above `C13` = Chai Nat) and runs south to `THA009` (Samut Sakhon) | `THA001` (Chai Nat) is 2.9 km from `CPY004` | same |
| Noi / Bang Ban west line | separate line branching just above `C13`, rejoining the main stem in the Pathum Thani reach (`CPY013`/`CPY014`) | Noi gauges `CPY009`/`C.36`, `CPY010`/`C.37`, `CPY017` all in the Ayutthaya reach; `CPY016` on Khlong Phraya Banlue | same system |
| Pasak | own line `S26 -> ATG05/06/07/08 -> FROC/BPK` (Bang Pakong) | `S.5` 5.7 km from `C.35` at Ayutthaya | same junction area |
| Sakae Krang | own line (`m-dam-18 -> SKG002`) meeting the main stem just below `C2` | `Ct.2A` (บ้านหาดทนง) is 8.5 km below `CPY002` | same, and adds a feeder the telemetry-only chain missed |

Corrections / additions taken from the cross-check

1. แม่น้ำน้อย (Noi) takes off at Muang Chai Nat (Pak Phraek) — in the dam reach just above `C13` — not in the
   Ang Thong–Ayutthaya reach as section 3 implies; the chart draws it the same way. Its gauges only start further
   downstream in Ayutthaya province.
2. Add แม่น้ำสะแกกรัง as a feeder: it joins the Chao Phraya between `CPY002` and `CPY003` (`Ct.2A` is its only gauge,
   8.5 km below `CPY002`; the chart also shows its dam `m-dam-18`).
3. Node coverage: of the legacy chart's 297 nodes, 131 exist in `waterlevel_load`. The remainder are 75 dam/regulator
   nodes (`DAM-*`, `REG-*`), 32 canal/Bangkok gauges (`ATG*`, `BKK*`, `WR*`, `ER*`, `GLF*`, `FROC*`) and 27 water-level
   stations absent from this payload (`C.4`, `C.22`, `C.29A`, `C.39`, `C.54`, `CPY013`, `YOM001/002/011`, `WAN005`,
   `KWN002`, `PAS004/010`, `THA002/011`, `S28A`, `S39`, ...). For a complete network, also pull
   `/public/watergate_load?basin_id=6,7,8,9,10,11,12,13,14,15,26` — that is exactly the pair the brief chart fetches.
4. The SVG carries water travel times between nodes (labels such as `2 วัน`, `1 วัน`, `6 ชม.`, `20 ชม.`) — usable as a
   check on flow path length, not yet captured in this file.

Caveats on this cross-check: the chart is a schematic (hand-placed nodes, not to scale), and snapping a node by its
leader line can mis-assign a station whose leader crosses another line — snap distances are printed by the tool. The
legacy markup order is drawing order, not proof of adjacency: `C.3` sits in its west-bank block yet its own coordinates
(14.8987, 100.4019) and level continuity (11.7 m MSL, bracketed by `CPY006` 13.3 and `CPY007` 10.1) put it on the main stem.

## 8. Water travel times and node coverage of the two chart pages (2026-09-30)

Travel times in the brief chart

The brief chart encodes travel time as plain SVG text labels (`2 วัน`, `6 ชม.`, ...) placed along the drawn river.
11 such labels exist. Extract them with the transform coordinates and pair each with the two nearest
station name boxes on the drawing (`tools/travel_time.py`):

| label | nearest station box | 2nd nearest | dist px |
|---|---|---|---|
| 2 วัน | DIV003 (`DIV003`) | NAN011 เมืองอุตรดิตถ์ (`NAN011`) | 23 / 39 |
| 3 วัน | DIV002 (`DIV002`) | ปตร.ยางซ้าย (`temp002`) | 18 / 74 |
| 2 วัน | DIV005 (`DIV005`) | PIN002 เมืองตาก (`PIN002`) | 52 / 110 |
| 2 วัน | NAN007 ตะพานหิน (`NAN007`) | NAN006 บางกระทุ่ม (`NAN006`) | 25 / 45 |
| 1 วัน | YOM009 โพธิ์ประทับช้าง (`YOM009`) | CPY001 สะพานเดชาติวงศ์ (`CPY001`) | 53 / 67 |
| 6 ชม. | CPY001 สะพานเดชาติวงศ์ (`CPY001`) | YOM009 โพธิ์ประทับช้าง (`YOM009`) | 20 / 100 |
| 20 ชม. | ATG12 ปตร.ท่าโบสถ์ (`ATG12`) | ปตร.มโนรมย์ (`ATG02`) | 92 / 93 |
| 2.5 วัน | CPY008 เมืองอ่างทอง (`CPY008`) | CPY009 คลองบางหลวง (`CPY009`) | 58 / 73 |
| 1 วัน | BKK013 หนองเสือ (`BKK013`) | เขื่อนพระราม 6 (`S26`) | 46 / 66 |
| 1 วัน | ATG07 ปตร.พระศรีศิลป์ (`ATG07`) | ปตร.เชียงรากน้อย (`ER013`) | 31 / 48 |
| 1 วัน | ปตร.เชียงรากน้อย (`ER013`) | FROC01 สะพานแดง (`FROC01`) | 78 / 88 |

Semantics warning: the labels are position-anchored only, so this pairing is geometric — a label can belong to the
reach *beside* it rather than the two boxes closest to it (e.g. two labels sit in the same Nakhon Sawan cluster),
and it is not yet confirmed whether they are per-segment or cumulative-from-a-reference times. Do not publish a
station-pair travel time without checking the chart's own legend or measuring the lag.

Independent lag check (attempted, weak): hourly level series from `public/waterlevel_graph` for adjacent main-stem
pairs (45 days), correlating hourly level increments gives peaks at 0-1 h for free-flowing reaches (CPY005->CPY006,
CPY006->C.3) and 12-14 h for CPY002->C.13, i.e. the signal is dominated by the basin-wide rainfall response rather
than by translation. Event peak matching (or discharge routing) is the right method instead.

Node coverage — which chart has what

| series | brief chart SVG | full chart page | in `waterlevel_load` |
|---|---|---|---|
| `DAM-*` (dams) | 0 | 11 | 0 |
| `m-dam-*` (dam markers) | 8 | 0 | 0 |
| `REG-*` (regulators) | 0 | 64 | 0 |
| `C.*` (RID Chao Phraya wl) | 2 (`C2`, `C13`) | 13 | 9 |
| `CPY*` | 10 | 17 | 17 |
| `THA*` (Tha Chin) | 4 | 11 | 9 |
| `ATG*` / `BKK*` canals | 17 / 13 | 18 / 21 | 0 / 0 |
| `WR*` / `ER*` canals | 9 / 6 | 0 / 0 | 9 / 0 |
| `DIV*` / `temp*` | 5 / 5 | 0 / 0 | 0 / 0 |
| `PAS*` (Pasak) | 0 | 7 | 15 |
| total nodes | 127 | 297 | (~806 nationally) |

- All 27 water-level stations missing from `waterlevel_load` (C.4, C.22, C.29A, C.39, C.54, P.5, W.10A, Y.6, Y.14,
  N.22, N.27, N.8A, S.28A, S.39, CHM006, WAN005, YOM001/002/011, KWN002, CPY013, THA002/011, PAS004/010, BPK002,
  NYK014) are drawn on the **full** chart; the brief chart has only 3 of them (WAN005, KWN002, CPY013).
- The brief chart draws no `REG-*` and only 8 dam markers, but its *data* layer is wider than its drawing: it pulls
  `public/watergate_load?basin_id=6..26` and `analyst/dam`, so gates/dams appear on it interactively without a
  hardcoded node each.
- Practical consequence: for a complete topology, combine `waterlevel_load` + `watergate_load` (basins 6-26) and use
  the full chart page's node list as the code inventory. The brief chart is a simplified view.

## 9. Measured travel times (rise-rate timing, 2026-09-30)

Method (`tools/event_lag.py`): each station's series is resampled to hourly; an "event" is a local
maximum of the 12-hour rise rate of at least 0.15 m with 72 h between events; the matching time
downstream is the strongest 12-hour rise within 36 h after it, requiring at least 0.05 m. The lag is
the difference. Correlation of the two series was tried first and rejected — both gauges see the same
basin-wide rain, so increments line up at zero lag and swamp the translation signal.

| reach | events | median lag (h) | range (h) | regulated? |
|---|---|---|---|---|
| C.2 -> CPY002 | 4 | 20 | 7-24 | - |
| CPY002 -> CPY004 | 3 | 17 | 2-25 | Chao Phraya Dam headpond (backwater) |
| CPY004 -> C.13 | 2 | 36 | 1-36 | Chao Phraya Dam tailrace (gate-controlled) |
| C.13 -> CPY005 | 4 | 16 | 1-29 | just below the dam, release-controlled |

Data coverage: 5 of 22 stations in the pair list returned at least one usable series in this run
(45 days requested). Stations that returned nothing: CPY006, C.3, CPY007, C.7A, CPY008, CPY012, CPY014, PIN002, PIN003, PIN004, PIN005, NAN007, NAN006, NAN014, NAN011, YOM009, CPY001.
The public graph endpoint was badly degraded while this ran (`500 ... pq: out of shared memory` on
most calls); re-run `python3 tools/event_lag.py` to fill the gaps from the cache, which resumes
where it left off.

How to read this

- The only reach with both ends free-flowing and enough events is C.2 -> CPY002 (27 km): median
  20.0 h, i.e. roughly 0.3-0.5 m/s. That is the same order as the chart's day-scale labels
  ("1 วัน" over comparable distances), so the chart is not contradicted, but ±10 h of spread means
  this cannot yet replace the chart's own figures.
- Reaches into or out of the Chao Phraya Dam (CPY004 headpond, C.13 tailrace, CPY005 below the dam)
  are marked regulated and must not be quoted as travel times: their levels jump when gates move
  (visible here as 1-hour lags).
- To tighten this: route on discharge (C.2 and C.13 both publish it), pick isolated events rather
  than every rise, and extend the window beyond the ~2 months available here.
