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

## M1_DATASET_PROFILE_6CSV_V1

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `M1_DATASET_PROFILE_6CSV_V1` |
| TYPE | `BRAIN_TO_BRAIN_WORK_ORDER` |
| ASSIGNEE | STUDENT-RESEARCH Brain |
| RESEARCH_DECISION | `PASS` |
| MAIN_DECISION | `PASS` |
| STATUS | `PASS` |
| ACCEPTED_COMMIT | `ea112bd4f9daac2c95006cc5dc95da70831d9772` |

- **EVIDENCE** — 驗收已核對 GitHub `main` 的 Commit SHA 與 6 份授權研究交付物。核對範圍涵蓋 Dataset Inventory、Dataset Profile、Data Quality Report、可重現程式、Execution Log 及交付說明。範圍為 1 個合成 CSV Dataset、6 筆資料與 4 個欄位，Research Domain Acceptance 與 MAIN Final Acceptance 均為 `PASS`。
- **LIMITATION** — MAIN Brain 未直接重跑私人原始 CSV。驗收依據為 GitHub 上的程式、執行證據與交付物一致性審查。

## M2_FD001_DATA_CONTRACT_V1

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `M2_FD001_DATA_CONTRACT_V1` |
| TYPE | `BRAIN_TO_BRAIN_WORK_ORDER` |
| ASSIGNEE / RESPONSIBLE_BRAIN | STUDENT-RESEARCH Brain |
| OWNER_APPROVAL | `GRANTED` |
| STATUS | `PASS` |
| RESEARCH_DECISION | `PASS` |
| MAIN_DECISION | `PASS` |
| RESEARCH_WORKER | `COMPLETED_AND_STOPPED` |
| GATE_A | `PASS` |
| GATE_B | `PASS` |
| GATE_C | `PASS` |
| DATA_CONTRACT_VERSION | `1.0.0` |
| ACCEPTED_COMMIT_GATE_A | `c47df8eebf95e1b6d487e81c657863e65a170564` |
| ACCEPTED_COMMIT_GATE_B | `ac4f97b220a6ec895c6cc0f18782190fefb45a82` |
| ACCEPTED_COMMIT_GATE_C | `b09981561028345fd5f66bfd8b158200f3cca3b9` |
| GATE_C_RESEARCH_ACCEPTANCE | `PASS` |
| GATE_C_MAIN_ACCEPTANCE | `PASS` |

- **OBJECTIVE** — 先驗證本地三份 NASA C-MAPSS FD001 TXT，通過後執行 Trend / Quality Analysis，最後交付可追溯的 Data Contract。
- **INPUT** — `train_FD001.txt`、`test_FD001.txt`、`RUL_FD001.txt`。
- **EXPECTED_OUTPUT** — 本地來源與結構驗證證據、趨勢及資料品質分析結果，以及可追溯至 Engine Unit、Cycle、Sensor 和來源檔案的 Data Contract。
- **STOP_IF** — 最新治理文件無法核對、前置治理同步尚未通過驗收、任一授權輸入無法驗證、前一 Gate 未通過，或需要修改或發布未授權的原始資料。
- **RETURN_TO** — STUDENT-MAIN Brain。

**派工規則** — M2 派工前，由 STUDENT-RESEARCH Brain 核對 GitHub `main` 上的最新治理文件，再依授權自行向其 RESEARCH Own Worker 派工。

### ACCEPTANCE_EVIDENCE

- MAIN Brain 已獨立讀取 GitHub 的 Gate A／B／C Commit 並核對遠端 `main` SHA，確認研究交付範圍符合授權。
- 來源 SHA-256 與報告一致。FD001 Data Contract `1.0.0` 已審查，包含 6 項操作及 6 個錯誤碼。
- Gate C Worker 的 35 項檢查全部通過。Research Brain Acceptance 與 MAIN Brain Final Acceptance 均為 `PASS`。

### ACCEPTANCE_LIMITATION

- MAIN Brain 未直接重跑私人原始 TXT。最終驗收依據為 GitHub 交付物、Worker 執行證據及 Research 驗收。
- RUL 映射依已文件化的 `MW_FD001_SORTED_ID` 慣例。公開產物是保護隱私的摘要。
- 原始 Data Contract JSON 的 `research_github_evidence.gate_c` 欄位保留交付當時的 `PENDING_BRAIN_ACCEPTANCE` 狀態。
- **CANONICAL_ACCEPTANCE_RECORD** — `WO-M2-001` 通過 MAIN Brain 遠端驗收後，以 GitHub `main` 治理文件為正式最終驗收紀錄。

### M3_RELEASE_CONDITION

M3 狀態為 `NOT_STARTED`，學生授權為 `NOT_GRANTED`，派工為 `NOT_AUTHORIZED`。開始 M3 前須依序完成下列事項。

1. MAIN Brain 驗收 `WO-M2-001` 為 `PASS`。
2. 核對 GitHub `main` 最新治理文件。
3. STUDENT 正式授權 M3。
4. MAIN Brain 正式指派 Web Brain。

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
