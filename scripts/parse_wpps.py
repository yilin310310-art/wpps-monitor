# -*- coding: utf-8 -*-
"""
解析 WPPS-Data.js 的內容。

這支檔案格式是：
    WPPS_HTM.FcstAllPrecipTable = ''+
        '<html片段第一段>'+
        '<html片段第二段>'+
        ...;
用 JS 字串串接組出一段 HTML，塞進對應的表格頁籤。
我們要做的是：
  1. 從整份 .js 文字裡，把 FcstAllPrecipTable / Fcst24hPrecipTable
     兩段真正被賦值的內容取出來（用正則抓所有 '...' 片段再串接）
  2. 用 BeautifulSoup 把串好的 HTML 解析成表格資料
"""
import re
from bs4 import BeautifulSoup


def _extract_assigned_html(js_text: str, varname: str) -> str:
    """
    抓出 `WPPS_HTM.<varname> = ''+ '...' + '...' + ...;` 這段組合出的完整 HTML。
    注意：檔案開頭有 `'FcstAllPrecipTable':''` 這種物件初始化，不是我們要的，
    所以只找 `WPPS_HTM.<varname> = ''+` 這個明確賦值語法。
    """
    # 注意：不能單純找第一個 ";" 當結尾，因為內容裡的 HTML 實體（例如 &lt;）
    # 本身就帶分號，會讓非貪婪比對提早截斷。改成找「引號緊接分號」(';)
    # 這個只有 JS 語句真正結尾才會出現的組合。
    pattern = re.compile(
        r"WPPS_HTM\." + re.escape(varname) + r"\s*=\s*''\s*\+(.*?)';",
        re.S,
    )
    m = pattern.search(js_text)
    if not m:
        return ""
    # 結尾的 "';" 只留下了分號當終止符，把被截掉的最後一個引號補回來，
    # 否則最後一段字串會因為找不到配對的收尾引號而被漏掉。
    block = m.group(1) + "'"
    # 抓出所有用單引號包起來的字串片段（處理內部的跳脫字元 \' \" ）
    parts = re.findall(r"'((?:\\.|[^'\\])*)'", block)
    html = "".join(parts)
    html = html.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
    return html


def _parse_precip_table(html: str, area_header_id: str):
    """
    共用的表格解析：從一段 HTML 片段中抓出
      - 事件名稱 / 發布時間
      - 表頭裡的時效說明文字（總雨量表：自X月X日X時至X月X日X時止；
        24小時表：有效時間：X月X日X時至X月X日X時）
      - 預定下次發布時間
      - 各分區 平地/山區 數值
    """
    soup = BeautifulSoup(html, "lxml")

    h3 = soup.find("h3")
    event_name = ""
    publish_time = ""
    if h3:
        notes = h3.find("span", class_="notes")
        if notes:
            publish_time = notes.get_text(strip=True)
            notes.extract()  # 拿掉後剩下的就是事件名稱
        event_name = h3.get_text(strip=True)

    # 表頭裡帶時效說明的那個 <th>（總雨量表 id 是 PrecAll，24h表是 Prec24h）
    period_text = ""
    header_th = soup.find("th", id=area_header_id)
    if header_th:
        full_text = header_th.get_text(separator=" ", strip=True)
        # 總雨量表格式：「...自08月23日00時 至8月25日24時止」
        # 24小時表格式：「...有效時間： 08月23日14時至08月24日14時」
        m = re.search(r"自.*?止", full_text)
        if not m:
            m = re.search(r"有效時間：\s*(.+)", full_text)
            period_text = m.group(1).strip() if m else full_text
        else:
            period_text = m.group(0).replace(" ", "")

    next_publish = ""
    for li in soup.find_all("li"):
        t = li.get_text(strip=True)
        if "預定下次發布時間" in t:
            next_publish = t.replace("預定下次發布時間：", "").strip()
            break

    areas = {}
    table = soup.find("table")
    if table:
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else []
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            area = tds[0].get_text(strip=True)
            plain = tds[1].get_text(strip=True)
            mountain = tds[2].get_text(strip=True)
            areas[area] = {"平地": plain, "山區": mountain}

    return {
        "event_name": event_name,
        "publish_time": publish_time,
        "period": period_text,
        "next_publish": next_publish,
        "areas": areas,
    }


def parse_wpps_js(js_text: str) -> dict:
    """回傳完整結構化結果"""
    m = re.search(r"//\s*Update:\s*(.+)", js_text)
    js_update_time = m.group(1).strip() if m else ""

    all_html = _extract_assigned_html(js_text, "FcstAllPrecipTable")
    h24_html = _extract_assigned_html(js_text, "Fcst24hPrecipTable")

    result = {
        "js_update_time": js_update_time,
        "all_precip": _parse_precip_table(all_html, "PrecAll") if all_html else None,
        "precip_24h": _parse_precip_table(h24_html, "Prec24h") if h24_html else None,
    }
    return result


if __name__ == "__main__":
    import sys
    import json

    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()
    print(json.dumps(parse_wpps_js(text), ensure_ascii=False, indent=2))
