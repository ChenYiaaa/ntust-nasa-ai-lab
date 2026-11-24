# FD001 Gate C Worker 驗收證據

工作單 `M2_FD001_DATA_CONTRACT_V1`。派工記錄的 Gate A 與 Gate B Research 驗收均為 PASS。其 Commit 分別為 `c47df8eebf95e1b6d487e81c657863e65a170564` 和 `ac4f97b220a6ec895c6cc0f18782190fefb45a82`。以下原始檔執行由 Worker 在本地完成。Gate C 交由 STUDENT-RESEARCH Brain 獨立驗收。

| 項目 | 獨立核對 |
| --- | --- |
| JSON、欄位與 Sensor | 三份規格的版本與必要欄位、1-based 欄位表、與 Gate A Train/Test Schema 及 SHA-256 一致 |
| Engine Unit | 由二進位實體行獨立分詞與分組，核對 Train/Test 共 200 個 Unit 的 Cycle 範圍、筆數與邊界定位 |
| Train Sensor | Unit 1、Sensor 2、Cycle 1–192，共 192 筆，逐筆比對原始讀值與來源行 |
| Test Sensor | Unit 1、Sensor 2、Cycle 1–31，共 31 筆，逐筆比對原始讀值與來源行 |
| 來源證據 | 原始分詞獨立核對 223 筆 Sensor 輸出。另以 Gate A Raw Locator CLI 回查兩組感測器範例的首筆與一筆 RUL，核對字串、數值、行欄位置或雜湊 |
| Trend | 兩個分割的範例均與 Gate B 摘要一致。浮點使用相對 1e-10、絕對 1e-12。單週期回報 NOT_APPLICABLE，常數 Sensor 斜率為 0 |
| Test RUL | 將獨立分組的 Test Unit ID 升序，與二進位解析的 RUL 順序核對全部 100 筆配對。單欄 TXT 無原生 Unit ID，依 MW_FD001_SORTED_ID 格式規則 |
| 錯誤 | 六個契約錯誤均通過。以記憶體替換預期雜湊觸發 SHA 不符，以記憶體移除一個已讀取 RUL 紀錄觸發配對不成立 |
| 重現 | 35 項檢查通過，原始三檔前後雜湊相同。獨立目錄重跑的三份 JSON 逐位元組一致 |

[執行日誌](execution.log) · [重跑日誌](reproduction.log) · [逐項檢查](fd001_contract_validation.json)

公開範例保留少量 Unit/Cycle 及 Sensor 查詢條件、已公開的趨勢摘要、來源雜湊與定位規則。完整查詢輸出、逐列索引、原始數值及全部 Test RUL 配對保存在本地 `local_only/run/local_only/complete_query_evidence.json`。查詢程式須持有雜湊相符的本地 TXT 才會回傳資料。來源維持唯讀。公開提交中的資訊不足以還原原始 Sensor 序列或 RUL 向量。
