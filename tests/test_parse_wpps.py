# -*- coding: utf-8 -*-
"""
迴歸測試：用真實抓到的 WPPS-Data.js 樣本（2026/08/23 10:00 正報）驗證解析邏輯。
不需要網路連線，事件結束後也能一直拿這份樣本測試「程式改壞了沒」。

執行方式：
    python -m tests.test_parse_wpps
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from parse_wpps import parse_wpps_js

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "real_wpps_20260823_1000.js")


def run():
    with open(FIXTURE, encoding="utf-8") as f:
        js_text = f.read()

    result = parse_wpps_js(js_text)
    failures = []

    def check(label, actual, expected):
        if actual != expected:
            failures.append(f"[FAIL] {label}: 預期 {expected!r}，實際 {actual!r}")

    check("js_update_time", result["js_update_time"], "2026-08-23 10:40:56")

    all_p = result["all_precip"]
    check("all_precip.event_name", all_p["event_name"],
          "0822低壓帶及西南風豪雨事件各地區總雨量預測")
    check("all_precip.publish_time", all_p["publish_time"],
          "發布時間：115年08月23日10時00分(正報)")
    check("all_precip.period", all_p["period"], "自08月23日00時至8月25日24時止")
    check("all_precip.next_publish", all_p["next_publish"], "115年08月23日13時00分")
    check("all_precip 分區數量", len(all_p["areas"]), 24)
    check("all_precip 高雄市", all_p["areas"]["高雄市"], {"平地": "400 - 600", "山區": "500 - 700"})
    check("all_precip 基隆市（山區無資料）", all_p["areas"]["基隆市"], {"平地": "80 - 150", "山區": "-"})

    h24 = result["precip_24h"]
    check("precip_24h.period", h24["period"], "08月23日14時至08月24日14時")
    check("precip_24h 分區數量", len(h24["areas"]), 24)
    check("precip_24h 基隆市（小於符號）", h24["areas"]["基隆市"], {"平地": "< 80", "山區": "-"})

    if failures:
        print("\n".join(failures))
        print(f"\n{len(failures)} 項測試失敗")
        sys.exit(1)
    else:
        print("全部通過：解析邏輯跟真實資料樣本一致")


if __name__ == "__main__":
    run()
