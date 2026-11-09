#!/usr/bin/env python3
"""Inspect and map real VLM outputs to original Sydney video clips and photos.

No hallucinated file paths. Time suggestions are approximate, images are
re-decoded from original 10-second video and are separately audited.
"""
from __future__ import annotations
import base64
from collections import Counter
import html
import json
import math
from pathlib import Path
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

HOME=Path.home()
DIR=HOME/"Documents/Nexleap/work_logs/evidence/sydney-video-full-160-fps-ab-20261109"
FFMPEG=HOME/"miniforge3/bin/ffmpeg"
try:FONT=ImageFont.truetype("/System/Library/Fonts/PingFang.ttc",17)
except:FONT=ImageFont.load_default()

def make_still(source:Path,t:float,dest:Path):
    if dest.exists():return
    c=subprocess.run([str(FFMPEG),"-hide_banner","-loglevel","error",
         "-nostdin","-y","-ss",f"{t:.3f}","-i",str(source),
         "-frames:v","1","-vf","scale=640:-1","-q:v","3",str(dest)],
        capture_output=True,text=True,timeout=35)
    if c.returncode or not dest.exists():
        raise RuntimeError("Failed source frame: "+str(source)+" "+c.stderr[-600:])

def make_montage(pics,output):
    if not pics:raise RuntimeError("No visual moments")
    W,H,COLS=380,270,4
    canvas=Image.new("RGB",(W*COLS,H*math.ceil(len(pics)/COLS)),(247,249,252))
    draw=ImageDraw.Draw(canvas)
    for i,(p,legend) in enumerate(pics):
        x=(i%COLS)*W;y=(i//COLS)*H
        image=Image.open(p).convert("RGB")
        image.thumbnail((W-12,H-52))
        canvas.paste(image,(x+6+(W-12-image.width)//2,y+8+(H-52-image.height)//2))
        draw.text((x+5,y+H-40),legend[:43],font=FONT,fill=(21,39,64))
    canvas.save(output,quality=83,optimize=True)

def build():
    preflight=json.loads((DIR/"preflight.json").read_text())
    summaries=[]
    visuals={}
    for key in ("0p5","1p0"):
        file=DIR/f"fps_{key}_result.json"
        if not file.exists():
            print("MISSING",file)
            continue
        datum=json.loads(file.read_text())
        meta=datum["metadata"]
        result=datum["model_output"]
        links=datum["mapped_source_moments"]
        assert meta["state"]=="COMPLETE",meta["state"]
        assert [c["sha256"] for c in preflight["parts"]]==meta["video_part_sha256"]
        assert meta["prompt_sha256"]==preflight["prompt_sha256"]
        assert len(links)==meta["selected_moments_count"]
        out_dir=DIR/f"fps_{key}_original_source_stills"
        out_dir.mkdir(exist_ok=True)
        picks=[]
        per_chapter={}
        for n,item in enumerate(links):
            orig=preflight["source_clips"][item["original_global_clip_seq"]-1]
            assert orig["asset_id"]==item["source_asset_id"]
            assert int(orig["part_id"])==item["part_id"]
            assert 0<=item["source_clip_focus_ms"]<10000
            outfile=out_dir/f"c{item['chapter']:02d}_{n+1:03d}_{item['source_asset_id']}.jpg"
            make_still(Path(orig["source_mp4"]),item["source_clip_focus_ms"]/1000,outfile)
            caption=(f"C{item['chapter']:02d} "
                     f"p{item['part_id']} @ {item['part_time_ms']/1000:.1f}s "
                     f"source#{item['original_global_clip_seq']}")
            picks.append((outfile,caption))
            per_chapter.setdefault(item["chapter"],[]).append((outfile,caption))
            item["rendered_original_jpg"]=str(outfile)
        montage=DIR/f"fps_{key}_full160_montage.jpg"
        make_montage(picks,montage)
        by_chapter=DIR/f"fps_{key}_chapters"
        by_chapter.mkdir(exist_ok=True)
        for chapter_i,pics in per_chapter.items():
            make_montage(pics,by_chapter/f"chapter_{chapter_i:02d}.jpg")
        order=[]
        dup=[]
        for ch_idx in range(1, len(result["chapters"])+1):
            items=[q for q in links if q["chapter"]==ch_idx]
            source_seqs=[q["original_global_clip_seq"] for q in items]
            order.append({"chapter":ch_idx,
                "title":result["chapters"][ch_idx-1].get("title"),
                "source_min":min(source_seqs) if source_seqs else None,
                "source_max":max(source_seqs) if source_seqs else None,
                "selected":len(items)})
        dup=[(k,v) for k,v in Counter(q["original_global_clip_seq"] for q in links).items() if v>1]
        overlap=[]
        for a,b in zip(order,order[1:]):
            if a["source_max"] is not None and b["source_min"] is not None and b["source_min"]<a["source_max"]:
                overlap.append({"chapters":[a["chapter"],b["chapter"]],
                 "earlier_max_source_clip":a["source_max"],
                 "later_min_source_clip":b["source_min"]})
        han=[]
        for chapter_i,ch in enumerate(result["chapters"],1):
            for field in ["title","story"]:
                txt=ch.get(field,"")
                count=sum("\u3400"<=c<="\u9fff" for c in txt)
                if count<2:han.append(f"C{chapter_i}:{field}")
        uniqueness=len(set(q["original_global_clip_seq"] for q in links))
        s={
            "fps":meta["fps"],"model_status":meta["state"],
            "chapter_count":len(result["chapters"]),
            "chapter_titles":[x.get("title") for x in result["chapters"]],
            "selected_moments":len(links),
            "distinct_source_clips_in_selection":uniqueness,
            "source_clips_total":160,
            "selected_source_clip_coverage":round(uniqueness/160,4),
            "overlapping_adjacent_chapter_time_bounds":overlap,
            "same_source_clip_multiple_selected_moments":dup,
            "language_warning":han,
            "input_tokens":meta["prompt_tokens"],
            "output_tokens":meta["completion_tokens"],
            "estimated_cost_cny":meta["estimated_cost_cny"],
            "source_time_mapping_valid":True,
            "model_visual_facts_certified":False,
            "photo_montage":str(montage),
            "chapter_time_bounds":order,
        }
        summaries.append(s)
        visuals[key]=(s,result,links)
        print("EVALUATED",key,"chapters",len(order),"moments",len(links),
            "source_clips",uniqueness,"bad_chrono",len(overlap),
            "cost",s["estimated_cost_cny"],flush=True)
    (DIR/"FINAL_160_VIDEO_COMPARISON.json").write_text(
        json.dumps({"experiment":"FULL160_SINGLE_VLM_REQUEST_MULTI_VIDEO_FPS_AB",
        "original_source_clips":160,"part_count":8,
        "video_input_seconds":1600,"video_sha256_per_part":[p["sha256"] for p in preflight["parts"]],
        "same_model_and_prompt":True,
        "only_changed_input_param":"video_url.fps",
        "semantic_judge_not_completed":True,
        "results":summaries},ensure_ascii=False,indent=2))
    page=[
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>悉尼Citywalk完整160段视频 VLM 0.5fps/1fps 对照</title>",
        """<style>body{max-width:1250px;margin:auto;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;color:#1c354d;background:#f4f7fb;padding:26px}section{border-radius:12px;background:white;padding:18px;margin:18px 0;border:1px solid #e4eaf0}article{border-top:1px solid #e4eaf0;padding:13px 0}h1{font-size:25px}h2{font-size:20px}h3{font-size:17px}p{line-height:1.75}img{width:100%;height:auto;border-radius:5px}small{color:#748496}table{width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #dce4eb;padding:10px}code{font-size:12px}</style></head><body>""",
        "<h1>Sydney Citywalk · 全部160段10秒视频：0.5 fps / 1 fps 实验</h1>",
        "<p>同一160个源视频片段，8个200秒分析视频块，按真实时间顺序一次发送给同一个 VLM。两个请求唯一差异是 video_url.fps。字幕/音频未参与理解。模型选点 JPG 均从真实原始10秒MP4重新截取。</p>",
        "<section><h2>API usage与结构指标</h2><table><tr><th>FPS</th><th>输入Tokens</th><th>输出Tokens</th><th>估算费用CNY</th><th>Chapter</th><th>重要瞬间</th><th>选中片段数</th></tr>",
    ]
    for s in summaries:
        page.append(f"<tr><td>{s['fps']}</td><td>{s['input_tokens']}</td><td>{s['output_tokens']}</td><td>{s['estimated_cost_cny']}</td><td>{s['chapter_count']}</td><td>{s['selected_moments']}</td><td>{s['distinct_source_clips_in_selection']}/160</td></tr>")
    page.append("</table><small>结构校验和来源映射通过，并不代表视觉地点真实性已核验。不同抽帧率每组仅一次调用，不构成统计显著性判断。</small></section>")
    for key,(s,result,links) in visuals.items():
        page.append(f"<section><h2>{s['fps']} fps：{s['chapter_count']} Chapter</h2>")
        for i,c in enumerate(result["chapters"],1):
            ch_links=[m for m in links if m['chapter']==i]
            page.append(f"<article><h3>C{i:02d} · {html.escape(c.get('title',''))}</h3><p>{html.escape(c.get('story',''))}</p>")
            for m in ch_links:
                page.append(f"<p><small>{html.escape(m.get('text',''))} · 视频part{m['part_id']}时刻{m['part_time_ms']/1000:.1f}s · 原片段#{m['original_global_clip_seq']} · 原片内{m['source_clip_focus_ms']/1000:.1f}s</small></p>")
            jpg=DIR/f"fps_{key}_chapters/chapter_{i:02d}.jpg"
            if jpg.is_file():
                page.append("<img src='data:image/jpeg;base64,"+base64.b64encode(jpg.read_bytes()).decode()+"'/>")
            page.append("</article>")
        page.append("</section>")
    page.append("</body></html>")
    dest=DIR/"FULL160_VIDEO_FPS_0P5_VS_1P0_REAL_IMAGES.html"
    dest.write_text("\n".join(page))
    print("GALLERY_HTML",dest,dest.stat().st_size,"bytes",flush=True)

if __name__=="__main__":build()
