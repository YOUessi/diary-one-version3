#!/usr/bin/env python3
"""Recreate labeled Tokyo/Manning Chapter examples as shareable Pages sites.

All displayed stories, statuses and JPG references come from verified
nexleap-chapter-examples exported JSON. Never fabricate Live videos.
This script never calls a VLM and never edits the source repository.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image,ImageOps
import hashlib
import html
import json
import re
import shutil
import subprocess

HOME=Path.home()
NEX=HOME/"Documents/Nexleap"
REPO=NEX/"Diary_one_chapter_v2"
SOURCE=NEX/"work_logs/evidence/tokyo-manning-chapter-examples-source-20261109"
OUT=NEX/"work_logs/evidence/nexleap-tokyo-manning-share-20261109"
SITE=OUT/"site"
ASSETS=REPO/"scripts/review_ui"
EXP_TYPES={"tokyo":["tokyo"],"manning-park":["manning0","manning10","manning20"]}
TAGS={
 "activity.hiking":"徒步",
 "subject.mountain":"山景",
 "subject.forest_landscape":"森林",
 "subject.lake_view":"湖泊",
 "subject.flower":"野花",
 "setting.mountain_area":"山地",
 "setting.forest":"林地",
 "setting.waterside":"水岸",
}
STATUS=("终选","候选","未选","排除")

def source_examples():
    roots=[p for p in SOURCE.iterdir() if p.is_dir() and
           (p.name.startswith("Manning Park BC") or p.name.startswith("【已标注范例】东京"))]
    assert len(roots)==4,[x.name for x in roots]
    examples={}
    for root in roots:
        d=json.loads((root/"整理结果.json").read_text())
        assert len(d["days"])==1
        city="tokyo" if "东京" in root.name else "manning-park"
        off=int(d["filters"]["offset_seconds"])
        key="tokyo" if city=="tokyo" else "manning"+str(off)
        assert key not in examples
        assert off in ((0,) if city=="tokyo" else (0,10,20))
        examples[key]=(root,d,city,off)
    assert sorted(examples)==["manning0","manning10","manning20","tokyo"]
    return examples

def image_index(root):
    by_filename=defaultdict(list)
    by_time=defaultdict(list)
    for p in root.rglob("*.jpg"):
        by_filename[p.name].append(p)
        if p.stem.count("_")>=1:
            by_time[p.stem.rsplit("_",1)[-1]].append(p)
    return by_filename,by_time

def scene_group(path):
    for x in path.parts:
        m=re.match(r"\d+_风貌组_(.+)",x)
        if m:return m.group(1)
    return "未单独分组"

def convert_photo(source,output):
    """Render a clean preview from true JPG content without synthetic bands.

    Exported JPGs are 768x1024 aspect-fit frames with ~28% solid black
    bars at top/bottom. Crop ONLY when both bands are unambiguously empty.
    The original source bytes stay intact in the separate read-only clone.
    """
    output.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(source) as original:
        img=ImageOps.exif_transpose(original).convert("RGB")
        w,h=img.size
        if h>w:
            lum=img.convert("L")
            bbox=lum.point(lambda x:255 if x>12 else 0).getbbox()
            if bbox:
                top,bottom=bbox[1],bbox[3]
                if top>h*.09 and bottom<h*.91 and bottom-top>h*.18:
                    img=img.crop((0,max(0,top-2),w,min(h,bottom+2)))
        img.thumbnail((1400,1400),Image.Resampling.LANCZOS)
        target=output.with_suffix(".tmp.jpg")
        img.save(target,"JPEG",quality=85,optimize=True,progressive=True)
        target.replace(output)

def to_seconds(label):
    try:
        h,m,s=label.split(":")
        return float(int(h)*3600+int(m)*60+float(s))
    except (ValueError,AttributeError):
        return None

def map_image(im,root,dataset,filename_index,time_index,folder):
    files=filename_index.get(im["filename"],[])
    if not files:
        files=time_index.get(str(im.get("time_label","")).replace(":","-"),[])
    if len(files)!=1:
        raise ValueError(f"Cannot uniquely locate image {root.name} ID={im['image_id']} paths={files[:5]}")
    original=files[0]
    name=f"{dataset}_{int(im['image_id'])}.jpg"
    dest=folder/"media"/dataset/name
    convert_photo(original,dest)
    idnum=int(im["image_id"])
    return {
        "id":idnum,
        "src":str(dest.relative_to(folder).as_posix()),
        "status":im["status"],
        "time":im.get("time_label",""),
        "originalSecond":to_seconds(im.get("time_label","")),
        "caption":im.get("note") or "",
        "note":im.get("note") or "",
        "group":scene_group(original),
        "sourceAsset":None,
        "focusMs":None,
        "position":int(im.get("position") or 0),
    }

def build_day(root,d,city,offset,folder):
    src_by_name,src_by_time=image_index(root)
    all_photos=[]
    chapters=[]
    for i,c in enumerate(sorted(d["chapters"],key=lambda x:x["position"]),1):
        photos=[map_image(im,root,("tokyo" if city=="tokyo" else "manning")+f"_offset{offset:03d}",
                     src_by_name,src_by_time,folder) for im in c["images"]]
        photos.sort(key=lambda im:(im["position"],im["id"]))
        ids={p["id"] for p in photos}
        if len(ids)!=len(photos):raise ValueError(f"Duplicate photo ID for {c['title']}")
        coverid=int(c["cover_image_id"])
        cover=next((im for im in photos if im["id"]==coverid),None)
        if not cover:raise ValueError(f"Cover image not present in exported JSON: {c['title']}")
        if cover["status"]!="终选":raise ValueError("Cover is not final-selected")
        finals=[cover]+[im for im in photos if im["status"]=="终选" and im["id"]!=coverid]
        extras=[im for im in photos if im["status"]!="终选"]
        assert len(finals)>=1
        stat=Counter(im["status"] for im in photos)
        if len(photos)!=int(c["image_count"]):
            raise ValueError("Mismatched image_count")
        notes=[{
            "text":im["note"],"info":(im["group"]+" · "+im["time"]),
            "warning":""
        } for im in finals if im["note"]]
        annotated=tuple(TAGS.get(tag,tag) for tag in c.get("tags",[]))
        first=min((im["originalSecond"] for im in finals if im["originalSecond"] is not None),
                  default=0.)
        chapters.append({
            "id":f"{city}_{offset:03d}_chapter_{i:02d}",
            "title":c["title"],
            "story":c["intro"],
            "firstSourceSecond":first,
            "photos":finals,
            "extraPhotos":extras,
            "moments":notes,
            "tags":list(annotated),
            "stats":dict(stat),
            "rawChapterId":int(c["chapter_id"]),
        })
        all_photos.extend(photos)
    assert sum(len(c["photos"])+len(c["extraPhotos"]) for c in chapters)==int(d["exported_image_count"])
    assert len(d["days"])==1
    return {
        "dayTitle":d["days"][0]["title"],
        "dayIntro":d["days"][0]["intro"],
        "chapters":chapters,
        "mediaCount":sum(len(c["photos"]) for c in chapters),
        "allImageCount":len(all_photos),
        "offsetSeconds":offset,
        "sourceLabel":root.name,
        "exportedAt":d["exported_at"],
    }

def adapt_base_js(city):
    s=(ASSETS/"nexleap.js").read_text()
    start=s.index("const METHODS={")
    stop=s.index("const $=s=>",start)
    s=s[:start]+('const METHODS={jpeg:{label:"人工标注",sub:"已标注范例",tag:"人工精选"}};\n')+s[stop:]
    s=s.replace('"nexleapOneSydFavoritesV1"','"nexleapOneExamplesFavoritesV1"')
    s=s.replace('"nexleapOneSydMyStoryV1"','"nexleapOneExamplesStoriesV1"')
    assert s.count("Sydney<br>citywalk.")==1
    s=s.replace("Sydney<br>citywalk.","Tokyo<br>citywalk." if city=="tokyo" else "Manning<br>Park.")
    old="从海港到老街，再到城市里的绿意。用真实画面重新发现这一天的故事。"
    assert s.count(old)==1
    s=s.replace(old,chr(36)+"{esc(group().dayIntro)}")
    s=s.replace("研究实验 · 2026.11.09","人工标注 · 真实图片范例")
    s=s.replace("本时间线的时间取自原始视频相对位置，不是拍摄日的实际钟点。<br>00:00–01:20 的总览画面已排除。",
                "视频时间来自标注数据，不是拍摄日的真实时钟。<br>本仓库不包含对应10秒原视频，Live 暂不可用。")
    s=s.replace("来自模型原始结果的关键时刻","来自人工标注的照片备注")
    assert s.count("悉尼 Citywalk")==1
    s=s.replace("悉尼 Citywalk","东京 Citywalk" if city=="tokyo" else "Manning Park BC")
    s=s.replace('<span class="tag">Citywalk</span>',
                '<span class="tag">'+("Citywalk" if city=="tokyo" else "Hiking")+'</span>')
    s=s.replace("LIVE · 自动播放","PHOTO · 查看照片")
    s=s.replace("PHOTOS / LIVE","PHOTOS · 终选")
    s=s.replace("滑动到照片就会静音自动播放 3 秒 Live，点击可放大，右上角可复制本地图片链接。",
                "这些照片保留人工终选状态和原始备注。点击查看大图，右上角可复制链接。")
    s=s.replace('disabled title="没有可验证的视频时间"',
                'aria-label="放大查看真实标注照片"')
    # Existing Live open handler never runs: a separate photo-only extension
    # intercepts tile/hero clicks in capture phase and shows an image dialog.
    return s

OVERRIDES = """
/* Human-labeled examples: selected photos only, no fake Live playback. */
.hero-live svg{display:none}
.hero-photo-label{position:absolute;bottom:110px;left:28px;z-index:3;
  background:#191917a8;border:1px solid #fff7;color:white;border-radius:12px;
  padding:11px 16px;font-size:13px;font-weight:750}
