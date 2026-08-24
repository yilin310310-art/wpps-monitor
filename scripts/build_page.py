# -*- coding: utf-8 -*-
"""
讀取 data/wpps/ 底下所有事件的所有快照，以及 data/countymax/latest.json，
產生一份 docs/index.html 靜態網頁。

呈現邏輯（依需求調整版）：
  - 每個事件依「總雨量預測時效區間文字」分成多個區塊(block)：
      時效沒變 -> 沿用同一區塊，往右加報次欄
      時效變了(氣象署改了預測起訖日期) -> 開一個新區塊，放在最右邊，
      之後新報次都加進這個最新區塊
  - 每個區塊獨立呈現：分區欄 + 該區塊所有報次(各拆平地/山區) + 一欄觀測雨量
  - 舊區塊不會再有新報次，但觀測雨量會持續更新，直到該區塊自己的時效
    結束時間到了為止，之後凍結（存成 _frozen_observed.json，不再跟著即時資料變動）
  - 跟前一報同一格比較：數值上修＝紅字，下修＝藍字，相同＝黑字
  - 24小時雨量預測持續存檔但不顯示於本頁
  - 提供「下載完整圖片」按鈕，用html2canvas把整個頁面轉成PNG下載
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import WPPS_DATA_DIR, COUNTYMAX_DATA_DIR, DOCS_DIR, EXPECTED_AREAS

TW_TZ = timezone(timedelta(hours=8))
DURATION_ORDER = ["本日累積", "2日累積", "3日累積", "4日累積", "5日累積"]


def _load_event_snapshots(event_dir: str):
    files = sorted(f for f in glob.glob(os.path.join(event_dir, "*.json"))
                    if not os.path.basename(f).startswith("_"))
    snapshots = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            snapshots.append(json.load(f))
    return snapshots


def _report_header_class(snap):
    ct = snap.get("change_type", "")
    if ct == "new_report":
        return "hdr-new"
    if ct == "same_report_modified":
        return "hdr-modified"
    return "hdr-first"


def _parse_num_range(text):
    """把 '80 - 150' /
