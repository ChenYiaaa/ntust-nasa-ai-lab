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

STUDENT-MAIN Brain 已對 `WO-M2-001` 核發 `PASS`，受驗 Commit 為 `9af6e6b6c98c349d1f211bfb08c28664a9aa2320`。STUDENT 已正式授權 M3，MAIN Brain 已派工給 STUDENT-WEB Brain。Web Own Worker 的派工解除條件見下方 M3 工作單。

## M3_FD001_HEALTH_WEBSITE_MVP_V1

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `M3_FD001_HEALTH_WEBSITE_MVP_V1` |
| TYPE | `BOUNDED_BRAIN_TO_BRAIN_WORK_ORDER` |
| FROM | STUDENT-MAIN Brain |
| TO | STUDENT-WEB Brain |
| OWNER_APPROVAL | `GRANTED` |
| STATUS | `PASS` |
| WEB_DECISION | `PASS` |
| MAIN_DECISION | `PASS` |
| ACCEPTED_API_WORK_ITEM | `WO-M3-WEB-001` |
| ACCEPTED_API_CORRECTION | `WO-M3-WEB-001-CORR-01` |
| ACCEPTED_API_COMMIT | `c50495ca02814018c8f4c30ae5285c48cf9f2a99` |
| ACCEPTED_FRONTEND_WORK_ITEM | `WO-M3-WEB-002` |
| ACCEPTED_FRONTEND_COMMIT | `e133b92786be350eef13dff82f4ad14b90d941f0` |
| API_STATUS | `PASS` |
| FRONTEND_STATUS | `PASS` |
| BROWSER_UAT_STATUS | `PASS_BY_REVIEWED_WORKER_EVIDENCE` |
| DATA_CONTRACT_VERSION | `1.0.0` |
| WEB_OWN_WORKER | `COMPLETED_AND_STOPPED` |
| ACCEPTANCE_OWNER | STUDENT-MAIN Brain |

### M3_FD001_READONLY_API_REQUIREMENTS_V1

- **OBJECTIVE** — 建立本地 FD001 唯讀 API 與網站 MVP。
- **INPUT** — 已驗收的 `M2_FD001_DATA_CONTRACT_V1`、Data Contract Schema `1.0.0`，以及學生工作區的三份已驗證 FD001 TXT。
- **EXPECTED_OUTPUT** — FD001 唯讀 API、成功與錯誤回應 Schema、JSON `null` 處理規則、來源追溯資訊、原始列與 API 的核對證據、M3 前端 MVP、感測器趨勢圖、Browser UAT、可重現的啟動說明，以及 GitHub 交付證據。
- **REQUIRED_ENDPOINTS** — `GET /api/health`、`GET /api/catalog`、`GET /api/units`、`GET /api/history`。
- **MANDATORY_TEST_QUERY** — `/api/history?split=train&unit=1&sensor=7&start=1&end=20`。
- **AUTHORIZED_SCOPE** — M3 網站、唯讀 API、測試、必要設定及操作說明。Web Brain 在自己的 Worker 工作單界定可寫目錄及檔案。既有 Research 產物、M2 Data Contract 與原始 TXT 均為唯讀。
- **RETURN_TO** — STUDENT-MAIN Brain。

#### ACCEPTANCE

STUDENT-WEB Brain 先驗收 Web Own Worker 成果，STUDENT-MAIN Brain 負責 M3 最終驗收。

1. API 讀取學生工作區的實際 FD001，來源 SHA-256 與 M2 契約一致。
2. 指定 History 查詢回傳 20 筆。逐筆核對 Sensor 7 的 API 值、Cycle 與原始實體行定位。
3. 來源追溯資訊完整，成功及錯誤回應 Schema 與 JSON `null` 語意遵循 Data Contract `1.0.0`。
4. Train 與 Test 均可獨立查詢，結果屬於指定分割。
5. 網站使用真實 API 繪圖，Browser UAT 通過，並提供可重現的啟動說明。
6. GitHub 提交範圍符合授權，公開交付範圍排除完整原始 TXT。

#### STOP_IF

- MAIN Brain 尚未對 `WO-M3-001` 核發 `PASS`，或無法確認最新治理文件。
- FD001 來源或 SHA-256 與 M2 Data Contract 不一致，或 API 回應與原始資料不符。
- 必須修改未授權檔案或 M2 Data Contract，或必須公開原始 TXT。
- GitHub Commit 或 Push 失敗。
- M4 或 M5 工作在各自的授權與派工條件成立前被觸發。

#### WEB_WORKER_RELEASE

