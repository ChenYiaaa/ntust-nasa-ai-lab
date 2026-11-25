# 真實瀏覽器驗證

`DIRECTLY_EXECUTED`。使用已安裝的 Windows Microsoft Edge 158.0.4370.33，透過 Playwright Core 1.65.1 的 Edge channel 以 headless 模式實際操作本機網站。桌面初始視窗寬 1240 px，窄視窗寬 375 px。

| 檢查 | 本次結果 |
| --- | --- |
| 開啟網站並選取 Train／Test、Engine Unit、Sensor、Cycle Range | 選單、查詢與後端資料一致 |
| Train 20 筆、Test 3 筆及單點案例 | 實際 canvas 標記、Source Records、資料品質統計及 provenance 通過查核 |
| 九段式 Evidence Prompt | 九段順序、Sensor 定義、真實讀值、定位、統計、選取與證據分級通過查核 |
| 實際 Copy Prompt 與 Clipboard Readback | 點擊按鈕並透過瀏覽器剪貼簿 API 讀回，與 Preview 相符，允許 Windows 原生 CRLF 轉換 |
| 變更選取、過期回應與失效證據 | 舊 Prompt 清除。過期回應、缺少來源定位或不一致 Catalog 無法產生合格 Prompt |
| 錯誤與空結果 | 驗證受控 HTTP 錯誤、網路失敗、空狀態，及隔離實際 503 經代理後的錯誤畫面 |
| 375 px 與鍵盤 | 查詢畫面寬度符合視窗，驗證 Tab 與方向鍵操作選取器 |

Runner exit code 為 0。0 個未捕捉 JavaScript 例外，17 個資源錯誤訊息來自預期的錯誤路徑或 favicon。剪貼簿權限只授予本機測試來源。完整結果及剪貼簿相關內容保留於 Git 忽略的私有執行證據，公開交付採文字摘要。

`NOT_VERIFIED`。其他瀏覽器、作業系統及不同剪貼簿權限政策超出本次涵蓋範圍。
