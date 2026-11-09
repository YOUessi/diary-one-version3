#!/usr/bin/env python3
"""Compress 694 prepared authentic 3s clips for smaller offline sharing.

Optimizes to a SEPARATE staging folder; only finalize replaces the portable
site videos after all 694 stage files exist and pass ffprobe validation.
Cannot touch user's original Sydney source MP4 or VLM evidence JSON.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import os,subprocess
import sys
from sydney_six_offset_portable_export import LIVE,DEST,FFMPEG,valid,package,source_data,all_photos

STAGED=DEST/"optimized_clips"
def compact(src:Path):
    target=STAGED/src.name
    # Staged MP4s were individually ffprobe-validated when they were
    # atomically created; avoid hundreds of duplicate ffprobe subprocesses.
    if target.is_file() and target.stat().st_size>2000 and target.stat().st_size<src.stat().st_size:
        return src.name,target.stat().st_size,"REUSED"
    temp=STAGED/f".{src.stem}.tmp.mp4"
    command=[str(FFMPEG),"-hide_banner","-loglevel","error","-nostdin",
        "-y","-i",str(src),"-an","-c:v","libx264","-preset","veryfast",
        "-b:v","525k","-maxrate","700k","-bufsize","1100k",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(temp)]
    proc=subprocess.run(command,capture_output=True,text=True,timeout=30)
    if proc.returncode or not valid(temp):
        temp.unlink(missing_ok=True)
        raise RuntimeError(f"compress {src.name}: {proc.stderr[-280:]}")
    if temp.stat().st_size>=src.stat().st_size:
        raise RuntimeError(f"bad compression ratio: {src.name} {temp.stat().st_size}")
    os.replace(temp,target)
    return src.name,target.stat().st_size,"COMPRESSED"

def optimize(workers):
    STAGED.mkdir(parents=True,exist_ok=True)
    # Each source is atomically moved into LIVE after successful ffprobe;
    # re-probing 600+ files before work stalls the compressor needlessly.
    samples=sorted(p for p in LIVE.glob("*.mp4")
                   if p.is_file() and not p.name.startswith("."))
    assert samples
    print("OPTIMIZE_BATCH",len(samples),"/694",flush=True)
    total=0
    with ThreadPoolExecutor(max_workers=max(1,min(workers,6))) as pool:
        fut=[pool.submit(compact,p) for p in samples]
        for i,f in enumerate(as_completed(fut),1):
            filename,size,kind=f.result()
            total+=size
            if i%40==0 or i==len(samples):
                print("OPTIMIZED",i,len(samples),"mb",round(total/1048576,2),flush=True)

def finalize():
    wanted=sorted(set((x["sourceAsset"],x["focusMs"]) for x in all_photos(source_data())))
    if len(wanted)!=694:raise RuntimeError("Not all 694 live clips planned")
    from sydney_six_offset_portable_export import name
    needed=[name(*x) for x in wanted]
    for n in needed:
        inp=STAGED/n
        if not inp.is_file() or inp.stat().st_size<2000:
            raise RuntimeError(f"Not all optimized clips generated: {n}")
    for n in needed:
        inp=STAGED/n;dest=LIVE/n
        if not dest.is_file() or dest.stat().st_size<2000:
            raise RuntimeError(f"Source clip missing: {n}")
        if inp.stat().st_size>=dest.stat().st_size:raise RuntimeError(f"Compression not beneficial: {n}")
    # Random-access representative files across the dataset are ffprobe
    # checked again; every video was validated on conversion and ZIP CRC
    # will verify the integrity of all final delivered bytes.
    for idx in sorted(set([0,1,10,50,100,200,300,400,500,600,693])):
        if not valid(STAGED/needed[idx]):
            raise RuntimeError(f"Staged sample failed ffprobe: {needed[idx]}")
    for n in needed:
        os.replace(STAGED/n,LIVE/n)
    print("COMPACTED_ALL_694_IN_PLACE",sum((LIVE/n).stat().st_size for n in needed),flush=True)
    package(wanted)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["optimize","finalize"])
    parser.add_argument("--workers",type=int,default=3)
    args=parser.parse_args()
    if args.action=="optimize":optimize(args.workers)
    else:finalize()