STUDENT 已正式授權 M3。Web Own Worker 已完成交付並停止。原派工程序如下，供追溯。

1. 將 `WO-M3-001` 的治理變更提交至 GitHub `main`。
2. STUDENT-MAIN Brain 從遠端獨立驗收 `WO-M3-001` 並核發 `PASS`。
3. STUDENT-WEB Brain 重新核對 GitHub 最新治理文件。
4. STUDENT-WEB Brain 確認其他治理阻塞均已解除。
5. STUDENT-WEB Brain 正式派遣自己的 Web Own Worker。

### M3_ACCEPTANCE_EVIDENCE

| 證據 | 路徑 |
| --- | --- |
| API | [api.py](web/fd001/backend/api.py)、[API.md](web/fd001/docs/API.md)、[success.schema.json](web/fd001/docs/success.schema.json)、[test_api.py](web/fd001/tests/test_api.py) |
| API PUBLIC_SAFE | [verification.md](outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/api/PUBLIC_SAFE/verification.md)、[execution.md](outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/api/PUBLIC_SAFE/execution.md) |
| Frontend 與啟動說明 | [web/fd001/frontend/](web/fd001/frontend/) |
| Frontend Tests | [web/fd001/frontend_tests/](web/fd001/frontend_tests/) |
| Browser UAT | [browser-uat.md](outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/frontend/PUBLIC_SAFE/browser-uat.md) |

| 檢查 | 驗收紀錄 |
| --- | --- |
| API REGRESSION | `WORKER_REPORTED_20_OF_20` |
| FRONTEND TESTS | `WORKER_REPORTED_4_OF_4` |
| BROWSER UAT GROUPS | `WORKER_REPORTED_9_OF_9` |
| TRAIN API PARITY | `WORKER_REPORTED_20_OF_20` |
| TEST API PARITY | `WORKER_REPORTED_3_OF_3` |
| UNCAUGHT JAVASCRIPT EXCEPTIONS | `WORKER_REPORTED_0` |
| JSON Schema | `PASS` |
| Source Provenance | `PASS` |
| Read-only Boundary | `PASS` |

### M3_ACCEPTANCE_LIMITATIONS

1. MAIN Brain 未直接重新執行學生本地私人 FD001 TXT。
2. MAIN Brain 未親自操作學生 Windows 環境中的 Edge。
3. Browser UAT 的 PASS 依據為 GitHub 可查核程式、公開報告與 Worker 執行證據。
4. 瀏覽器涵蓋範圍限於已測試的 Edge Desktop 與 375 px 窄視窗。
5. 本地原始檔變更後，須重啟服務才會重新驗證來源快照。
6. 私人逐筆比對證據保留於學生本地的 Git 忽略目錄，公開證據未刊載完整來源數值。

### M3_FINAL_ACCEPTANCE_RECORD

- **STUDENT-WEB Brain / STUDENT-MAIN Brain** — `PASS` / `PASS`。
- **API Accepted SHA** — `c50495ca02814018c8f4c30ae5285c48cf9f2a99`。
- **Frontend Accepted SHA** — `e133b92786be350eef13dff82f4ad14b90d941f0`。
- **CANONICAL_ACCEPTANCE_RECORD** — `WO-M3-002` 通過 MAIN Brain 遠端驗收後，以 GitHub `main` 治理文件為 M3 正式最終驗收紀錄。

### M4_RELEASE_CONDITION

1. `WO-M3-002` 已 Commit 並 Push 至 GitHub `main`。
2. STUDENT-MAIN Brain 已獨立驗收 `WO-M3-002` 為 `PASS`。
3. STUDENT 正式批准 M4 階段轉換。
4. STUDENT-MAIN Brain 核對 GitHub `main` 最新治理文件。
5. STUDENT-MAIN Brain 正式建立 M4 工作單。

STUDENT-MAIN Brain 已對 `WO-M3-002` 核發 `PASS`，受驗 Commit 為 `d5216cfac4a26ea861d654dfc42f56fbb898ddf0`。STUDENT 已正式授權 M4，MAIN Brain 已將工作單派給 STUDENT-WEB Brain。Web Own Worker 派工須符合下方的解除條件。

