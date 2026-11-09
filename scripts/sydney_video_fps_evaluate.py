#!/usr/bin/env python3
"""Map Qwen time proposals back to original 10-second sources and render real frames."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, subprocess

ROOT=Path.home()/"Documents/Nexleap/work_logs/evidence/sydney-video-fps-ab-20261109"
FFMPEG=Path.home()/"miniforge3/bin/ffmpeg"
VIDEO=ROOT/"concat_16clips_160s_640x360.mp4"
source=json.loads((ROOT/"source_time_map.json").read_text())
clips=source["clips"]
reports=[]
try: font=ImageFont.truetype("/System/Library/Fonts/PingFang.ttc",16)
except: font=ImageFont.load_default()
for key in ("0p5","1p0"):
    row=json.loads((ROOT/f"fps_{key}_result.json").read_text())
    conf=row["summary"]
    assert conf["state"]=="COMPLETE"
    assert conf["video_sha256"]==json.loads((ROOT/"preflight.json").read_text())["output_sha256"]
    assert conf["prompt_sha256"]==json.loads((ROOT/f"fps_{key}_status.json").read_text())["prompt_sha256"]
    out=ROOT/f"fps_{key}_real_moments"
    out.mkdir(exist_ok=True)
    spots=[]
    gallery=[]
    for ci,chapter in enumerate(row["model_result"]["chapters"],1):
        for mi,moment in enumerate(chapter["selected_moments"],1):
            ms=moment["video_time_ms"]
            assert type(ms)==int and 0<=ms<160000
            t=ms/1000
            slot=min(int(t//10),15)
            entry=clips[slot]
            clip_ms=ms-slot*10000
            assert 0<=clip_ms<10000
            original_ms=entry["source_start_s"]*1000+clip_ms
            outfile=out/f"c{ci:02d}_m{mi:02d}_t{ms:06d}.jpg"
            if not outfile.exists():
                p=subprocess.run([str(FFMPEG),"-hide_banner","-loglevel","error","-nostdin","-y",
                                  "-ss",str(t),"-i",str(VIDEO),"-frames:v","1",
                                  "-q:v","3",str(outfile)],capture_output=True,text=True,timeout=20)
                assert p.returncode==0 and outfile.is_file(),p.stderr[-300:]
            spot={"chapter_number":ci,"chapter_title":chapter["title"],"moment_number":mi,
                  "video_time_ms":ms,
                  "input_slot":slot+1,"original_asset_id":entry["source_asset_id"],
                  "source_video_time_ms":original_ms,
                  "source_video_in_clip_ms":clip_ms,
                  "description":moment["text"],"actual_jpeg":str(outfile)}
            spots.append(spot)
            pic=Image.open(outfile).convert("RGB")
            pic.thumbnail((350,200))
            gallery.append((pic, f"C{ci}M{mi} | {t:.1f}s | {entry['source_asset_id']}"))
    w,h,cols=380,244,3
    sheet=Image.new("RGB",(w*cols,h*math.ceil(len(gallery)/cols)),(250,250,250))
    draw=ImageDraw.Draw(sheet)
    for i,(pic,label) in enumerate(gallery):
        x=(i%cols)*w;y=(i//cols)*h
        sheet.paste(pic,(x+10,y+8))
        draw.text((x+10,y+207),label[:43],font=font,fill=(18,28,42))
    montage=ROOT/f"fps_{key}_real_moments_montage.jpg"
    sheet.save(montage,quality=87,optimize=True)
    used_slots=sorted(set(s["input_slot"] for s in spots))
    report={
        "fps":conf["fps"],"input_tokens":conf["prompt_tokens"],
        "output_tokens":conf["completion_tokens"],"cost_cny":conf["cost_cny"],
        "model_chapter_count":conf["chapter_count"],
        "model_chapter_titles":[x["title"] for x in row["model_result"]["chapters"]],
        "selected_moment_count":len(spots),
        "selected_video_slot_count":len(used_slots),"selected_video_slots":used_slots,
        "source_clips_provided":len(clips),
        "source_time_mapping_valid":True,
        "model_selected_moments_mapped_to_true_original_video":spots,
        "montage_path":str(montage),
        "model_visual_story_truth_certified":False,
    }
    reports.append(report)
    print("ASSESSED",key,"chapters",report["model_chapter_count"],
          "moments",len(spots),"slots_covered",len(used_slots),
          "cost",report["cost_cny"],flush=True)
    print("MONTAGE",montage,flush=True)
summary={
    "experiment":"VIDEO_FPS_PILOT_REAL_QWEN3_8_FLASH",
    "same_source_video_sha256":json.loads((ROOT/"preflight.json").read_text())["output_sha256"],
    "held_constant":["16 originals","source slot mapping","video bytes","prompt","model",
                     "resolution","video encoding","response JSON contract"],
    "only_changed":"video_url.fps",
    "both_fps_returned_valid_json":True,
    "results":reports,
    "caveats":["This is a 16-of-160-clips pilot, not whole-day B validation.",
               "Video concatenation compresses real-world gaps; source clock mapping shown to model.",
               "Models choose approximate moments; still/3s motion must be verified on native originals.",
               "One nondeterministic run per fps cannot establish superior quality.",
               "No audio input."],
}
(ROOT/"FINAL_VIDEO_FPS_COMPARISON.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print("FINAL_SUMMARY",ROOT/"FINAL_VIDEO_FPS_COMPARISON.json")
