#!/usr/bin/env python3
"""Complete six-offset Chapter editorial review from existing real assets.

Zero VLM calls. The same HTML address replaces the former "cover + 110 chars"
overview. All stories, media selection, key moments, provenance and real
re-decoded video frames are presented in openable chapters.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageOps
import html
import json
import re
import shutil

ROOT = Path.home() / "Documents/Nexleap/work_logs/evidence"
BASE = ROOT / "sydney-six-offset-image-vs-video-20261109"
PHOTO = ROOT / "sydney-direct-vlm-compact-v03-20261105"
VIDEO10 = ROOT / "sydney-video-full-160-fps-ab-20261109"
OFFSETS = (10, 20, 30, 50, 60, 70)
OUTPUT = BASE / "SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html"
OLD_OVERVIEW = BASE / "SIX_GROUPS_JPEG_VS_VIDEO_OLD_OVERVIEW_BACKUP.html"
ASSET = BASE / "full_chapter_media"
ASSET.mkdir(exist_ok=True)

def esc(obj):
    return html.escape(str(obj), quote=True)

def render_image(src: Path, dest: Path):
    """Full-detail review image, 1000px wide, no synthesis or stock art."""
    if dest.exists() and dest.stat().st_size > 400:
        return
    if not src.is_file():
        raise FileNotFoundError(str(src))
    dest.parent.mkdir(exist_ok=True, parents=True)
    with Image.open(src) as raw:
        img = ImageOps.exif_transpose(raw)
        img = img.convert("RGB")
        img.thumbnail((1000, 780), Image.Resampling.LANCZOS)
        img.save(dest, format="JPEG", quality=84, optimize=True)

def picture(absolute: Path, dst: Path, caption: str, *, lead: bool = False, live_asset: str | None = None, focus_ms: int | None = None) -> str:
    render_image(absolute,dst)
    rel = dst.relative_to(BASE).as_posix()
    live_control = ""
    if live_asset is not None:
        assert re.fullmatch(r"sydney_(?:01|02|03|05|06|07)_\d{6}",live_asset), live_asset
        assert isinstance(focus_ms,int) and 0 <= focus_ms < 10000, (live_asset,focus_ms)
        label = "▶ Live · 3 秒动态画面" if lead else "▶ Live 3s"
        live_control=(
            f'<button type="button" class="live-trigger" data-live-asset="{esc(live_asset)}" '
            f'data-live-focus-ms="{focus_ms}" data-live-caption="{esc(caption)}" '
            f'aria-label="播放原始视频的3秒动态画面：{esc(caption)}">{label}</button>'
        )
    return ('<figure class="photo' + (' is-hero' if lead else '') + '">'
            f'<a href="{esc(rel)}" target="_blank" title="打开真实图片原图"><img loading="lazy" decoding="async" src="{esc(rel)}" alt="{esc(caption)}"></a>'
            f'<figcaption>{esc(caption)}</figcaption>{live_control}</figure>')

def hhmmss(sec:float):
    h=int(sec//3600); m=int(sec%3600//60); s=sec%60
    return f"{h:02d}:{m:02d}:{s:05.2f}"

def f_id_abs_time_ms(fid: str):
    """Frame IDs encode physical source start via 10-second source index."""
    mm=re.search(r"sydney_\d{2}_(\d{6})-f\d+$",fid)
    return ((int(mm.group(1))-1)*10000) if mm else None

def source_index_from_asset(aid):
    mm=re.search(r"sydney_\d{2}_(\d{6})$",aid)
    return ((int(mm.group(1))-1)*10) if mm else None

def photo_lookup(offset):
    inp=ROOT/f"sydney-intro-cut-72s-20261105/offset_{offset:03d}/input"
    data=json.loads((inp/"bundle.json").read_text())
    frames={}
    for clip_seq,asset in enumerate(data["assets"],1):
        start=source_index_from_asset(asset["asset_id"])
        for frame in asset["frames"]:
            frames[frame["frame_id"]]={
                "path":inp/frame["relative_path"],
                "clip_seq":clip_seq,"start_s":start,
                "source_id":asset["asset_id"],
                "pts":frame.get("source_timestamp_ms") or frame.get("canonical_offset_ms") or 0
            }
    assert len(data["assets"])==160
    return frames

def photo_chapters(offset):
    file=PHOTO/f"offset_{offset:03d}/result.json"
    result=json.loads(file.read_text())
    source=photo_lookup(offset)
    chapter_blocks=[]
    pictures=0
    for i,chapter in enumerate(result["chapters"],1):
        key_moments=chapter.get("key_moments",[])
        media=chapter.get("selected_media",[])
        assert media
        gallery=[]
        shown=set()
        for j,m in enumerate(media,1):
            fid=m["representative_frame_id"]
            shown.add(fid)
            a=source[fid]
            pts=m.get("focus_pts_ms")
            if type(pts)!=int: pts=a["pts"]
            label=f"#{j} · 源片段 {a['clip_seq']}/160 · {a['source_id']} · 片内 {pts/1000:.2f}s"
            dest=ASSET/f"jpeg_{offset:03d}"/f"c{i:02d}_m{j:02d}.jpg"
            gallery.append(picture(a["path"],dest,label,lead=j==1,
                live_asset=a["source_id"],focus_ms=pts))
            pictures+=1
        moment_blocks=[]
        for j,m in enumerate(key_moments,1):
            ids=m.get("frame_ids",[])
            parts=[f'<strong>关键瞬间 {j}：</strong>{esc(m.get("description",""))}']
            for k,fid in enumerate(ids,1):
                if fid not in source:
                    parts.append(f'<span class="warn">原图 ID 无法在源输入中定位：{esc(fid)}</span>')
                    continue
                a=source[fid]
                parts.append(f'<span class="meta">真实证据：源片段 {a["clip_seq"]}，{esc(fid)}</span>')
                if fid not in shown:
                    dest=ASSET/f"jpeg_{offset:03d}"/f"c{i:02d}_key{j:02d}_{k:02d}.jpg"
                    parts.append('<div class="key-photo">'+picture(a["path"],dest,
                        f"关键瞬间真实证据 · 源片段 {a['clip_seq']}",
                        live_asset=a["source_id"],focus_ms=int(a["pts"]))+'</div>')
                    shown.add(fid)
            moment_blocks.append('<li>'+' '.join(parts)+'</li>')
        gallery_html=''.join(gallery)
        episode=(
            f'<details class="chapter" {"open" if i==1 else ""}>'
            f'<summary><div class="chapter-top">'
            f'<img loading="lazy" class="cover" src="{esc((ASSET/f"jpeg_{offset:03d}"/f"c{i:02d}_m01.jpg").relative_to(BASE).as_posix())}" alt="本章真实封面">'
            f'<div><span class="chapter-no">C{i:02d}</span> <strong>{esc(chapter["title"])}</strong>'
            f'<p class="muted">图库 {len(media)} 张 · 关键瞬间 {len(key_moments)} 条 · 点击展开全部</p>'
            f'</div></div></summary>'
            f'<div class="chapter-content"><h4>完整 Chapter Story</h4>'
            f'<p class="story">{esc(chapter["story"])}</p>'
            f'<h4>关键瞬间与对应证据</h4>'
            f'<ol class="moments">{"".join(moment_blocks) if moment_blocks else "<li>模型未提供文字关键瞬间</li>"}</ol>'
            f'<h4>全部 {len(media)} 张入选图片（首张为 HERO）</h4>'
            f'<div class="gallery">{gallery_html}</div></div></details>'
        )
        chapter_blocks.append(episode)
    return chapter_blocks,pictures

def video_chapters(offset, fps):
    key="0p5" if fps==.5 else "1p0"
    folder=VIDEO10 if offset==10 else BASE/f"video/offset_{offset:03d}"
    result=json.loads((folder/f"fps_{key}_result.json").read_text())
    chapters=result["model_output"]["chapters"]
    mapped=result["mapped_source_moments"]
    groups=defaultdict(list)
    for pos,m in enumerate(mapped,1):
        groups[m["chapter"]].append((pos,m))
    chapter_blocks=[]
    screenshots=0
    for i,chapter in enumerate(chapters,1):
        items=chapter.get("selected_moments",[])
        shown=groups.get(i,[])
        figs=[]
        for j,(source_order,m) in enumerate(shown,1):
            name=f"c{i:02d}_{source_order:03d}_{m['source_asset_id']}.jpg"
            img=folder/f"fps_{key}_original_source_stills"/name
            if not img.is_file():
                raise FileNotFoundError(str(img))
            label=(f"#{j} · {m['text']} · 原始10s片段 {m['original_global_clip_seq']}/160 · "
                   f"片内 {m['source_clip_focus_ms']/1000:.3f}s · part {m['part_id']} @ {m['part_time_ms']/1000:.2f}s")
            dest=ASSET/f"video_{offset:03d}_{key}"/f"c{i:02d}_m{j:03d}.jpg"
            figs.append(picture(img,dest,label,lead=j==1,
                live_asset=m["source_asset_id"],focus_ms=int(m["source_clip_focus_ms"])))
            screenshots+=1
        selected_positions={(m["part_id"],m["part_time_ms"],m.get("text","")) for _,m in shown}
        time_lines=[]
        for j,m in enumerate(items,1):
            part=m.get("part_id")
            ms=m.get("video_time_ms")
            text=m.get("text","")
            source_matches=(part,ms,text) in selected_positions
            flag='' if source_matches else ' <span class="warn">分块边界位置，未直接映射（保留原输出）</span>'
            time_lines.append('<li>'
                +f'<strong>Moment {j}：</strong>{esc(text)} '
                +f'<span class="meta">part {esc(part)} · {esc(ms)} ms</span>{flag}'
                +'</li>')
        chapter_blocks.append(
            f'<details class="chapter" {"open" if i==1 else ""}>'
            f'<summary><div class="chapter-top">'
            + (f'<img class="cover" loading="lazy" src="{esc((ASSET/f"video_{offset:03d}_{key}"/f"c{i:02d}_m001.jpg").relative_to(BASE).as_posix())}" alt="本章实际视频选点封面">' if shown else '')
            +f'<div><span class="chapter-no">C{i:02d}</span> <strong>{esc(chapter["title"])}</strong>'
            +f'<p class="muted">模型选点 {len(items)} · 已还原真实图片 {len(shown)} 张 · 点击展开全部</p>'
            +'</div></div></summary>'
            +f'<div class="chapter-content"><h4>完整 Chapter Story</h4>'
            +f'<p class="story">{esc(chapter["story"])}</p>'
            +'<h4>模型返回的全部 Moment 文字及时间</h4>'
            +f'<ol class="moments">{"".join(time_lines)}</ol>'
            +f'<h4>从原始 10 秒视频实际截出的 {len(shown)} 张图片</h4>'
            +f'<div class="gallery">{"".join(figs)}</div></div></details>'
        )
    return chapter_blocks,screenshots

def main():
    score=json.loads((BASE/"SIX_GROUP_COMPARISON.json").read_text())
    old=OUTPUT.read_text() if OUTPUT.exists() else None
    if old and not OLD_OVERVIEW.exists():
        OLD_OVERVIEW.write_text(old)
    headings=[
        "<!doctype html><html lang='zh-CN'><head><meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Diary One｜悉尼六组 · 完整 Chapter + 真实图片</title>",
        """<style>
        :root{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC",sans-serif;color:#15283a;background:#f5f7fb}
        *{box-sizing:border-box}body{max-width:1470px;margin:0 auto;padding:24px 18px 70px}
        h1{font-size:26px;margin:0 0 10px;line-height:1.3}h2{font-size:21px}h3{font-size:17px}h4{font-size:15px;margin:18px 0 8px}
        p{line-height:1.75;margin:8px 0}.muted{color:#6a7d8c}.meta{color:#627789;font-size:12px}
        .intro{color:#52697d}.hint{background:#fdf3e6;padding:12px;border-radius:8px}
        .tabs{display:flex;flex-wrap:wrap;gap:8px;position:sticky;top:0;z-index:20;padding:11px 0;background:#f5f7fbe8;backdrop-filter:blur(12px)}
        button{border:1px solid #ccd6e0;background:white;padding:9px 15px;border-radius:9px;cursor:pointer;font-size:14px;color:#203c52}
        button.active{background:#215a86;color:#fff;border-color:#215a86}
        button:hover{border-color:#215a86}
        .toolbar{display:flex;gap:9px;flex-wrap:wrap;margin:12px 0}
        .offset{padding:18px 0}.method{background:#fff;padding:18px 20px;border:1px solid #dce5ee;border-radius:12px;margin:18px 0}
        .method>h3{margin-top:0}.kpis{color:#506d83;font-size:13px;margin-bottom:16px}
        .chapter{border:1px solid #e0e6ec;border-radius:11px;margin:10px 0;background:#fff;overflow:hidden}
        .chapter[open]{border-color:#b7ccdc}
        .chapter summary{cursor:pointer;list-style:none;display:block}
        .chapter summary::-webkit-details-marker{display:none}
        .chapter-top{display:flex;gap:16px;align-items:center;padding:10px 13px;background:#f8fafc;min-height:100px}
        .chapter-top .cover{width:126px;height:82px;object-fit:cover;border-radius:6px}
        .chapter-top strong{font-size:16px}.chapter-no{font-weight:700;color:#286791}
        .chapter-content{padding:16px 20px 24px}
        .story{font-size:15px;line-height:1.9;white-space:pre-wrap}
        .moments{margin:8px 0;padding-left:25px}
        .moments li{padding:8px 0;border-bottom:1px solid #edf1f5;font-size:14px;line-height:1.65}
        .meta{display:inline;margin-left:6px}.warn{color:#a24d24;font-size:12px}
        .gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:12px 0}
        figure.photo{margin:0;border:1px solid #e0e7ec;background:#f6f8fa;overflow:hidden;border-radius:9px}
        figure.photo img{width:100%;height:177px;object-fit:cover;display:block}
        figure.photo figcaption{padding:10px;color:#476176;font-size:12px;line-height:1.5}
        figure.is-hero{outline:2px solid #77a5c7}
        .live-trigger{display:block;width:calc(100% - 18px);margin:0 9px 9px;
          background:#e8f3fc;border:1px solid #b4d0e5;color:#174e75;
          padding:9px 5px;border-radius:7px;cursor:pointer;font-weight:700;font-size:13px}
        .live-trigger:hover{background:#d7eaf7;border-color:#77a6cc}
        .live-dialog{border:1px solid #6e879a;border-radius:12px;background:#172b3c;
          color:white;max-width:min(92vw,820px);width:820px;padding:0;box-shadow:0 24px 70px #0007}
        .live-dialog::backdrop{background:#081827e0}
        .live-header{display:flex;gap:10px;align-items:center;justify-content:space-between;
          padding:12px 16px;background:#263d50}
        .live-header b{font-size:16px}
        .live-close{background:#fff2;color:#fff;border-color:#fff5;min-width:40px}
        .live-stage{position:relative;background:black;min-height:260px;display:flex;
          align-items:center;justify-content:center}
        #liveVideo{display:block;width:100%;max-height:60vh;object-fit:contain;background:black}
        #liveStatus{padding:12px 16px;color:#c9e0ee;font-size:14px;min-height:42px}
        #liveMeta{font-size:12px;line-height:1.55;color:#d5e4ee;padding:0 16px 10px}
        .live-footer{display:flex;justify-content:space-between;align-items:center;
          gap:12px;padding:8px 16px 14px}
        .live-footer span{font-size:12px;color:#b1c9dd}
        .key-photo .photo{max-width:310px;margin:8px 0}
        .table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;white-space:nowrap}
        td,th{padding:10px;border-bottom:1px solid #e0e7ec;text-align:left;font-size:13px}
        th{background:#f4f7fb}.hidden{display:none!important}
        .footer{margin-top:25px;color:#718295;font-size:12px}
        @media(max-width:640px){.chapter-top .cover{width:94px;height:65px}.chapter-content{padding:13px}.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}figure.photo img{height:115px}}
        </style></head><body>""",
        "<h1>Sydney Citywalk · 六偏移组完整 Chapter 与真实图库对照</h1>",
        "<p class='intro'><strong>这不是只有封面的简略页。</strong> 每章可以展开 <b>完整 story、全部图片、全部关键瞬间/时间戳及来源片段</b>。"
        "输入统一来自 Citywalk 各偏移组的 160 段真实 10 秒片段（00:00–01:20 总览已排除）。"
        "图片 V03 的历史结果直接复用，视频来自同一源片段的 0.5/1 fps 实验。点击照片可单独放大。</p>",
        "<p class='hint'>注意：20s/1fps 模型实际输出5章、79条 Moment，但4条落在200000ms分块边界，75条已从真实原视频定位并还原。"
        "保留79条原始文案供效果评价，不把结构差异当作 Chapter 不存在。</p>",
        '<div class="tabs" role="navigation" aria-label="选择偏移组">'
        +''.join(f'<button type="button" data-offset="{off}" onclick="showOffset({off})">{off}s 偏移</button>' for off in OFFSETS)
        +'</div>',
        '<div class="toolbar"><button type="button" onclick="toggleAll(true)">展开当前组全部 Chapter</button>'
        '<button type="button" onclick="toggleAll(false)">折叠当前组全部 Chapter</button></div>',
        '<div class="method"><h3>完整实验数据总览</h3><div class="table-wrap"><table>'
        '<tr><th>偏移</th><th>方法</th><th>章数</th><th>代表照片/时间点</th><th>真实模型费用 CNY</th><th>备注</th></tr>'
    ]
    chapters_count=0;image_count=0
    for row in score["rows"]:
        mode="JPEG V03" if row["method"]=="V03_JPEG" else f"纯视频 {row['fps']}fps"
        chapters_count+=int(row.get("chapter_count") or 0)
        headings.append('<tr>'
           +f'<td>{row["offset"]}s</td><td>{mode}</td><td>{row.get("chapter_count","—")}</td>'
           +f'<td>{row.get("raw_model_moment_count",row.get("selected_total","—"))}</td>'
           +f'<td>{row.get("estimated_cost_cny","—")}</td>'
           +f'<td>{esc(row.get("status"))}</td></tr>')
    headings+=['</table></div></div>']
    for offset in OFFSETS:
        headings.append(f'<section class="offset" id="offset-{offset}" data-offset-panel="{offset}"><h2>{offset}s 偏移组</h2>')
        for method,fps in (("JPEG + MobileCLIP + VLM V03",None),("纯视频 VLM · 0.5 fps",.5),("纯视频 VLM · 1 fps",1.0)):
            if fps is None:
                blocks,images=photo_chapters(offset)
            else:
                blocks,images=video_chapters(offset,fps)
            image_count+=images
            headings.append('<section class="method">'
                f'<h3>{esc(method)} · {len(blocks)} 个 Chapter</h3>'
                f'<p class="kpis">已加载完整故事及 {images} 张真实入选画面；点击每个 Chapter 标题可展开或折叠。</p>'
                +''.join(blocks)+'</section>')
        headings.append("</section>")
    headings.append("""
    <dialog class="live-dialog" id="liveDialog" aria-label="3秒动态视频预览">
      <div class="live-header"><b>▶ 原始 10 秒视频 · 3 秒 Live 预览</b>
        <button type="button" class="live-close" id="liveClose" aria-label="关闭动态视频">✕ 关闭</button>
      </div>
      <div class="live-stage"><video id="liveVideo" preload="auto" muted playsinline webkit-playsinline loop></video></div>
      <p id="liveStatus">点击图片下方的 Live 按钮播放</p>
      <p id="liveMeta"></p>
      <div class="live-footer">
        <span>从原始 10 秒视频按需导出 3 秒 MP4 · 本地缓存 · 不上传云端</span>
        <button type="button" id="liveToggle">暂停 / 继续</button>
      </div>
    </dialog>""")
    headings.append("<p class='footer'>来源：本地原始 JPEG 与原始 MP4 实际解码画面。所有语言及故事保持模型原文，无 VLM 再调用。"
                    "选帧的具体 PTS 来自输入／回放映射；这里的“完整 Chapter 内容”指现有模型实际输出内容，而非原始视频的每一帧。</p>")
    headings.append("""<script>
      const liveDialog = document.getElementById("liveDialog");
      const liveVideo = document.getElementById("liveVideo");
      const liveStatus = document.getElementById("liveStatus");
      const liveMeta = document.getElementById("liveMeta");
      let liveRange = {start:0,end:3};
      let liveReady = false;
      let liveToken = 0;
      function stopLive(){
        liveToken += 1;
        liveReady = false;
        liveVideo.pause();
        liveVideo.removeAttribute("src");
        liveVideo.load();
      }
      function closeLive(){
        stopLive();
        if (liveDialog.open) liveDialog.close();
      }
      function openLive(button){
        const asset = button.dataset.liveAsset;
        const ms = Number(button.dataset.liveFocusMs);
        if (!/^sydney_(01|02|03|05|06|07)_\\d{6}$/.test(asset) ||
            !Number.isInteger(ms) || ms<0 || ms>=10000) {
          alert("原始视频来源或时间不可验证，无法播放 Live。");
          return;
        }
        stopLive();
        const start = Math.max(0,Math.min(ms/1000-1.5,7));
        liveRange = {start:0, end:3};
        liveReady = false;
        liveStatus.textContent = "正在从 Mac 原视频提取 3 秒 Live（首次播放需要本地导出）…";
        liveMeta.textContent = asset + " · focus " + (ms/1000).toFixed(3) +
          "s · Live 窗口 " + start.toFixed(3) + "–" + (start+3).toFixed(3) +
          "s · " + button.dataset.liveCaption;
        if (!liveDialog.open) liveDialog.showModal();
        const host = (window.location.protocol==='http:' || window.location.protocol==='https:')
          ? window.location.origin : 'http://127.0.0.1:8810';
        liveVideo.src = host + "/api/live3s/" + encodeURIComponent(asset) + "/" + ms + ".mp4";
        liveVideo.load();
      }
      document.addEventListener("click",event=>{
        const button = event.target.closest("button.live-trigger");
        if (button) { event.preventDefault(); event.stopPropagation(); openLive(button); }
      });
      document.getElementById("liveClose").addEventListener("click",closeLive);
      liveDialog.addEventListener("close",stopLive);
      liveDialog.addEventListener("click", event=>{if(event.target===liveDialog)closeLive()});
      document.getElementById("liveToggle").addEventListener("click",()=>{
        if (!liveVideo.src)return;
        if(liveVideo.paused){liveVideo.play().catch(()=>{});}
        else liveVideo.pause();
      });
      liveVideo.addEventListener("loadedmetadata",()=>{
        if (!liveDialog.open)return;
        liveReady=true;
        liveStatus.textContent = "正在循环播放实际截取的 3 秒 Live…";
        liveVideo.play().catch(e=>{
          liveStatus.textContent = "视频已就绪，请点击“暂停 / 继续”播放：" + e.message;
        });
      });
      liveVideo.addEventListener("error",()=>{
        if(!liveDialog.open)return;
        liveStatus.textContent = "视频加载失败。请确认 Mac 上 Live 预览服务仍在运行：http://127.0.0.1:8810";
      });
      function showOffset(value) {
        document.querySelectorAll('[data-offset-panel]').forEach(el => {
          el.classList.toggle('hidden', Number(el.dataset.offsetPanel)!==value);
        });
        document.querySelectorAll('[data-offset]').forEach(el=>{
          const active = Number(el.dataset.offset)===value;
          el.classList.toggle('active', active);
          el.setAttribute('aria-pressed',String(active));
        });
        history.replaceState(null,'','#offset-'+value);
      }
      function toggleAll(value){
        document.querySelectorAll('.offset:not(.hidden) details.chapter').forEach(el=>{el.open=value});
      }
      const hash = Number((window.location.hash||'').replace('#offset-',''));
      showOffset([10,20,30,50,60,70].includes(hash)?hash:10);
    </script></body></html>""")
    OUTPUT.write_text('\n'.join(headings))
    manifest={"offsets":list(OFFSETS),"methods":3,"chapters":chapters_count,
              "full_selected_gallery_images":image_count,
              "key_moment_evidence_images_extra":None,
              "generator":str(Path(__file__).resolve()),
              "rendered_html":str(OUTPUT),
              "old_overview_saved":str(OLD_OVERVIEW),
              "live_preview_enabled":True,
              "live_preview_mode":"on_demand_cached_real_3s_mp4_from_original_10s_source",
              "live_preview_server":"http://127.0.0.1:8810",
              "no_new_model_calls":True}
    (BASE/"FULL_CONTENT_PAGE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print("FULL_CHAPTER_CONTENT_PAGE_READY",OUTPUT,
          "chapters",chapters_count,"selected_gallery_images",image_count,
          "actual_media_files",len(list(ASSET.glob("**/*.jpg"))),
          "html_size",OUTPUT.stat().st_size,flush=True)

if __name__=="__main__":
    main()
