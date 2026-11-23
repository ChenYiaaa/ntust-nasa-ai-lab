# NTUST_SYNTHETIC_AGENT_LAB Decision Log

以下決策依 `WO-M0-001` 記錄。調整已生效的決策時，應記錄新的 Decision ID、核准依據、適用範圍及被取代的決策。

| Decision ID | Decision | Rationale | Scope | Status |
| --- | --- | --- | --- | --- |
| D-001 | STUDENT 為最終授權者。 | 明確界定 Roadmap、重大決策及階段轉換的核准權。 | 所有 Milestone 與重大範圍變更。 | ACTIVE |
| D-002 | MAIN Brain 負責 Roadmap、跨 Brain 協調及最終驗收。 | 由單一負責角色維護整體順序與驗收一致性。 | 專案 Roadmap、跨 Brain 介面及整體驗收。 | ACTIVE |
| D-003 | RESEARCH Brain 獨立管理 RESEARCH Own Worker，先驗收再回報 MAIN Brain。 | 保留研究指派與證據驗證的責任鏈。 | 研究工作派發、驗收與回報。 | ACTIVE |
| D-004 | 所有 Worker 必須依 `BOUNDED_WORK_ORDER` 執行。 | 使授權、輸出與停止條件可核對。 | MAIN 與 RESEARCH 的所有 Worker 工作。 | ACTIVE |
| D-005 | 採單一 `main` 分支與循序開發。 | 讓派工與驗收依同一條正式歷史進行。 | GitHub 正式歷史、派工順序及階段交接。 | ACTIVE |
| D-006 | 每次派工前，Brain 必須讀取 GitHub `main` 最新 `AGENTS.md`。首次建立該檔的一次性例外限 `WO-M0-001`。 | 以遠端正式版本派工，並允許初版建立。 | Brain 派工、Worker 遵循及 M0 初始治理。 | ACTIVE |
| D-007 | Worker 必須 Commit、Push。Brain 必須從 GitHub 讀取實際成果後才可 `PASS`。 | 讓提交證據及驗收結果能獨立驗證。 | 所有交付物、Worker 回傳及 Brain 驗收。 | ACTIVE |
| D-008 | 前一項工作完成驗收且取得 MAIN 授權後，才能啟動下一項 Worker 工作。 | 避免後續工作依賴尚未驗收的交付物。 | Worker 工作排序與 Milestone 交接。 | ACTIVE |
| D-009 | GitHub 無法存取或驗證時必須回報 `BLOCKED`。 | 避免以無法核對的資料宣告完成或驗收。 | GitHub 派工依據、發布及遠端驗證。 | ACTIVE |
| D-010 | M0 僅授權治理初始化。M1 至 M5 保持 `NOT_STARTED`，直到各階段另獲授權。 | 將治理建立與研究、開發及交付的授權分開。 | `WO-M0-001` 與 M0 至 M5 的階段轉換。 | ACTIVE |
