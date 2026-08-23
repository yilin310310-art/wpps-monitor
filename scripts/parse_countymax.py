# -*- coding: utf-8 -*-
"""解析 CountyMax_X.html 這種縣市雨量最大值 HTML 片段

真實結構範例：
  <tr data-updatetime='2026/08/23 11:56:47' data-timefrom='2026/08/23 10:40' data-timeto='2026/08/23 11:40'>
    <th scope="row"><a href="..." title="基隆市">基隆市</a></th>
    <td class="is_show"><span class='rain-level-1'>0.5</span></td>
    <td class="is_show">C0B05</td>
    <td class="is_show">八斗子</td>
    <td style='text-align:left;'>基隆市中正區漁港1街9號(八斗子安檢所樓頂)</td>
  </tr>
縣市名稱在 <th> 不是 <td>；同縣市多測站用同一個儲存格裡 <BR> 分隔，不是多個 <tr>。
"""
from bs4 import BeautifulSoup


def parse_countymax_html(html: str) -> dict:
    """
    回傳 {
      "period": {"updatetime":.., "timefrom":.., "timeto":..},  # 取自第一列的 data-* 屬性
      "counties": {
        縣市名稱: {"rain": "0.5" 或 None(代表'-'無資料),
                  "stations": [{"id":..,"name":..,"location":..}, ...]}
      }
    }
    """
    soup = BeautifulSoup(html, "lxml")
    counties = {}
    period = {}

    rows = soup.find_all("tr")
    if rows:
        first = rows[0]
        period = {
            "updatetime": first.get("data-updatetime", ""),
            "timefrom": first.get("data-timefrom", ""),
            "timeto": first.get("data-timeto", ""),
        }

    for tr in rows:
        th = tr.find("th")
        if not th:
            continue
        county_link = th.find("a")
        county = (county_link.get("title") or county_link.get_text(strip=True)
                  if county_link else th.get_text(strip=True))
        if not county:
            continue

        tds = tr.find_all("td")
        if len(tds) < 4:
            continue

        rain_text = tds[0].get_text(strip=True)
        rain = None if rain_text in ("-", "", "--") else rain_text

        def split_cell(td):
            # <BR> 會被 BeautifulSoup 轉成換行，用這個切開多測站
            return [s.strip() for s in td.get_text(separator="\n").split("\n") if s.strip()]

        ids = split_cell(tds[1])
        names = split_cell(tds[2])
        locs = split_cell(tds[3])

        stations = []
        for i in range(max(len(ids), len(names), len(locs))):
            sid = ids[i] if i < len(ids) else ""
            if sid == "-":
                continue
            stations.append({
                "id": sid,
                "name": names[i] if i < len(names) else "",
                "location": locs[i] if i < len(locs) else "",
            })

        counties[county] = {"rain": rain, "stations": stations}

    return {"period": period, "counties": counties}


if __name__ == "__main__":
    import sys
    import json

    with open(sys.argv[1], encoding="utf-8") as f:
        html = f.read()
    print(json.dumps(parse_countymax_html(html), ensure_ascii=False, indent=2))