## M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1` |
| TYPE | `BOUNDED_BRAIN_TO_BRAIN_WORK_ORDER` |
| FROM | STUDENT-MAIN Brain |
| TO | STUDENT-WEB Brain |
| OWNER_APPROVAL | `GRANTED` |
| MAIN_AUTHORIZATION | `GRANTED` |
| STATUS | `PASS` |
| WEB_DECISION | `PASS` |
| MAIN_DECISION | `PASS` |
| WEB_WORK_ITEM | `WO-M4-WEB-001` |
| SCOPE_EXTENSION | `WO-M4-WEB-001-SCOPE-EXT-01` |
| ACCEPTED_COMMIT | `42a36bb73793a691c8d6a463ab6b697de4f7e468` |
| PROMPT_GENERATOR | `PASS` |
| PROMPT_COPY | `PASS_BY_REVIEWED_EVIDENCE` |
| SOURCE_TRACEABILITY | `PASS` |
| BROWSER_UAT | `PASS_BY_REVIEWED_WORKER_EVIDENCE` |
| WEB_OWN_WORKER | `COMPLETED_AND_STOPPED` |
| ACCEPTANCE_OWNER | STUDENT-MAIN Brain |

- **OBJECTIVE** — 以 M3 已驗收的網站及 FD001 API 為基礎，交付可啟動的互動式網站，支援真實資料查詢、Sensor Trend、原始來源定位，以及 Evidence Prompt 生成與複製。
- **INPUT** — FD001 Data Contract `1.0.0`、M3 受驗 API Commit `c50495ca02814018c8f4c30ae5285c48cf9f2a99`、M3 受驗 Frontend Commit `e133b92786be350eef13dff82f4ad14b90d941f0`、[M3 Browser UAT 證據](outputs/M3_FD001_HEALTH_WEBSITE_MVP_V1/frontend/PUBLIC_SAFE/browser-uat.md)，以及學生工作區的已驗證本地 FD001 來源。
- **EXPECTED_OUTPUT** — 可啟動的網站、Train／Test 選取、Unit 選單、Sensor 選單、Cycle 範圍選取、Sensor Trend Chart、Source Record Table、Source Provenance、Evidence Prompt Generator、Copy Prompt、啟動命令、實際 Local URL、真實 Browser 或人工 UAT、畫面與 API 及原始列的比對證據，以及 GitHub Commit 證據。
- **RETURN_TO** — STUDENT-MAIN Brain。

### M4_ACCEPTANCE

1. 依交付的啟動命令啟動網站，並在本地瀏覽器開啟交付的 Local URL。
2. 核對 Train／Test、Unit、Sensor 與 Cycle 範圍的選取與 API 一致。
3. 逐筆核對畫面趨勢、來源資料列、API 回應與原始 TXT，確認來源定位可追溯。
4. 依目前選取生成 Evidence Prompt，確認引用數值可重現，並實際驗證複製功能。
5. 驗證錯誤及空資料處理，提供真實瀏覽器或人工 UAT 的執行證據。靜態截圖可作佐證。
6. 確認 GitHub 變更符合授權範圍，公開交付排除未授權的原始 TXT，並保留 M3 已驗收成果與 FD001 Data Contract 定義。

### WEB_WORKER_RELEASE

M4 的派工前置條件為 STUDENT-MAIN Brain 遠端獨立驗收 `WO-M4-001`，再由 STUDENT-WEB Brain 核對最新治理文件並派工。Web Own Worker 已完成交付並停止。

### M4_ACCEPTANCE_EVIDENCE

STUDENT-WEB Brain 與 STUDENT-MAIN Brain 均對 `WO-M4-WEB-001` 核發 `PASS`。受驗結果可查閱 [PUBLIC_SAFE](outputs/M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1/PUBLIC_SAFE/)、[執行記錄](outputs/M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1/PUBLIC_SAFE/execution.md)、[比對證據](outputs/M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1/PUBLIC_SAFE/verification.md)與 [Browser UAT](outputs/M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1/PUBLIC_SAFE/browser-uat.md)。

| 檢查 | Worker 執行證據 |
| --- | --- |
| BACKEND | `WORKER_REPORTED_20_OF_20` |
| M3_MODEL | `WORKER_REPORTED_4_OF_4` |
| M4_PROMPT | `WORKER_REPORTED_4_OF_4` |
| TRAIN_PARITY | `WORKER_REPORTED_20_OF_20` |
| TEST_PARITY | `WORKER_REPORTED_3_OF_3` |
| FINAL_BROWSER_EXIT | `WORKER_REPORTED_0` |

#### STARTUP

在專案根目錄的兩個終端機分別啟動。

- **Backend** — `python -B web/fd001/backend/api.py --port 8765`
- **Frontend** — `node web/fd001/frontend/serve.mjs`
- **LOCAL_URL** — `http://127.0.0.1:8766/`

### M4_ACCEPTANCE_LIMITATIONS

