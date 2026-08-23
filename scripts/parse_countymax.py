# -*- coding: utf-8 -*-
"""解析 CountyMax_X.html 這種縣市雨量最大值 HTML 片段"""
from bs4 import BeautifulSoup


def parse_countymax_html(html: str) -> dict:
    """
    回傳 {縣市名稱: {"rain": "134.0" 或 None(代表'-'無資料),
                    "stations": [{"id":..,"name":..,"location":..}, ...]}}
    一個縣市可能對應多個測站（同雨量值時會列出多筆並列測站），我們把它們都留著，
    但比對時只需要看 rain 這個數值。
    """
    soup = BeautifulSoup(html, "lxml")
    result = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        county_link = tds[0].find("a")
        county = (county_link.get_text(strip=True) if county_link
                  else tds[0].get_text(strip=True))
        if not county:
            continue
        rain_text = tds[1].get_text(strip=True)
        rain = None if rain_text in ("-", "", "--") else rain_text

        stations = []
        if len(tds) >= 5:
            ids = [s.strip() for s in tds[2].get_text(separator="\n").split("\n") if s.strip()]
            names = [s.strip() for s in tds[3].get_text(separator="\n").split("\n") if s.strip()]
            locs = [s.strip() for s in tds[4].get_text(separator="\n").split("\n") if s.strip()]
            for i in range(max(len(ids), len(names), len(locs))):
                stations.append({
                    "id": ids[i] if i < len(ids) else "",
                    "name": names[i] if i < len(names) else "",
                    "location": locs[i] if i < len(locs) else "",
                })

        result[county] = {"rain": rain, "stations": stations}
    return result


if __name__ == "__main__":
    import sys
    import json

    with open(sys.argv[1], encoding="utf-8") as f:
        html = f.read()
    print(json.dumps(parse_countymax_html(html), ensure_ascii=False, indent=2))
