# -*- coding: utf-8 -*-
"""共用設定"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
WPPS_DATA_DIR = os.path.join(DATA_DIR, "wpps")
COUNTYMAX_DATA_DIR = os.path.join(DATA_DIR, "countymax")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

WPPS_DATA_URL = "https://www.cwa.gov.tw/Data/js/typhoon/WPPS-Data.js"
WPPS_PAGE_URL = "https://www.cwa.gov.tw/V8/C/P/Typhoon/WPPS.html"

# 累積時段對照：0=最近1小時 1=本日累積 2=2日累積 3=3日累積 4=4日累積 5=5日累積
COUNTYMAX_LABELS = {
    0: "最近1小時",
    1: "本日累積",
    2: "2日累積",
    3: "3日累積",
    4: "4日累積",
    5: "5日累積",
}
COUNTYMAX_URL_TMPL = "https://www.cwa.gov.tw/V8/C/P/Rainfall/MOD/CountyMax_{n}.html"
COUNTYMAX_PAGE_URL = "https://www.cwa.gov.tw/V8/C/P/Rainfall/Rainfall_CountyMax.html"

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9",
}

# CountyMax_X.html 是 XHR 局部載入，氣象署後端會檢查這幾個標頭
COUNTYMAX_HEADERS = {
    **COMMON_HEADERS,
    "Referer": COUNTYMAX_PAGE_URL,
    "X-Requested-With": "XMLHttpRequest",
}

WPPS_HEADERS = {
    **COMMON_HEADERS,
    "Referer": WPPS_PAGE_URL,
}

# 台灣所有分區名稱，用來確保表格解析數量正確（總雨量表為24個分區）
EXPECTED_AREAS = [
    "基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣",
    "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "臺南市",
    "高雄市", "屏東縣", "恆春半島", "宜蘭縣", "花蓮縣", "臺東縣",
    "蘭嶼綠島", "連江縣", "金門縣", "澎湖縣",
]

# 縣市雨量最大值頁面用的縣市清單（不含恆春半島/蘭嶼綠島，因為那是氣象分區不是行政區）
COUNTYMAX_COUNTIES = [
    "基隆市", "新北市", "臺北市", "桃園市", "新竹市", "新竹縣", "苗栗縣",
    "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "臺南市",
    "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣",
]
