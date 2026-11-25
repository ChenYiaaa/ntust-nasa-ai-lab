# FD001 最終交付與重現

## 固定版本與元件

使用 [已驗證的固定 GitHub Commit](https://github.com/ChenYiaaa/ntust-nasa-ai-lab/commit/ec5bb7b06235b28d4a3387681127575f55abdd57) `ec5bb7b06235b28d4a3387681127575f55abdd57`。FD001 Data Contract `1.0.0`、Flask 唯讀 API、Node 同來源代理、互動式網站及九段式 Evidence Prompt 構成此版本。剪貼簿複製在本機瀏覽器內完成。

| 交付基準 | Commit |
| --- | --- |
| M3 API | `c50495ca02814018c8f4c30ae5285c48cf9f2a99` |
| M3 Frontend | `e133b92786be350eef13dff82f4ad14b90d941f0` |
| M4 實作 | `42a36bb73793a691c8d6a463ab6b697de4f7e468` |
| M5 Prompt 強化及本次驗證基準 | `ec5bb7b06235b28d4a3387681127575f55abdd57` |

## 啟動與操作

在已授權的本地工作區備妥三份 FD001 TXT，以 SHA-256 比對契約固定值。版本、依賴及核對方式見 [execution.md](execution.md) 與 [verification.md](verification.md)。受驗的環境使用 Python 3.13.9、Node.js 24.19.0、Flask 3.1.2 與 Windows Edge。依 [API 環境說明](../../../web/fd001/docs/API.md) 備妥依賴。

從專案根目錄在兩個終端機分別執行。

```powershell
python -B web/fd001/backend/api.py --port 8765
node web/fd001/frontend/serve.mjs
```

- **API** — 已驗證 `http://127.0.0.1:8765`，唯讀 GET 端點為 `/api/health`、`/api/catalog`、`/api/units`、`/api/history`。
- **網站** — 已驗證 `http://127.0.0.1:8766/`。開啟網站，選取分割、Unit 和 Sensor，輸入 Cycle 範圍，再按 **Query history**。查閱趨勢圖、統計與 **Source records**。
- **Evidence Prompt** — 按 **Generate evidence prompt**，核對預覽的觀測值、來源、統計與限制，然後按 **Copy prompt**。可將內容貼入本地編輯器與 Preview 核對。瀏覽器須允許 localhost 的剪貼簿操作。

## 重現測試與證據

保持正向兩服務啟動，從根目錄執行下列三項。

```powershell
$env:FD001_TEST_PORT = '8765'
python -B web/fd001/tests/test_api.py
node --test web/fd001/frontend_tests/model.test.mjs
node --test web/fd001/frontend_tests/prompt.test.mjs
```

依 [Frontend 驗證說明](../../../web/fd001/frontend/README.md#verification) 備妥 Playwright Core、Edge 和隔離 503 環境。在需保留受驗檔案的工作區，將已受驗 Browser Runner 複製至 `web/fd001/frontend_tests/local_only/` 下的新子目錄。副本將匯入指向上一層的 `node_modules/playwright-core/index.mjs`，並將 screenshot URL 與 privateDir 指向副本目錄。從根目錄執行該副本，保持正向服務運作，並設定 `FD001_NEGATIVE_ORIGIN=http://127.0.0.1:8768`。測試結果中的逐筆內容留在 Git 忽略目錄。核對方法與安全摘要見 [verification.md](verification.md) 及 [browser-uat.md](browser-uat.md)。

## 限制、已知問題與關閉

Browser UAT 涵蓋 Windows Edge 桌面及 375 px 窄視窗。剪貼簿權限由瀏覽器控制，讀回可能採用 Windows CRLF。原始檔改變後須重啟服務以重新驗證固定來源。公開文件只包含驗證方法與摘要，重新執行需要已授權的私人來源。既有非阻塞候選事項 `README_STATIC_ASSET_COUNT_STALE` 仍保留於治理紀錄。

在各服務終端按 Ctrl+C 關閉 Backend 與 Frontend。若建立隔離 503 環境，同樣關閉隔離服務並確認原先使用的本機埠已停止監聽。最終交付驗收由 STUDENT-MAIN Brain 執行。
