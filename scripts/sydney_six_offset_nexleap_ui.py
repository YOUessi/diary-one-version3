#!/usr/bin/env python3
"""Build Nexleap One styled Day timeline + Chapter detail from real local
Sydney six-offset JPEG+VLM and direct-video+VLM outputs.

Zero model calls. Never overwrite model result files, original footage or
recorded usage. All 129 chapters / 701 selected media remain accessible.
"""
from __future__ import annotations

from collections import defaultdict, Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
from PIL import Image

HOME = Path.home()
REPO = HOME / "Documents/Nexleap/Diary_one_chapter_v2"
ROOT = HOME / "Documents/Nexleap/work_logs/evidence"
BASE = ROOT / "sydney-six-offset-image-vs-video-20261109"
PHOTO = ROOT / "sydney-direct-vlm-compact-v03-20261105"
VIDEO10 = ROOT / "sydney-video-full-160-fps-ab-20261109"
OFFSETS = (10,20,30,50,60,70)
METHODS = ("jpeg","video05","video1")
MEDIA = BASE / "full_chapter_media"
CROPPED = BASE / "nexleap_editorial_media"
HTML_NAME = "SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html"
ALT_NAME = "NEXLEAP_ONE_SIX_GROUPS_INTERACTIVE.html"
BACKUP_NAME = "SIX_GROUPS_PRE_NEXLEAP_EDITORIAL_BACKUP.html"
SOURCE_CSS = REPO / "scripts/review_ui/nexleap.css"
SOURCE_JS = REPO / "scripts/review_ui/nexleap.js"
ASSET_RE = re.compile(r"^sydney_\d{2}_(\d{6})$")


def raw_asset_time(asset_id: str, focus_ms: int) -> float:
    match = ASSET_RE.fullmatch(asset_id)
    if not match:
        raise ValueError(f"Unexpected source asset identifier: {asset_id}")
    start = (int(match.group(1))-1)*10
    if start < 80:
        raise ValueError(f"Intro media in result: {asset_id}")
    if not isinstance(focus_ms,int) or not 0<=focus_ms<10000:
        raise ValueError(f"Video point outside 10s: {asset_id} {focus_ms}")
    return round(start + focus_ms / 1000.0, 3)


def photo_without_artificial_letterbox(source:Path) -> str:
    """Crop only black ASPECT_FIT_LETTERBOX mattes in old MobileCLIP JPEG.
    Never alter input evidence. Save a separate purely visual preview.
    """
    assert source.is_file(),source
    dest=CROPPED/source.relative_to(MEDIA)
    if not dest.is_file():
        dest.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(source) as raw:
            img=raw.convert("RGB")
            w,h=img.size
            lum=img.convert("L")
            mask=lum.point(lambda value:255 if value>12 else 0)
            box=mask.getbbox()
            if box is not None:
                top, bottom=box[1],box[3]
                if top>h*.08 and bottom<h*.92 and bottom-top>h*.25:
                    img=img.crop((0,max(0,top-2),w,min(h,bottom+2)))
            img.save(dest,format="JPEG",quality=88,optimize=True)
    return dest.relative_to(BASE).as_posix()


def make_photo_map(offset: int):
    inp = ROOT / f"sydney-intro-cut-72s-20261105/offset_{offset:03d}/input"
    source = json.loads((inp/"bundle.json").read_text())
    assert len(source["assets"]) == 160
    frames = {}
    for i, asset in enumerate(source["assets"],1):
        for frame in asset["frames"]:
            frames[frame["frame_id"]] = {
                "clipSeq":i,
                "assetId":asset["asset_id"],
                "focusMs":int(frame.get("source_timestamp_ms") if
                              frame.get("source_timestamp_ms") is not None else frame.get("canonical_offset_ms",0))
            }
    return frames


