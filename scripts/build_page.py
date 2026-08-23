# -*- coding: utf-8 -*-
"""
讀取 data/wpps/ 底下所有事件的所有快照，以及 data/countymax/latest.json，
產生一份 docs/index.html 靜態網頁。

呈現邏輯（依需求調整版）：
  - 每個事件一個區塊，只顯示「總雨量預測」（24小時雨量預測持續存檔但不顯示）
  - 每一報拆成「平地」「山區」兩欄
  - 跟前一報同一格比較：數值上修＝紅字，下修＝藍字，相同＝黑字，
    任一邊是「-」（無資料）則不比較、維持黑字
  - 報次表頭本身：首筆快照灰底、新一報藍底、同報修改橘底
  - 最右欄附上「觀測雨量」，依「總雨量預測時效起始時間」到現在經過幾天，
    自動挑選最接近的累積時段（最近1小時～5日累積，5日封頂）
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


def _load_event_snapshots(event_dir: str):
    files = sorted(glob.glob(os.path.join(event_dir, "*.json")))
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
    """把 '80 - 150' / '< 80' / '-' 這種文字轉成 (min, max) 數字區間，供比大小用"""
    if text is None:
        return None
    text = text.strip()
    if text in ("-", "", "--"):
        return None
    m = re.match(r"<\s*([\d.]+)", text)
    if m:
        return (0.0, float(m.group(1)))
    m = re.match(r"([\d.]+)\s*-\s*([\d.]+)", text)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    m = re.search(r"[\d.]+", text)
    if m:
        v = float(m.group(0))
        return (v, v)
    return None


def _compare_class(old_text, new_text):
    """回傳 'up'（紅字，上修）/ 'down'（藍字，下修）/ ''（黑字，相同或無法比較）"""
    old_r = _parse_num_range(old_text)
    new_r = _parse_num_range(new_text)
    if old_r is None or new_r is None:
        return ""
    if new_r > old_r:
        return "up"
    if new_r < old_r:
        return "down"
    return ""


def _parse_period_start(period_text, now):
    """從 '自08月23日00時至8月25日24時止' 這種文字抓出起始時間"""
    if not period_text:
        return None
    m = re.search(r"自\s*(\d{1,2})月(\d{1,2})日(\d{1,2})時", period_text)
    if not m:
        return None
    month, day, hour = (int(x) for x in m.groups())
    year = now.year
    try:
        dt = datetime(year, month, day, min(hour, 23), tzinfo=TW_TZ)
    except ValueError:
        return None
    # 若算出來的日期離現在超過200天，代表跨年了，往前一年校正
    if (dt - now).days > 200:
        dt = dt.replace(year=year - 1)
    return dt


def _pick_observed_label(period_text, now):
    """依總雨量預測時效起始時間到現在經過幾天，挑最接近的累積時段標籤"""
    start = _parse_period_start(period_text, now)
    if start is None:
        return "最近1小時"
    elapsed_days = (now - start).days
    if elapsed_days <= 0:
        return "最近1小時"
    if elapsed_days == 1:
        return "本日累積"
    if elapsed_days == 2:
        return "2日累積"
    if elapsed_days == 3:
        return "3日累積"
    if elapsed_days == 4:
        return "4日累積"
    return "5日累積"


def _load_countymax_latest():
    latest_path = os.path.join(COUNTYMAX_DATA_DIR, "latest.json")
    if not os.path.exists(latest_path):
        return None
    with open(latest_path, encoding="utf-8") as f:
        return json.load(f)


def _render_table(snapshots, table_key: str, title: str, countymax_data, now):
    """table_key: 目前只會傳 'all_precip'（24h表已不顯示）"""
    if not snapshots:
        return f"<p>（目前尚無{title}資料）</p>"

    areas = list(EXPECTED_AREAS)
    seen = set(areas)
    for snap in snapshots:
        for a in (snap.get(table_key) or {}).get("areas", {}):
            if a not in seen:
                areas.append(a)
                seen.add(a)

    # 挑選觀測雨量要用的時段：用「最新一筆快照」的時效起始時間去判斷
    latest_period = (snapshots[-1].get(table_key) or {}).get("period", "")
    observed_label = _pick_observed_label(latest_period, now)
    observed_counties = {}
    observed_period_text = ""
    if countymax_data:
        dur = countymax_data.get("durations", {}).get(observed_label, {})
        observed_counties = dur.get("counties", {})
        p = dur.get("period", {})
        if p.get("timefrom"):
            observed_period_text = f"{p.get('timefrom','')}~{p.get('timeto','')}"

    html = [f"<h3>{title}</h3>", '<div class="table-scroll"><table class="cmp-table">']

    # 表頭第一列：分區 + 每報（colspan=2）+ 觀測雨量
    html.append("<tr><th class='sticky-col' rowspan='2'>分區</th>")
    for snap in snapshots:
        tbl = snap.get(table_key) or {}
        pub = tbl.get("publish_time", "")
        period = tbl.get("period", "")
        cls = _report_header_class(snap)
        html.append(
            f"<th class='{cls}' colspan='2'>{pub}<br>"
            f"<span class='period'>{period}</span></th>"
        )
    obs_sub = f"<br><span class='period'>{observed_period_text}</span>" if observed_period_text else ""
    html.append(f"<th class='hdr-observed' rowspan='2'>觀測雨量<br><span class='period'>({observed_label}){obs_sub}</span></th>")
    html.append("</tr>")

    # 表頭第二列：每報底下的 平地/山區
    html.append("<tr>")
    for _ in snapshots:
        html.append("<th class='sub-hdr'>平地</th><th class='sub-hdr'>山區</th>")
    html.append("</tr>")

    for area in areas:
        html.append(f"<tr><td class='sticky-col'>{area}</td>")
        prev_areas_data = None
        for snap in snapshots:
            tbl = snap.get(table_key) or {}
            areas_data = tbl.get("areas", {})
            curr = areas_data.get(area, {"平地": "-", "山區": "-"})
            prev = (prev_areas_data or {}).get(area) if prev_areas_data else None

            plain_val = curr.get("平地", "-")
            mtn_val = curr.get("山區", "-")
            plain_cls = _compare_class(prev.get("平地") if prev else None, plain_val) if prev else ""
            mtn_cls = _compare_class(prev.get("山區") if prev else None, mtn_val) if prev else ""

            html.append(f"<td class='{plain_cls}'>{plain_val}</td>")
            html.append(f"<td class='{mtn_cls}'>{mtn_val}</td>")
            prev_areas_data = areas_data

        obs_rain = observed_counties.get(area, {}).get("rain")
        html.append(f"<td class='obs-col'>{obs_rain if obs_rain is not None else '-'}</td>")
        html.append("</tr>")
    html.append("</table></div>")
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
  table.cmp-table th {{ background:#e9edf2; position:sticky; top:0; }}
  th.sub-hdr {{ font-weight:normal; font-size:0.78rem; }}
  .sticky-col {{ position:sticky; left:0; background:#f5f6f8; z-index:2; font-weight:bold; }}
  tr th.sticky-col {{ z-index:3; }}
  td.up {{ color:#c00; font-weight:bold; }}
  td.down {{ color:#06c; font-weight:bold; }}
  td.obs-col {{ background:#f7f9e8; font-weight:bold; }}
  th.hdr-new {{ background:#d6e8ff; }}
  th.hdr-modified {{ background:#ffe6c2; }}
  th.hdr-first {{ background:#e9edf2; }}
  th.hdr-observed {{ background:#eef4d8; }}
  .period {{ font-weight:normal; font-size:0.72rem; color:#555; }}
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
  <span style="color:#c00;">紅字 = 與前一報相比預報上修</span>
  <span style="color:#06c;">藍字 = 與前一報相比預報下修</span>
  <span style="background:#eef4d8;">觀測雨量欄 = 依事件經過天數自動挑選對應累積時段的實測值</span>
</div>
{event_sections}
<footer>本頁為自動化擷取結果，僅供內部情資參考，正式資料請以中央氣象署官方發布為準。（24小時雨量預測資料持續存檔，暫未於本頁顯示）</footer>
</body>
</html>
"""


def build():
    os.makedirs(DOCS_DIR, exist_ok=True)
    event_dirs = sorted(
        d for d in glob.glob(os.path.join(WPPS_DATA_DIR, "*")) if os.path.isdir(d)
    )
    now = datetime.now(TW_TZ)
    countymax_data = _load_countymax_latest()

    sections = []
    for event_dir in event_dirs:
        event_name = os.path.basename(event_dir)
        snapshots = _load_event_snapshots(event_dir)
        if not snapshots:
            continue
        sections.append(f"<h2>{event_name}</h2>")
        sections.append(_render_table(snapshots, "all_precip", "總雨量預測",
                                       countymax_data, now))

    if not sections:
        sections.append("<p>目前沒有進行中的事件資料。</p>")

    html = PAGE_TEMPLATE.format(
        generated_at=now.strftime("%Y-%m-%d %H:%M:%S"),
        event_sections="\n".join(sections),
    )

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    p = build()
    print(f"已產生：{p}")
