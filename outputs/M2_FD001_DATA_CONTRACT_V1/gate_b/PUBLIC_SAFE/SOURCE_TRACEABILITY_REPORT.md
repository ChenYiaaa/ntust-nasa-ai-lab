# FD001 Gate B 來源追溯

四個公開範例各以 split、Unit ID、Cycle、Sensor ID 指定來源。Train 與 Test 各挑選最小 Unit ID 的 sensor_1（常數）和 sensor_2（變動）作人工驗證。每個範例記錄來源 SHA-256、Cycle 範圍、有效觀測與缺失數、描述統計和斜率。

原始資料採 Gate A 欄位順序，Sensor 的 1-based 位置為 Sensor ID + 5。數值源自對應列的原始字串。程式以獨立二進位分行與空白切詞得到實體行號及 1-based 紀錄序號，再比對 Gate A 解析矩陣與來源行。四個範例共 446 筆定位紀錄全部核對。每個範例另以 Gate A Raw Locator 回查首筆、中段及尾筆，共 12 次，比對原始字串、行欄位置、來源檔與 Unit/Cycle。

```powershell
python outputs/M2_FD001_DATA_CONTRACT_V1/gate_a/PUBLIC_SAFE/validate.py --locate train --unit 1 --cycle 1 --column sensor_2
```

公開版只保留上述查詢鍵、記錄數及範例統計。完整範例的起訖原始讀值與每筆來源定位保存在 `local_only/run/local_only/trend_examples_full.json`。本地亦保留各 Unit 斜率及逐項獨立檢查。原始 TXT、RUL 向量、逐列 Sensor 序列、實體行號表和原始定位樣本值留在本地。

公開品質與趨勢檔只提供分割層級摘要，範例只涉及四組指定的 Unit/Sensor。公開統計會揭示常數欄值，但其餘欄位的有序量測和逐 Unit 記錄位置沒有足夠資訊可從公開產物還原。
