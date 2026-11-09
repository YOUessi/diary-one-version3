#!/usr/bin/env python3
"""Real video pilot: 16 authentic Sydney 10s clips, same MP4/prompt, 0.5/1 fps."""
import argparse, base64, hashlib, json, math, os, re, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

HOME=Path.home()
ROOT=HOME/"Documents/Nexleap"
RUN=ROOT/"work_logs/evidence/sydney-video-fps-ab-20261109"
SRC=ROOT/"work_logs/evidence/sydney-intro-cut-72s-20261105/offset_010/input/bundle.json"
CLIPS_DIR=HOME/"Downloads/视频切分_10s_悉尼_20261027/sydney"
FFMPEG=HOME/"miniforge3/bin/ffmpeg"
FFPROBE=HOME/"miniforge3/bin/ffprobe"
MP4=RUN/"concat_16clips_160s_640x360.mp4"
INDEX=RUN/"source_time_map.json"
PROMPT=RUN/"chapter_prompt.txt"
FPS=(0.5,1.0)
MODEL="qwen3.8-flash"

def save(path,data):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    os.replace(tmp,path)

def prepare():
    assets=json.loads(SRC.read_text())["assets"]
    assert len(assets)==160
    indexes=[round(i*(len(assets)-1)/15) for i in range(16)]
    assert len(set(indexes))==16
    clips=[]
    for j,i in enumerate(indexes):
        aid=assets[i]["asset_id"]
        m=re.fullmatch(r"sydney_01_(\d{6})",aid)
        assert m,aid
        source_index=int(m.group(1))
        assert (source_index-1)*10>=80, "Sydney overview 00:00-01:20 must be excluded"
        match=list(CLIPS_DIR.glob(f"sydney_{source_index:06d}_*.mp4"))
        assert len(match)==1,(aid,match)
        clips.append({"slot":j+1,"source_asset_id":aid,"file":str(match[0]),
           "source_start_s":(source_index-1)*10,"concat_nominal_start_s":j*10})
    save(INDEX,{"source":"Sydney phase_01 offset 10s","intro_removed":True,
      "discontinuous_source_video":True,"clips":clips})
    concat_list=RUN/"concat_list.txt"
    # Mixed early FFmpeg and later AVFoundation H.264 clips cannot safely be
    # concat-decoded as one stream. Re-encode each independently to a uniform
    # H.264/AAC-free, 640x360/15fps, precisely 150-frame media segment first.
    media_dir=RUN/"uniform_10s"
    media_dir.mkdir(exist_ok=True)
    lines=[]
    for item in clips:
        local=media_dir/("slot_%02d.mp4"%item["slot"])
        if not local.exists():
            print("UNIFORM_TRANSCODE",item["slot"],flush=True)
            proc=subprocess.run([
              str(FFMPEG),"-hide_banner","-loglevel","error","-nostdin",
              "-y","-i",item["file"],"-an",
              "-vf","fps=15,scale=640:360:flags=bicubic,format=yuv420p",
              "-frames:v","150","-c:v","libx264","-preset","veryfast",
              "-b:v","255k","-maxrate","320k","-bufsize","640k",
              "-movflags","+faststart",str(local)
            ],capture_output=True,text=True,timeout=120)
            if proc.returncode:raise RuntimeError(str(proc.stderr)[-750:])
        verify=subprocess.run([
          str(FFPROBE),"-v","error","-select_streams","v:0",
          "-show_entries","stream=nb_frames:format=duration",
          "-of","json",str(local)
        ],capture_output=True,text=True,timeout=20)
        meta=json.loads(verify.stdout)
        if int(meta["streams"][0]["nb_frames"])!=150:
            raise RuntimeError("Invalid duration/frames in "+str(local)+": "+str(meta))
        lines.append("file '"+str(local)+"'")
    concat_list.write_text("\n".join(lines)+"\n")
    prompt=("你是第一人称生活视频的章节编辑。输入是一段由16个不连续的真实10秒片段按时间顺序拼成的约160秒分析视频。"
        "片段之间在原视频中存在很长的间隔，不能把拼接之后的160秒误认为真实连续经历。\n"
        "请仅根据真实可见内容，按照地点、活动和主题划分自然 Chapter；不要每片段硬拆一章，也不要因都属于citywalk就将不同区域合并。"
        "标题、故事、selected_moments.text必须是自然简体中文；英文专名允许括注。"
        "不要虚构购买、人物意图、星期和地名。短暂而独特的场景应保留。\n"
        "每章精选1-6个不重复的精彩位置用于手机端生成封面JPG和3秒动态短片，"
        "第一项为封面。只返回一个JSON对象，格式："
        '{"chapters":[{"title":"...","story":"...","selected_moments":['
        '{"video_time_ms":3500,"text":"..."}]}]}。'
        "video_time_ms为拼接后视频起点起的整数毫秒，范围[0,160000)，不要写原始长视频时间；"
        "模型给的是粗略位置，最终帧需要从原片另行核实。\n"
        "以下是拼接时间到原始时间的映射（用于理解真实事件间隔，非额外视觉事实）：\n")
    for c in clips:
        ss=c["source_start_s"]
        prompt+=(f"slot{c['slot']:02d}:拼接{c['concat_nominal_start_s']}–{c['concat_nominal_start_s']+10}s;"
                 f"原始视频{ss//3600:02d}:{ss//60%60:02d}:{ss%60:02d}起10s\n")
    prompt+="只输出JSON对象，不输出Markdown或解释。"
    PROMPT.write_text(prompt)
    if not (RUN/"preflight.json").exists() and MP4.exists():
        # Only failed/partial derived output may be replaced; never source clips.
        MP4.unlink()
    if not MP4.exists():
        print("CONCAT_UNIFORM_CLIPS",len(clips),flush=True)
        command=[str(FFMPEG),"-hide_banner","-loglevel","error","-nostdin","-y",
            "-f","concat","-safe","0","-i",str(concat_list),
            "-c","copy","-an","-movflags","+faststart",str(MP4)]
        run=subprocess.run(command,capture_output=True,text=True,timeout=80)
        if run.returncode:raise RuntimeError(run.stderr[-1400:])
    size=MP4.stat().st_size
    b64_count=4*math.ceil(size/3)
    assert b64_count<9_500_000,(size,b64_count)
    probe=subprocess.run([str(FFPROBE),"-v","error","-select_streams","v:0",
        "-show_entries","stream=nb_frames,avg_frame_rate,width,height:format=duration",
        "-of","json",str(MP4)],capture_output=True,text=True,timeout=20)
    info=json.loads(probe.stdout)
    duration=float(info["format"]["duration"])
    assert 150<duration<170,duration
    report={"clips":len(clips),"output_s":duration,"input_video_bytes":size,
       "base64_bytes_est":b64_count,"transcoded_frames":info["streams"][0].get("nb_frames"),
       "output_sha256":hashlib.sha256(MP4.read_bytes()).hexdigest(),
       "expected_provider_sampling":{"0.5fps":round(duration*.5),"1fps":round(duration)}}
    save(RUN/"preflight.json",report)
    print("PREPARED",json.dumps(report,ensure_ascii=False),flush=True)

