# NTUST_SYNTHETIC_AGENT_LAB Roadmap

階段依 M0 至 M5 順序進行。每階段的派工須符合 [AGENTS.md](AGENTS.md)、前一階段驗收及 STUDENT 授權。M1 至 M5 的初始狀態均為 `NOT_STARTED`，此 Roadmap 的建立僅啟動 M0 治理初始化。

## M0 — AI COMPANY GOVERNANCE

- **Status** — `PASS`。STUDENT-MAIN Brain 已完成 `WO-M0-001` 的遠端驗收，詳見 [WORK_ITEM.md](WORK_ITEM.md#wo-m0-001)。
- **Goal** — 建立 AI 團隊治理、權責邊界及 GitHub 流程。
- **Input** — STUDENT 核准的 `WO-M0-001`、已確認的專案根目錄與學生 GitHub 帳號。
- **Deliverables** — `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md` 與 GitHub 公開儲存庫 `ntust-nasa-ai-lab` 的 `main` 正式版本。
- **Responsible Brain** — STUDENT-MAIN Brain。
- **Acceptance Criteria** — Brain 從 GitHub `main` 實際讀取四份完整文件，核對遠端 SHA 與 Worker 回傳的本機 SHA，驗證儲存庫為 `PUBLIC`，檢查提交範圍及 Evidence，並記錄獨立驗收結果。
- **STOP_IF** — 無法確認根目錄、認證、擁有者或遠端歷史，發現機密或超範圍變更，或無法安全完成 Commit、Push 與遠端驗證。Worker 完成遠端檢查後停止並回報。
- **Next Role** — STUDENT-MAIN Brain 驗收 `WO-M0-002` 後，依學生授權向 RESEARCH Brain 交付 M1。

## M1 — FIRST VERIFIED DATASET RETURN

- **Status** — `PASS`。
- **Work Item ID** — `M1_DATASET_PROFILE_6CSV_V1`。
- **Research Decision / MAIN Decision** — `PASS` / `PASS`。
- **Accepted Commit** — `ea112bd4f9daac2c95006cc5dc95da70831d9772`。
- **Acceptance Scope** — 1 個合成 CSV Dataset、6 筆資料、4 個欄位與 6 份 GitHub 研究交付物。Research Domain Acceptance 與 MAIN Final Acceptance 均為 `PASS`。
- **Acceptance Limitation** — MAIN Brain 未親自重新執行私人原始 CSV。驗收依據為 GitHub 上的程式、執行證據與交付物一致性審查。
- **Goal** — 由 RESEARCH Brain 協調自己的 Worker，對六筆合成 CSV 資料建立可驗證的 Dataset Profile。
- **Input** — 已知檔名 `synthetic_sensor.csv`、經授權的資料位置與六筆資料的來源或辨識方式。六筆的分布須依盤點證據判定，禁止假定有六個既存獨立檔案。
- **Deliverables** — Dataset Profile、資料盤點、可重現的處理方式與實際執行證據。
- **Responsible Brain** — RESEARCH Brain。
- **Acceptance Criteria** — 每筆資料可追溯至實際來源。Profile 的 shape、columns、dtype、missing、duplicates 及 statistics 均有真實證據，且盤點清楚說明六筆資料的涵蓋方式。RESEARCH Brain 驗收後回報 MAIN Brain。
- **STOP_IF** — 尚未授權、資料來源不可讀、無法用實際證據確認六筆的範圍，或無法重現任何必要欄位或統計。保留現有證據並回報缺口。
- **Next Role** — STUDENT-MAIN Brain 驗收 `WO-M1-002` 後，由 STUDENT-RESEARCH Brain 依 M2 授權與最新治理文件處理派工。

## M2 — NASA C-MAPSS FD001 DATA INTEGRATION

- **Status** — `PASS`。
- **Work Item ID** — `M2_FD001_DATA_CONTRACT_V1`。
- **Owner Approval** — `GRANTED`。
- **Research Decision / MAIN Decision** — `PASS` / `PASS`。
- **GATE_A_RAW_VALIDATION / GATE_B_TREND_QUALITY / GATE_C_DATA_CONTRACT** — `PASS` / `PASS` / `PASS`。
- **ACCEPTED_COMMITS** — Gate A `c47df8eebf95e1b6d487e81c657863e65a170564`、Gate B `ac4f97b220a6ec895c6cc0f18782190fefb45a82`、Gate C `b09981561028345fd5f66bfd8b158200f3cca3b9`。
- **CONTRACT_SCHEMA_VERSION** — `1.0.0`。
- **GATE_C_RESEARCH_ACCEPTANCE / GATE_C_MAIN_ACCEPTANCE** — `PASS` / `PASS`。
- **ACCEPTANCE_SCOPE** — 三份本地 FD001 TXT。Train 20,631 列、Test 13,096 列、RUL 100 列。Train 與 Test 各 26 欄、各 100 個 Unit，共 21 個 Sensor。來源 SHA-256 已固定，Raw Locator 已驗證。Train／Test／RUL 資料語意、感測器趨勢、資料品質、Data Contract 操作及 Error Contract 均已審查。Research 與 MAIN 的正式驗收均為 `PASS`。
- **ACCEPTANCE_LIMITATIONS** — MAIN Brain 未親自重新執行本地私人 TXT。驗收依據為 GitHub 遠端交付物、Worker 執行證據及 Research 驗收。RUL 映射依 `MW_FD001_SORTED_ID` 慣例。Gate C Contract JSON 的 `PENDING_BRAIN_ACCEPTANCE` 是原始交付快照的狀態。
- **CANONICAL_ACCEPTANCE_RECORD** — `WO-M2-001` 通過 MAIN Brain 遠端驗收後，以 GitHub `main` 治理文件為正式最終驗收紀錄。
- **Goal** — 接入學生本地 NASA C-MAPSS FD001 真實資料，建立 Engine Unit、Cycle、Sensor 索引與來源追溯。
- **Input** — 學生授權的本地 FD001 檔案、資料規格與 M1 驗收紀錄。
- **Deliverables** — 可重現的 FD001 資料讀取方式、欄位與索引對照、來源清單及抽樣驗證證據。
- **Responsible Brain** — RESEARCH Brain。
- **Acceptance Criteria** — 可依 Engine Unit、Cycle 與 Sensor 找到對應讀值。以本地資料抽樣比對讀值、欄位映射及資料分組，並記錄來源與驗證方式。
- **STOP_IF** — 檔案或資料規格無法確認、索引或讀值與來源不一致，或作業涉及未授權的資料修改或發布。
- **Next Role** — STUDENT-MAIN Brain 已對 `WO-M2-001` 核發 `PASS`，受驗 Commit 為 `9af6e6b6c98c349d1f211bfb08c28664a9aa2320`。STUDENT 已授權 M3，Web Own Worker 的派工依 M3 解除條件辦理。

## M3 — HEALTH ANALYSIS WEBSITE MVP

- **MILESTONE** — `M3_HEALTH_ANALYSIS_WEBSITE_MVP`。
- **Status** — `PASS`。
- **OWNER_APPROVAL** — `GRANTED`。
- **MAIN_BRAIN_AUTHORIZATION** — `GRANTED`。
- **BRAIN_TO_BRAIN_WORK_ORDER** — `M3_FD001_HEALTH_WEBSITE_MVP_V1`。
- **BRAIN_TO_BRAIN_STATUS** — `COMMAND_DISPATCHED`。
- **ASSIGNED_BRAIN** — STUDENT-WEB Brain。
- **WEB_WORKER_STATUS** — `COMPLETED_AND_STOPPED`。
- **WEB_DECISION / MAIN_DECISION** — `PASS` / `PASS`。
- **API_STATUS / FRONTEND_STATUS** — `PASS` / `PASS`。
- **BROWSER_UAT_STATUS** — `PASS_BY_REVIEWED_WORKER_EVIDENCE`。
- **ACCEPTED_API_COMMIT** — `c50495ca02814018c8f4c30ae5285c48cf9f2a99`。
- **ACCEPTED_FRONTEND_COMMIT** — `e133b92786be350eef13dff82f4ad14b90d941f0`。
- **DATA_CONTRACT_VERSION** — `1.0.0`。
- **Goal** — 建立網站，讓使用者選擇 Engine Unit、Cycle 與 Sensor，查看真實感測器趨勢及資料來源。
- **Input** — M2 已驗收的 FD001 介面、欄位索引、資料來源紀錄及授權的網站工作範圍。
- **Deliverables** — 可啟動的網站 MVP、選取介面、感測器趨勢、來源呈現與操作驗證證據。
- **Responsible Brain** — STUDENT-WEB Brain 負責執行與初驗，STUDENT-MAIN Brain 負責最終驗收。
- **Acceptance Criteria** — 使用者可完成三項選取，網站從真實 API 取得趨勢與來源，並處理空結果與無效選取。唯讀 API 須使用學生工作區的已驗證 FD001，嚴格遵守 Data Contract `1.0.0`，定義成功及錯誤回應與 JSON `null` 語意，並保留來源追溯資訊。以實際 FD001 原始列逐筆核對 API，指定 History 查詢須核對 20 筆。Train 與 Test 須正確區分，公開交付範圍排除完整原始 TXT。
- **STOP_IF** — `WO-M3-001` 尚未獲 MAIN Brain 驗收、FD001 資料無法查詢、選取結果與來源不一致，或須傳輸未授權資料。
- **AMENDMENT_ID** — `M3_FD001_READONLY_API_REQUIREMENTS_V1`。
- **REQUIRED_ENDPOINTS** — `GET /api/health`、`GET /api/catalog`、`GET /api/units`、`GET /api/history`。
- **MANDATORY_TEST_QUERY** — `/api/history?split=train&unit=1&sensor=7&start=1&end=20`。
- **Next Role** — STUDENT-MAIN Brain 已獨立驗收 `WO-M3-002` 為 `PASS`，受驗 Commit 為 `d5216cfac4a26ea861d654dfc42f56fbb898ddf0`。STUDENT 已正式授權 M4，Web Own Worker 的派工依 M4 的解除條件辦理。

### M3_ACCEPTANCE_SUMMARY

- **API** — 四個 FD001 唯讀端點通過驗收。
- **Frontend** — Train／Test 分割、動態 Unit、Sensor 1–21 與 Cycle 範圍選取均通過驗收。Sensor 趨勢圖、資料品質統計與來源追溯均通過驗收。
- **互動狀態** — Loading、Empty、Error 與過期回應防護均通過驗收。
- **審查證據** — Browser UAT 證據與本地啟動說明均已審查。受驗版本與證據路徑見 [WORK_ITEM.md](WORK_ITEM.md#m3_acceptance_evidence)。

### M3_ACCEPTANCE_LIMITATIONS

1. MAIN Brain 未直接重新執行學生本地私人 FD001 TXT。
2. MAIN Brain 未親自操作學生 Windows 環境中的 Edge。
3. Browser UAT 的 PASS 依據為 GitHub 可查核程式、公開報告與 Worker 執行證據。
4. 瀏覽器涵蓋範圍限於已測試的 Edge Desktop 與 375 px 窄視窗。
5. 本地原始檔變更後，須重啟服務才會重新驗證來源快照。
6. 私人逐筆比對證據保留於學生本地的 Git 忽略目錄，公開證據未刊載完整來源數值。

## M4 — EVIDENCE PROMPT GENERATION

- **MILESTONE** — `M4_EVIDENCE_PROMPT_GENERATION`。
- **Status** — `PASS`。
- **OWNER_APPROVAL** — `GRANTED`。
- **MAIN_AUTHORIZATION** — `GRANTED`。
- **ASSIGNED_BRAIN** — STUDENT-WEB Brain。
- **BRAIN_TO_BRAIN_WORK_ITEM** — `M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1`。
- **WEB_DECISION / MAIN_DECISION** — `PASS` / `PASS`。
- **WEB_WORK_ITEM** — `WO-M4-WEB-001`。
- **SCOPE_EXTENSION** — `WO-M4-WEB-001-SCOPE-EXT-01`。
- **ACCEPTED_COMMIT** — `42a36bb73793a691c8d6a463ab6b697de4f7e468`。
- **WEB_WORKER_STATUS** — `COMPLETED_AND_STOPPED`。
- **PROMPT_GENERATOR / SOURCE_TRACEABILITY** — `PASS` / `PASS`。
- **PROMPT_COPY** — `PASS_BY_REVIEWED_EVIDENCE`。
- **BROWSER_UAT** — `PASS_BY_REVIEWED_WORKER_EVIDENCE`。
- **EVIDENCE** — [M4 公開證據](outputs/M4_FD001_INTERACTIVE_EVIDENCE_WEB_V1/PUBLIC_SAFE/)與[測試及啟動紀錄](WORK_ITEM.md#m4_acceptance_evidence)。
- **ACCEPTANCE_LIMITATIONS** — MAIN Brain 未親自重跑私人 TXT 或操作學生的 Edge。Browser PASS 依據為 Worker 執行證據，瀏覽器覆蓋限 Windows Edge。剪貼簿需要瀏覽器權限，原始資料變更後須重啟服務以重新驗證。
- **維護候選事項** — `README_STATIC_ASSET_COUNT_STALE` 為非阻塞問題。
- **Goal** — 根據網站選取條件與真實資料產生可複製、可追溯的 Evidence Prompt。
- **Input** — M3 已驗收的選取與查詢介面、M2 的來源資訊及授權的 Prompt 格式。
- **Deliverables** — Evidence Prompt 產生與複製功能、輸出範例及原始資料比對證據。
- **Responsible Brain** — STUDENT-WEB Brain 負責執行與初驗，STUDENT-MAIN Brain 負責最終驗收。
- **互動式網站** — 沿用 M3 已驗收的網站與 FD001 API，整合 Train／Test、Engine Unit、Sensor 與 Cycle 範圍選取，顯示真實 Sensor Trend 及對應 Source Records。保留 M3 已驗收成果與 FD001 Data Contract `1.0.0`。
- **Acceptance Criteria** — 使用目前選取產生可複製的 Evidence Prompt，引用的讀值與統計須可重現並追溯至來源。交付可依命令啟動的網站及實際 Local URL，以真實瀏覽器或人工 UAT 核對畫面、API 與原始 TXT，並驗證錯誤與空結果。靜態截圖可作佐證，交付須包含可操作網站與 UAT 執行證據。
- **STOP_IF** — `WO-M4-001` 尚未獲 MAIN Brain 驗收、Prompt 與網站選取或原始讀值不一致、來源缺漏，或輸出含未授權資訊。
- **Next Role** — 等待 STUDENT-MAIN Brain 遠端獨立驗收 `WO-M4-002`。通過後由 STUDENT 決定是否授權 M5，完整條件見 [WORK_ITEM.md](WORK_ITEM.md#m5_release_condition)。

## M5 — END-TO-END VALIDATION AND DELIVERY

- **Status** — `NOT_STARTED`。
- **OWNER_APPROVAL** — `NOT_GRANTED`。
- **AUTHORIZATION** — `NOT_AUTHORIZED`。
- **DISPATCH** — `NOT_AUTHORIZED`。
- **Goal** — 完成網站、資料、Evidence Prompt、GitHub 與啟動流程的整體驗收。
- **Input** — M0 至 M4 的驗收紀錄、GitHub `main`、授權的本地資料及執行環境。
- **Deliverables** — 啟動與驗證說明、端到端驗收紀錄、可追溯的 GitHub 交付版本及已知問題紀錄。
- **Responsible Brain** — STUDENT-MAIN Brain。
- **Acceptance Criteria** — 可從已識別的 GitHub `main` Commit 依說明啟動，並走完載入 FD001、選取 Engine Unit／Cycle／Sensor、核對趨勢及複製 Evidence Prompt 的流程。遠端版本、資料來源及驗收結果可追溯。
- **STOP_IF** — 無法重現啟動、遠端 Commit 無法驗證、端到端結果不符來源，或交付需要未取得的授權。
- **Next Role** — STUDENT-MAIN Brain 記錄最終驗收並將成果交給 STUDENT。
