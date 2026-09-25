import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the phone-library test-day contract", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Diary One · Real-media Test Lab<\/title>/i);
  assert.match(html, /一次导入 = 一个测试日/);
  assert.match(html, /仅按导入顺序，不代表真实时间/);
  assert.match(html, /GPS 与拍摄时间/);
  assert.match(html, /照片 1 帧 · 视频按时长分 Window/);
  assert.match(html, /不校准穿戴分布/);
  assert.match(html, /本页要求 Storyline V03 \/ Writer V02/);
  assert.doesNotMatch(html, /Captured by You|Mock output only/);
});

test("keeps browser evidence generation and research boundaries explicit", async () => {
  const [page, evidence, contracts, findings, resultContract, runControl, readme, layout] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/media-evidence.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/contracts.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/contract-findings.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/result-contract.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/research-run-control.ts", import.meta.url), "utf8"),
    readFile(new URL("../README.md", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
  ]);

  assert.match(page, /PHONE_LIBRARY_DAY_TEST/);
  assert.match(page, /不推算间隔或当天时长/);
  assert.match(page, /eachImportIsOneDay:\s*true/);
  assert.match(page, /captureTimeIgnored:\s*true/);
  assert.match(page, /gpsIgnored:\s*true/);
  assert.match(page, /fullProductionPipelineClaimed:\s*false/);
  assert.match(page, /importOrderIsSequenceOnly:\s*true/);
  assert.match(page, /syntheticChronologyClaimed:\s*false/);
  assert.match(page, /logicalAssetDuration9000IsNormalizationOnly:\s*true/);
  assert.doesNotMatch(page, /importOrderIsSyntheticChronology/);
  assert.match(page, /X02_STAGED_REAL_MEDIA_PREVIEW_NOT_PRODUCTION/);
  assert.match(page, /DIARY_ONE_HUMAN_EVALUATION_V02/);
  assert.match(page, /saveRunSidecar/);
  assert.match(page, /只收集，暂不自动学习/);
  assert.match(page, /可审计判断依据，不是模型隐藏思维/);
  assert.match(page, /Boundary Ledger/);
  assert.match(page, /被拒绝的 Observation/);
  assert.match(page, /EvidenceImage/);
  assert.match(page, /为什么现在可以超过 24 项/);
  assert.match(page, /逐流程消耗/);
  assert.match(evidence, /const OUTPUT_WIDTH = 768/);
  assert.match(evidence, /const OUTPUT_HEIGHT = 1024/);
  assert.match(evidence, /PHONE_TEST_DURATION_WINDOWS_V01/);
  assert.match(evidence, /durationMs <= 10_000/);
  assert.match(evidence, /durationMs <= 30_000/);
  assert.match(evidence, /durationMs <= 90_000/);
  assert.match(evidence, /PHOTO_SINGLE_FRAME/);
  assert.match(evidence, /VIDEO_MULTI_WINDOW_TWO_PER_WINDOW/);
  assert.match(evidence, /DIARY_ONE_X02_STAGED_PREVIEW_V04_1/);
  assert.match(evidence, /DIARY_ONE_X02_STORYLINE_V03/);
  assert.match(evidence, /DIARY_ONE_X02_WRITER_SURFACE_V02/);
  assert.match(evidence, /\/x02\/v0\.4\.1\/preview/);
  assert.match(evidence, /\/x02\/v0\.4\.1\/run-sidecar/);
  assert.match(evidence, /timeline_basis !== "SYNTHETIC_SEQUENCE_ONLY"/);
  assert.match(evidence, /timeline_date !== null/);
  assert.match(evidence, /sequence_index: index/);
  assert.match(evidence, /DIARY_ONE_APP_LIBRARY_BUNDLE_V04/);
  assert.match(evidence, /trace\?\.input_bundle_version !== bundle.manifest.bundle_version/);
  assert.doesNotMatch(evidence, /timeline_offset_ms: index \* 120_000/);
  assert.match(evidence, /V041_SEMANTIC_DAY_STATES/);
  assert.match(evidence, /coverageStateConsistent/);
  assert.match(evidence, /v041ResultContractConsistent/);
  assert.match(evidence, /perceptionBatchMaxAssets !== 3/);
  assert.match(evidence, /perceptionBatchMaxFrames !== 18/);
  assert.match(evidence, /FRESH_FULL_RUN/);
  assert.match(evidence, /original_included:\s*false/);
  assert.match(evidence, /source_display_name:\s*asset\.name/);
  assert.match(evidence, /run-sidecar/);
  assert.match(evidence, /client_trace/);
  assert.match(evidence, /runAuditEnabled/);
  assert.match(evidence, /granularObservationValidation/);
  assert.match(evidence, /fieldLevelObservationDegradation/);
  assert.match(evidence, /durationAwarePhoneTestEvidence/);
  assert.match(evidence, /失败详情、Token 与成本已经保存/);
  assert.match(evidence, /runSidecarPath/);
  assert.match(contracts, /evaluation_id: string/);
  assert.match(contracts, /revision: number/);
  assert.match(contracts, /boundary_edges: Array/);
  assert.match(contracts, /observation_candidates\?: X01ObservationDecision\[\]/);
  assert.match(contracts, /PASSED_WITH_FIELD_DEGRADATION/);
  assert.match(contracts, /X02StorylineIdentity/);
  assert.match(contracts, /semantic_day_state: X02SemanticDayState/);
  assert.match(contracts, /UNRESOLVED_DAY/);
  assert.match(contracts, /validation_scope: "STAGED_PREVIEW_ONLY"/);
  assert.match(contracts, /writer_surface_policy_version: "DIARY_ONE_X02_WRITER_SURFACE_V02"/);
  assert.match(contracts, /delivery_state: X02DeliveryState/);
  assert.match(contracts, /coverage_status: "COMPLETE" \| "PARTIAL_UNRESOLVED"/);
  assert.match(contracts, /selected_memory_outcomes: X02SelectedMemoryOutcome\[\]/);
  assert.match(contracts, /perceptionBatchMaxEvidenceBytes: 4194304/);
  assert.match(contracts, /perceptionSingleAssetRetryLimit: 1/);
  assert.match(contracts, /perception_batching: X02PerceptionBatching/);
  assert.match(contracts, /MODEL_SURFACE_VERIFIED/);
  assert.match(contracts, /DETERMINISTIC_FALLBACK_VERIFIED/);
  assert.match(contracts, /surface_source: "MODEL_WRITER" \| "DETERMINISTIC_GROUNDED_FALLBACK"/);
  assert.match(contracts, /timeline_date: string \| null/);
  assert.match(page, /本章聚类依据/);
  assert.match(page, /仅结构与引用检查通过，内容关系仍需评价/);
  assert.match(page, /本轮实际算法版本/);
  assert.match(page, /next\.writer_surface_policy_version !== server\.writerSurfacePolicyVersion/);
  assert.match(page, /逐项查看为什么归入这条 Storyline/);
  assert.match(page, /每个入选记忆最终去了哪里/);
  assert.match(page, /语义日状态/);
  assert.match(page, /交付状态/);
  assert.match(page, /可靠事实兜底文案/);
  assert.match(page, /每批最多 3 项/);
  assert.match(page, /算法找到了，但不能当作正式结果/);
  assert.match(page, /不会计入上方 Chapter \/ Aha 数量/);
  assert.match(page, /诊断候选不进入正式逐项评分/);
  assert.match(page, /projectV041Memories/);
  assert.match(page, /本轮结果使用的算法合同与连接时不一致/);
  assert.match(page, /没有从导入时间伪造拍摄日期/);
  assert.match(page, /`导入顺序\$\{normalized\}`/);
  assert.match(page, /当前接口不提供阶段心跳/);
  assert.match(page, /取消本轮/);
  assert.match(page, /indeterminate=\{runState === "RUNNING"\}/);
  assert.match(page, /elapsed\(cloudRunElapsedMs\)/);
  assert.match(findings, /AHA_VISIBLE_MEDIA_COUNT/);
  assert.match(findings, /UNREGISTERED_CANONICAL_TAG/);
  assert.match(findings, /projectV041Memories/);
  assert.match(resultContract, /publicationAndOutcomeConsistent/);
  assert.match(resultContract, /resultStateMatrixConsistent/);
  assert.match(resultContract, /perceptionBatchingConsistent/);
  assert.match(resultContract, /selectedOutcomeLineageConsistent/);
  assert.match(resultContract, /roots\.flatMap\(\(attempt\) => attempt\.asset_ids\)/);
  assert.match(resultContract, /terminalUnresolved/);
  assert.match(resultContract, /expectedAttemptMetrics/);
  assert.match(resultContract, /surface_policy_version !== result\.writer_surface_policy_version/);
  assert.match(contracts, /RESPONSE_INVALID/);
  assert.match(contracts, /ORIGINAL_BATCH_RETRY/);
  assert.match(contracts, /run_max_model_call_attempts: 96/);
  assert.match(runControl, /15 \* 60 \* 1000/);
  assert.match(runControl, /no stage heartbeat/i);
  assert.match(readme, /3–9 分钟/);
  assert.match(readme, /15 分钟/);
  assert.match(readme, /标准化包络/);
  assert.match(layout, /Real-media Test Lab/);
});
