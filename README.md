# WPPS 雨量預報歷次報次比對

自動擷取中央氣象署「颱風警報/大規模豪雨期間」的雨量預報資料，
比對每一報跟上一報（含同一報被事後修改時效區間）的差異，並附上
各縣市雨量觀測最大值作為實測參考，產生成一份靜態網頁。

## 資料來源

| 項目 | 網址 |
|---|---|
| 總雨量預測 / 24小時雨量預測 | `https://www.cwa.gov.tw/Data/js/typhoon/WPPS-Data.js` |
| 各縣市雨量最大值（6個累積時段） | `https://www.cwa.gov.tw/V8/C/P/Rainfall/MOD/CountyMax_{0~5}.html` |

這兩支都是氣象署官方網頁前端載入用的公開資源，不需要 API 金鑰。

## 架構

```
排程觸發（GitHub Actions，每10分鐘）
    → scripts/run_all.py
        → fetch_wpps.py       抓總雨量/24h雨量預測，跟上一筆快照比對，有變化才存新快照
        → fetch_countymax.py  抓6個時段的縣市雨量最大值，每次都存一筆快照
        → build_page.py       讀取全部快照，重新產生 docs/index.html
    → git commit + push（有變化才commit）
    → GitHub Pages 自動部署 docs/ 底下的內容
```

## 首次部署步驟

1. 建立一個新的 **public** GitHub repo，把這個資料夾整個推上去
2. 到 repo 的 **Settings → Pages**，Source 選擇 `Deploy from a branch`，
   Branch 選 `main`，資料夾選 `/docs`，儲存
3. 到 **Settings → Actions → General**，確認 Workflow permissions 是
   `Read and write permissions`（要能讓排程 commit 資料回 repo）
4. 到 **Actions** 分頁，找到「雨量預報排程抓取」這個 workflow，
   手動按一次 `Run workflow` 測試（不用等排程時間到）
5. 幾分鐘後到 repo 的 Pages 網址（`https://你的帳號.github.io/repo名稱/`）
   確認網頁有正確顯示

## 已知限制 / 之後要注意的事

- **GitHub 免費排程不保證準時**：`schedule` 觸發在系統忙碌時可能延遲
  數分鐘到十幾分鐘，不是保證剛好10分鐘一次，這是 GitHub Actions
  的平台限制，無法完全避免。
- **排程超過60天沒有任何 commit 會被 GitHub 自動停用**：如果一整個
  颱風季都沒有事件發生、repo 完全沒有變化，60天後 schedule 會自動
  關閉，要回到 Actions 分頁手動重新啟用（或隨便 commit 一次喚醒）。
  這點之後要留意，最好排一個提醒。
- **CountyMax_X.html 需要正確的請求標頭**（Referer / X-Requested-With）
  才抓得到內容，這點已經在 `config.py` 的 `COUNTYMAX_HEADERS` 處理好，
  但如果氣象署未來調整防護機制，這裡可能要跟著調整。
- **尚未實作**：把「總雨量預測時效」自動對應到「該抓幾日累積實測值」
  的邏輯（目前網頁是把6個時段全部列出來，由人工自己對照，還沒有
  自動判斷「事件開始到現在過了幾天、該看哪一欄」）。

## 之後移交團隊 GitHub

目前先在個人帳號下運作、確認穩定後，可以直接把整個 repo transfer 到
團隊的 GitHub organization 下（GitHub 有內建 `Transfer ownership` 功能，
會保留完整的 commit 歷史、Actions 排程設定，網址會變成
`https://團隊帳號.github.io/repo名稱/`，需要重新在 Pages 設定裡確認一次）。