- MAIN Brain 未親自重跑私人 TXT。
- MAIN Brain 未親自操作學生 Windows 環境中的 Edge。
- Browser PASS 依據為 Worker 執行證據。
- Browser Coverage 限 Windows Edge。
- Clipboard 需要瀏覽器權限。
- 本地原始資料變更後須重啟服務以重新驗證。

### M4_FOLLOW_UP

`README_STATIC_ASSET_COUNT_STALE` 為非阻塞問題，列為後續維護候選事項。

### M5_RELEASE_CONDITION

M5 階段轉換前置條件如下。

1. 將 `WO-M4-002` Commit 並 Push 至 GitHub `main`。
2. STUDENT-MAIN Brain 獨立驗收 `WO-M4-002` 並核發 `PASS`。
3. STUDENT 正式批准 M5。
4. STUDENT-MAIN Brain 核對 GitHub `main` 最新治理文件。
5. STUDENT-MAIN Brain 建立 M5 限定工作單。

STUDENT-MAIN Brain 已正式驗收 `WO-M4-002` 為 `PASS`，受驗 Commit 為 `3f048f092aed02597ff132622db0a6a76b0e1aa8`。STUDENT 已正式授權 M5。Web Own Worker 的派工解除條件見 M5 Web 子工作。

## M5_END_TO_END_VALIDATION_AND_DELIVERY

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `M5_END_TO_END_VALIDATION_AND_DELIVERY` |
| STATUS | `PASS` |
| OWNER_APPROVAL | `GRANTED` |
| MAIN_AUTHORIZATION | `GRANTED` |
| MAIN_ACCEPTANCE_OWNER | STUDENT-MAIN Brain |
| WEB_SUBTASK | `M5_FD001_EVIDENCE_PROMPT_HARDENING_V1` |
| WEB_WORKER_STATUS | `COMPLETED_AND_STOPPED` |
| M5_MAIN_DECISION | `PASS` |
| M5_WEB_PROMPT_HARDENING | `PASS` |
| M5_FINAL_E2E | `PASS` |
| M5_BROWSER_UAT_SUPPLEMENT | `PASS` |
| M5_WEB_ACCEPTANCE | `PASS` |
| M5_MAIN_ACCEPTANCE | `PASS` |
| ACCEPTED_WEB_PROMPT_COMMIT | `ec5bb7b06235b28d4a3387681127575f55abdd57` |
| ACCEPTED_FINAL_E2E_COMMIT | `39093a0b2c6823158ac2f72a0ce098327a370e88` |
| ACCEPTED_BROWSER_UAT_COMMIT | `90c45cb67a521a6e9bfb67e355b7fc4eabc81c9d` |

- **OBJECTIVE** — 完成最終 End-to-End Validation、既有 Evidence Prompt 強化、互動式網站驗證，以及可重現的最終交付。
- **INPUT** — M0–M4 驗收紀錄、GitHub `main`、FD001 Data Contract `1.0.0`、M3 已驗收 API、M4 已驗收網站與 Prompt，以及學生工作區已驗證的原始資料。
- **EXPECTED_OUTPUT** — Web 子工作驗收證據、Raw／API／UI／Prompt 比對、Browser UAT、啟動命令及已驗證的 Local URL、固定的交付 Commit、完整端到端重現步驟及最終驗收紀錄。
- **ACCEPTANCE** — STUDENT-MAIN Brain 已對 `WO-M5-001`、`WO-M5-WEB-001`、`WO-M5-002` 與 `WO-M5-WEB-002` 核發 `PASS`。最終端到端驗收、重現性查核與交付由 STUDENT-MAIN Brain 負責。
- **STOP_IF** — 治理前置條件未滿足、端到端流程無法重現、證據與來源不一致，或需要未取得的授權。
- **RETURN_TO** — STUDENT-MAIN Brain 彙整最終結果並交付 STUDENT。

### M5_TEST_EVIDENCE

- **PUBLIC_EVIDENCE** — [M5 Final E2E](outputs/M5_FINAL_E2E_VALIDATION_V1/PUBLIC_SAFE/)。
- **SUPPLEMENTAL_UAT_EVIDENCE** — [Browser UAT 補充證據](outputs/M5_FD001_BROWSER_UAT_SUPPLEMENT_V1/PUBLIC_SAFE/)。

