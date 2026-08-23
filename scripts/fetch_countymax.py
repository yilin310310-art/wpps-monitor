# -*- coding: utf-8 -*-
"""
排程主程式：抓 CountyMax_0.html ~ CountyMax_5.html（最近1小時~5日累積），
每次都存一筆快照（這份資料量小、且本來就是持續變動的觀測資料，
不像預報文字那樣需要判斷「有沒有變化才存」，直接每次存一筆時間序列即可）。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    COUNTYMAX_URL_TMPL, COUNTYMAX_HEADERS, COUNTYMAX_DATA_DIR, COUNTYMAX_LABELS,
)
from parse_countymax import parse_countymax_html

TW_TZ = timezone(timedelta(hours=8))


def _now_str():
    return datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S")


def fetch_and_store() -> dict:
    os.makedirs(COUNTYMAX_DATA_DIR, exist_ok=True)
    now = datetime.now(TW_TZ)
    fname = now.strftime("%Y%m%d_%H%M%S") + ".json"

    all_durations = {}
    errors = {}
    raw_html_debug = {}
    for n, label in COUNTYMAX_LABELS.items():
        url = COUNTYMAX_URL_TMPL.format(n=n) + f"?_={int(now.timestamp() * 1000)}"
        try:
            resp = requests.get(url, headers=COUNTYMAX_HEADERS, timeout=20)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            all_durations[label] = parse_countymax_html(resp.text)
            raw_html_debug[label] = resp.text
        except Exception as e:  # noqa: BLE001 - 排程腳本，單一時段失敗不該中斷整支程式
            errors[label] = str(e)

    # 除錯用：暫時把「最近1小時」這個時段的原始HTML也存下來，方便確認表格真實結構
    # （解析邏輯確認沒問題後，這段可以拿掉）
    debug_dir = os.path.join(COUNTYMAX_DATA_DIR, "raw_debug")
    os.makedirs(debug_dir, exist_ok=True)
    if "最近1小時" in raw_html_debug:
        with open(os.path.join(debug_dir, "countymax_0_raw.html"), "w", encoding="utf-8") as f:
            f.write(raw_html_debug["最近1小時"])

    snapshot = {
        "fetched_at": _now_str(),
        "durations": all_durations,
        "errors": errors,
    }

    path = os.path.join(COUNTYMAX_DATA_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # 額外存一份 latest.json 方便網頁固定路徑讀取「目前最新」
    latest_path = os.path.join(COUNTYMAX_DATA_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    return {"path": path, "durations_ok": list(all_durations.keys()), "errors": errors}


if __name__ == "__main__":
    r = fetch_and_store()
    print(json.dumps(r, ensure_ascii=False, indent=2))
