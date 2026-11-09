#!/usr/bin/env python3
"""Build Tokyo + Manning Park example landing and optional portable ZIP."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,zipfile

HOME=Path.home()
ROOT=HOME/"Documents/Nexleap"
BASE=ROOT/"work_logs/evidence/nexleap-tokyo-manning-share-20261109"
SITE=BASE/"site"
SYN_FAV=ROOT/"work_logs/evidence/Nexleap_One_Sydney_Portable_Share_20261109/github-pages-worktree/favicon.svg"
MARK='<script id="chapter-data" type="application/json">'

def build():
    favicon=SITE/"favicon.svg"
    if SYN_FAV.is_file():shutil.copy2(SYN_FAV,favicon)
    else:favicon.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#292721"/><text x="15" y="47" font-size="42" fill="white" font-family="sans-serif">n</text></svg>')
    info={}
    for city in ("tokyo","manning-park"):
        doc=SITE/city/"index.html"
        s=doc.read_text()
        raw=s.split(MARK,1)[1].split("</script>",1)[0]
        data=json.loads(raw)
        imgs=[x["photos"][0]["src"] for group in data["groups"].values()
              for m in group.values() for x in m["chapters"]]
        first=imgs[0]
        if '<meta name="robots"' not in s:
            s=s.replace('<meta name="theme-color" content="#f8f7f3">',
                '<meta name="theme-color" content="#f8f7f3">\n<meta name="robots" content="noindex,nofollow">')
            doc.write_text(s)
        info[city]={"hero":first,
          "chapters":sum(len(m["chapters"]) for group in data["groups"].values() for m in group.values()),
          "finals":sum(m["mediaCount"] for group in data["groups"].values() for m in group.values()),
          "all":sum(m["allImageCount"] for group in data["groups"].values() for m in group.values())}
    landing=SITE/"examples"
    landing.mkdir(exist_ok=True)
    html="""<!doctype html><html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#f8f7f3"><meta name="robots" content="noindex,nofollow">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<title>Nexleap One · Chapter 范例库</title>
<style>
:root{--paper:#f8f7f3;--ink:#272624;--muted:#888079}
*{box-sizing:border-box}body{background:var(--paper);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;max-width:1330px;padding:38px clamp(18px,5vw,68px);margin:auto}
h1{font-size:clamp(36px,5vw,62px);letter-spacing:-2px;line-height:1.08;margin:40px 0 22px}
.brand{font-size:22px;font-style:italic;letter-spacing:-.8px;font-weight:850;display:flex;gap:10px;align-items:center}
.symbol{width:35px;height:35px;border:2px solid #292725;border-radius:11px;display:grid;place-items:center;transform:rotate(-9deg)}
.pill{display:inline-block;color:#926944;font-size:11px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;margin-top:54px}
.intro{font-size:17px;color:#807971;line-height:1.8;max-width:680px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;margin:48px 0}
.card{display:block;text-decoration:none;color:inherit;background:#fff;border:1px solid #e7e2db;border-radius:22px;overflow:hidden;box-shadow:0 10px 30px #332a210d;transition:transform .18s,box-shadow .18s}
.card:hover{transform:translateY(-5px);box-shadow:0 17px 40px #332a211b}
.card img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover}
.copy{padding:22px}.copy h2{font-size:23px;margin:0 0 13px;letter-spacing:-.55px}.copy p{font-size:13px;line-height:1.7;color:#7c766d;margin:0 0 17px}
.copy span{font-size:12px;color:#966d4a;font-weight:750}
.note{padding:18px 22px;border:1px solid #e5ded5;border-radius:13px;background:#fcf9f3;color:#77685c;font-size:13px;line-height:1.7}
footer{padding:34px 0;color:#a19a91;font-size:12px}
</style></head><body>
<div class="brand"><span class="symbol">n</span> Nexleap one</div>
<span class="pill">THE CHAPTER COLLECTION</span>
<h1>把每段旅程<br>重新读成一个故事。</h1>
<p class="intro">三组目的地范例，采用同样的 Day 时间线与 Chapter 阅读体验。每张照片都来自实际实验或人工标注素材。</p>
<div class="grid">
<a class="card" href="../tokyo/"><img src="../tokyo/PLACEHOLDER_TOKYO" alt="东京城市漫步实际照片">
<div class="copy"><h2>东京 Citywalk</h2><p>从新宿御苑、浅草寺到涩谷与六本木，六段人工整理的春日城市故事。</p><span>6 CHAPTERS · 47 SELECTED PHOTOS</span></div></a>
<a class="card" href="../manning-park/"><img src="../manning-park/PLACEHOLDER_MANNING" alt="Manning Park 徒步真实照片">
<div class="copy"><h2>Manning Park</h2><p>BC 山谷草甸、林间野花与 Lightning Lake。可以切换 0s、10s、20s 三组。</p><span>3 OFFSETS · 49 SELECTED PHOTOS</span></div></a>
<a class="card" href="https://youessi.github.io/diary-one-version3/"><img src="../nexleap_editorial_media/jpeg_010/c01_m01.jpg" alt="悉尼城市漫步真实照片">
<div class="copy"><h2>Sydney Citywalk</h2><p>六个偏移组、三种 VLM 路线与自动播放的真实 3 秒 Live 动态回忆。</p><span>129 CHAPTERS · 694 LIVE CLIPS</span></div></a>
</div>
<div class="note">东京和 Manning Park 的仓库只有真实抽帧照片、人工整理的 Chapter 和标注信息，不包含对应的原始 10 秒 MP4；因此这两组暂时只展示静态照片，不会把照片动画冒充 Live。悉尼示例包含已核实的原片 Live。</div>
<footer>© Nexleap One Research Preview · GitHub Pages 静态展示 · 不含私人 API 密钥</footer>
</body></html>"""
    html=html.replace("PLACEHOLDER_TOKYO",info["tokyo"]["hero"]).replace("PLACEHOLDER_MANNING",info["manning-park"]["hero"])
    (landing/"index.html").write_text(html)
    for city in ("tokyo","manning-park"):
        assert (SITE/city/info[city]["hero"]).is_file()
    print("PORTAL_READY",landing/"index.html",info,flush=True)

def package():
    output=BASE/"Nexleap_One_Tokyo_ManningPark_Offline_20261109.zip"
    files=sorted(p for p in SITE.rglob("*") if p.is_file())
    assert sum(x.suffix.lower()==".jpg" for x in files)==643
    with zipfile.ZipFile(output,"w",zipfile.ZIP_STORED) as z:
        for file in files:z.write(file,file.relative_to(SITE.parent))
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
    print("PORTABLE_ZIP_READY",output,output.stat().st_size,len(files),flush=True)
    download=HOME/"Downloads"/output.name
    shutil.copy2(output,download)
    with zipfile.ZipFile(download) as z:
        assert z.testzip() is None
    print("DOWNLOADS_ZIP_READY",download,flush=True)

if __name__=="__main__":
    build()
    package()
