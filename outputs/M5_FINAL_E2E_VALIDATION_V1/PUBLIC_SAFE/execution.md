# 執行紀錄

## DIRECTLY_EXECUTED

| 元件 | 實際版本 |
| --- | --- |
| Python | 3.13.9 |
| Flask / Werkzeug | 3.1.2 / 3.1.3 |
| jsonschema / NumPy | 4.25.0 / 2.3.5 |
| Node.js | 24.19.0 |
| Playwright Core / Microsoft Edge | 1.65.1 / 158.0.4370.33 |

從專案根目錄啟動 Backend `python -B web/fd001/backend/api.py --port 8765` 及 Frontend `node web/fd001/frontend/serve.mjs`。本次以既有 Anaconda Python 執行前者。兩服務均限 IPv4 loopback。另以空來源啟動隔離 Backend 8767，並以 8768 的隔離 Frontend 代理，驗證 real fail-closed HTTP 503。未移動或改寫任何來源資料。

| HTTP 查核 | 結果 |
| --- | --- |
| `127.0.0.1:8765` 的 Health、Catalog、Train / Test Units 與兩個指定 History 查詢 | 200 |
| `http://127.0.0.1:8766/` | 200，Edge 實際開啟及操作 |
| 隔離 Backend 8767 及透過 Frontend 8768 的 Health | 503，瀏覽器顯示 `SOURCE_NOT_VERIFIED` |

| 測試 | 結果 | 程序 exit code |
| --- | --- | --- |
| `FD001_TEST_PORT=8765`，`python -B web/fd001/tests/test_api.py` | 20/20 | 0 |
| `node --test web/fd001/frontend_tests/model.test.mjs` | 4/4 | 0 |
| `node --test web/fd001/frontend_tests/prompt.test.mjs` | 6/6 | 0 |
| 既有 Edge UAT Runner 的私有副本，設定 `FD001_NEGATIVE_ORIGIN=http://127.0.0.1:8768` | 15 個 OK 訊息，0 個未捕捉 JavaScript 例外 | 0 |

Edge Runner 由原始已受驗腳本複製，僅轉接模組路徑與輸出目的地。截圖、JSON 和測試日誌寫入 Git 忽略目錄。Edge 由測試腳本在 finally 關閉。四個本次新啟動的服務均按程序物件停止，Windows 回報服務程序 exit code `-1`。後續查核確認四個 loopback 埠皆已關閉。手動操作時可在各服務終端按 Ctrl+C。
