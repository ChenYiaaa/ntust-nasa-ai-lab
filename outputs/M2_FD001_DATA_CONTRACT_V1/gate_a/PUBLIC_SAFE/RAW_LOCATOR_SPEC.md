# FD001 原始值定位規格

遙測用 split、Unit ID、Cycle、欄名查詢。Train 與 Test 的鍵分開。RUL 用自己的正整數紀錄序號查詢。程式先核對檔案 SHA-256，再按實體行掃描、以連續空白分割並單獨計算非空白紀錄序號。

| 輸出 | 定義 |
| --- | --- |
| dataset_id、split | FD001 與 train、test 或 rul |
| source_filename、source_sha256 | 來源檔名及完整 SHA-256 |
| source_record_index、source_physical_line | 自 1 起算的非空白紀錄序號與含空白行的實體行號 |
| unit_id、cycle | 遙測的第 1、2 欄，RUL 原始定位時為 null |
| column_name、column_position | 欄名與自 1 起算的位置，設定欄 3–5、Sensor 6–26 |
| original_value、parsed_value | 原始字串與數值解析結果 |

`validate.py --locate train --unit 1 --cycle 1 --column sensor_1` 示範從本地檔案取單一原始值。`--locate rul --record 1` 示範單欄 RUL 查詢。Train、Test、RUL 分別驗證首筆、中段及末筆，共 9 個定位樣本。標準庫重新切分原始位元組，與解析值、實體行、紀錄序號、欄位位置逐項比對。公開檢查保留結果，完整回傳值保存在本地。
