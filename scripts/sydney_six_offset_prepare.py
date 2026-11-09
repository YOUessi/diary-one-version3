#!/usr/bin/env python3
"""Prepare five extra Sydney video phases for REAL Video VLM A/B tests.

This script never calls an image VLM and NEVER sends a paid model request.
Prior JPEG V03 and 10s Video 0.5/1fps are reused by separate readers. Source
and per-phase timing are validated by the generated full160_video_fps_ab script.
"""
from pathlib import Path
import argparse
import concurrent.futures
import subprocess
import sys
import json

HOME=Path.home()
ROOT=HOME/"Documents/Nexleap"
REPO=ROOT/"Diary_one_chapter_v2"
EVIDENCE=ROOT/"work_logs/evidence"
OUT=EVIDENCE/"sydney-six-offset-image-vs-video-20261109"
PHASES=(20,30,50,60,70)


def generate(offset:int)->Path:
    if offset not in PHASES:raise ValueError(f"Unexpected phase {offset}")
    target=OUT/"video"/f"offset_{offset:03d}"
    target.mkdir(parents=True,exist_ok=True)
    script=target/"run_video.py"
    original=(REPO/"scripts/sydney_full160_video_fps_ab.py").read_text()
    original=original.replace(
        "sydney-video-full-160-fps-ab-20261109",
        f"sydney-six-offset-image-vs-video-20261109/video/offset_{offset:03d}")
    original=original.replace(
        "offset_010/input/bundle.json",
        f"offset_{offset:03d}/input/bundle.json")
    original=original.replace(
        'r"sydney_01_(\\d{6})"',
        f'r"sydney_{offset//10:02d}_(\\d{{6}})"'
    )
    original=original.replace(
        "phase_01_offset_010s",
        f"phase_{offset//10:02d}_offset_{offset:03d}s"
    )
    assert f'r"sydney_{offset//10:02d}_(\\d{{6}})"' in original
    if script.exists():
        if script.read_text()!=original:
            # Existing research attempts were created before the 72s->80s
            # code-guard update. Their first source clip starts >=130s, so
            # the actual input is already clean. Preserve recorded scripts
            # and API receipts rather than silently altering evidence.
            preflight=target/"preflight.json"
            if not preflight.exists():
                raise RuntimeError(f"Existing unverified script differs: {script}")
            data=json.loads(preflight.read_text())
            assert len(data["source_clips"])==160
            assert min(x["source_original_start_s"] for x in data["source_clips"])>=80
            print(f"EXISTING_HISTORICAL_PHASE_SCRIPT_PRESERVED {offset}",flush=True)
    else:
        script.write_text(original)
    return script


def prep(offset:int,workers:int):
    script=generate(offset)
    status=script.parent/"preflight.json"
    if status.exists():
        data=json.loads(status.read_text())
        assert data["total_original_video_clips"]==160
        assert data["part_count"]==8 and data["total_recorded_seconds"]==1600
        print(f"EXISTING_VERIFIED_VIDEO_SOURCE {offset}",flush=True)
        return
    print(f"PREPARING_VIDEO_ONLY {offset}",flush=True)
    log=script.parent/"prepare.log"
    with log.open("a") as f:
        proc=subprocess.run([sys.executable,str(script),"prepare","--workers",str(workers)],
                            stdout=f,stderr=subprocess.STDOUT)
    if proc.returncode:raise RuntimeError(f"Video preprocessing failed {offset}; see {log}")
    assert status.exists()
    print(f"PREPARED_160_VIDEO_CLIPS {offset}",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--offsets",type=int,nargs="+",default=list(PHASES))
    parser.add_argument("--parallel",type=int,default=3)
    parser.add_argument("--ffmpeg-workers-per-phase",type=int,default=2)
    args=parser.parse_args()
    if not set(args.offsets)<=set(PHASES):raise ValueError("Allowed 20,30,50,60,70 only")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.parallel,3))) as pool:
        futures=[pool.submit(prep,n,args.ffmpeg_workers_per_phase) for n in args.offsets]
        for f in futures:f.result()
    print("ALL_VIDEO_ONLY_INPUTS_READY",args.offsets)
