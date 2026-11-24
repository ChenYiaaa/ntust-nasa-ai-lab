# FD001 Data Contract 1.0.0

此本地 Python 契約供後續授權的資料消費端使用。它提供 Train/Test Unit 與 Cycle 範圍、Sensor 清單、逐 Cycle 來源讀值、趨勢證據及 Test RUL。來源為固定 SHA-256 的三份本地 FD001 TXT。

## 使用方式

在專案根目錄執行。預設資料路徑為 `data/FD001/`，也可在子命令前傳入 `--source-dir`。查詢程式只需要 Python 標準函式庫。每次建立 `FD001` 時，三檔都要通過雜湊及結構驗證。一個實例代表已驗證的記憶體快照；需要再次確認磁碟檔案時，重新建立實例。

```powershell
$q = 'outputs/M2_FD001_DATA_CONTRACT_V1/gate_c/PUBLIC_SAFE/reference_query.py'
python $q units train
python $q sensors
python $q unit test 1
python $q sensor train 1 2 1 3
python $q trend test 1 2 1 31
python $q rul test 1
```

Python 使用端可呼叫同名的 `FD001` 方法並捕捉 `ContractError.payload`。CLI 成功時輸出 JSON 並回傳 0。契約查詢錯誤輸出 JSON 錯誤物件並回傳 2。CLI 語法或型別轉換錯誤由 argparse 回報。Cycle 查詢包含起訖，按實際 Cycle 升序回傳。超界、反向或含未觀測 Cycle 的區間回傳 `CYCLE_OUT_OF_RANGE`。

Train 與 Test 的末次觀測均以 `last_observed_cycle` 表示。Test RUL 是最後觀測點的剩餘壽命，由遞增 Test Unit ID 配對單欄 RUL 的邏輯紀錄。這個契約的 RUL 操作支援 Test 最後觀測點。趨勢沿用 Gate B 的含截距 OLS，X 為 Cycle，Y 為 Sensor 讀值，標準差 `ddof=1`。固定版本拒絕非有限值；單一觀測沒有可估計的斜率或樣本標準差。感測器的物理單位標記為 `UNKNOWN`。

## 驗證

驗證環境為 Python 3.12.14、NumPy 2.3.5。NumPy 用於回查 Gate A CLI。從專案根目錄執行下列命令。預設輸出在 Git 忽略的 `gate_c/local_only/reproduced/`。可用 `--output` 指向獨立本地私有目錄。兩次執行應產生三個同路徑、內容逐位元組一致的 JSON。

```powershell
python outputs/M2_FD001_DATA_CONTRACT_V1/gate_c/PUBLIC_SAFE/validate_contract.py
```

- [機器可讀契約](fd001_data_contract.json) 定義操作、證據、來源版本和驗收狀態。
- [欄位規格](fd001_column_schema.json) 與[錯誤規格](fd001_error_contract.json) 定義來源欄位與穩定錯誤。
- [已驗證範例](fd001_verified_examples.json)、[驗證結果](fd001_contract_validation.json) 與[驗收證據](ACCEPTANCE_EVIDENCE.md) 提供遠端審查資料。