.live-pill{background:#242321d9}
.photo-badge{background:#2c2a27c9}
.example-extra{margin-top:34px;border:1px solid #e2dcd2;border-radius:14px;padding:18px;background:#fffdfa}
.example-extra>summary{cursor:pointer;font-size:15px;color:#62564c;font-weight:750}
.example-extra-intro{font-size:13px;color:#969088;line-height:1.7;margin:14px 0}
.example-extra-stats{display:flex;flex-wrap:wrap;gap:9px;margin:15px 0}
.example-extra-stats span{background:#f0ede7;color:#706960;border-radius:999px;padding:6px 12px;font-size:12px}
.example-extra-stats .emphasis{background:#eee0d1;color:#734f32}
.example-extra-buttons{display:flex;gap:6px;flex-wrap:wrap;margin:16px 0}
.example-extra-filter{padding:9px 14px;background:#f1eee9;border:1px solid #e4ded7;border-radius:999px;
  color:#665e55;font-size:12px}
.example-extra-filter.active{background:#2e2b27;color:#fff}
.example-extra-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(154px,1fr));gap:12px}
.example-extra-tile{background:#f9f7f4;border-radius:10px;overflow:hidden}
.example-extra-photo{width:100%;border:0;background:#e6e1d9;padding:0;display:block;cursor:zoom-in}
.example-extra-photo img{display:block;width:100%;height:160px;object-fit:cover}
.example-extra-caption{font-size:11px;color:#756f65;padding:9px;line-height:1.55}
.example-photo-dialog{width:min(95vw,890px);max-width:none;border:0;padding:0;
 background:#f9f7f3;color:#38332c;border-radius:17px;box-shadow:0 24px 80px #0008}
.example-photo-dialog::backdrop{background:#111b22dc}
.example-photo-header{display:flex;justify-content:space-between;align-items:center;padding:13px 19px}
.example-photo-title{font-weight:800;font-style:italic;font-size:17px}
.example-photo-close{border:1px solid #d9d0c4;border-radius:999px;background:#fff;
 font-size:13px;padding:8px 13px}
.example-photo-full{width:100%;max-height:75vh;object-fit:contain;background:#151719;display:block}
.example-photo-note{font-size:14px;line-height:1.7;margin:12px 19px}
.example-photo-meta{font-size:12px;color:#8e8a84;margin:0 19px 19px}
.photo-availability-note{color:#a18269;font-size:12px;margin:24px 0 0;line-height:1.7}
.review-top-nav{display:flex;align-items:center;gap:5px}
.review-top-nav a{padding:9px 13px;font-size:12px;font-weight:700;border-radius:999px;
 text-decoration:none;color:#756d63;white-space:nowrap}
.review-top-nav a.active{background:#fffefa;color:#2d2924;box-shadow:0 2px 11px #0001}
.review-top-nav a:hover{background:#f7ece0}
@media(max-width:760px){
 .review-top-nav{overflow-x:auto}
 .review-top-nav a{font-size:10px;padding:8px 10px}
 .example-extra-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
 .example-photo-dialog{width:98vw}
 .review-top-nav a:last-child{display:none}
}
"""

def page_html(city,payload):
    raw=json.dumps(payload,ensure_ascii=False,separators=(",",":"))
    raw=raw.replace("<",r"\u003c").replace(">",r"\u003e").replace("&",r"\u0026")
    title="东京 Citywalk" if city=="tokyo" else "Manning Park BC"
    blurb="六段已标注城市旅行 Chapter" if city=="tokyo" else "山地草甸、森林与 Lightning Lake 的三个偏移组"
    body="""<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f8f7f3">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<title>Nexleap One · PLACEHOLDER_TITLE</title>
<meta name="description" content="PLACEHOLDER_DESC">
<link rel="stylesheet" href="nexleap.css">
<script src="nexleap.js" defer></script>
<script src="nexleap-example-extensions.js" defer></script>
</head><body>
<div class="page">
<header class="app-top">
 <div class="brand"><span class="brand-symbol">n</span><div>
 <div class="brand-logo">Nexleap one</div><div class="brand-line">LIFE, AS IT HAPPENS</div>
 </div></div>
 <div class="toolbar-main">
   <nav class="review-top-nav selectors" aria-label="切换展示地点">
     <a href="https://youessi.github.io/diary-one-version3/">Sydney</a>
     <a href="../tokyo/" class="PLACEHOLDER_TOKYO">Tokyo</a>
     <a href="../manning-park/" class="PLACEHOLDER_MANNING">Manning Park</a>
     <a href="../examples/">全部范例</a>
   </nav>
   <div class="dropdown-wrap">
    <label class="dropdown-label" for="offsetSelector">采样偏移</label>
    <select id="offsetSelector" class="offset-select"></select>
   </div>
   <div id="header-info" class="top-context"></div>
 </div>
</header>
<main class="workspace">
  <aside id="timeline-panel" class="timeline-panel"></aside>
  <section id="detail-zone" class="detail-zone"></section>
</main>
<p class="utility-footer">NEXLEAP ONE · 人工标注示例 · 来自真实 JPG 与原始标注 JSON · 并非新 VLM 推理结果</p>
<nav class="mobile-nav" aria-label="移动端浏览">
 <button type="button" class="nav-button" data-nav="day">
 <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>Life</button>
 <button type="button" class="nav-button" data-nav="detail">
 <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 9h8m-8 4h6"/></svg>Chapter</button>
</nav></div>
<dialog class="live-modal" id="liveDialog" style="display:none" aria-hidden="true">
  <button id="playerClose"></button><video id="liveVideo"></video>
  <span id="playerStatus"></span><span id="playerCaption"></span>
  <button id="playerToggle"></button>
</dialog>
<div id="toast" role="status" class="copy-feedback"></div>
<script id="chapter-data" type="application/json">PLACEHOLDER_DATA</script>
</body></html>"""
    return (body.replace("PLACEHOLDER_TITLE",html.escape(title))
                .replace("PLACEHOLDER_DESC",html.escape(blurb))
                .replace("PLACEHOLDER_TOKYO","active" if city=="tokyo" else "")
                .replace("PLACEHOLDER_MANNING","active" if city=="manning-park" else "")
                .replace("PLACEHOLDER_DATA",raw))

def export():
    OUT.mkdir(parents=True,exist_ok=True)
    SRC=source_examples()
    groups={}
    for key,(folder,obj,city,off) in SRC.items():
        dest=SITE/city
        dest.mkdir(parents=True,exist_ok=True)
        group=build_day(folder,obj,city,off,dest)
        groups[key]=(city,off,group)
        print("DATA_OK",key,"chapters",len(group["chapters"]),"final",group["mediaCount"],
              "all_images",group["allImageCount"],flush=True)
    totals={}
    for city,choices in EXP_TYPES.items():
        target=SITE/city
        target.mkdir(parents=True,exist_ok=True)
        offsets=[groups[key][1] for key in choices]
        cases={str(groups[key][1]):{"jpeg":groups[key][2]} for key in choices}
        payload={"region":city,"offsets":offsets,"groups":cases}
        (target/"index.html").write_text(page_html(city,payload))
        (target/"nexleap.js").write_text(adapt_base_js(city))
        (target/"nexleap.css").write_text((ASSETS/"nexleap.css").read_text()+OVERRIDES)
        shutil.copy2(ASSETS/"nexleap-example-extensions.js",target/"nexleap-example-extensions.js")
        count=sum(groups[key][2]["allImageCount"] for key in choices)
        selected=sum(groups[key][2]["mediaCount"] for key in choices)
        chapters=sum(len(groups[key][2]["chapters"]) for key in choices)
        images=list((target/"media").rglob("*.jpg"))
        assert len(images)==count,(city,len(images),count)
        assert (chapters,selected,count)==((6,47,165) if city=="tokyo" else (3,49,478))
        totals[city]={"chapters":chapters,"selected":selected,"all_images":count}
        (target/"manifest.json").write_text(json.dumps({
            "source_repo":"13021068599zyf-glitch/nexleap-chapter-examples",
            "source_git_commit":"b61d684ab8765c93b5c75ccaabd91bfbcfe8470d",
            "region":city,"offsets":offsets,"chapters":chapters,
            "final_selected":selected,"all_images":count,
            "is_human_labeled":True,"has_original_video":False,
            "genuine_live_available":False,"no_vlm_calls":True,
            "built_utc":datetime.now(timezone.utc).isoformat()
        },ensure_ascii=False,indent=2))
        print("SITE_BUILT",city,"html_bytes",(target/"index.html").stat().st_size,
              "photos",len(images),flush=True)
    (OUT/"BUILD_SUMMARY.json").write_text(json.dumps(totals,ensure_ascii=False,indent=2))
    print("ALL_EXAMPLE_SITES_COMPLETE",SITE,totals)

if __name__=="__main__":
    export()
