# M1 合成感測資料剖析

工作單 `M1_DATASET_PROFILE_6CSV_V1`。STUDENT-RESEARCH Brain 確認以 `data/synthetic_sensor.csv` 的全部 6 筆資料列建立 1 個資料集。來源定位採專案相對路徑，CSV 邏輯紀錄從標頭後第 1 筆編到第 6 筆。重複紀錄也有自己的列序。

## 輸入與輸出

工作區盤點排除 Git 內部目錄及 M2 的 `data/FD001/`，找到 1 個 CSV。來源為 234 bytes。授權持有者可用清單中的 SHA-256 確認本地檔案。公開交付物僅含分析程式、彙總與執行證據。

| 檔案 | 用途 |
| --- | --- |
| dataset_inventory.json | 授權範圍、來源識別及雜湊 |
| dataset_profiles.json | 欄位型別、統計、資料品質與結構 |
| DATA_QUALITY.md | 缺失、重複、結構及數值摘要 |
| profile_sensor.py | 唯讀解析來源、計算統計及驗證一致性 |
| execution.log | 本次執行的命令、版本、主控台輸出及程序結束碼 |

## 重現

使用 Python 3.12.14 和 Pandas 3.0.1，由專案根目錄執行下列 PowerShell 命令。先將已授權且雜湊相符的來源置於清單指定位置。預設輸出位置是分析程式所在目錄。以下指定暫存目錄，以便與已提交的兩份 JSON 比對。

```powershell
$report = 'outputs/M1_DATASET_PROFILE_6CSV_V1/verified'
$repeat = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
python "$report/profile_sensor.py" --output-dir "$repeat"
if ($LASTEXITCODE -ne 0) { throw "Profiling failed with exit code $LASTEXITCODE" }
foreach ($name in @('dataset_inventory.json', 'dataset_profiles.json')) {
    $expected = Get-Content -Raw -LiteralPath "$report/$name" | ConvertFrom-Json
    $actual = Get-Content -Raw -LiteralPath "$repeat/$name" | ConvertFrom-Json
    if ((ConvertTo-Json $expected -Depth 20 -Compress) -cne (ConvertTo-Json $actual -Depth 20 -Compress)) {
        throw "Output differs in $name"
    }
}
```

## 解析與統計規則

- 使用 UTF-8（接受 BOM）、逗號分隔、雙引號包覆、連續雙引號跳脫、小數點為句點。第一列是標頭。保留分隔符號後的空白與空白列，遇欄位數不符或格式錯誤即中止。僅空欄視為缺失，停用 Pandas 預設缺失字串。
- 時間依 `%Y-%m-%dT%H:%M:%S` 解析，保留來源的無時區表示。JSON 同列 CSV 初讀與時間轉型後的 dtype。此資料集各欄的分析角色為時間或數值，類別統計標為 `NOT_APPLICABLE`。
- 保留全部紀錄。數值統計逐欄排除缺失，以有效觀測數計算平均、中位數、極值和樣本標準差（分母為有效觀測數減 1）。完整重複以所有欄位相同且每組保留首列計數。常數欄有 1 個非缺失相異值，全空欄為 0 個。
- 無效值檢查涵蓋非空時間解析失敗、非空數值解析失敗及非有限數值。工作單未提供設備規格或物理上下限。數值範圍為實際觀測範圍。
- 以 3 個數值遙測欄（含負載）作為 Sensor Count 的計數單位。各欄缺失率分母為 6，合計缺失率分母為 18。Engine Unit、Cycle、Health Label 及 RUL 相關指標標為 `NOT_APPLICABLE`。
- 獨立使用 Python 標準函式庫重新解析 CSV，核對欄名、列寬、列數、缺失、重複、時間與所有數值統計。浮點比對使用相對及絕對容差 1e-12。程式核對來源雜湊，並在計算後重新讀取檔案確認位元組相同。
