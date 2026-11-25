# 資料、API 與逐筆驗證

## DIRECTLY_EXECUTED

執行前後重新計算 Train、Test、RUL 三份本地 TXT 的 SHA-256，均與 [M2 Data Contract 1.0.0](../../M2_FD001_DATA_CONTRACT_V1/gate_c/PUBLIC_SAFE/fd001_data_contract.json) 的公開固定值一致。

| 來源 | SHA-256 |
| --- | --- |
| train_FD001.txt | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` |
| test_FD001.txt | `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851` |
| RUL_FD001.txt | `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca` |

四個唯讀端點 `GET /api/health`、`GET /api/catalog`、`GET /api/units`、`GET /api/history` 均以 loopback HTTP 驗證。回歸套件核對 FD001、Contract 1.0.0、Train／Test 隔離、Sensor Catalog 1–21、來源定位及成功與錯誤 JSON Schema。測試涵蓋參數錯誤、未知 Unit／Sensor、來源缺失與不符、RUL 映射錯誤、非有限數值、唯讀限制及 HTTP 503。來源未驗證時拒絕回傳觀測值。單點資料的標準差及斜率在網站顯示 N/A。

| 必查案例 | 資料、API、UI 與 Prompt |
| --- | --- |
| Train Unit 1、Sensor 7、Cycle 1–20 | 20/20 筆逐筆一致 |
| Test Unit 2、Sensor 7、Cycle 3–5 | 3/3 筆逐筆一致 |

API 回歸測試直接解析 TXT，以十進位數值核對 Cycle、Sensor Value、Source Record Index、Source Physical Line 和 Column Position。Edge 輸出再與這次的原始列對照結果核對。圖表的 Cycle／Value 與原始列精確一致，來源表及 Prompt 同時核對五項欄位。兩組案例皆確認檔名、來源 SHA-256、Contract 版本、Sensor Catalog 欄位語意及 Prompt 選取一致性。另以原始讀值獨立重算計數、最小值、最大值、平均、樣本標準差、OLS 斜率和缺失計數。兩組案例的 UI 及 Prompt 七項統計與重算值的絕對差均小於 `1e-7`。

## REVIEWED_PRIOR_EVIDENCE

既有 M2–M5 交付與各階段驗收證據作為版本及重現基準。M5 前次 Web Worker 結果見 [已受驗公開證據](../../M5_FD001_EVIDENCE_PROMPT_HARDENING_V1/PUBLIC_SAFE/)。
