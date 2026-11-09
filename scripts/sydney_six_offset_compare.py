#!/usr/bin/env python3
"""Compare *existing* V03 JPEG results against real same-offset video runs.

No API calls. Photo baseline never reruns. Interpret counts as selections, not
semantic GT recall. Keep actual provider costs from usage receipts separate
from current marginal expenses.
"""
from pathlib import Path
from collections import Counter
import json
from datetime import datetime, timezone
import re

HOME=Path.home()
ROOT=HOME/"Documents/Nexleap/work_logs/evidence"
RUN=ROOT/"sydney-six-offset-image-vs-video-20261109"
IMAGE=ROOT/"sydney-direct-vlm-compact-v03-20261105"
VIDEO10=ROOT/"sydney-video-full-160-fps-ab-20261109"
OFFSETS=(10,20,30,50,60,70)
ALIAS={
  "歌剧院":("歌剧院","Opera House","opera house"),
  "环形码头":("环形码头","Circular Quay","circular quay"),
  "岩石区/市集":("岩石区","The Rocks","市集","market"),
  "海港大桥":("海港大桥","Harbour Bridge","Harbor Bridge","harbour bridge"),
  "Barangaroo":("巴兰加鲁","Barangaroo"),
  "达令港":("达令港","Darling Harbour"),
  "海事博物馆":("海事博物馆","Maritime Museum","Maritime"),
  "唐人街":("唐人街","Chinatown"),
  "QVB":("维多利亚女王大厦","Queen Victoria Building","QVB"),
  "教堂":("大教堂","St Mary's","圣玛丽","St Andrew","教堂"),
  "海德公园":("海德公园","Hyde Park"),
  "ANZAC纪念碑":("澳新军团","ANZAC","战争纪念碑","纪念碑"),
  "皇家植物园":("皇家植物园","Royal Botanic","Botanic Garden"),
}
def aliases(chapters):
  txt=" ".join(c.get("title","")+" "+c.get("story","") for c in chapters)
  return [key for key,pats in ALIAS.items() if any(n.lower() in txt.lower() for n in pats)]

def image_metrics(off):
    p=IMAGE/f"offset_{off:03d}"
    status=json.loads((p/"status.json").read_text())
    result=json.loads((p/"result.json").read_text())
    chapters=result["chapters"]
    assert status["state"]=="COMPLETE"
    index={}
    doc=ROOT/f"sydney-intro-cut-72s-20261105/offset_{off:03d}/input/bundle.json"
    b=json.loads(doc.read_text())
    assert len(b["assets"])==160
    for seq,asset in enumerate(b["assets"],1):
        for frame in asset["frames"]:
            index[frame["frame_id"]]=seq
    spans=[]
    selected_sources=set()
    per_ch=[]
    for i,c in enumerate(chapters,1):
        raw_src=[m["source_asset_id"] for m in c["selected_media"]]
        for s in raw_src:selected_sources.add(s)
        fid=[m["representative_frame_id"] for m in c["selected_media"]]
        a,b=min(index[f] for f in fid),max(index[f] for f in fid)
        spans.append((a,b))
        per_ch.append({"order":i,"title":c["title"],"story":c["story"],
          "gallery_count":len(c["selected_media"]),
          "unique_source_clips":len(set(raw_src)),
          "earliest_selected_clip":a,"latest_selected_clip":b})
    overlap=[{"chapters":[i,i+1],"earlier_max_clip":spans[i-1][1],"later_min_clip":spans[i][0]}
          for i in range(1,len(spans)) if spans[i][0]<spans[i-1][1]]
    return {"offset":off,"method":"V03_JPEG","status":status["state"],
       "source_video_clips":160,"input_jpg":status["source_frames"],
       "chapter_count":len(chapters),"selected_total":sum(len(c["selected_media"]) for c in chapters),
       "selected_unique_source_clips":len(selected_sources),
       "api_calls":status["model_calls"],
       "input_tokens":status["prompt_tokens"],"output_tokens":status["completion_tokens"],
       "estimated_cost_cny":status["cost_cny_est"],"when":"historical",
       "chapters":per_ch,"narrative_theme_mentions":aliases(chapters),
       "time_span_overlap":overlap,
       "language_nonchinese_chapter_titles":[c["title"] for c in chapters
           if sum("\u3400"<=z<="\u9fff" for z in c["title"])<2],
       "schema_bff_publish_admit":True,"visual_semantic_truth_certified":False,
       "artifact_file":str(p/"result.json")}

