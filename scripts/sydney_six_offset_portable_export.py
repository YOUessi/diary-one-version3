#!/usr/bin/env python3
"""Export the real six-group Chapter review as portable offline HTML + 3s Live.

No provider calls. Never modify original 10s video, model outputs or usage.
Public distribution of third-party Prowalk Tours imagery requires permission.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
from shutil import copy2
import hashlib,json,os,re,subprocess,zipfile

HOME=Path.home()
ROOT=HOME/"Documents/Nexleap"
SOURCE=ROOT/"work_logs/evidence/sydney-six-offset-image-vs-video-20261109"
REPO=ROOT/"Diary_one_chapter_v2"
VIDEO=HOME/"Downloads/视频切分_10s_悉尼_20261027/sydney"
FFMPEG=HOME/"miniforge3/bin/ffmpeg"
FFPROBE=HOME/"miniforge3/bin/ffprobe"
DEST=ROOT/"work_logs/evidence/Nexleap_One_Sydney_Portable_Share_20261109"
SITE=DEST/"Nexleap_One_Sydney"
LIVE=SITE/"media/live3s"
ASSET_RE=re.compile(r"sydney_(?:01|02|03|05|06|07)_(\d{6})$")
MODEL_NAME="SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html"
MODEL_MARK='<script id="chapter-data" type="application/json">'

def source_data():
    html=(SOURCE/MODEL_NAME).read_text()
    obj=json.loads(html.split(MODEL_MARK,1)[1].split("</script>",1)[0])
    assert len(obj["offsets"])==6
    return obj

def all_photos(data):
    images=[image for group in data["groups"].values()
            for method in group.values()
            for chapter in method["chapters"]
            for image in chapter["photos"]]
    assert len(images)==701,len(images)
    for i in images:
        assert (SOURCE/i["src"]).is_file(),i
        assert ASSET_RE.fullmatch(i["sourceAsset"]),i
        assert type(i["focusMs"])==int and 0<=i["focusMs"]<10000,i
    return images

def origin(asset):
    m=ASSET_RE.fullmatch(asset)
    assert m,asset
    num=int(m.group(1))
    assert (num-1)*10>=80,asset
    files=list(VIDEO.glob(f"sydney_{num:06d}_*.mp4"))
    assert len(files)==1,(asset,files)
    f=files[0].resolve()
    assert VIDEO.resolve() in f.parents
    return f

def name(asset,ms):
    return f"{asset}_focus{ms:04d}_3s.mp4"

def valid(path):
    if not path.is_file() or path.stat().st_size<2000:return False
    r=subprocess.run([str(FFPROBE),"-v","error","-select_streams","v:0",
        "-show_entries","stream=codec_name,width,height,nb_frames:format=duration",
        "-of","json",str(path)],capture_output=True,text=True,timeout=20)
    if r.returncode:return False
    try:
        data=json.loads(r.stdout);s=data["streams"][0]
        return s["codec_name"]=="h264" and int(s["width"])==640 and \
               int(s["height"])==360 and int(s["nb_frames"])==72 and \
               2.95<=float(data["format"]["duration"])<=3.05
    except (ValueError,KeyError,IndexError,TypeError):
        return False

def render_video(pair):
    asset,ms=pair
    target=LIVE/name(asset,ms)
    if valid(target):return target.stat().st_size,"REUSED"
    src=origin(asset)
    begin=max(0.,min(ms/1000.-1.5,7.))
    temp=target.with_name("."+target.stem+".tmp.mp4")
    cmd=[str(FFMPEG),"-hide_banner","-loglevel","error","-nostdin","-y",
         "-ss",f"{begin:.3f}","-i",str(src),"-t","3.0","-an",
         "-vf","fps=24,scale=640:360:flags=fast_bilinear,format=yuv420p",
         "-frames:v","72","-c:v","libx264","-preset","ultrafast",
         "-crf","29","-threads","1","-movflags","+faststart",str(temp)]
    done=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    if done.returncode or not valid(temp):
        temp.unlink(missing_ok=True)
        raise RuntimeError(f"Failed 3s MP4 {asset}/{ms}: {done.stderr[-400:]}")
    os.replace(temp,target)
    return target.stat().st_size,"CREATED"

def prepare(photos):
    SITE.mkdir(parents=True,exist_ok=True)
    LIVE.mkdir(parents=True,exist_ok=True)
    unique=sorted(set(x["src"] for x in photos))
    for path in unique:
        src=SOURCE/path;dest=SITE/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.is_file() or dest.stat().st_size!=src.stat().st_size:
            copy2(src,dest)
    print("STILLS_READY",len(unique),"bytes",
          sum((SITE/x).stat().st_size for x in unique),flush=True)
    for file in ("nexleap.css",):
        copy2(SOURCE/file,SITE/file)
    auto=(SOURCE/"nexleap-autolive.js").read_text()
    old='player.src = serverBase + "/api/live3s/" + key + ".mp4";'
    new='player.src = "media/live3s/" + key.split("/")[0] + "_focus" + key.split("/")[1].padStart(4,"0") + "_3s.mp4";'
    assert auto.count(old)==1
    auto=auto.replace(old,new)
    (SITE/"nexleap-autolive.js").write_text(auto)
    ui=(SOURCE/"nexleap.js").read_text()
    old='v.src=host+"/api/live3s/"+encodeURIComponent(p.sourceAsset)+"/"+p.focusMs+".mp4";'
    new='v.src="media/live3s/"+p.sourceAsset+"_focus"+String(p.focusMs).padStart(4,"0")+"_3s.mp4";'
    assert ui.count(old)==1
    ui=ui.replace(old,new)
    (SITE/"nexleap.js").write_text(ui)
    (SITE/"index.html").write_text((SOURCE/MODEL_NAME).read_text())
    readme="""NEXLEAP ONE | SYDNEY CITYWALK OFFLINE REVIEW