def jpeg_chapters(offset: int):
    source = json.loads((PHOTO/f"offset_{offset:03d}/result.json").read_text())
    frames = make_photo_map(offset)
    result=[]
    for chapter_index,chapter in enumerate(source["chapters"],1):
        explanations={}
        moments=[]
        for idx, mom in enumerate(chapter.get("key_moments",[]),1):
            text = str(mom.get("description","")).strip()
            frameids = mom.get("frame_ids",[])
            moments.append({"text":text,
                            "info":" · ".join([fid for fid in frameids]),
                            "warning":""})
            for fid in frameids:
                if text:explanations.setdefault(fid,text)
        photos=[]
        for index,media in enumerate(chapter["selected_media"],1):
            fid=media["representative_frame_id"]
            assert fid in frames,fid
            fm=frames[fid]
            asset=media["source_asset_id"]
            assert asset==fm["assetId"]
            ms=media.get("focus_pts_ms")
            if type(ms)!=int:
                ms=fm["focusMs"]
            original=raw_asset_time(asset,ms)
            photo=MEDIA / f"jpeg_{offset:03d}" / f"c{chapter_index:02d}_m{index:02d}.jpg"
            assert photo.is_file(),photo
            caption=explanations.get(fid) or (f"真实街景 · 第 {fm['clipSeq']} 段代表照片")
            photos.append({
                "src":photo_without_artificial_letterbox(photo),
                "sourceAsset":asset,"focusMs":ms,
                "originalSecond":original,"clipSeq":fm["clipSeq"],
                "caption":caption,"hero":index==1,
            })
        result.append({
            "id":f"offset{offset:03d}_jpeg_c{chapter_index:02d}",
            "title":chapter["title"],
            "story":chapter["story"],
            "firstSourceSecond":min(x["originalSecond"] for x in photos),
            "photos":photos,"moments":moments,
            "modelStatus":"COMPLETE",
        })
    return result


def video_chapters(offset:int,fps:float):
    key="0p5" if fps==.5 else "1p0"
    directory = VIDEO10 if offset==10 else BASE / f"video/offset_{offset:03d}"
    data = json.loads((directory/f"fps_{key}_result.json").read_text())
    raw = data["model_output"]["chapters"]
    mapped = data["mapped_source_moments"]
    by_chapter = defaultdict(list)
    keyed = defaultdict(list)
    for source_order,moment in enumerate(mapped,1):
        assert 1<=moment["chapter"]<=len(raw)
        keytuple=(moment["part_id"],moment["part_time_ms"],moment["text"])
        by_chapter[moment["chapter"]].append((source_order,moment))
        keyed[(moment["chapter"],keytuple)].append((source_order,moment))
    result=[]
    total_raw=0
    total_mapped=0
    for i, chapter in enumerate(raw,1):
        moments=[]
        pictures=[]
        for moment_index,moment in enumerate(chapter["selected_moments"],1):
            total_raw+=1
            keytuple=(moment.get("part_id"),moment.get("video_time_ms"),moment.get("text"))
            available=keyed.get((i,keytuple),[])
            matching=available.pop(0) if available else None
            note=f"Part {moment.get('part_id')} · {moment.get('video_time_ms')}ms"
            warning="" if matching else "此位置未直接映射至10秒原片（原始输出保留）"
            moments.append({"text":moment.get("text",""),"info":note,"warning":warning})
            if matching:
                source_order,m=matching
                source_file=MEDIA / f"video_{offset:03d}_{key}" / f"c{i:02d}_m{len(pictures)+1:03d}.jpg"
                assert source_file.is_file(),source_file
                original=raw_asset_time(m["source_asset_id"],int(m["source_clip_focus_ms"]))
                assert abs(original-m["original_video_time_ms"]/1000)<.0001
                photos_entry={
                    "src":str(source_file.relative_to(BASE).as_posix()),
                    "sourceAsset":m["source_asset_id"],
                    "focusMs":int(m["source_clip_focus_ms"]),
                    "originalSecond":original,
                    "clipSeq":int(m["original_global_clip_seq"]),
                    "caption":m["text"] or f"真实视频关键帧 {moment_index}",
                    "hero":len(pictures)==0
                }
                pictures.append(photos_entry)
                total_mapped+=1
        # Every model-generated Chapter is represented. 20s/1fps has 4
        # exact 200000ms endpoint errors; preserve the textual moments but do
        # not invent images for them.
        assert len(pictures)==len(by_chapter.get(i,[])),(offset,fps,i,len(pictures),len(by_chapter.get(i,[])))
        assert pictures,(offset,fps,i)
        result.append({
            "id":f"offset{offset:03d}_video{key}_c{i:02d}",
            "title":chapter["title"],
            "story":chapter["story"],
            "firstSourceSecond":min(x["originalSecond"] for x in pictures),
            "photos":pictures,"moments":moments,
            "modelStatus":data["metadata"]["state"],
        })
    assert total_mapped == len(mapped)
    if offset==20 and fps==1:
        assert total_raw==79 and total_mapped==75
    else:
        assert total_raw==total_mapped,(offset,fps,total_raw,total_mapped)
    return result


