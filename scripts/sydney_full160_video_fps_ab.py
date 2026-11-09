#!/usr/bin/env python3
"""Real full Sydney 160 × 10-second video clips FPS AB for Qwen3.8-Flash.

The model receives all 160 video slices as eight sequential 200-second video
blocks within ONE chat completion, with exact independent source-time mapping.
Each media block is Base64 <10MB, and no raw footage/Base64/credential is saved
to the audit. Both runs use identical bytes and prompt, only fps differs.
"""
from __future__ import annotations
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime,timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any

from dotenv import load_dotenv

HOME = Path.home()
NEX = HOME / "Documents/Nexleap"
BASE = NEX / "work_logs/evidence/sydney-video-full-160-fps-ab-20261109"
SOURCES = HOME / "Downloads/视频切分_10s_悉尼_20261027/sydney"
BUNDLE = NEX / "work_logs/evidence/sydney-intro-cut-72s-20261105/offset_010/input/bundle.json"
PILOT = NEX / "work_logs/evidence/sydney-video-fps-ab-20261109"
FFMPEG = HOME / "miniforge3/bin/ffmpeg"
FFPROBE = HOME / "miniforge3/bin/ffprobe"
UNIFORM = BASE / "uniform_10s"
CHUNKS = BASE / "parts"
TMP = BASE / "_tmp"
PARTS = 8
CLIPS_PER_PART = 20
ORIGINAL_CLIPS = 160
FPS_OPTIONS = (0.5, 1.0)
MODEL = "qwen3.8-flash"
MAX_B64 = 9_500_000
MAX_BODY = 72_000_000


def save_json(path:Path,data:Any) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    os.replace(tmp, path)


def ffprobe(path:Path) -> dict:
    c = subprocess.run([str(FFPROBE), "-v", "error", "-select_streams","v:0",
        "-show_entries","stream=nb_frames,width,height,avg_frame_rate:format=duration,size",
        "-of","json",str(path)], capture_output=True,text=True,timeout=20)
    if c.returncode:
        raise RuntimeError("FFPROBE error on " + str(path) + ": " + c.stderr[-280:])
    return json.loads(c.stdout)


def input_clips() -> list[dict]:
    assert BUNDLE.is_file()
    assets=json.loads(BUNDLE.read_text())["assets"]
    assert len(assets)==ORIGINAL_CLIPS
    entries=[]
    prev_start=None
    for n,asset in enumerate(assets):
        aid=asset["asset_id"]
        match=re.fullmatch(r"sydney_01_(\d{6})",aid)
        assert match,aid
        original_s=(int(match.group(1))-1)*10
        assert original_s >= 80, ("intro 00:00–01:20 leaked",aid)
        if prev_start is not None:
            assert original_s-prev_start==120,(aid,original_s,prev_start)
        prev_start=original_s
        files=list(SOURCES.glob(f"sydney_{int(match.group(1)):06d}_*.mp4"))
        assert len(files)==1,(aid,len(files))
        assert files[0].stat().st_size>100000
        entries.append({
            "seq":n+1,
            "asset_id":aid,
            "source_original_start_s":original_s,
            "part_id":n//CLIPS_PER_PART+1,
            "part_local_slot":n%CLIPS_PER_PART+1,
            "part_local_start_ms":(n%CLIPS_PER_PART)*10000,
            "source_mp4":str(files[0]),
        })
    assert entries[-1]["source_original_start_s"]-entries[0]["source_original_start_s"]==159*120
    return entries


def saved_mp4_ok(path:Path,*, expected_frames:int, duration:float) -> bool:
    if not path.exists() or path.stat().st_size<1500:
        return False
    probe=ffprobe(path)
    v=probe["streams"][0]
    return (int(v["nb_frames"])==expected_frames and
            abs(float(probe["format"]["duration"])-duration)<0.10)


