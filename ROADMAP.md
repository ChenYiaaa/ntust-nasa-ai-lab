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

- **Status** — `AUTHORIZED_NOT_STARTED`。STUDENT 已授權 `M1_DATASET_PROFILE_6CSV_V1`，RESEARCH Own Worker 尚未開始執行。
- **Goal** — 由 RESEARCH Brain 協調自己的 Worker，對六筆合成 CSV 資料建立可驗證的 Dataset Profile。
- **Input** — 已知檔名 `synthetic_sensor.csv`、經授權的資料位置與六筆資料的來源或辨識方式。六筆的分布須依盤點證據判定，禁止假定有六個既存獨立檔案。
- **Deliverables** — Dataset Profile、資料盤點、可重現的處理方式與實際執行證據。
- **Responsible Brain** — RESEARCH Brain。
- **Acceptance Criteria** — 每筆資料可追溯至實際來源。Profile 的 shape、columns、dtype、missing、duplicates 及 statistics 均有真實證據，且盤點清楚說明六筆資料的涵蓋方式。RESEARCH Brain 驗收後回報 MAIN Brain。
- **STOP_IF** — 尚未授權、資料來源不可讀、無法用實際證據確認六筆的範圍，或無法重現任何必要欄位或統計。保留現有證據並回報缺口。
- **Next Role** — RESEARCH Brain 驗收後回報 STUDENT-MAIN Brain，由 STUDENT 核准是否進入 M2。

## M2 — NASA C-MAPSS FD001 DATA INTEGRATION

- **Status** — `NOT_STARTED`。
- **Goal** — 接入學生本地 NASA C-MAPSS FD001 真實資料，建立 Engine Unit、Cycle、Sensor 索引與來源追溯。
- **Input** — 學生授權的本地 FD001 檔案、資料規格與 M1 驗收紀錄。
- **Deliverables** — 可重現的 FD001 資料讀取方式、欄位與索引對照、來源清單及抽樣驗證證據。
- **Responsible Brain** — RESEARCH Brain。
- **Acceptance Criteria** — 可依 Engine Unit、Cycle 與 Sensor 找到對應讀值。以本地資料抽樣比對讀值、欄位映射及資料分組，並記錄來源與驗證方式。
- **STOP_IF** — 檔案或資料規格無法確認、索引或讀值與來源不一致，或作業涉及未授權的資料修改或發布。
- **Next Role** — RESEARCH Brain 驗收後回報 STUDENT-MAIN Brain，由 MAIN Brain 於核准後派發 M3。

## M3 — HEALTH ANALYSIS WEBSITE MVP

- **Status** — `NOT_STARTED`。
- **Goal** — 建立網站，讓使用者選擇 Engine Unit、Cycle 與 Sensor，查看真實感測器趨勢及資料來源。
- **Input** — M2 已驗收的 FD001 介面、欄位索引、資料來源紀錄及授權的網站工作範圍。
- **Deliverables** — 可啟動的網站 MVP、選取介面、感測器趨勢、來源呈現與操作驗證證據。
- **Responsible Brain** — STUDENT-MAIN Brain。
- **Acceptance Criteria** — 使用者可完成三項選取，趨勢、範圍與來源隨選取更新。抽樣結果可與 FD001 原始讀值核對，空結果與無效選取會提供明確回饋。
- **STOP_IF** — M2 未驗收、真實資料無法查詢、選取結果與來源不一致，或須傳輸未授權資料。
- **Next Role** — STUDENT-MAIN Brain 驗收並取得 STUDENT 核准後，派發 M4。

## M4 — EVIDENCE PROMPT GENERATION

- **Status** — `NOT_STARTED`。
- **Goal** — 根據網站選取條件與真實資料產生可複製、可追溯的 Evidence Prompt。
- **Input** — M3 已驗收的選取與查詢介面、M2 的來源資訊及授權的 Prompt 格式。
- **Deliverables** — Evidence Prompt 產生與複製功能、輸出範例及原始資料比對證據。
- **Responsible Brain** — STUDENT-MAIN Brain。
- **Acceptance Criteria** — Prompt 可複製，能追溯到選定的 Engine Unit、Cycle、Sensor 與資料來源，所引用的讀值及統計可由同一輸入重現。空結果需有明確行為。
- **STOP_IF** — Prompt 與網站選取、實際讀值或來源不一致，來源缺漏，或輸出含未授權的資訊。
- **Next Role** — STUDENT-MAIN Brain 驗收並取得 STUDENT 核准後，派發 M5。

## M5 — END-TO-END VALIDATION AND DELIVERY

- **Status** — `NOT_STARTED`。
- **Goal** — 完成網站、資料、Evidence Prompt、GitHub 與啟動流程的整體驗收。
- **Input** — M0 至 M4 的驗收紀錄、GitHub `main`、授權的本地資料及執行環境。
- **Deliverables** — 啟動與驗證說明、端到端驗收紀錄、可追溯的 GitHub 交付版本及已知問題紀錄。
- **Responsible Brain** — STUDENT-MAIN Brain。
- **Acceptance Criteria** — 可從已識別的 GitHub `main` Commit 依說明啟動，並走完載入 FD001、選取 Engine Unit／Cycle／Sensor、核對趨勢及複製 Evidence Prompt 的流程。遠端版本、資料來源及驗收結果可追溯。
- **STOP_IF** — 無法重現啟動、遠端 Commit 無法驗證、端到端結果不符來源，或交付需要未取得的授權。
- **Next Role** — STUDENT-MAIN Brain 記錄最終驗收並將成果交給 STUDENT。