def build_data():
    data={"offsets":list(OFFSETS),"methods":list(METHODS),"groups":{}}
    expected_totals={"jpeg":236,"video05":192,"video1":273}
    n_chapters=0
    n_photos=0
    subtotals=Counter()
    for offset in OFFSETS:
        score={}
        for method in METHODS:
            if method=="jpeg":
                chapters=jpeg_chapters(offset)
                status=json.loads((PHOTO/f"offset_{offset:03d}/status.json").read_text())
                usage={"costCNY":status["cost_cny_est"],
                       "inputTokens":status["prompt_tokens"],"outputTokens":status["completion_tokens"],
                       "modelCalls":status["model_calls"]}
            else:
                fps=.5 if method=="video05" else 1.0
                chapters=video_chapters(offset,fps)
                folder=VIDEO10 if offset==10 else BASE/f"video/offset_{offset:03d}"
                usage_raw=json.loads((folder/f"fps_{'0p5' if method=='video05' else '1p0'}_status.json").read_text())
                usage={"costCNY":usage_raw["estimated_cost_cny"],
                       "inputTokens":usage_raw["prompt_tokens"],
                       "outputTokens":usage_raw["completion_tokens"],
                       "modelCalls":1}
            n_chapters+=len(chapters)
            media_count=sum(len(c["photos"]) for c in chapters)
            n_photos+=media_count
            subtotals[method]+=media_count
            score[method]={"chapters":chapters,"mediaCount":media_count,"usage":usage}
        data["groups"][str(offset)]=score
    assert n_chapters==129,(n_chapters,n_photos)
    assert n_photos==701,n_photos
    assert dict(subtotals)==expected_totals,subtotals
    return data


def render_html(data):
    raw=json.dumps(data,ensure_ascii=False,separators=(",",":"))
    # Make data safe in an HTML <script> raw-text element.
    raw=raw.replace("<",r"\u003c").replace(">",r"\u003e").replace("&",r"\u0026")
    html=f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#f8f7f3">
