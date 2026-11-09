#!/usr/bin/env python3
"""Non-invented six-offset VLM financial ledger, historical vs new.

Charges are taken ONLY from persisted provider usage. Interrupted HTTP calls
without usage are flagged unknown, never silently treated as free.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
import csv

ROOT=Path.home()/"Documents/Nexleap/work_logs/evidence"
BENCH=ROOT/"sydney-six-offset-image-vs-video-20261109"
IMAGE=ROOT/"sydney-direct-vlm-compact-v03-20261105"
VIDEO10=ROOT/"sydney-video-full-160-fps-ab-20261109"
OFFSETS=[10,20,30,50,60,70]
EXPENSE=[]
def put(method,version,off,fps,when,path,model_calls,input_tokens,output_tokens,cost,state,notes="",receipt=None):
    EXPENSE.append({
        "method":method,"version":version,"offset_s":off,"fps":fps,
        "period":when,"state":state,"model_calls":model_calls,
        "input_tokens":input_tokens,"output_tokens":output_tokens,
        "estimated_cny":cost,"source":str(path),
        "notes":notes,"request_id":receipt,
    })
for off in OFFSETS:
    source=IMAGE/f"offset_{off:03d}/status.json"
    data=json.loads(source.read_text())
    assert data["state"]=="COMPLETE"
    attempts=sorted((source.parent/"attempt_audit").glob("attempt_*.json"))
    assert len(attempts)==data["model_calls"]
    for i,attempt in enumerate(attempts,1):
        x=json.loads(attempt.read_text())
        assert abs(sum(json.loads(a.read_text())["estimated_cost_native"] for a in attempts)-data["cost_cny_est"])<0.00001
        put("JPEG+VLM","V03",off,None,"historical",attempt,1,x["input_tokens"],
            x["output_tokens"],round(x["estimated_cost_native"],8),"COMPLETE",
            f"prior real image API attempt {i}/{len(attempts)}",x.get("request_id"))
        # prompt and run model stage is known from trace

off10=ROOT/"sydney-direct-vlm-compact-v04b-coverage-20261105/offset_010/status.json"
if off10.exists():
    data=json.loads(off10.read_text())
    put("JPEG+VLM","V04b",10,None,"historical_auxiliary",off10,
        data.get("model_calls"),data.get("prompt_tokens"),data.get("completion_tokens"),
        data.get("cost_cny_est"),data.get("state"),"V04b alternate photo baseline; excluded from main six-group V03 totals")

for off in OFFSETS:
    for fps,key in ((0.5,"0p5"),(1.0,"1p0")):
        folder=(VIDEO10 if off==10 else BENCH/"video"/f"offset_{off:03d}")
        source=folder/f"fps_{key}_status.json"
        if not source.exists():
            put("VIDEO+VLM","video_full160",off,fps,
                "historical" if off==10 else "new",source,0,0,0,None,"NOT_STARTED",
                "Video processing or API is not yet complete")
            continue
        data=json.loads(source.read_text())
        put("VIDEO+VLM","video_full160",off,fps,
            "historical" if off==10 else "new",source,
            1 if data.get("http_status")==200 else None,
            data.get("prompt_tokens"),data.get("completion_tokens"),
            data.get("estimated_cost_cny"),data.get("state"),
            "provider usage read from actual status.json" if "estimated_cost_cny" in data
            else "NO PROVIDER USAGE: billing unconfirmed",data.get("model_request_id"))

for off in (20,30):
    folder=BENCH/"image"/f"offset_{off:03d}"
    source=folder/"status.json"
    if source.is_file():
        d=json.loads(source.read_text())
        audits=list((folder/"attempt_audit").glob("*.json"))
        if audits:
            for a in audits:
                x=json.loads(a.read_text())
                put("JPEG+VLM","V04_unintended_repeat",off,None,"new_unplanned",a,1,
                    x.get("input_tokens"),x.get("output_tokens"),
                    x.get("estimated_cost_native"),"STOPPED_AFTER_DUPLICATE_DETECTED",
                    "Unexpected image rerun stopped, actual usage audit saved")
        else:
            put("JPEG+VLM","V04_unintended_repeat",off,None,"new_unplanned",source,None,
                None,None,None,"CANCELLED_NO_RESPONSE",
                "Interrupted before any usage receipt. Provider may still bill; account billing requires reconciliation.")

totals={}
for p in EXPENSE:
    group=(p["method"],p["period"])
    total=totals.setdefault(group,{"known_cny":0,"known_calls":0,
                                   "unknown_cost_records":0,"input_tokens":0,"output_tokens":0})
    if p["estimated_cny"] is not None:
        total["known_cny"]+=p["estimated_cny"]
        total["known_calls"]+=(p["model_calls"] or 0)
        total["input_tokens"]+=p["input_tokens"] or 0
        total["output_tokens"]+=p["output_tokens"] or 0
    elif p["state"] not in ("NOT_STARTED",):
        total["unknown_cost_records"]+=1
for t in totals.values():
    t["known_cny"]=round(t["known_cny"],8)
raw={"recorded_at_utc":datetime.now(timezone.utc).isoformat(),
     "experiment":"sydney_phase_01_02_03_05_06_07",
     "currency":"CNY",
     "unit_prices_cny_per_million_tokens":{"input":0.8,"output":2.7},
     "historical_and_new_disjoint":True,
     "estimated_cost_not_provider_invoice":True,
     "expenses":EXPENSE,
     "totals":[{"method":m,"period":period,**value} for (m,period),value in sorted(totals.items())],
    }
out=BENCH/"API_EXPENSE_LEDGER.json"
out.write_text(json.dumps(raw,ensure_ascii=False,indent=2))
lines=["# 悉尼六组对照：实际调用与费用记录", "",
       "费用来自真实已保存的模型 usage；¥ 为人民币估算，不是服务商实际账单。取消请求未收到 usage 时标记为未知，不记为 ¥0。",
       "",
       "| 方法 | 版本 | 偏移 | FPS | 发生时期 | 状态 | API 次数 | 输入 Tokens | 输出 Tokens | 估算费用(CNY) |",
       "|---|---|---:|---:|---|---|---:|---:|---:|---:|"]
for p in EXPENSE:
    lines.append("| {method} | {version} | {offset_s}s | {fps} | {period} | {state} | {calls} | {input} | {output} | {cost} |".format(
        method=p["method"],version=p["version"],offset_s=p["offset_s"],
        fps=p["fps"] if p["fps"] is not None else "—",
        period=p["period"],state=p["state"],
        calls=p["model_calls"] if p["model_calls"] is not None else "待核对",
        input=p["input_tokens"] if p["input_tokens"] is not None else "待核对",
        output=p["output_tokens"] if p["output_tokens"] is not None else "待核对",
        cost=f'{p["estimated_cny"]:.8f}' if p["estimated_cny"] is not None else "待核对" ))
lines+=["","## 分类汇总","","| 方法 | 期间 | 已确认调用 | 已知费用 CNY | 费用待核对数 |",
        "|---|---|---:|---:|---:|"]
for (m,period),value in sorted(totals.items()):
    lines.append(f"| {m} | {period} | {value['known_calls']} | {value['known_cny']:.8f} | {value['unknown_cost_records']} |")
lines+=["","备注：图片 V03 的六组历史结果均已存在，新的基线不需要重跑。10s V04b 是不同 Prompt/版本，仅作辅助对照，避免与 V03 六组汇总重复记账。",
        "Cancelled V04 image runs in 20s/30s were terminated without recorded usage; no definitive cost claim until provider billing data is available."]
(BENCH/"API_EXPENSE_LEDGER.md").write_text("\n".join(lines)+"\n")
print("LEDGER_WRITTEN",out)
for (m,period),v in sorted(totals.items()):
    print("TOTAL",m,period,v)