def transform(clip:dict,pilot_map:dict) -> tuple[int,int]:
    n=clip["seq"]
    dest=UNIFORM/f"slot_{n:03d}.mp4"
    if saved_mp4_ok(dest,expected_frames=150,duration=10.0):
        return n,dest.stat().st_size
    source=pilot_map.get(clip["asset_id"])
    if source and saved_mp4_ok(source,expected_frames=150,duration=10.0):
        shutil.copyfile(source,dest)
        return n,dest.stat().st_size
    tmp=TMP/f"slot_{n:03d}.mp4"
    command=[str(FFMPEG),"-hide_banner","-loglevel","error","-nostdin",
        "-y","-i",clip["source_mp4"],"-an",
        "-vf","fps=15,scale=640:360:flags=bicubic,format=yuv420p",
        "-frames:v","150","-c:v","libx264","-preset","veryfast",
        "-b:v","255k","-maxrate","320k","-bufsize","640k",
        "-movflags","+faststart",str(tmp)]
    proc=subprocess.run(command,capture_output=True,text=True,timeout=160)
    if proc.returncode:
        raise RuntimeError(f"reencoding {n} failed: {proc.stderr[-380:]}")
    if not saved_mp4_ok(tmp,expected_frames=150,duration=10.0):
        raise RuntimeError(f"reencoded slot {n} has wrong frame_count/duration")
    os.replace(tmp,dest)
    return n,dest.stat().st_size