<title>Nexleap One · Sydney Citywalk Chapter Stories</title>
<meta name="description" content="悉尼 Citywalk，六个偏移组。真实 Day 时间线、Chapter 故事、照片和三秒 Live 动态视频。">
<link rel="stylesheet" href="nexleap.css">
<script src="nexleap.js" defer></script>
</head>
<body>
<div class="page">
 <header class="app-top">
  <div class="brand"><span class="brand-symbol" aria-hidden="true">n</span><div>
      <div class="brand-logo">Nexleap one</div>
      <div class="brand-line">LIFE, AS IT HAPPENS</div></div>
  </div>
  <div class="toolbar-main">
    <div class="selectors" role="group" aria-label="选择 Chapter 编辑算法">
      <button type="button" class="selector-btn" data-method="jpeg">抽帧 + VLM</button>
      <button type="button" class="selector-btn" data-method="video05">视频 · 0.5 fps</button>
      <button type="button" class="selector-btn" data-method="video1">视频 · 1 fps</button>
    </div>
    <div class="dropdown-wrap">
      <label class="dropdown-label" for="offsetSelector">采样组</label>
      <select class="offset-select" id="offsetSelector" aria-label="悉尼采样偏移组"></select>
    </div>
    <div class="top-context" id="header-info"></div>
  </div>
 </header>
 <main class="workspace">
   <aside class="timeline-panel" id="timeline-panel" aria-label="Day Chapter 时间线"></aside>
   <section class="detail-zone" id="detail-zone" aria-label="Chapter 完整故事和照片"></section>
 </main>
 <p class="utility-footer">NEXLEAP ONE · SYDNEY CHAPTER RESEARCH · 原片真实画面，不代表手机实际拍摄日期 · 本地实验预览</p>
 <nav class="mobile-nav" aria-label="底部导航">
   <button type="button" class="nav-button" data-nav="day">
    <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>Life
   </button>
   <button type="button" class="nav-button" data-nav="detail">
    <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 9h8m-8 4h6"/></svg>Chapter
   </button>
 </nav>
</div>
<dialog class="live-modal" id="liveDialog" aria-label="三秒 Live 视频预览">
 <div class="player-head">
  <div><span class="player-brand">Nexleap one</span><span class="player-sub">3 SECOND LIVE MOMENT</span></div>
  <button class="player-close" id="playerClose" type="button" aria-label="关闭视频">×</button>
 </div>
 <video class="player-video" id="liveVideo" muted playsinline loop preload="metadata"></video>
 <div class="player-status" id="playerStatus">正在准备真实动态画面…</div>
 <div class="player-caption" id="playerCaption"></div>
 <div class="player-foot"><p>源视频中截取 · 真实 3 秒 · 本地缓存<br>非 Apple Photos 系统 Live Photo</p>
  <button class="player-toggle" id="playerToggle" type="button">暂停 / 继续</button>
 </div>
</dialog>
<div id="toast" role="status" class="copy-feedback" aria-live="polite"></div>
<script id="chapter-data" type="application/json">{raw}</script>
</body>
</html>"""
    return html


def main():
    data=build_data()
    current=BASE/HTML_NAME
    backup=BASE/BACKUP_NAME
    if current.exists() and not backup.exists():
        shutil.copy2(current,backup)
    for file in [SOURCE_CSS,SOURCE_JS]:
        assert file.exists(),file
        shutil.copy2(file,BASE/file.name)
    content=render_html(data)
    target=BASE/ALT_NAME
    target.write_text(content,encoding="utf-8")
    current.write_text(content,encoding="utf-8")
    manifest={
        "version":"NEXLEAP_ONE_EDITORIAL_UI_V1",
        "user_reference":"day-timeline-and-full-chapter-photo-story",
        "chapters":129,
        "media":701,
        "six_offsets":list(OFFSETS),
        "three_paths":list(METHODS),
        "preview_http":"http://127.0.0.1:8810/",
        "primary_html":str(current),
        "alternate_html":str(target),
        "main_script":str(Path(__file__).resolve()),
        "css_sha256":hashlib.sha256((BASE/"nexleap.css").read_bytes()).hexdigest(),
        "js_sha256":hashlib.sha256((BASE/"nexleap.js").read_bytes()).hexdigest(),
        "new_api_calls":0,
        "cropped_old_letterbox_media_count":len(list(CROPPED.rglob("*.jpg"))),
        "cost_cny":0,
        "historical_original_data_modified":False
    }
    (BASE/"NEXLEAP_UI_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print("NEXLEAP_ONE_UI_BUILT",current,"bytes",len(content.encode()),
        "chapters",129,"real_media",701,"source_media_unchanged",flush=True)


if __name__=="__main__":
    main()