def call(fps):
    assert fps in FPS
    info=json.loads((RUN/"preflight.json").read_text())
    assert hashlib.sha256(MP4.read_bytes()).hexdigest()==info["output_sha256"]
    config=json.loads((ROOT/"diary-one-algorithm-review/.local/chapter.json").read_text())
    load_dotenv(config["env_file"],override=False)
    sys.path.insert(0,str(ROOT/"Diary_one_chapter_v2/services/algorithm/algorithm/src"))
    from diary_one_ci.x01 import QwenChatCompletionsAdapter
    adapter=QwenChatCompletionsAdapter(model=MODEL,timeout_seconds=360)
    assert adapter.ready and adapter.input_rate_per_million==0.8 and adapter.output_rate_per_million==2.7
    label=str(fps).replace(".","p")
    receipt=RUN/f"fps_{label}_status.json"
    if receipt.exists():raise FileExistsError("No duplicate billing: "+str(receipt))
    summary={"state":"STARTED","fps":fps,"model":MODEL,
        "video_sha256":info["output_sha256"],"video_seconds":info["output_s"],
        "input_clips":info["clips"],"input_video_bytes":info["input_video_bytes"],
        "prompt_sha256":hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
        "created_utc":datetime.now(timezone.utc).isoformat()}
    save(receipt,summary)
    video_url="data:video/mp4;base64,"+base64.b64encode(MP4.read_bytes()).decode()
    assert len(video_url)<9_500_000
    request={"model":MODEL,"messages":[{"role":"user","content":[
        {"type":"text","text":PROMPT.read_text()},
        {"type":"video_url","video_url":{"url":video_url},
         "fps":fps,"min_pixels":65536,"max_pixels":262144}
    ]}],"response_format":{"type":"json_object"},"enable_thinking":False,
        "stream":False,"max_tokens":3000}
    import requests
    started=time.monotonic()
    try:
        response=requests.post(adapter.base_url+"/chat/completions",json=request,
          headers={"Authorization":"Bearer "+adapter.api_key},timeout=(30,360))
        payload=response.json()
        usage=payload.get("usage",{})
        in_tok=int(usage.get("prompt_tokens",0))
        out_tok=int(usage.get("completion_tokens",0))
        price=(in_tok*adapter.input_rate_per_million+out_tok*adapter.output_rate_per_million)/1_000_000
        summary.update({"http_status":response.status_code,"prompt_tokens":in_tok,
            "completion_tokens":out_tok,"cost_cny":round(price,8),
            "duration_s":round(time.monotonic()-started,2),
            "provider_request_id":payload.get("id")})
        if response.status_code!=200:
            summary.update({"state":"PROVIDER_ERROR","code":payload.get("code"),
                "message":str(payload.get("message",""))[:700]})
            save(receipt,summary);print("PROVIDER_ERROR",json.dumps(summary,ensure_ascii=False),flush=True);return
        choice=payload["choices"][0]
        content=choice["message"].get("content","")
        try:
            obj=json.loads(content)
        except Exception:obj={"raw_text":str(content)[:20000]}
        summary["finish_reason"]=choice.get("finish_reason")
        summary["chapter_count"]=len(obj.get("chapters",[])) if isinstance(obj.get("chapters"),list) else None
        errors=[]
        if not isinstance(obj.get("chapters"),list) or not obj["chapters"]:errors.append("chapters_invalid")
        else:
            for chapter in obj["chapters"]:
                for moment in chapter.get("selected_moments",[]):
                    t=moment.get("video_time_ms")
                    if type(t)!=int or not (0<=t<info["output_s"]*1000):
                        errors.append("invalid_video_time_ms")
        summary["errors"]=errors
        summary["state"]="COMPLETE" if not errors else "OUTPUT_INVALID"
        save(RUN/f"fps_{label}_result.json",{"summary":summary,"model_result":obj})
        save(receipt,summary)
        print("MODEL_RESULT",json.dumps(summary,ensure_ascii=False),flush=True)
    except Exception as e:
        summary.update({"state":"EXCEPTION","error":type(e).__name__+": "+str(e)[:400],
            "duration_s":round(time.monotonic()-started,2)})
        save(receipt,summary)
        print("MODEL_EXCEPTION",json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["prepare","run"])
    ap.add_argument("--fps",type=float)
    args=ap.parse_args()
    if args.action=="prepare":prepare()
    else:call(args.fps)