def video_metrics(off,fps):
    key=str(fps).replace(".","p")
    folder=VIDEO10 if off==10 else RUN/"video"/f"offset_{off:03d}"
    path=folder/f"fps_{key}_result.json"
    if not path.exists():
        return {"offset":off,"method":"VIDEO","fps":fps,"status":"NOT_RUN",
                "when":"historical" if off==10 else "new","artifact_file":str(path)}
    # Enforce SAME 160 original source clips as the historical JPEG input.
    pre=json.loads((folder/"preflight.json").read_text())
    jpeg_bundle=json.loads(
        (ROOT/f"sydney-intro-cut-72s-20261105/offset_{off:03d}/input/bundle.json").read_text()
    )
    original_jpeg_assets=[asset["asset_id"] for asset in jpeg_bundle["assets"]]
    original_video_assets=[asset["asset_id"] for asset in pre["source_clips"]]
    assert len(original_jpeg_assets)==len(original_video_assets)==160
    assert original_jpeg_assets==original_video_assets, ("SOURCE_MISMATCH",off,fps)
    assert min(asset["source_original_start_s"] for asset in pre["source_clips"])>=80
    d=json.loads(path.read_text())
    m=d.get("metadata")
    assert m["prompt_sha256"]==pre["prompt_sha256"]
    assert m["video_part_sha256"]==[x["sha256"] for x in pre["parts"]]
    assert isinstance(m,dict)
    if not isinstance(d.get("model_output"),dict):
        return {"offset":off,"method":"VIDEO","fps":fps,"status":"OUTPUT_INVALID",
                "when":"historical" if off==10 else "new","artifact_file":str(path)}
    rows=d["model_output"].get("chapters",[])
    ref=d["mapped_source_moments"]
    raw_moments=sum(len(x.get("selected_moments", [])) for x in rows if isinstance(x,dict))
    # For qualitative evaluation, retain valid model Chapters even if a video
    # timestamp equals an exact 200-second block boundary. Provider state stays
    # OUTPUT_INVALID, and we distinguish raw vs source-mapped moment counts.
    posthoc=folder/f"fps_{key}_posthoc_boundary_recovery.json"
    replay=json.loads(posthoc.read_text()) if posthoc.is_file() else None
    if replay:
        assert replay["source_model_request_id"]==m["model_request_id"]
        assert replay["additional_api_calls"]==0
        ref=[{
            **x,
            "original_global_clip_seq":x["original_clip_sequence"],
        } for x in replay["mapped_moments"]]
    per_ch=[]
    spans=[]
    for i,c in enumerate(rows,1):
        loc=[x["original_global_clip_seq"] for x in ref if x["chapter"]==i]
        if loc:spans.append((min(loc),max(loc)))
        else:spans.append(None)
        per_ch.append({"order":i,"title":c.get("title",""),"story":c.get("story",""),
          "gallery_count":len(loc),"unique_source_clips":len(set(loc)),
          "earliest_selected_clip":min(loc) if loc else None,
          "latest_selected_clip":max(loc) if loc else None})
    overlap=[{"chapters":[i,i+1],"earlier_max_clip":spans[i-1][1],"later_min_clip":spans[i][0]}
          for i in range(1,len(spans)) if spans[i-1] and spans[i] and spans[i][0]<spans[i-1][1]]
    return {"offset":off,"method":"VIDEO","fps":fps,"status":m["state"],
       "source_video_clips":160,"input_jpg":0,
       "chapter_count":len(rows),"selected_total":len(ref),
       "raw_model_moment_count":raw_moments,
       "time_reference_errors_ignored_for_semantic_evaluation":m.get("errors",[]),
       "posthoc_only_no_new_api_calls":bool(replay),
       "selected_unique_source_clips":len(set(x["source_asset_id"] for x in ref)),
       "api_calls":1,"input_tokens":m["prompt_tokens"],"output_tokens":m["completion_tokens"],
       "estimated_cost_cny":m["estimated_cost_cny"],
       "when":"historical" if off==10 else "new",
       "chapters":per_ch,"narrative_theme_mentions":aliases(rows),
       "time_span_overlap":overlap,
       "language_nonchinese_chapter_titles":[c["title"] for c in rows
          if sum("\u3400"<=z<="\u9fff" for z in c.get("title",""))<2],
       "schema_bff_publish_admit":False,
       "video_source_time_mapped":True,
       "visual_semantic_truth_certified":False,
       "artifact_file":str(path)}
