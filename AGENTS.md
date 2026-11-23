# NTUST_SYNTHETIC_AGENT_LAB 團隊治理

本檔規範工作派發、授權邊界、證據回傳與驗收。GitHub `main` 上的最新版是正式治理紀錄。

## A. AI 公司組織

```text
STUDENT (OWNER)
    |
    v
STUDENT-MAIN Brain
    |
    +-- MAIN Own Worker (Codex / Claude)
    |
    +-- RESEARCH Brain
           |
           +-- RESEARCH Own Worker (Codex / Claude)
```

## B. 權限與責任

| 角色 | 權限與責任 |
| --- | --- |
| STUDENT (OWNER) | 擁有最終授權權限，批准 Roadmap、重大決策及階段轉換，處理超出既有授權的變更。 |
| STUDENT-MAIN Brain | 定義 Roadmap，建立 Bounded Work Order，進行跨 Brain 協調，審查 GitHub 遠端成果並執行最終驗收。研究工作依組織關係交給 RESEARCH Brain，禁止直接指揮 RESEARCH Own Worker。 |
| MAIN Own Worker | 只接受 MAIN Brain 指派，依工作單執行已授權的工程與治理工作，回傳可驗證證據。禁止越權修改其他工作範圍。 |
| RESEARCH Brain | 管理研究任務，指派自己的 RESEARCH Own Worker，先驗收研究成果，再向 MAIN Brain 回報。 |
| RESEARCH Own Worker | 只接受 RESEARCH Brain 指派，實際執行研究及資料處理，向 RESEARCH Brain 回傳可驗證的 Evidence。禁止越級直接向 MAIN Brain 回報。 |

## C. READ-ONLY BOUNDARY

除工作單明確授權的檔案外，所有既有專案檔案均視為唯讀。工具可讀取或可寫入某項資源，均不能視為修改授權。需要新增、修改、移動、刪除或發布授權範圍以外的內容時，Worker 應停止並回報所需範圍。

依工作單指定的最小範圍讀取資料。公開 Commit 禁止夾帶未授權的原始資料、模型、研究程式、機密、憑證與個人資料。

## D. MANDATORY GIT GOVERNANCE

1. GitHub `main` 是正式治理紀錄。採單一 `main` 分支，依序派發及執行工作。
2. 每次派工前，派工 Brain 必須從 GitHub `main` 讀取最新版 `AGENTS.md`，並確認適用版本。Own Worker 必須遵守該版本。
3. Worker 依 [工作單格式](WORK_ITEM.md) 檢查授權、輸入與停止條件，完成後檢查變更範圍，Commit 並 Push 到 GitHub `main`，回報實際命令結果、Commit SHA 與檔案證據。
4. 指定驗收 Brain 必須實際讀取 GitHub 遠端成果、比對 SHA 並確認符合工作單，才可判定 `PASS`。研究成果先由 RESEARCH Brain 驗收，再由 MAIN Brain 執行最終驗收。
5. 前一項工作完成驗收並取得 MAIN 授權後，才可以啟動下一項 Worker 工作。涉及階段轉換時，同時適用 STUDENT 的最終授權。
6. GitHub 無法存取或無法驗證時，狀態為 `BLOCKED`。禁止虛構 Commit、執行結果或 Evidence。禁止以強制 Push 或破壞性操作處理遠端歷史衝突。

### BOOTSTRAP_EXCEPTION

唯一例外限定於 `WO-M0-001`。首次建立治理檔案時，若 GitHub `main` 尚無 `AGENTS.md`，可依已核准的工作單建立初版。遠端讀取及 Brain 驗收仍為必要步驟。初版上線後，每次派工均依 D 節執行。
