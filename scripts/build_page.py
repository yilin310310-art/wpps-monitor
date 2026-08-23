# -*- coding: utf-8 -*-
"""
讀取 data/wpps/ 底下所有事件的所有快照，以及 data/countymax/latest.json，
產生一份 docs/index.html 靜態網頁。

呈現邏輯：
  - 每個事件一個區塊
  - 總雨量預測 / 24小時雨量預測 各一個表格，橫向是「報次」，縱向是「分區」
  - 儲存格跟「前一報」數值不同時標色：
      淺紅 = 這一格數值有變化
      報次標頭本身：新一報用藍底、同報修改用橘底
  - 頁尾附上「目前縣市雨量最大值」（六個時段）當作實測值參考
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import WPPS_DATA_DIR, COUNTYMAX_DATA_DIR, DOCS_DIR, EXPECTED_AREAS

TW_TZ = timezone(timedelta(hours=8))


def _load_event_snapshots(event_dir: str):
    files = sorted(glob.glob(os.path.join(event_dir, "*.json")))
    snapshots = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            snapshots.append(json.load(f))
    return snapshots


def _cell_class(curr, prev, key):
    """回傳這個儲存格要不要標記成「有變化」"""
    if prev is None:
        return ""
    c = (curr or {}).get(key, {})
    p = (prev or {}).get(key, {})
    return "changed" if c != p else ""


def _report_header_class(snap):
    ct = snap.get("change_type", "")
    if ct == "new_report":
        return "hdr-new"
    if ct == "same_report_modified":
        return "hdr-modified"
    return "hdr-first"


def _render_table(snapshots, table_key: str, title: str):
    """table_key: 'all_precip' 或 'precip_24h'"""
    if not snapshots:
        return f"<p>（目前尚無{title}資料）</p>"

    areas = list(EXPECTED_AREAS)
    seen = set(areas)
    for snap in snapshots:
        for a in (snap.get(table_key) or {}).get("areas", {}):
            if a not in seen:
                areas.append(a)
                seen.add(a)

    html = [f"<h3>{title}</h3>", '<div class="table-scroll"><table class="cmp-table">']
    html.append("<thead><tr><th class='sticky-col'>分區</th>")
    for snap in snapshots:
        tbl = snap.get(table_key) or {}
        pub = tbl.get("publish_time", "")
        period = tbl.get("period", "")
        cls = _report_header_class(snap)
        html.append(
            f"<th class='{cls}'>{pub}<br><span class='period'>{period}</span></th>"
        )
    html.append("</tr></thead><tbody>")

    for area in areas:
        html.append(f"<tr><td class='sticky-col'>{area}</td>")
        prev_tbl = None
        for snap in snapshots:
            tbl = snap.get(table_key) or {}
            areas_data = tbl.get("areas", {})
            curr = areas_data.get(area, {"平地": "", "山區": ""})
            prev = (prev_tbl or {}).get(area) if prev_tbl else None
            cls = "changed" if (prev is not None and curr != prev) else ""
            html.append(
                f"<td class='{cls}'>{curr.get('平地','')} / {curr.get('山區','')}</td>"
            )
            prev_tbl = areas_data
        html.append("</tr>")
    html.append("</tbody></table></div>")
    return "\n".join(html)


def _render_countymax():
    latest_path = os.path.join(COUNTYMAX_DATA_DIR, "latest.json")
    if not os.path.exists(latest_path):
        return "<p>（尚無縣市雨量最大值資料）</p>"
    with open(latest_path, encoding="utf-8") as f:
        data = json.load(f)

    durations = data.get("durations", {})
    if not durations:
        return "<p>（尚無縣市雨量最大值資料）</p>"

    labels = list(durations.keys())
    counties = []
    seen = set()
    for lab in labels:
        for c in durations[lab].get("counties", {}):
            if c not in seen:
                counties.append(c)
                seen.add(c)

    html = [f"<p class='muted'>更新時間：{data.get('fetched_at','')}</p>",
            "<div class='table-scroll'><table class='cmp-table'>"]
    html.append("<thead><tr><th class='sticky-col'>縣市</th>")
    for lab in labels:
        tf = durations[lab].get("period", {}).get("timefrom", "")
        tt = durations[lab].get("period", {}).get("timeto", "")
        sub = f"<br><span class='period'>{tf}~{tt}</span>" if tf else ""
        html.append(f"<th>{lab}{sub}</th>")
    html.append("</tr></thead><tbody>")
    for county in counties:
        html.append(f"<tr><td class='sticky-col'>{county}</td>")
        for lab in labels:
            rec = durations[lab].get("counties", {}).get(county, {})
            rain = rec.get("rain")
            html.append(f"<td>{rain if rain is not None else '-'}</td>")
        html.append("</tr>")
    html.append("</tbody></table></div>")
    return "\n".join(html)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>雨量預報歷次報次比對</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif; margin: 20px; background:#f5f6f8; color:#222; }}
  h1 {{ font-size: 1.4rem; }}
  h2 {{ margin-top: 2.5rem; border-bottom: 2px solid #ccc; padding-bottom: 4px; }}
  h3 {{ margin-top: 1.5rem; }}
  .muted {{ color:#777; font-size:0.85rem; }}
  .table-scroll {{ overflow-x:auto; max-width:100%; }}
  table.cmp-table {{ border-collapse: collapse; font-size:0.82rem; white-space:nowrap; }}
  table.cmp-table th, table.cmp-table td {{ border:1px solid #ccc; padding:4px 8px; text-align:center; }}
  table.cmp-table thead th {{ background:#e9edf2; position:sticky; top:0; }}
  .sticky-col {{ position:sticky; left:0; background:#f5f6f8; z-index:2; font-weight:bold; }}
  thead .sticky-col {{ z-index:3; }}
  td.changed {{ background:#ffe3e3; font-weight:bold; }}
  th.hdr-new {{ background:#d6e8ff; }}
  th.hdr-modified {{ background:#ffe6c2; }}
  th.hdr-first {{ background:#e9edf2; }}
  .period {{ font-weight:normal; font-size:0.75rem; color:#555; }}
  .legend span {{ display:inline-block; margin-right:16px; padding:2px 8px; border-radius:4px; font-size:0.8rem; }}
  footer {{ margin-top:3rem; font-size:0.75rem; color:#999; }}
</style>
</head>
<body>
<h1>颱風/豪雨事件 雨量預報歷次報次比對</h1>
<p class="muted">產生時間：{generated_at}（每10分鐘自動更新，資料來源：交通部中央氣象署）</p>
<div class="legend">
  <span style="background:#e9edf2;">灰底表頭 = 首筆快照</span>
  <span style="background:#d6e8ff;">藍底表頭 = 新一報</span>
  <span style="background:#ffe6c2;">橘底表頭 = 同報時效/內容被事後修改</span>
  <span style="background:#ffe3e3;">紅底儲存格 = 該分區與前一欄相比數值不同</span>
</div>
{event_sections}
<h2>各縣市雨量最大值（實測參考）</h2>
{countymax_section}
<footer>本頁為自動化擷取結果，僅供內部情資參考，正式資料請以中央氣象署官方發布為準。</footer>
</body>
</html>
"""


def build():
    os.makedirs(DOCS_DIR, exist_ok=True)
    event_dirs = sorted(
        d for d in glob.glob(os.path.join(WPPS_DATA_DIR, "*")) if os.path.isdir(d)
    )

    sections = []
    for event_dir in event_dirs:
        event_name = os.path.basename(event_dir)
        snapshots = _load_event_snapshots(event_dir)
        if not snapshots:
            continue
        sections.append(f"<h2>{event_name}</h2>")
        sections.append(_render_table(snapshots, "all_precip", "總雨量預測"))
        sections.append(_render_table(snapshots, "precip_24h", "24小時雨量預測"))

    if not sections:
        sections.append("<p>目前沒有進行中的事件資料。</p>")

    html = PAGE_TEMPLATE.format(
        generated_at=datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        event_sections="\n".join(sections),
        countymax_section=_render_countymax(),
    )

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    p = build()
    print(f"已產生：{p}")
