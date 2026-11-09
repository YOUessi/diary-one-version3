#!/usr/bin/env python3
"""Real API calls for missing video fps, never image or historical video reruns.

Preprocessing and provider calls are individually auditable. Photo V03 six
groups are read only. A status receipt forbids duplicate paid calls.
"""
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path.home()/"Documents/Nexleap/work_logs/evidence/sydney-six-offset-image-vs-video-20261109"
PY=Path.home()/"miniforge3/bin/python3.13"
PHASES=(20,30,50,60,70)
SRC=Path.home()/"Documents/Nexleap/Diary_one_chapter_v2/scripts/sydney_full160_video_evaluate.py"

def status_snapshot():
    result=[]
    for offset in PHASES:
        base=ROOT/"video"/f"offset_{offset:03d}"
        for label in ("0p5","1p0"):
            file=base/f"fps_{label}_status.json"
            if file.exists():
                x=json.loads(file.read_text())
                result.append((offset,label,x["state"],x.get("estimated_cost_cny")))
            else:
                result.append((offset,label,"NOT_STARTED",None))
    return result

def run(offset):
    base=ROOT/"video"/f"offset_{offset:03d}"
    entry=base/"preflight.json"
    if not entry.exists():
        raise RuntimeError("No verified 160 clip input for video offset "+str(offset))
    pre=json.loads(entry.read_text())
    assert pre["total_original_video_clips"]==160
    assert pre["part_count"]==8
    assert pre["total_recorded_seconds"]==1600
    assert all(x["base64_chars"]<9_500_000 for x in pre["parts"])
    assert min(x["source_original_start_s"] for x in pre["source_clips"])>=80
    evaltext=SRC.read_text()
    evaltext=evaltext.replace(
         "sydney-video-full-160-fps-ab-20261109",
         f"sydney-six-offset-image-vs-video-20261109/video/offset_{offset:03d}")
    evaluator=base/"evaluate_video.py"
    evaluator.write_text(evaltext)
    for fps,label in ((0.5,"0p5"),(1.0,"1p0")):
        receipt=base/f"fps_{label}_status.json"
        if receipt.exists():
            print("EXISTING_RECEIPT_NO_NEW_API_CALL",offset,fps, json.loads(receipt.read_text())["state"],flush=True)
            continue
        log=base/f"real_fps_{label}.log"
        print("VIDEO_API_CALL_START",offset,fps,datetime.now(timezone.utc).isoformat(),flush=True)
        with log.open("w") as f:
            completed=subprocess.run([str(PY),str(base/"run_video.py"),"run","--fps",str(fps)],
                                      stdout=f,stderr=subprocess.STDOUT,timeout=1000)
        d=json.loads(receipt.read_text()) if receipt.exists() else {}
        print("VIDEO_API_CALL_END",offset,fps,
              "process_exit",completed.returncode,"state",d.get("state"),
              "provider_in_tokens",d.get("prompt_tokens"),
              "out_tokens",d.get("completion_tokens"),
              "estimated_cny",d.get("estimated_cost_cny"),
              "request_id",d.get("model_request_id"),flush=True)
        subprocess.run([str(PY),str(ROOT/"record_costs.py")],check=True,
                       stdout=subprocess.DEVNULL)
        subprocess.run([str(PY),str(ROOT/"compare_six.py")],check=True,
                       stdout=subprocess.DEVNULL)
    a=base/"fps_0p5_status.json";b=base/"fps_1p0_status.json"
    if a.is_file() and b.is_file():
        states=(json.loads(a.read_text())["state"],json.loads(b.read_text())["state"])
        if states==("COMPLETE","COMPLETE"):
            eval_log=base/"evaluate.log"
            with eval_log.open("w") as f:
                result=subprocess.run([str(PY),str(evaluator)],stdout=f,stderr=subprocess.STDOUT,timeout=1200)
            print("VIDEO_OFFSET_EVALUATED",offset,
                  "exit_code",result.returncode,
                  "scoreboard_exists",(base/"FINAL_160_VIDEO_COMPARISON.json").is_file(),flush=True)
        else:
            print("OFFSET_HAS_INVALID_RUN_PRESERVED_FOR_POSTHOC_REVIEW",offset,states,flush=True)

if __name__=="__main__":
    print("START_VIDEO_ONLY_BATCH",status_snapshot(),flush=True)
    count=0
    while count<len(PHASES):
        offset=PHASES[count]
        part=ROOT/"video"/f"offset_{offset:03d}"/"preflight.json"
        if part.is_file():
            run(offset)
            count+=1
        else:
            # Never send a model request until all 160 clips and 8 media parts
            # for that offset are SHA-verified and preflight-confirmed.
            tasklog=ROOT/"video_preprocessing.log"
            if tasklog.exists() and "PREP_BATCH_EXIT=1" in tasklog.read_text():
                raise RuntimeError("Video preprocessing failed for some offset")
            time.sleep(10)
    print("VIDEO_SIX_OFFSET_NEW_BATCH_COMPLETE",status_snapshot(),flush=True)
