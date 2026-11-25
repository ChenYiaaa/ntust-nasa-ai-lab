# M5 端到端驗證證據

`WO-M5-002` 依已受驗的 GitHub `main` 基準 `ec5bb7b06235b28d4a3387681127575f55abdd57` 執行。學生日常資料、服務及網站以本地 FD001 來源重現。最終驗收權屬於 STUDENT-MAIN Brain。

| 證據 | 內容 |
| --- | --- |
| [execution.md](execution.md) | 執行環境、啟動、HTTP、回歸測試及關閉 |
| [verification.md](verification.md) | 來源 SHA-256、API 契約與逐筆一致性 |
| [browser-uat.md](browser-uat.md) | Windows Edge 操作與實際剪貼簿讀回結果 |
| [delivery.md](delivery.md) | 固定交付版本、操作與完整重現步驟 |

`DIRECTLY_EXECUTED` 指本次重新執行。 `REVIEWED_PRIOR_EVIDENCE` 指沿用已接受的治理或交付紀錄。 `NOT_VERIFIED` 指本次未覆蓋的環境或配置。公開檔案只刊載方法及安全摘要，逐筆值、Prompt 內容、私人來源與本機絕對路徑留在 Git 忽略目錄。
