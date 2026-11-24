# NTUST_SYNTHETIC_AGENT_LAB 工作單管理

所有 Worker 工作均使用 `BOUNDED_WORK_ORDER`，遵循 [AGENTS.md](AGENTS.md) 的派發、Git 與驗收規則。

## 狀態與移轉

| 狀態 | 進入條件 |
| --- | --- |
| `CREATED_NOT_DISPATCHED` | Brain 建立工作單並記錄範圍，尚未派發。 |
| `COMMAND_DISPATCHED` | 派工 Brain 依授權將工作單交付指定 Worker。 |
| `IN_PROGRESS` | Worker 已依工作單開始執行，並以實際證據記錄進度。 |
| `WORKER_COMPLETED` | Worker 完成授權交付物、Commit、Push 與必要的 Worker 端檢查。 |
| `PENDING_BRAIN_ACCEPTANCE` | Worker 回傳執行證據，交由指定 Brain 從 GitHub 遠端獨立驗收。 |
| `PASS` | 驗收 Brain 已讀取 GitHub 遠端成果，所有驗收條件成立並留下紀錄。 |
| `FAIL` | 驗收 Brain 發現成果不符合工作單，並留下實際缺項與證據。 |
| `BLOCKED` | 停止條件成立或無法執行必要驗證，記錄阻礙、已完成步驟及可驗證的執行結果。 |

狀態以實際證據更新。Worker 完成 Commit 與 Push、執行必要的遠端檢查並回傳後，應標記 `PENDING_BRAIN_ACCEPTANCE`。只有指定 Brain 遠端驗收成功後才可標記 `PASS`。恢復阻擋中的工作時，先重新確認阻礙已解除，再依原授權與最新證據更新狀態。

## WO-M0-001

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `WO-M0-001` |
| TYPE | `BOUNDED_WORK_ORDER` |
| MILESTONE | `M0_AI_COMPANY_GOVERNANCE` |
| ASSIGNEE | MAIN Own Worker |
| OWNER_APPROVAL | `GRANTED` |
| INITIAL_STATUS | `COMMAND_DISPATCHED` |
| STATUS | `PASS` |
| ACCEPTANCE_OWNER | STUDENT-MAIN Brain |
| ACCEPTED_COMMIT | `04593b11da7c8c498546e0c20a7e0eb375f0360d` |

- **OBJECTIVE** — 初始化團隊治理，建立可從 GitHub `main` 驗收的正式版本。
- **INPUT** — STUDENT 核准的 `WO-M0-001`、專案根目錄與學生帳號下的公開 `ntust-nasa-ai-lab` 儲存庫。
- **EXPECTED_OUTPUT** — `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`、GitHub `main` 及 Worker 執行回傳。
- **AUTHORIZED_SCOPE** — 四份治理文件及完成交付所需的 Git 初始化、提交、Push 和驗證。其餘既有專案檔案唯讀。
- **ACCEPTANCE** — Brain 逐一讀取四份 GitHub `main` 文件，確認完整性、授權範圍、`PUBLIC` 屬性及 Commit SHA，並記錄獨立驗收。Worker 應回傳關鍵命令 exit code、Commit SHA 與 Git object format、四份檔案 SHA-256、儲存庫網址、遠端 `main` SHA、檔案驗證結果及已知阻礙。
- **STOP_IF** — 根目錄或 Repo 擁有權未能確認、認證失敗、遠端歷史衝突、需要修改未授權檔案、可能提交敏感資訊、Commit 或 Push 無法安全完成、遠端驗證失敗，或 Worker 已完成交付及遠端檢查。
- **RETURN_TO** — STUDENT-MAIN Brain。Brain 依遠端證據判定 `PASS`、`FAIL` 或 `BLOCKED`。

### ACCEPTANCE_EVIDENCE

- STUDENT-MAIN Brain 已從 GitHub `main` 獨立驗證 `WO-M0-001`。
- 四份治理文件（`AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`）完整，Commit 範圍符合 `WO-M0-001`。
- GitHub 儲存庫為 `PUBLIC`，遠端驗收所核對的 SHA 與 `ACCEPTED_COMMIT` 一致。

### ACCEPTANCE_RECORD

STUDENT-MAIN Brain 正式驗收 `WO-M0-001` 為 `PASS`。`WO-M0-002` 依 MAIN Brain 的正式授權同步此驗收結果。

## 後續工作單必填欄位

| 欄位 | 填寫要求 |
| --- | --- |
| WORK_ITEM_ID | 全專案唯一的工作識別碼。 |
| OBJECTIVE | 本次要完成的具體目標。 |
| INPUT | 已核准的來源、路徑、版本與先決條件。 |
| EXPECTED_OUTPUT | 交付物、格式、位置與應回傳的證據。 |
| AUTHORIZED_SCOPE | 可讀取、修改、提交或發布的明確範圍。 |
| ACCEPTANCE | 驗收人、可重現的檢查與通過條件。 |
| STOP_IF | 必須停止並回報的情況及完成後的停止點。 |
| RETURN_TO | 接收回傳並負責驗收的 Brain。 |