def go():
    all_rows=[]
    for off in OFFSETS:
        all_rows.append(image_metrics(off))
        for fps in (.5,1.0):
            all_rows.append(video_metrics(off,fps))
    known=[p for p in all_rows if p["status"]=="COMPLETE"]
    semantic_available=[p for p in all_rows if p.get("chapter_count",0)>0]
    total={"historic_jpeg_v03":round(sum(r["estimated_cost_cny"] for r in all_rows if r["method"]=="V03_JPEG"),8),
      "historic_video10":round(sum(r["estimated_cost_cny"] for r in all_rows if r["method"]=="VIDEO" and r["offset"]==10 and r["status"]=="COMPLETE"),8),
      "new_video":round(sum(r["estimated_cost_cny"] for r in all_rows if r["method"]=="VIDEO" and r["offset"]!=10 and "estimated_cost_cny" in r),8),
      "image_v04_aborted_cost_unknown":2,
      "completed_video_runs":len([r for r in all_rows if r["method"]=="VIDEO" and r["status"]=="COMPLETE"]),
      "video_runs_with_generated_chapters":len([r for r in all_rows if r["method"]=="VIDEO" and r.get("chapter_count",0)>0]),
      "total_video_six_cost_cny":round(sum(r["estimated_cost_cny"] for r in all_rows if r["method"]=="VIDEO" and "estimated_cost_cny" in r),8)}
    out={"captured_at_utc":datetime.now(timezone.utc).isoformat(),
        "method_compare":"Existing V03 JPEG vs compressed full 10s Video Qwen, not identical prompts/schemas",
        "important_caveat":"Model-selected source clips and chapter counts are not semantic quality scores.",
        "groups":OFFSETS,"rows":all_rows,"totals":total}
    (RUN/"SIX_GROUP_COMPARISON.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
    table=["# Sydney Citywalk 六偏移组：已有图片 V03 与视频 VLM 对比",
      "","图片组直接读取历史 V03 JSON，不重新向图片 VLM 发送任何请求。",
      "视频组是每个偏移组全 160 个真实 10 秒源视频片段；0.5fps、1fps 各一次，已实测不重复调用。",
      "**注意：输入和 Prompt / 输出 JSON 不同，因此是算法方案对照，而不是控制其他因素不变的纯输入模态消融。**",
      "","| 偏移 | 方法 | FPS | 运行状态 | Chapter | 最终入选媒体 | 入选的不同10s源片段 | 模型调用 | 输入Token | 输出Token | 历史/新增 | 估算¥ |",
      "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|---:|"]
    for r in all_rows:
        table.append("| {off}s | {method} | {fps} | {state} | {chap} | {imgs} | {uniq} | {calls} | {ipt} | {opt} | {when} | {cost} |".format(
            off=r["offset"],method=r["method"],fps=r.get("fps","—"),
            state=r["status"],chap=r.get("chapter_count","—"),
            imgs=r.get("selected_total","—"),uniq=r.get("selected_unique_source_clips","—"),
            calls=r.get("api_calls","—"),ipt=r.get("input_tokens","—"),
            opt=r.get("output_tokens","—"),when=r.get("when","—"),
            cost=f'{r["estimated_cost_cny"]:.8f}' if "estimated_cost_cny" in r else "—"))
    table.extend(["","## 真实费用","",f"图片 V03 历史（六组）：¥{total['historic_jpeg_v03']:.8f}",
       f"视频 10s 偏移历史（0.5/1fps）：¥{total['historic_video10']:.8f}",
       f"本轮新增视频（当前已有结果）：¥{total['new_video']:.8f}",
       "误启动但被取消的图片 V04 20s/30s 请求没有 usage 回执，费用未知；请另查实际账单。",
       "","## 按偏移组逐章比对",""])
    for off in OFFSETS:
        table.append(f"### {off}s")
        for r in all_rows:
            if r["offset"]!=off:continue
            title=r["method"]+(f" {r['fps']}fps" if r["method"]=="VIDEO" else "")
            table.append(f"**{title}**：{r['status']}，{r.get('chapter_count','—')} 章，{r.get('selected_total','—')} 张图/选点")
            for c in r.get("chapters",[]):
                table.append(f"- C{c['order']:02d} · {c['title']}（{c['gallery_count']} 图/点，源片 {c['earliest_selected_clip']}–{c['latest_selected_clip']}）")
            if r.get("time_span_overlap"):
                table.append(f"相邻分章时间范围重叠：{r['time_span_overlap']}")
            if r.get("narrative_theme_mentions"):
                table.append(f"叙述提及地标/场景：{'、'.join(r['narrative_theme_mentions'])}（仅文本提及，不等于视觉证实）")
            table.append("")
    (RUN/"SIX_GROUP_COMPARISON.md").write_text("\n".join(table))
    print("SIX_GROUPS_COMPARISON_UPDATED",len(known),"/",len(all_rows),
          "schema-valid rows; qualitative outputs",len(semantic_available),"/",len(all_rows),
          "including boundary-invalid with real Chapters; known fees",total,flush=True)
if __name__=="__main__":go()