HOW TO OPEN:
1. Extract the ZIP. Keep all folders together.
2. Double-click Nexleap_One_Sydney/index.html and open in Chrome/Edge.
3. Choose offset and algorithm; browse Day timeline / Chapter content.
4. Live images autoplay as real silent 3s MP4s when visible.

No Internet, API key, Mac computer, local server or installation required.
If your browser blocks playback from a file URL, open this folder in a
terminal, run: python3 -m http.server 8080, then open 127.0.0.1:8080.

Included: 6 offsets, 3 VLM pipelines, 129 Chapter outputs, 701 real
selected JPG photos, 694 unique source-accurate 3-second video excerpts.
Original research JSON, full-length recordings, and secrets are NOT
included. Model-generated titles/stories have not been changed.

The source Citywalk recording is from Prowalk Tours. This bundle is for
authorized internal evaluation. Re-sharing the stills and video excerpts
may require rights-holder permission; do not publish as a public
commercial website without securing distribution rights.

Live is an MP4 effect, not Apple Photos native HEIC/MOV Live Photo.
All notes and favorites remain in each browser's local storage.
"""
    (SITE/"README_如何观看.txt").write_text(readme)
    assert all((SITE/x).is_file() for x in
        ("index.html","nexleap.js","nexleap-autolive.js","nexleap.css"))
    print("OFFLINE_HTML_READY",SITE/"index.html",flush=True)

def package(jobs):
    assert len(jobs)==694
    bad=[x for x in jobs if not valid(LIVE/name(*x))]
    if bad:raise RuntimeError(f"{len(bad)} missing offline clips: {bad[:4]}")
    files=sorted(x for x in SITE.rglob("*") if x.is_file())
    assert len([x for x in files if x.suffix==".mp4"])==694
    manifest={
      "version":"NEXLEAP_ONE_SYDNEY_OFFLINE_V1",
      "date_utc":datetime.now(timezone.utc).isoformat(),
      "chapters":129,"selected_images":701,"unique_live_clips":694,
      "no_original_10s_or_5h_video":True,
      "no_provider_secrets":True,"no_mac_localhost_needed":True,
      "total_uncompressed_bytes":sum(x.stat().st_size for x in files),
      "source_rights":"Third-party footage; public reuse needs permission",
    }
    (SITE/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    files=sorted(x for x in SITE.rglob("*") if x.is_file())
    dest=DEST/"Nexleap_One_Sydney_6Groups_Offline_Live_20261109.zip"
    print("PACKAGE_STARTED",len(files),"files",manifest["total_uncompressed_bytes"],"bytes",flush=True)
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_STORED,allowZip64=True) as out:
        for f in files:out.write(f,f.relative_to(DEST))
    with zipfile.ZipFile(dest) as z:
        corrupt=z.testzip()
        if corrupt:raise RuntimeError(f"CRC failed: {corrupt}")
    digest=hashlib.sha256()
    with dest.open("rb") as f:
        while b:=f.read(1048576):digest.update(b)
    (DEST/"SHARE_BUNDLE_STATUS.json").write_text(json.dumps({
      "zip_path":str(dest),"zip_size":dest.stat().st_size,
      "sha256":digest.hexdigest(),"manifest":manifest
    },indent=2,ensure_ascii=False))
    print("ZIP_VALIDATED",dest,"bytes",dest.stat().st_size,flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["prepare","render","zip","all"])
    parser.add_argument("--workers",type=int,default=4)
    args=parser.parse_args()
    media=all_photos(source_data())
    prepare(media)
    if args.action=="prepare":return
    jobs=sorted(set((p["sourceAsset"],p["focusMs"]) for p in media))
    assert len(jobs)==694
    if args.action in ("all","render"):
        total=created=reused=0
        print("START_RENDER_3S",len(jobs),"unique",flush=True)
        with ThreadPoolExecutor(max_workers=max(1,min(args.workers,6))) as pool:
            fs=[pool.submit(render_video,j) for j in jobs]
            for i,f in enumerate(as_completed(fs),1):
                size,status=f.result()
                total+=size
                created+=status=="CREATED"
                reused+=status=="REUSED"
                if i%20==0 or i==len(jobs):
                    print("RENDER_PROGRESS",i,len(jobs),
                          "created",created,"reused",reused,
                          "MB",round(total/1048576,2),flush=True)
    if args.action in ("all","zip"):package(jobs)

if __name__=="__main__":
    main()