def prepare(workers:int):
    for p in (BASE,UNIFORM,CHUNKS,TMP):
        p.mkdir(parents=True,exist_ok=True)
    entries=input_clips()
    # The existing 16-slot pilot used the exact same encoding settings.
    pilot_map={}
    prior_path=PILOT/"source_time_map.json"
    if prior_path.exists():
        for row in json.loads(prior_path.read_text())["clips"]:
            candidate=PILOT/"uniform_10s"/f"slot_{row['slot']:02d}.mp4"
            if candidate.is_file():
                pilot_map[row["source_asset_id"]]=candidate
    print("INPUT_VERIFIED",len(entries),"clips",
          "source_total_gib",round(sum(Path(x["source_mp4"]).stat().st_size for x in entries)/1024**3,2),
          "pilot_reusable",len(pilot_map),flush=True)
    sizes=[]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        tasks=[executor.submit(transform,clip,pilot_map) for clip in entries]
        for i,f in enumerate(as_completed(tasks),1):
            sizes.append(f.result())
            if i%10==0 or i==ORIGINAL_CLIPS:
                print("UNIFORM_READY",i,"/",ORIGINAL_CLIPS,
                  "total_mib",round(sum(size for _,size in sizes)/1024**2,2),flush=True)
    media=[]
    for part_id in range(1,PARTS+1):
        group=entries[(part_id-1)*CLIPS_PER_PART:part_id*CLIPS_PER_PART]
        assert len(group)==CLIPS_PER_PART
        target=CHUNKS/f"part_{part_id:02d}_20clips_200s.mp4"
        if not saved_mp4_ok(target,expected_frames=3000,duration=200.0):
            listing=TMP/f"part_{part_id:02d}_concat.txt"
            listing.write_text("\n".join(
                f"file '{UNIFORM / ('slot_%03d.mp4' % x['seq'])}'"
                for x in group)+"\n")
            staging=TMP/f"part_{part_id:02d}_200s.mp4"
            proc=subprocess.run([str(FFMPEG),"-hide_banner","-loglevel","error",
                "-nostdin","-y","-f","concat","-safe","0",
                "-i",str(listing),"-c","copy","-an",
                "-movflags","+faststart",str(staging)],
                capture_output=True,text=True,timeout=120)
            if proc.returncode:raise RuntimeError(proc.stderr[-500:])
            if not saved_mp4_ok(staging,expected_frames=3000,duration=200.0):
                raise RuntimeError(f"part {part_id} video frame count/duration bad")
            os.replace(staging,target)
        length=target.stat().st_size
        b64=4*math.ceil(length/3)
        assert b64<MAX_B64, (part_id,length,b64)
        media.append({
            "part_id":part_id,
            "relative_path":str(target.relative_to(BASE)),
            "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "video_seconds":200.0,
            "transcoded_frames":3000,
            "video_bytes":length,
            "base64_chars":b64,
            "original_clip_first_seq":group[0]["seq"],
            "original_clip_last_seq":group[-1]["seq"],
            "original_video_first_start_seconds":group[0]["source_original_start_s"],
            "original_video_last_start_seconds":group[-1]["source_original_start_s"],
        })
        print("PART_OK",part_id,"file_mib",round(length/1048576,2),
              "base64_mib",round(b64/1048576,2),flush=True)
    assert len(media)==PARTS
    prompt=(
        "你是一名第一人称生活记录视频的全局 Chapter 编辑。"
        "下面按原始拍摄时间顺序提供8段视频，每段恰好200秒，由20个真实的10秒来源片段拼接。"
        "这些10秒片段在原长视频中每隔120秒采样一次，拼接后的相邻10秒片段并非连续真实生活经历，"
        "必须依据下列源时间映射正确理解跨片段时间距离。"
        "整天总共160个10秒真实视频片段，跨度约5小时20分钟。"
        "先理解完整时间线，再按地点、活动及主题连续性决定自然 Chapter。"
        "同一个区域内的连续市集/街道/短暂活动优先合章；不同城市区域、海事博物馆、唐人街、CBD、植物园等"
        "重要经历应分别考虑，不强行固定5章，也不为了出图拆成十几章。"
        "不能遗漏短暂而独特的建筑/活动；只能根据画面可见事实写作，不能推测真实星期、黄昏、"
        "个人心情、购买动作或不知道的地点名称。\n"
        "输出全部为自然简体中文（title、story、selected_moments[].text），允许英文专名括注"
        "如岩石区（The Rocks）、环形码头（Circular Quay）。"
        "每个Chapter按内容重要性挑选1-12个不同的真实关键画面位置，"
        "第一个是封面，低价值同景不要凑数。"
        "VLM只负责选择时间点及故事，不需要产生JPEG/MOV文件，后端会映射到原视频帧PTS并校验。"
        '只输出一个JSON对象：{"chapters":[{"title":"中文章名","story":"中文叙述",'
        '"selected_moments":[{"part_id":1,"video_time_ms":4200,"text":"中文瞬间描述"}]}]}。'
        "part_id=1..8，video_time_ms是选中part内部的整数毫秒[0,200000)，绝不是原始5小时视频的时间。"
        "不同Chapter不要复用同一(part_id,video_time_ms)，每章尽量选不同的原始10秒片段。"
        "章节必须按真正拍摄时间先后返回。\n"
        "源时间映射：每个part由20个10秒片段组成，"
        "part内slot=1..20；slot j 的拼接视频局部开始毫秒=(j-1)*10000；"
        "它在原长视频中的实际开始秒数=本part下列first_source_start_s+(j-1)*120。\n"
    )
    for part in media:
        prompt+=f"part {part['part_id']} first_source_start_s={part['original_video_first_start_seconds']}; 包含原片段全局序号 {part['original_clip_first_seq']}..{part['original_clip_last_seq']}。\n"
    prompt+="只返回合法JSON对象，无Markdown或解释。"
    (BASE/"shared_prompt.txt").write_text(prompt)
    data={
        "source":"Sydney Citywalk phase_01_offset_010s full 160 video clips",
        "confirmed_00_to_80s_absent":True,
        "all_clips_have_original_120s_sampling_gaps":True,
        "total_original_video_clips":ORIGINAL_CLIPS,
        "total_recorded_seconds":1600,
        "part_count":PARTS,
        "parts":media,
        "source_clips":entries,
        "fps_requested":[.5,1.0],
        "expected_frames_by_fps":{"0.5":800,"1.0":1600},
        "expected_input_fixed_except_fps":True,
        "total_video_bytes":sum(m["video_bytes"] for m in media),
        "total_b64_chars":sum(m["base64_chars"] for m in media),
        "prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
        "codec":"H264 640x360 15fps x264 255kbps noaudio",
    }
    assert data["total_b64_chars"]<MAX_BODY,(data["total_b64_chars"],MAX_BODY)
    save_json(BASE/"preflight.json",data)
    print("PREPARED_160",json.dumps({
        "parts":PARTS,"clips":len(entries),
        "actual_bytes":data["total_video_bytes"],
        "base64_chars":data["total_b64_chars"],
        "theoretical_0p5_frames":800,
        "theoretical_1p0_frames":1600,
        "prompt_sha256":data["prompt_sha256"]
    },ensure_ascii=False),flush=True)


