# FD001 Gate A 遠端審查

工作單 `M2_FD001_DATA_CONTRACT_V1`。此 checkpoint 交由 STUDENT-RESEARCH Brain 獨立驗收。

## 審查與重現

從專案根目錄用 Python 3.12.14 與 NumPy 2.3.5 執行。需持有已授權的三份本地 TXT，並置於 `data/FD001/`。程式會核對清單中的 SHA-256。預設重跑結果寫入 Git 忽略的 `gate_a/local_only/reproduced/`。可用 `--output` 指定其他本地私有位置。

```powershell
python outputs/M2_FD001_DATA_CONTRACT_V1/gate_a/PUBLIC_SAFE/validate.py
```

- [驗證報告](GATE_A_VALIDATION_REPORT.md) 包含數量、品質、RUL 映射依據和發布審查。
- [來源清單](file_inventory.json)、[欄型與順序](raw_schema.json)、[Unit/Cycle 彙總索引](unit_cycle_index.json)、[RUL 映射規格](rul_mapping_spec.json) 提供審查所需的描述與來源雜湊。
- [定位規格](RAW_LOCATOR_SPEC.md)、[60 項檢查](checks.json)、[執行紀錄](execution.log)、[重跑紀錄](reproduction.log) 提供驗證方法與結果。

PUBLIC_SAFE 含規格、資料集層級彙總、通過紀錄與程式。LOCAL_ONLY 含完整逐 Unit 索引與 RUL 映射、原始定位樣本、精確實體行號及私人實際路徑。原始 TXT 仍由本地資料持有人管理。程式執行會輸出完整本地證據，請保存在私有目錄。
