# -*- coding: utf-8 -*-
"""
迴歸測試：用真實抓到的 CountyMax_0.html 樣本（2026/08/23 11:56 最近1小時）
驗證解析邏輯。不需要網路連線。

執行方式：
    python -m tests.test_parse_countymax
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from parse_countymax import parse_countymax_html

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "real_countymax_0_20260823_1156.html")


def run():
    with open(FIXTURE, encoding="utf-8") as f:
        html = f.read()

    result = parse_countymax_html(html)
    failures = []

    def check(label, actual, expected):
        if actual != expected:
            failures.append(f"[FAIL] {label}: 預期 {expected!r}，實際 {actual!r}")

    check("period.timefrom", result["period"]["timefrom"], "2026/08/23 10:40")
    check("period.timeto", result["period"]["timeto"], "2026/08/23 11:40")

    counties = result["counties"]
    check("縣市數量", len(counties), 5)

    check("基隆市 rain", counties["基隆市"]["rain"], "0.5")
    check("基隆市 測站數", len(counties["基隆市"]["stations"]), 1)
    check("基隆市 測站代碼", counties["基隆市"]["stations"][0]["id"], "C0B05")

    check("新竹市（無資料）rain", counties["新竹市"]["rain"], None)
    check("新竹市（無資料）測站數", len(counties["新竹市"]["stations"]), 0)

    check("桃園市 多測站數", len(counties["桃園市"]["stations"]), 2)
    check("桃園市 第2測站代碼", counties["桃園市"]["stations"][1]["id"], "C0C79")

    check("新竹縣 多測站數(3個)", len(counties["新竹縣"]["stations"]), 3)
    check("新竹縣 第3測站名稱", counties["新竹縣"]["stations"][2]["name"], "石鹿")

    if failures:
        print("\n".join(failures))
        print(f"\n{len(failures)} 項測試失敗")
        sys.exit(1)
    else:
        print("全部通過：縣市雨量最大值解析邏輯跟真實資料樣本一致")


if __name__ == "__main__":
    run()