| 測試 | 驗收證據 |
| --- | --- |
| Backend | `WORKER_REPORTED_20_OF_20` |
| Node | `WORKER_REPORTED_10_OF_10` |
| Supplemental Browser | `WORKER_REPORTED_16_OF_16` |
| Train | `WORKER_REPORTED_20_OF_20` |
| Test | `WORKER_REPORTED_3_OF_3` |
| Source Hash Pins | `MATCHED_M2_CONTRACT` |
| API Errors | `WORKER_REPORTED_10_OF_10` |
| Browser Invalid Ranges | `WORKER_REPORTED_5_OF_5` |
| Real Backend Interruption | `WORKER_REPORTED_HTTP_502` |
| Backend Recovery | `WORKER_REPORTED_HTTP_200` |
| Isolated Fail-Closed | `WORKER_REPORTED_HTTP_503` |
| Prompt | `PASS_9_OF_9` |
| Clipboard | `PASS_BY_REVIEWED_WORKER_EVIDENCE` |

### M5_NON_BLOCKING_FINDINGS

- 補充 UAT 首次 Runner 回傳 exit code `1`，公開執行紀錄已說明原因，重新執行成功。
- 瀏覽器涵蓋範圍為 Windows Edge。剪貼簿需要瀏覽器權限。
- 重現需要已授權的私人 FD001 來源。Backend 在啟動時驗證來源，原始檔變更後需重啟驗證。
- PNG 視覺安全查核屬 Worker 回報，MAIN 未獨立驗證。

最終治理同步 `WO-M5-003` 交由 STUDENT-MAIN Brain 從 GitHub 獨立驗收。

## M5_FD001_EVIDENCE_PROMPT_HARDENING_V1

| 欄位 | 值 |
| --- | --- |
| WORK_ITEM_ID | `M5_FD001_EVIDENCE_PROMPT_HARDENING_V1` |
| PARENT_WORK_ITEM | `M5_END_TO_END_VALIDATION_AND_DELIVERY` |
| ASSIGNEE | STUDENT-WEB Brain |
| OWNER_APPROVAL | `GRANTED` |
| MAIN_AUTHORIZATION | `GRANTED` |
| STATUS | `PASS` |
| WEB_WORKER_STATUS | `COMPLETED_AND_STOPPED` |
| ACCEPTED_COMMIT | `ec5bb7b06235b28d4a3387681127575f55abdd57` |

- **OBJECTIVE** — STUDENT-WEB Brain 管理其 Web Own Worker，負責強化既有 Evidence Prompt、整合互動式網站及驗證 Browser UAT。
- **INPUT** — FD001 Data Contract `1.0.0`、M3 已驗收 API、M4 已驗收 Prompt Generator、互動式網站及學生工作區已驗證的 FD001 原始資料。
- **EXPECTED_OUTPUT** — 強化後的 Evidence Prompt、互動整合證據、複製與剪貼簿讀回證據、Raw／API／UI／Prompt 一致性驗證，以及可重現的啟動命令與已驗證的 Local URL。
- **RETURN_TO** — STUDENT-MAIN Brain。

### M5_PROMPT_EVIDENCE_RULES

- **KNOWN** — 直接依 Data Contract 與 API 驗證的事實。保留 FD001 來源追溯、原始紀錄及實體行位置、已定義的 Sensor 欄位語意、選取樣本範圍與實際觀測值。
- **INFERRED** — 經明確定義的計算結果或有限的資料解釋。資料品質摘要中的推導統計須記錄所用資料範圍、計算方法與限制。
- **UNKNOWN** — 無法由證據驗證的設備狀態、故障類型、故障原因、實際 RUL 與未定義的感測器物理意義。

Prompt 須明確要求外部 AI 區分推論與觀測事實，並禁止無證據宣稱已發生故障、捏造故障診斷、提供無依據的 RUL 預測或健康分數。

### M5_WEB_ACCEPTANCE

1. 核對 Prompt 與目前選取及樣本範圍一致，Raw／API／UI／Prompt 的資料、來源定位與語意可追溯，資料品質摘要可重現。
2. 使用真實瀏覽器或人工 UAT 驗證互動式網站、實際複製及剪貼簿讀回。
3. 提供啟動命令、已驗證的 Local URL、交付 Commit 及完整端到端重現步驟。
4. 由 STUDENT-WEB Brain 先驗收並回報 STUDENT-MAIN Brain。MAIN Brain 接受 Web 子工作後，才可啟動 MAIN Final E2E Work Item。

### M5_WEB_WORKER_RELEASE

STUDENT-MAIN Brain 已從 GitHub 獨立驗收 `WO-M5-001` 為 `PASS`。STUDENT-WEB Brain 管理其 Web Own Worker 的派工與交付。Web Own Worker 已完成並停止。

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
