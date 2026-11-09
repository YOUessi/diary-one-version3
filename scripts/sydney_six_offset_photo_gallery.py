#!/usr/bin/env python3
"""Only render existing local JPEG V03 baseline; never invoke provider."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import Counter
import json,html,base64
R=Path.home()/"Documents/Nexleap/work_logs/evidence"
B=R/"sydney-six-offset-image-vs-video-20261109"
V03=R/"sydney-direct-vlm-compact-v03-20261105"
PHASE=(10,20,30,50,60,70)
out=B/"image_existing_gallery"
out.mkdir(parents=True,exist_ok=True)
try:font=ImageFont.truetype('/System/Library/Fonts/PingFang.ttc',16)
except:font=ImageFont.load_default()
css="""
body{background:#f5f7fb;font:15px -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;
color:#1c3448;max-width:1380px;margin:auto;padding:26px}
h1{font-size:26px}h2{font-size:21px}h3{font-size:17px}
p{line-height:1.7}small{color:#66788a}section{padding:18px 20px;border:1px solid #dfe5ed;
background:white;border-radius:13px;margin:20px 0}article{padding:12px 0;border-top:1px solid #e4ebf1}
img{max-width:100%;border-radius:6px}
nav a{margin-right:14px;color:#23629c}
"""
page=["<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>",
      "<meta name='viewport' content='width=device-width,initial-scale=1'>",
      "<title>Sydney 六偏移历史 JPEG VLM 图库（不重复调用）</title>",
      "<style>"+css+"</style></head><body>",
      "<h1>悉尼 Citywalk · 六组已有 JPEG＋VLM V03 真实图库</h1>",
      "<p>本页完全由已存在的历史真实 V03 结果及原始输入 JPEG 生成；未重新调用任何图片模型。"
      "10s 与 70s 组的旧结果含英文内容，按原文保留供对照；结构成功不代表视觉事实正确。</p>",
      "<nav>"+" ".join(f"<a href='#offset-{n}'>{n}s</a>" for n in PHASE)+"</nav>"]
for off in PHASE:
    raw=json.loads((V03/f"offset_{off:03d}/result.json").read_text())
    data=json.loads((V03/f"offset_{off:03d}/status.json").read_text())
    inp=R/f"sydney-intro-cut-72s-20261105/offset_{off:03d}/input"
    bundle=json.loads((inp/"bundle.json").read_text())
    indices={}
    for seq,asset in enumerate(bundle["assets"],1):
        for frame in asset["frames"]:
            indices[frame["frame_id"]]=(inp/frame["relative_path"],seq)
    page += [f"<section id='offset-{off}'><h2>{off}s 偏移</h2>",
        f"<p><small>输入 {data['source_frames']} JPEG · {len(raw['chapters'])} Chapter · "
        f"{data['gallery_count']} 入选图库 · 模型 {data['model_calls']} 次 · ¥{data['cost_cny_est']:.7f}（历史）</small></p>"]
    for cidx,ch in enumerate(raw["chapters"],1):
        selected=ch["selected_media"]
        count=len(selected)
        width=290
        margin=11
        h=215
        sheet=Image.new("RGB",(count*width,h),(247,249,252))
        draw=ImageDraw.Draw(sheet)
        for i,media in enumerate(selected):
            fid=media["representative_frame_id"]
            image_file,seq=indices[fid]
            if not image_file.is_file():
                raise FileNotFoundError(image_file)
            image=Image.open(image_file).convert("RGB")
            image.thumbnail((width-2*margin,173))
            x=i*width+(width-image.width)//2
            sheet.paste(image,(x,5))
            draw.text((i*width+margin,183),f"SOURCE CLIP #{seq} {'HERO' if i==0 else ''}",
                font=font,fill=(20,43,62))
        dest=out/f"offset_{off:03d}_C{cidx:02d}_images.jpg"
        sheet.save(dest,quality=84,optimize=True)
        page.extend([
            f"<article><h3>C{cidx:02d} · {html.escape(ch['title'])}</h3>",
            f"<p>{html.escape(ch['story'])}</p>",
            f"<small>{count} 张 JPEG · 均为原始选定真实照片，首张为 HERO</small>",
            f"<p style='overflow-x:auto'><img src='image_existing_gallery/{dest.name}' "
            f"alt='{off}s C{cidx} real JPEG' style='max-width:none;width:auto;height:215px'/></p></article>"
        ])
    page.append("</section>")
page.append("<p>注意：这里的V03是统一旧基线；最新版V04b已单独测试10s但不是六组统一的同版结果。</p></body></html>")
file=B/"EXISTING_JPEG_V03_SIX_OFFSETS_REAL_IMAGES.html"
file.write_text("\n".join(page))
print('CREATED_PHOTO_BASELINE_VIEW',file, 'chapters',sum(len(json.loads((V03/f"offset_{off:03d}/result.json").read_text())['chapters']) for off in PHASE),'html_bytes',file.stat().st_size)
