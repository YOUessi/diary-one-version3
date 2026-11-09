#!/usr/bin/env python3
"""Side-by-side 6-offset actual evidence comparison, no new model API requests.

Image V03 thumbnails are original selected JPEGs; video thumbnails are
re-decoded from original 10s MP4 at model-chosen video time points.
"""
import html,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

HOME=Path.home()
DATA=HOME/"Documents/Nexleap/work_logs/evidence"
ROOT=DATA/"sydney-six-offset-image-vs-video-20261109"
OLD=DATA/"sydney-direct-vlm-compact-v03-20261105"
VIDEO10=DATA/"sydney-video-full-160-fps-ab-20261109"
OFFSETS=(10,20,30,50,60,70)
OUT=ROOT/"comparative_posters";OUT.mkdir(exist_ok=True)
try: FONT=ImageFont.truetype("/System/Library/Fonts/PingFang.ttc",16)
except:FONT=ImageFont.load_default()

def photo_frame_map(off):
    p=DATA/f"sydney-intro-cut-72s-20261105/offset_{off:03d}/input"
    m=json.loads((p/"bundle.json").read_text())
    return {f["frame_id"]:(p/f["relative_path"],i+1)
            for i,a in enumerate(m["assets"]) for f in a["frames"]}
def thumb(file, destination):
    if destination.exists():return
    image=Image.open(file).convert("RGB")
    image.thumbnail((400,260))
    canvas=Image.new("RGB",(400,260),(236,239,243))
    canvas.paste(image,((400-image.width)//2,(260-image.height)//2))
    canvas.save(destination,quality=83,optimize=True)
def get_image_chapters(off):
    src=json.loads((OLD/f"offset_{off:03d}/result.json").read_text())
    frames=photo_frame_map(off)
    posts=[]
    for i,ch in enumerate(src["chapters"],1):
        fid=ch["selected_media"][0]["representative_frame_id"]
        f,seq=frames[fid]
        dest=OUT/f"offset_{off:03d}_jpeg_c{i:02d}.jpg"
        thumb(f,dest)
        selections=[frames[m["representative_frame_id"]][1] for m in ch["selected_media"]]
        posts.append({"chapter":i,"title":ch["title"],"story":ch["story"],
          "photo":dest.name,"selected_count":len(selections),
          "first_clip":min(selections),"last_clip":max(selections)})
    return posts
def get_video_chapters(off,fps):
    key="0p5" if fps==.5 else "1p0"
    folder=VIDEO10 if off==10 else ROOT/f"video/offset_{off:03d}"
    f=folder/f"fps_{key}_result.json"
    if not f.is_file():return []
    data=json.loads(f.read_text())
    model=data["model_output"];moments=data["mapped_source_moments"]
    posts=[]
    for i,ch in enumerate(model.get("chapters",[]),1):
        frames=sorted((folder/f"fps_{key}_original_source_stills").glob(f"c{i:02d}_*.jpg"))
        if not frames:
            continue
        dest=OUT/f"offset_{off:03d}_video{key}_c{i:02d}.jpg"
        thumb(frames[0],dest)
        picks=[m for m in moments if m["chapter"]==i]
        clips=[m["original_global_clip_seq"] for m in picks]
        posts.append({"chapter":i,"title":ch["title"],"story":ch.get("story",""),
          "photo":dest.name,
          "selected_count":len(ch.get("selected_moments",[])),
          "mapped_count":len(picks),
          "first_clip":min(clips) if clips else None,
          "last_clip":max(clips) if clips else None})
    return posts
def render():
    score=json.loads((ROOT/"SIX_GROUP_COMPARISON.json").read_text())
    pairs={}
    for off in OFFSETS:
        pairs[off]={
            "JPEG+VLM V03":get_image_chapters(off),
            "视频 VLM · 0.5 fps":get_video_chapters(off,.5),
            "视频 VLM · 1 fps":get_video_chapters(off,1.0)}
    css=""":root{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;color:#162b40;
    background:#f5f7fa}body{max-width:1510px;padding:28px 20px;margin:auto}
    h1{font-size:26px;margin:0 0 12px}h2{font-size:21px}h3{font-size:16px}
    p{line-height:1.6}nav a{display:inline-block;margin:8px;color:#235990}
    section{margin:22px 0;padding:22px;background:#fff;border:1px solid #e0e7ee;border-radius:12px}
    table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #dce5ee;text-align:left}
    .category{font-size:18px;font-weight:700;padding:10px 0;margin-top:12px;border-bottom:2px solid #e5ecf4}
    .chapters{display:flex;gap:13px;flex-wrap:wrap;padding:12px 0}
    .card{width:219px;max-width:100%;background:#fff;border:1px solid #d7e0e9;border-radius:8px;overflow:hidden}
    .card img{width:100%;aspect-ratio:20/13;object-fit:cover;background:#eee}
    .card .txt{padding:9px}.card strong{font-size:13px;line-height:1.4;display:block;min-height:34px}
    .card small{color:#718294;display:block;font-size:11px}
    .card p{font-size:11px;line-height:1.5;color:#516373;min-height:35px}
    .warn{background:#fff7e6;border:1px solid #f0c47c;border-radius:8px;padding:13px}
    """;
    page=["<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>",
          "<meta name='viewport' content='width=device-width,initial-scale=1'>",
          "<title>Sydney 6组｜JPEG+VLM vs 纯视频VLM 对照</title>",
          "<style>"+css+"</style></head><body>",
          "<h1>悉尼 Citywalk：六偏移组 · 真实 Chapter 与代表画面对照</h1>",
          "<p>每组原始 10 秒视频来源一致，全部 160 段，剔除 00:00–01:20 总览。图片模型来自已保存的 V03 历史结果；"
          "视频 0.5/1 fps 来自真实 8 块视频的一次全局模型调用。图片和视频 Prompt/输出协议不同，不能视为只改变单个变量的消融实验。</p>",
          "<p class='warn'>20s / 1 fps 的原始输出包含 5 个 Chapter、79 个视频时间点，但其中 4 个位置等于200秒分块边界，"
          "因此只有75个直接可映射的位置；展示语义结果，不把它错误地当作没有产生Chapter，也不重新调用模型。"
          "其余场景的名称是否完全属实，需要逐章人工视觉核对；章节数、入选图数不是准确率。</p>",
          "<nav>"+"".join(f"<a href='#offset-{off}'>{off}s</a>" for off in OFFSETS)+"</nav>",
          "<section><h2>模型输出与费用（完成的数据）</h2>",
          "<table><tr><th>偏移</th><th>方法</th><th>状态</th><th>Chapter</th><th>选中图/点</th><th>费用 ¥</th></tr>"]
    for off in OFFSETS:
        for a in score["rows"]:
            if a["offset"]!=off:continue
            variant=("JPEG V03" if a["method"]=="V03_JPEG" else f"Video {a['fps']}fps")
            page.append(f"<tr><td>{off}s</td><td>{variant}</td><td>{html.escape(a['status'])}</td>"
                        f"<td>{a.get('chapter_count','—')}</td><td>{a.get('selected_total','—')}</td>"
                        f"<td>{a.get('estimated_cost_cny','—')}</td></tr>")
    page.append("</table></section>")
    for off in OFFSETS:
        page.append(f"<section id='offset-{off}'><h2>偏移 {off}s</h2>")
        for typ,chapters in pairs[off].items():
            page.append(f"<div class='category'>{html.escape(typ)} · {len(chapters)} 个 Chapter</div>")
            if not chapters:
                page.append("<p>尚未完成视频实测或图片复原。</p>")
                continue
            page.append("<div class='chapters'>")
            for c in chapters:
                note=(f"选中 {c['selected_count']} · 源片 #{c['first_clip']}–{c['last_clip']}")
                if "mapped_count" in c and c["mapped_count"]!=c["selected_count"]:
                    note+=f" · 有效映射 {c['mapped_count']}"
                page.append(
                    f"<div class='card'><img loading='lazy' src='comparative_posters/{c['photo']}' alt='source frame'>"
                    f"<div class='txt'><strong>C{c['chapter']:02d} · {html.escape(c['title'])}</strong>"
                    f"<small>{note}</small>"
                    f"<p>{html.escape(c['story'][:110])}</p></div></div>"
                )
            page.append("</div>")
        page.append("</section>")
    page.append("<p>图片是各组最终 Chapter 真实入选的封面帧；视频封面由模型时间点重新在原始 MP4 中解码，非图像生成。"
                "本页面可比较章节主题和封面覆盖，但不代表全部关键瞬间的盲评结果。</p></body></html>")
    target=ROOT/"SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html"
    target.write_text("\n".join(page))
    print("SIX_GROUP_VISUAL_DASHBOARD",target,target.stat().st_size,
          "thumbnails",len(list(OUT.glob("*.jpg"))),flush=True)
if __name__=="__main__":render()
