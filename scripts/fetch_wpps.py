# -*- coding: utf-8 -*-
"""
排程主程式：抓 WPPS-Data.js，解析後跟上一筆快照比對，
有變化才寫入新快照檔案。
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import WPPS_DATA_URL, WPPS_HEADERS, WPPS_DATA_DIR
from parse_wpps import parse_wpps_js

TW_TZ = timezone(timedelta(hours=8))


def _now_str():
    return datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _event_slug(event_name: str) -> str:
    """把事件名稱轉成可以當資料夾名稱的字串"""
    keep = "".join(c for c in event_name if c.isalnum() or c in "-_一二三四五六七八九十")
    return keep[:60] if keep else "unknown_event"


def _latest_snapshot_path(event_dir: str):
    if not os.path.isdir(event_dir):
        return None
    files = sorted(f for f in os.listdir(event_dir) if f.endswith(".json"))
    return os.path.join(event_dir, files[-1]) if files else None


def _snapshots_differ(old: dict, new: dict) -> bool:
    """比較兩筆快照的「內容」是否不同（忽略 fetched_at 這種每次都會變的欄位）"""
    def strip(d):
        return {"js_update_time": d.get("js_update_time"),
                "all_precip": d.get("all_precip"),
                "precip_24h": d.get("precip_24h")}
    return strip(old) != strip(new)


def _classify_change(old: dict, new: dict) -> str:
    """判斷是「新一報」還是「同報修改」"""
    old_pub = (old.get("all_precip") or {}).get("publish_time")
    new_pub = (new.get("all_precip") or {}).get("publish_time")
    if old_pub != new_pub:
        return "new_report"
    return "same_report_modified"


def fetch_and_store() -> dict:
    os.makedirs(WPPS_DATA_DIR, exist_ok=True)  # 確保資料夾存在，避免首次執行時寫檔失敗

    resp = requests.get(WPPS_DATA_URL, headers=WPPS_HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    js_text = resp.text

    parsed = parse_wpps_js(js_text)
    parsed["fetched_at"] = _now_str()

    all_precip = parsed.get("all_precip")
    if not all_precip or not all_precip.get("areas"):
        # 沒有進行中的事件（WPPS-Data.js 內容是空的），不建立事件資料夾，
        # 只更新最後檢查時間，避免產生垃圾資料。
        status_path = os.path.join(WPPS_DATA_DIR, "last_check.json")
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(
                {"last_checked_at": _now_str(), "last_result": {"active_event": False}},
                f, ensure_ascii=False, indent=2,
            )
        return {"active_event": False, "saved": False}

    event_name = all_precip.get("event_name") or "unknown_event"
    event_dir = os.path.join(WPPS_DATA_DIR, _event_slug(event_name))
    os.makedirs(event_dir, exist_ok=True)

    latest_path = _latest_snapshot_path(event_dir)
    change_type = "first_snapshot"
    should_save = True

    if latest_path:
        with open(latest_path, encoding="utf-8") as f:
            old = json.load(f)
        if _snapshots_differ(old, parsed):
            change_type = _classify_change(old, parsed)
        else:
            should_save = False
            change_type = "no_change"

    result = {
        "event_name": event_name,
        "change_type": change_type,
        "saved": should_save,
        "path": None,
    }

    if should_save:
        fname = datetime.now(TW_TZ).strftime("%Y%m%d_%H%M%S_%f") + f"_{change_type}.json"
        path = os.path.join(event_dir, fname)
        parsed["change_type"] = change_type
        with open(path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        result["path"] = path

    # 不管有沒有存新快照，都更新一個「最後檢查時間」紀錄檔，方便網頁顯示資料多新
    status_path = os.path.join(WPPS_DATA_DIR, "last_check.json")
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump({"last_checked_at": _now_str(), "last_result": result},
                   f, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    r = fetch_and_store()
    print(json.dumps(r, ensure_ascii=False, indent=2))
