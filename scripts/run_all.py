# -*- coding: utf-8 -*-
"""排程進入點：一次跑完 抓WPPS -> 抓縣市雨量最大值 -> 重新產生網頁"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_wpps
import fetch_countymax
import build_page


def main():
    print("=== 抓取 WPPS 雨量預報 ===")
    r1 = fetch_wpps.fetch_and_store()
    print(json.dumps(r1, ensure_ascii=False, indent=2))

    print("=== 抓取縣市雨量最大值 ===")
    r2 = fetch_countymax.fetch_and_store()
    print(json.dumps(r2, ensure_ascii=False, indent=2))

    print("=== 重新產生網頁 ===")
    out = build_page.build()
    print(f"已產生：{out}")


if __name__ == "__main__":
    main()
