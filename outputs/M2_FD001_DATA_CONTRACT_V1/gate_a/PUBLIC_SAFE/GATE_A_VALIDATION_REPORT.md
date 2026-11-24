# FD001 Gate A 驗證報告

本地基準與派工時的 GitHub main 為 `e0fa58a0bb9e06630e4ca9326153de216033f856`。遠端治理紀錄為 M1 PASS、M2 AUTHORIZED_NOT_STARTED。以下為 Worker 自檢結果，等待 STUDENT-RESEARCH Brain 驗收。

| 來源 | 實體行 | 有效紀錄 | 邏輯欄 | Unit | 觀測 Cycle |
| --- | ---: | ---: | ---: | --- | --- |
| Train | 20,631 | 20,631 | 26 | 100，ID 1–100 | 1–362 |
| Test | 13,096 | 13,096 | 26 | 100，ID 1–100 | 1–303 |
| RUL | 100 | 100 | 1 | 100 個 Test Unit 的末次觀測標籤 | 不適用 |

三檔均以嚴格 ASCII 解碼，每行有行尾空白，空白行數為 0。兩套解析器都確認 Train、Test 欄序為 Unit、Cycle、3 個操作設定、21 個 Sensor。兩個分割的 Unit/Cycle 鍵均唯一，每個 Unit 的 Cycle 自 1 連續遞增，末次 Cycle 記為最後觀測。Train、Test 完整重複列皆為 0。三檔的缺失、非數字、NaN、無窮值皆為 0。[NASA 資料說明](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data)

兩個分割各有 7 個常數欄，即 setting_3 與 sensor_1、5、10、16、18、19。近常數定義為至少兩個相異值且最高頻值占比至少 99%，兩個分割均無符合此定義者。RUL 由 100 筆非負整數構成，重複標籤數值允許出現在不同 Unit。

## RUL 配對

MathWorks 的 FD001 範例將 Test Unit 的相異 ID 升序排列，將 RUL 第 i 筆配給第 i 個排序後的 Unit。程式核對本地 Test ID 為 1–100，逐筆驗證 100 個映射的 RUL 值及來源行。單欄 RUL 檔本身無 Unit 鍵，配對結論依賴此格式慣例及受信任的本地輸入。[MathWorks 資料載入函式](https://it.mathworks.com/help/predmaint/ug/remaining-useful-life-estimation-using-convolutional-neural-network.html)

## 一致性及發布審查

Python 標準庫和 NumPy 獨立核對來源穩定性、實體行、筆數、欄寬、所有數值、Unit/Cycle 鍵、缺失與無效值、RUL 行及原始定位。60 項本地檢查通過，9 個 JSON 在獨立輸出目錄重跑後逐位元組一致。公開清單的 SHA-256 供授權持有人核對本地檔案。

Unit/Cycle 索引只給各 split 的範圍及計數，省略逐 Unit 長度、個別末次 Cycle 及實體行。公開 schema 只保留名稱、順序與型別。RUL 規格只給配對算法與筆數，省略逐 Unit 值與原始序列。公開檢查表將長序列轉為元素數與一致性狀態，抽樣保留結果。以上資訊合併後仍缺每筆遙測值、逐 Unit 界線及 RUL 的有序值。驗證程式須讀取另外取得授權的原始輸入才能生成完整本地證據。