def run(fps:float):
    assert fps in FPS_OPTIONS
    info=json.loads((BASE/"preflight.json").read_text())
    assert info["total_original_video_clips"]==160 and info["part_count"]==8
    prompt=(BASE/"shared_prompt.txt").read_text()
    assert hashlib.sha256(prompt.encode()).hexdigest()==info["prompt_sha256"]
    paths=[BASE/p["relative_path"] for p in info["parts"]]
    assert all(p.is_file() for p in paths)
    for p,meta in zip(paths,info["parts"]):
        assert hashlib.sha256(p.read_bytes()).hexdigest()==meta["sha256"]
    config=json.loads((NEX/"diary-one-algorithm-review/.local/chapter.json").read_text())
    load_dotenv(config["env_file"],override=False)
    sys.path.insert(0,str(NEX/"Diary_one_chapter_v2/services/algorithm/algorithm/src"))
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    adapter=QwenChatCompletionsAdapter(model=MODEL,timeout_seconds=900)
    assert adapter.ready and adapter.input_rate_per_million==0.8 and adapter.output_rate_per_million==2.7
    ident=str(fps).replace(".","p")
    statusfile=BASE/f"fps_{ident}_status.json"
    if statusfile.exists():
        raise FileExistsError("Refusing repeated billable API request: "+str(statusfile))
    content=[{"type":"text","text":prompt}]
    for part,p in zip(info["parts"],paths):
        raw=base64.b64encode(p.read_bytes()).decode("ascii")
        assert len(raw)<MAX_B64
        content.append({"type":"text","text":f"视频第{part['part_id']}部分（part_id={part['part_id']}），连续序号{part['original_clip_first_seq']}至{part['original_clip_last_seq']}；其余按全局Prompt给出的120秒间隔映射。"})
        content.append({"type":"video_url","video_url":{"url":"data:video/mp4;base64,"+raw},
                        "fps":fps,"min_pixels":65536,"max_pixels":262144})
    del raw
    body={"model":MODEL,"messages":[{"role":"user","content":content}],
          "response_format":{"type":"json_object"},"enable_thinking":False,
          "stream":False,"max_tokens":6500}
    receipt={
        "state":"STARTED","fps":fps,"model":MODEL,
        "parts":len(paths),"source_clips":160,
        "source_video_seconds":1600,
        "total_video_bytes":info["total_video_bytes"],
        "total_video_base64_chars":info["total_b64_chars"],
        "video_part_sha256":[x["sha256"] for x in info["parts"]],
        "prompt_sha256":info["prompt_sha256"],
        "time":datetime.now(timezone.utc).isoformat(),
        "video_pixels":{"min":65536,"max":262144},
        "max_tokens":6500,
    }
    save_json(statusfile,receipt)
    import requests
    started=time.monotonic()
    try:
        print("API_REQUEST_STARTED",ident,"8 video parts","bytes",info["total_video_bytes"],flush=True)
        response=requests.post(adapter.base_url+"/chat/completions",json=body,
           headers={"Authorization":"Bearer "+adapter.api_key},
           timeout=(45,900))
        elapsed=round(time.monotonic()-started,3)
        try:payload=response.json()
        except ValueError:
            payload={"message":response.text[:500]}
        usage=payload.get("usage",{}) if isinstance(payload,dict) else {}
        tokens_in=int(usage.get("prompt_tokens",0))
        tokens_out=int(usage.get("completion_tokens",0))
        cost=round((tokens_in*adapter.input_rate_per_million
                   +tokens_out*adapter.output_rate_per_million)/1e6,8)
        receipt.update({"http_status":response.status_code,
            "model_request_id":payload.get("id"),
            "prompt_tokens":tokens_in,"completion_tokens":tokens_out,
            "estimated_cost_cny":cost,"elapsed_seconds":elapsed})
        if response.status_code!=200:
            receipt.update({"state":"PROVIDER_ERROR",
              "error_code":payload.get("code"),
              "message":str(payload.get("message",""))[:750]})
            save_json(statusfile,receipt)
            print("API_PROVIDER_ERROR",json.dumps(receipt,ensure_ascii=False),flush=True)
            return
        choice=payload["choices"][0]
        output=choice.get("message",{}).get("content","")
        try:parsed=json.loads(output)
        except Exception:parsed={"raw":str(output)[:12000]}
        errors=[]
        rows=parsed.get("chapters")
        if not isinstance(rows,list) or not 1<=len(rows)<=22:
            errors.append("chapters_absent_invalid_count")
            rows=[]
        known=set()
        choices=[]
        for i,row in enumerate(rows,1):
            if not isinstance(row,dict):
                errors.append(f"chapter_{i}:not_obj")
                continue
            for k in ("title","story"):
                if not isinstance(row.get(k),str) or len(row[k])<2:errors.append(f"chapter_{i}:{k}")
            moments=row.get("selected_moments")
            if not isinstance(moments,list) or not moments:
                errors.append(f"chapter_{i}:no_moments")
                continue
            for m in moments:
                if not isinstance(m,dict):
                    errors.append(f"chapter_{i}:non_obj_moment")
                    continue
                part,t=m.get("part_id"),m.get("video_time_ms")
                if type(part)!=int or not 1<=part<=PARTS or type(t)!=int or not 0<=t<200000:
                    errors.append(f"chapter_{i}:invalid_moment_time_or_part")
                elif (part,t) in known:
                    errors.append(f"chapter_{i}:moment_duplicate")
                else:known.add((part,t))
                if type(part)==int and 1<=part<=PARTS and type(t)==int and 0<=t<200000:
                    src_slot=int(t//10000)
                    clip=info["source_clips"][(part-1)*20+src_slot]
                    choices.append({
                      "chapter":i,"part_id":part,"part_time_ms":t,
                      "original_global_clip_seq":clip["seq"],
                      "source_asset_id":clip["asset_id"],
                      "original_video_time_ms":clip["source_original_start_s"]*1000+(t%10000),
                      "source_clip_focus_ms":t%10000,
                      "text":m.get("text",""),
                    })
        receipt["chapter_count"]=len(rows)
        receipt["selected_moments_count"]=len(choices)
        receipt["errors"]=errors
        receipt["finish_reason"]=choice.get("finish_reason")
        receipt["state"]="COMPLETE" if not errors else "OUTPUT_INVALID"
        save_json(BASE/f"fps_{ident}_result.json",{
            "metadata":receipt,
            "model_output":parsed,
            "mapped_source_moments":choices
        })
        save_json(statusfile,receipt)
        print("API_RESULT",json.dumps(receipt,ensure_ascii=False),flush=True)
    except Exception as exc:
        receipt.update({"state":"EXECUTION_ERROR",
            "error_type":type(exc).__name__,"error":str(exc)[:600],
            "elapsed_seconds":round(time.monotonic()-started,3)})
        save_json(statusfile,receipt)
        print("API_EXCEPTION",json.dumps(receipt,ensure_ascii=False),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","run"))
    parser.add_argument("--fps",type=float,choices=FPS_OPTIONS)
    parser.add_argument("--workers",type=int,default=4)
    args=parser.parse_args()
    if args.action=="prepare":prepare(max(1,min(args.workers,8)))
    else:run(args.fps)
