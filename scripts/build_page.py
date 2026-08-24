# -*- coding: utf-8 -*-
"""
讀取 data/wpps/ 底下所有事件的所有快照，以及 data/countymax/latest.json，
產生一份 docs/index.html 靜態網頁。

呈現邏輯（依需求調整版）：
  - 每個事件依「總雨量預測時效區間文字」分成多個區塊(block)：
      時效沒變 -> 沿用同一區塊，往右加報次欄
      時效變了(氣象署改了預測起訖日期) -> 開一個新區塊，放在最右邊，
      之後新報次都加進這個最新區塊
  - 每個區塊獨立呈現：分區欄 + 該區塊所有報次(各拆平地/山區) + 一欄觀測雨量
  - 舊區塊不會再有新報次，但觀測雨量會持續更新，直到該區塊自己的時效
    結束時間到了為止，之後凍結（存成 _frozen_observed.json，不再跟著即時資料變動）
  - 跟前一報同一格比較：數值上修＝紅字，下修＝藍字，相同＝黑字
  - 24小時雨量預測持續存檔但不顯示於本頁
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
DURATION_ORDER = ["本日累積", "2日累積", "3日累積", "4日累積", "5日累積"]


def _load_event_snapshots(event_dir: str):
    files = sorted(f for f in glob.glob(os.path.join(event_dir, "*.json"))
                    if not os.path.basename(f).startswith("_"))
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


def _resolve_year(month, day, hour, now):
    """從月/日/時猜出正確的年份（處理跨年邊界），回傳最接近now的datetime"""
    hour = min(hour, 23)
    candidates = []
    for y in (now.year - 1, now.year, now.year + 1):
        try:
            candidates.append(datetime(y, month, day, hour, tzinfo=TW_TZ))
        except ValueError:
            continue
    if not candidates:
        return None
    return min(candidates, key=lambda d: abs((d - now).total_seconds()))


def _parse_period_start(period_text, now):
    """從 '自08月23日00時至8月25日24時止' 這種文字抓出起始時間"""
    if not period_text:
        return None
    m = re.search(r"自\s*(\d{1,2})月(\d{1,2})日(\d{1,2})時", period_text)
    if not m:
        return None
    month, day, hour = (int(x) for x in m.groups())
    return _resolve_year(month, day, hour, now)


def _parse_period_end(period_text, now):
    """從 '自08月23日00時至8月25日24時止' 這種文字抓出結束時間（處理24時=隔天0時）"""
    if not period_text:
        return None
    m = re.search(r"至\s*(\d{1,2})月(\d{1,2})日(\d{1,2})時", period_text)
    if not m:
        return None
    month, day, hour = (int(x) for x in m.groups())
    extra_day = 0
    if hour >= 24:
        extra_day = 1
        hour -= 24
    dt = _resolve_year(month, day, hour, now)
    if dt is None:
        return None
    return dt + timedelta(days=extra_day)


def _pick_duration_label(elapsed_days):
    """依經過天數挑累積時段標籤：當天用本日累積，之後每過一天多一天累積，5日封頂"""
    idx = max(0, min(elapsed_days, len(DURATION_ORDER) - 1))
    return DURATION_ORDER[idx]


def _load_countymax_latest():
    latest_path = os.path.join(COUNTYMAX_DATA_DIR, "latest.json")
    if not os.path.exists(latest_path):
        return None
    with open(latest_path, encoding="utf-8") as f:
        return json.load(f)


def _group_into_blocks(snapshots, table_key):
    """依總雨量預測的時效區間文字分組，時效文字相同視為同一區塊"""
    blocks = []
    for snap in snapshots:
        period = (snap.get(table_key) or {}).get("period", "")
        if blocks and blocks[-1]["period"] == period:
            blocks[-1]["snapshots"].append(snap)
        else:
            blocks.append({"period": period, "snapshots": [snap]})
    return blocks


def _load_frozen_store(event_dir):
    path = os.path.join(event_dir, "_frozen_observed.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_frozen_store(event_dir, store):
    path = os.path.join(event_dir, "_frozen_observed.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def _get_observed_for_block(period_text, now, countymax_data, frozen_store, is_latest_block):
    """
    回傳 (counties_dict, label文字, 觀測時間範圍文字, 是否已凍結)
    - 最新區塊：一律用動態經過天數挑選，持續更新
    - 舊區塊：時效還沒結束前一樣動態更新；結束後改用/建立凍結值
    """
    block_end = _parse_period_end(period_text, now)
    frozen = frozen_store.get(period_text)

    if not is_latest_block and frozen is not None:
        return frozen["counties"], frozen["label"], frozen.get("range_text", ""), True

    if not is_latest_block and block_end is not None and now >= block_end:
        # 時效剛結束，準備凍結：用目前最新一次觀測值定案
        label = _pick_duration_label((now - _parse_period_start(period_text, now)).days) \
            if _parse_period_start(period_text, now) else "本日累積"
        counties = {}
        range_text = ""
        if countymax_data:
            dur = countymax_data.get("durations", {}).get(label, {})
            counties = dur.get("counties", {})
            p = dur.get("period", {})
            if p.get("timefrom"):
                range_text = f"{p.get('timefrom','')}~{p.get('timeto','')}"
        frozen_store[period_text] = {
            "counties": counties, "label": label, "range_text": range_text,
            "frozen_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return counties, label, range_text, True

    # 動態更新中（最新區塊，或舊區塊時效還沒結束）
    start = _parse_period_start(period_text, now)
    elapsed_days = (now - start).days if start else 0
    label = _pick_duration_label(elapsed_days)
    counties = {}
    range_text = ""
    if countymax_data:
        dur = countymax_data.get("durations", {}).get(label, {})
        counties = dur.get("counties", {})
        p = dur.get("period", {})
        if p.get("timefrom"):
            range_text = f"{p.get('timefrom','')}~{p.get('timeto','')}"
    return counties, label, range_text, False


def _render_block(block, table_key, countymax_data, now, frozen_store, is_latest_block):
    period_text = block["period"]
    snapshots = block["snapshots"]

    areas = list(EXPECTED_AREAS)
    seen = set(areas)
    for snap in snapshots:
        for a in (snap.get(table_key) or {}).get("areas", {}):
            if a not in seen:
                areas.append(a)
                seen.add(a)

    observed_counties, observed_label, observed_range, is_frozen = _get_observed_for_block(
        period_text, now, countymax_data, frozen_store, is_latest_block
    )
    frozen_tag = "（已定案）" if is_frozen else "（更新中）"

    html = ['<div class="block-card"><table class="cmp-table">']
    html.append(f"<caption>{period_text}</caption>")
    html.append("<tr><th class='sticky-col' rowspan='2'>分區</th>")
    for snap in snapshots:
        tbl = snap.get(table_key) or {}
        pub = tbl.get("publish_time", "")
        cls = _report_header_class(snap)
        html.append(f"<th class='{cls}' colspan='2'>{pub}</th>")
    obs_sub = f"<br><span class='period'>{observed_range}</span>" if observed_range else ""
    html.append(
        f"<th class='hdr-observed' rowspan='2'>觀測雨量<br>"
        f"<span class='period'>({observed_label}){frozen_tag}{obs_sub}</span></th>"
    )
    html.append("</tr><tr>")
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


def _render_event(event_dir, snapshots, table_key, title, countymax_data, now):
    if not snapshots:
        return f"<p>（目前尚無{title}資料）</p>"

    blocks = _group_into_blocks(snapshots, table_key)
    frozen_store = _load_frozen_store(event_dir)
    before = json.dumps(frozen_store, sort_keys=True)

    html = [f"<h3>{title}</h3>", '<div class="blocks-row">']
    for i, block in enumerate(blocks):
        is_latest = (i == len(blocks) - 1)
        html.append(_render_block(block, table_key, countymax_data, now,
                                   frozen_store, is_latest))
    html.append("</div>")

    after = json.dumps(frozen_store, sort_keys=True)
    if after != before:
        _save_frozen_store(event_dir, frozen_store)

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
  .toolbar {{ margin-bottom: 16px; }}
  .toolbar button {{
    background:#2c6ecb; color:#fff; border:none; border-radius:6px;
    padding:8px 16px; font-size:0.9rem; cursor:pointer;
  }}
  .toolbar button:disabled {{ background:#9ab3d9; cursor:wait; }}
  .blocks-row {{ display:flex; gap:16px; overflow-x:auto; align-items:flex-start; padding-bottom:8px; }}
  .block-card {{ flex:0 0 auto; }}
  table.cmp-table {{ border-collapse: collapse; font-size:0.82rem; white-space:nowrap; }}
  table.cmp-table caption {{ text-align:left; font-weight:bold; padding:4px 2px; font-size:0.85rem; }}
  table.cmp-table th, table.cmp-table td {{ border:1px solid #ccc; padding:4px 8px; text-align:center; }}
  table.cmp-table th {{ background:#e9edf2; }}
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
<div class="toolbar">
  <button id="downloadBtn" onclick="downloadAsImage()">下載完整圖片</button>
</div>
<div id="capture-area">
<h1>颱風/豪雨事件 雨量預報歷次報次比對</h1>
<p class="muted">產生時間：{generated_at}（每10分鐘自動更新，資料來源：交通部中央氣象署）</p>
<div class="legend">
  <span style="background:#e9edf2;">灰底表頭 = 首筆快照</span>
  <span style="background:#d6e8ff;">藍底表頭 = 新一報</span>
  <span style="background:#ffe6c2;">橘底表頭 = 同報時效/內容被事後修改</span>
  <span style="color:#c00;">紅字 = 與前一報相比預報上修</span>
  <span style="color:#06c;">藍字 = 與前一報相比預報下修</span>
  <span style="background:#eef4d8;">觀測雨量欄 = 依區塊時效自動挑選累積時段，時效結束後定案凍結</span>
</div>
<p class="muted">說明：氣象署變更「總雨量預測時效區間」時會自動另開一個區塊（見下方橫向排列的表格），
舊區塊不再新增預報報次，但觀測雨量會持續更新直到該區塊時效結束為止，屆時定案不再變動。</p>
{event_sections}
<footer>本頁為自動化擷取結果，僅供內部情資參考，正式資料請以中央氣象署官方發布為準。（24小時雨量預測資料持續存檔，暫未於本頁顯示）</footer>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
async function downloadAsImage() {{
  const btn = document.getElementById('downloadBtn');
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '產生圖片中...';

  // 暫時讓每個可橫向捲動的區塊完全展開，避免圖片只截到目前看得到的範圍
  const scrollers = document.querySelectorAll('.blocks-row');
  const originalStyles = [];
  scrollers.forEach(el => {{
    originalStyles.push(el.style.cssText);
    el.style.overflow = 'visible';
    el.style.width = 'max-content';
  }});

  try {{
    const target = document.getElementById('capture-area');
    const canvas = await html2canvas(target, {{
      backgroundColor: '#f5f6f8',
      scale: 2,
      useCORS: true,
    }});
    const link = document.createElement('a');
    const ts = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '');
    link.download = `雨量預報比對_${{ts}}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  }} catch (err) {{
    alert('產生圖片失敗，請改用瀏覽器內建的截圖功能：' + err.message);
  }} finally {{
    scrollers.forEach((el, i) => {{ el.style.cssText = originalStyles[i]; }});
    btn.disabled = false;
    btn.textContent = originalText;
  }}
}}
</script>
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
        sections.append(_render_event(event_dir, snapshots, "all_precip", "總雨量預測",
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
