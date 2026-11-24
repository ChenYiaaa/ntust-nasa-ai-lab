# FD001 Gate B 趨勢與品質分析

工作單 `M2_FD001_DATA_CONTRACT_V1`。本分析以 Gate A 驗收 Commit `c47df8eebf95e1b6d487e81c657863e65a170564` 為基準。Worker 證據待 STUDENT-RESEARCH Brain 獨立驗收。

## 重現

在專案根目錄使用 Python 3.12.14 與 NumPy 2.3.5。將授權的三份 TXT 放在 `data/FD001/`，程式會核對 Gate A SHA-256。所有重跑結果預設寫在 Git 忽略的 `gate_b/local_only/reproduced/`。可用 `--output` 指定另一個本地私有目錄。

```powershell
python outputs/M2_FD001_DATA_CONTRACT_V1/gate_b/PUBLIC_SAFE/analyze.py
```

- [資料品質](data_quality_report.json) 按分割和欄位列出樣本數、缺失與非有限值、重複、週期覆蓋及數值分布。
- [Sensor 趨勢](sensor_trend_summary.json) 含 Train 及 Test 的 21 個分割層級斜率摘要。[範例](trend_examples.json) 含兩個分割各一個常數、一個變動 Sensor。
- [來源追溯](SOURCE_TRACEABILITY_REPORT.md) 記錄定位方法，以及公開與本地證據的內容。
- [獨立檢查](independent_checks.json)、[執行日誌](execution.log) 與[重跑日誌](reproduction.log) 記錄檢查類別、實際結束碼及重現結果。

## 計算規則

Gate A 以 ASCII 空白解析 26 欄。Unit、Cycle、3 個操作設定與 21 個 Sensor 保持原欄序及原始量綱。物理單位未知，記為 `UNKNOWN`。缺失率分母是欄位觀測位置數，整檔缺失率使用資料列數乘欄數。嚴格解析中，欄寬錯誤、不合法數字或非有限值會中止。交付結果涵蓋 SHA 固定且沒有這類異常的版本。

數值統計只使用有限值，樣本標準差使用 `ddof=1`。操作設定分布以值域、平均、樣本標準差、相異數、最高頻值出現數與占比摘要。常數欄只有一個相異值。近常數欄至少有兩個相異值，且最高頻值占比至少 99%。分析保留全部 Sensor 及資料列。

每個 split、Unit 和 Sensor 各以 Cycle 為 X、Sensor 讀值為 Y 做含截距的 OLS。斜率為 `sum((x - mean(x)) * (y - mean(y))) / sum((x - mean(x))^2)`。僅使用 X、Y 皆有限的配對。有效數量少於 2 或分母為 0 時，回報 `NOT_APPLICABLE` 及原因。常數 Sensor 在有足夠且不同 Cycle 的情況下為 0。單位為 Sensor Unit / Cycle，本資料標為 `UNKNOWN / Cycle`。斜率描述量測方向與變化率。

## 結果與獨立核對

| 分割 | 列數 | Unit | 觀測 Cycle | Unit × Sensor 斜率 |
| --- | ---: | ---: | --- | ---: |
| Train | 20,631 | 100 | 1–362 | 2,100 |
| Test | 13,096 | 100 | 1–303 | 2,100 |

兩分割的缺失、重複資料列、無效數字、NaN、無窮值和重複 Unit/Cycle 鍵均為 0。每個 Unit 均從 Cycle 1 連續遞增。兩者各有 7 個常數欄、0 個近常數欄。

Python 的集合、Counter、statistics 與線性迴歸函式獨立核對 NumPy。浮點容差為相對 1e-10、絕對 1e-12。5,022 項檢查全數通過，包含 4,200 次斜率、200 次連續性及 16 次來源核對。另以獨立輸出目錄重跑，比對 7 份 JSON 的相對路徑與內容位元組。
