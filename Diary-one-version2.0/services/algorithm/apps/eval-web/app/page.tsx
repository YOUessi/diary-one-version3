"use client";

import { ChangeEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import { canonicalTagLabels, evaluateLatestContract } from "./lib/contract-findings";
import {
  buildEvidenceBundle,
  checkResearchServer,
  inspectFiles,
  runResearchPreview,
  saveRunSidecar,
} from "./lib/media-evidence";
import { projectV041Memories } from "./lib/result-contract";
import { currentRuntimePolicies, runtimePolicyLabel } from "./lib/codex-runtime-policy";
import { ahaLengthReview } from "./lib/codex-writer-review";
import { ResearchPreviewCancelledError } from "./lib/research-run-control";
import type {
  AppLibraryBundleManifest,
  ContractFinding,
  HumanEvaluationIssueCodeV02,
  HumanEvaluationV02,
  HumanReviewAction,
  HumanReviewAspect,
  HumanReviewItemV02,
  HumanReviewTargetType,
  HumanReviewVerdict,
  TestAsset,
  X01Editorial,
  X01Health,
  X01Result,
} from "./lib/contracts";

type Tab = "测试日" | "今日记忆" | "结果评估" | "决策轨迹" | "运行信息";
type RunState = "EMPTY" | "READING" | "READY" | "PREPARING" | "RUNNING" | "COMPLETE" | "FAILED";
type SaveState = "IDLE" | "SAVING" | "SAVED" | "FAILED";
type EvidencePreview = {
  frameId: string;
  assetId: string;
  canonicalOffsetMs: number;
  windowIndex: number;
  windowCount: number;
  sourceTimestampMs: number | null;
  url: string;
};

const tabs: Array<{ id: Tab; en: string }> = [
  { id: "测试日", en: "Test Day" },
  { id: "今日记忆", en: "Memory Result" },
  { id: "结果评估", en: "Evaluation" },
  { id: "决策轨迹", en: "Decision Trace" },
  { id: "运行信息", en: "Run Info" },
];

const globalIssueOptions: Array<[HumanEvaluationIssueCodeV02, string]> = [
  ["CHAPTER_COUNT_WRONG", "Chapter 数量不合适"],
  ["AHA_COUNT_WRONG", "Aha 数量不合适"],
  ["DAY_NOT_REPRESENTATIVE", "没有代表这一天"],
  ["FALSE_CLAIM_GLOBAL", "存在事实编纂"],
];

const verdictOptions: Array<[HumanReviewVerdict, string]> = [
  ["PASS", "正确"],
  ["NEEDS_CHANGE", "需要修改"],
  ["REJECT", "不应保留"],
  ["MISSING", "有遗漏"],
];

const aspectIssueOptions: Record<HumanReviewAspect, Array<[HumanEvaluationIssueCodeV02, string]>> = {
  BOUNDARY: [
    ["START_WRONG", "开始位置不对"], ["END_WRONG", "结束位置不对"],
    ["SHOULD_SPLIT", "应该拆开"], ["SHOULD_MERGE", "应该合并"],
    ["UNRELATED_ASSET_GROUPED", "混入无关素材"], ["RELATED_ASSET_SEPARATED", "相关素材被分开"],
  ],
  MEDIA_SELECTION: [
    ["MEDIA_IRRELEVANT", "素材不相关"], ["MEDIA_REDUNDANT", "素材重复"],
    ["MEDIA_MISSING", "遗漏关键素材"], ["HERO_WRONG", "封面不对"],
    ["FRAME_WRONG", "代表帧不对"], ["LOW_QUALITY_SELECTED", "选中了低质量素材"],
  ],
  TITLE: [
    ["TITLE_INACCURATE", "标题不准确"], ["TITLE_GENERIC", "标题太泛"],
    ["TITLE_TONE", "标题语气不对"], ["TITLE_TOO_LONG", "标题太长"],
  ],
  STORY: [
    ["STORY_FALSE_CLAIM", "文案有编纂"], ["STORY_STIFF", "文案生硬"],
    ["STORY_OVER_INTERPRETED", "过度解读"], ["STORY_MISSES_KEY_POINT", "遗漏重点"],
    ["STORY_TOO_LONG", "文案太长"],
  ],
  TAGS: [
    ["TAG_WRONG", "Tag 错误"], ["TAG_MISSING", "缺少 Tag"], ["TAG_TOO_BROAD", "Tag 太宽泛"],
  ],
  AHA_INDEPENDENCE: [
    ["AHA_NOT_INDEPENDENT", "不是独立故事"], ["AHA_WRONG_CORE_ASSET", "核心素材不对"],
    ["AHA_SHOULD_EXIST", "应该形成 Aha"], ["AHA_SHOULD_NOT_EXIST", "不应该形成 Aha"],
  ],
  ASSET_UNDERSTANDING: [
    ["ASSET_MISUNDERSTOOD", "素材理解错误"], ["ASSET_IMPORTANT_BUT_UNUSED", "重要但没有使用"],
    ["ASSET_CORRECTLY_UNUSED", "未使用是正确的"], ["CROP_LOST_SUBJECT", "裁切丢失主体"],
  ],
};

const decisionReasonLabels: Record<string, string> = {
  AHA_ASSET_COUNT_NOT_ONE: "Aha 核心素材不是恰好一项",
  AHA_CAPACITY_LIMIT: "超过本轮 Aha 数量上限",
  AHA_COPY_CONTRACT_FAILED: "Aha 文案不符合合同",
  ASSET_IDS_INVALID: "素材引用格式无效",
  ASSET_ID_INVALID: "Observation 的素材引用格式无效",
  ASSET_OVERLAP_WITH_SELECTED_CHAPTER: "素材已被入选 Chapter 使用",
  ASSET_WITHOUT_MATERIALIZED_MOMENT: "素材没有形成有效 Moment",
  BELOW_CONFIDENCE_THRESHOLD: "置信度低于门槛",
  CANDIDATE_NOT_OBJECT: "候选结构无效",
  CHAPTER_ASSET_COUNT_OUT_OF_RANGE: "Chapter 素材数量不符合当前合同",
  CHAPTER_CAPACITY_LIMIT: "超过本轮 Chapter 数量上限",
  CHAPTER_COPY_CONTRACT_FAILED: "Chapter 文案不符合合同",
  CLAIMS_INVALID: "事实声明缺少合法依据",
  CONFIDENCE_INVALID: "置信度格式无效",
  COPY_FIELD_INVALID: "文案字段无效",
  COPY_HARD_LENGTH_LIMIT: "文案超过硬长度限制",
  CORE_ASSET_ALREADY_OWNED_BY_CHAPTER: "核心素材已属于 Chapter 主故事",
  DUPLICATE_KEY: "候选标识重复",
  DUPLICATE_ASSET_OBSERVATION: "同一素材出现了重复 Observation",
  EDITORIAL_OVERLAP_THRESHOLD: "与已选故事过于相似",
  EVIDENCE_FRAME_IDS_INVALID: "Evidence 帧引用无效",
  EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL: "引用了模型没有看到的 Evidence",
  EVIDENCE_FRAME_OUTSIDE_CANDIDATE: "Evidence 不属于该候选素材",
  HERO_ASSET_INVALID: "封面素材引用无效",
  HERO_ASSET_OUTSIDE_CANDIDATE: "封面不属于该候选",
  INVALID_FRAME: "Evidence 帧无效或归属错误",
  KEY_INVALID: "候选标识无效",
  LOW_CONFIDENCE: "置信度较低",
  MATERIALIZED: "已形成可用 Moment",
  MOMENT_KEYS_INVALID: "Moment 引用格式无效",
  OBSERVED_FACTS_INVALID: "Observation 的事实字段无效",
  MOMENT_NOT_MATERIALIZED: "引用的 Moment 没有通过最终实例化",
  SELECTED_BY_CONFIDENCE_AND_NARRATIVE_SEPARATION: "按置信度与故事独立性入选",
  SELECTED_BY_CONFIDENCE_AND_TIMELINE: "按置信度与时间线覆盖入选",
  SUPERSEDED_BY_EARLIER_EQUAL_CONFIDENCE: "被更早的同置信度候选替代",
  SUPERSEDED_BY_HIGHER_CONFIDENCE: "被更高置信度候选替代",
  TAGS_INVALID: "Tag 结构无效",
  UNKNOWN_ASSET: "引用了未知素材",
  UNKNOWN_CANONICAL_TAG: "包含未注册的 Canonical Tag",
  UNKNOWN_MOMENT_KEY: "引用了未知 Moment",
  UNSUPPORTED_USER_STATE_TERM: "包含无证据的用户状态表达",
  VALIDATION_PASSED: "基础合同校验通过",
  ONE_STORY_GATE_PASSED: "候选只承担一条清晰故事线",
  PRIMARY_FOCUS_PURITY_PASSED: "所有成员属于同一核心经历",
  BEAT_MAP_COMPLETE: "每项素材的贡献引用已齐全",
  MODEL_MEMBERSHIP_STRUCTURE_PASSED_NOT_QUALITY_VERIFIED: "模型分组已通过结构检查，内容质量待评价",
  SELECTED_BY_EXISTING_VALUE_FORMULA_NOT_QUALITY_VERIFIED: "按现有评分入选，不代表内容质量已验证",
  MODEL_GROUPING_NOT_OVERRIDDEN_BY_TAGS_OR_IMPORT_ORDER: "保留模型分组，不按标签或导入位置改组",
  STORYLINE_STRUCTURE_GATE_REJECTED: "素材数量或分组结构未通过检查",
  NO_SHARED_ASSET_NOT_PROOF_OF_STORY_INDEPENDENCE: "未重复使用素材，不等于故事独立性已证明",
  STORYLINE_MEMBER_PRIMARY_FOCUS_MISMATCH: "混入了其他核心经历的素材",
  STORYLINE_MEMBER_GAP_EXCEEDS_BOUND: "同类素材在时间线上相距过远",
  STORYLINE_BASIS_FOCUS_MISMATCH: "故事组织方式与核心经历不匹配",
  SAME_FOCUS_BOUNDED_MEMORY_REDUNDANCY: "与已选故事是同一段连续经历",
  MAXIMIZES_MEANINGFUL_STORYLINE_SET: "在合格故事中组成最有意义的一组",
  LOWER_INDEPENDENT_STORYLINE_VALUE: "独立成章价值低于已选组合",
};

function decisionReason(code: string) {
  return decisionReasonLabels[code] ? `${decisionReasonLabels[code]} · ${code}` : code;
}

const storylineBasisLabels: Record<string, string> = {
  EVENT_PROGRESSION: "事件发展",
  ACTIVITY_THREAD: "持续活动",
  DISCOVERY_SERIES: "一组相关发现",
  SOCIAL_INTERACTION: "具体互动",
};

const storylineFormLabels: Record<string, string> = {
  SINGLE: "来自同一上游素材组",
  ADJACENT_GROUP: "导入顺序相邻的成员",
  RESUMED_EPISODE: "导入序列中的两段成员",
  LOCAL_EPISODE_GROUP: "导入序列中的多段成员",
  COMPACT_TWO_MEMBER: "两项素材的紧凑候选",
};

function bytes(value: number) {
  if (value < 1024 * 1024) return `${Math.max(1, Math.round(value / 1024))} KB`;
  if (value < 1024 * 1024 * 1024) return `${(value / 1024 / 1024).toFixed(1)} MB`;
  return `${(value / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

function duration(value: number | null) {
  if (value === null) return "照片";
  const seconds = Math.round(value / 1000);
  if (seconds < 60) return `${seconds} 秒`;
  return `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`;
}

function elapsed(value: number | null | undefined) {
  if (value === null || value === undefined) return "—";
  if (value < 1_000) return `${Math.round(value)} ms`;
  const seconds = value / 1_000;
  if (seconds < 60) return `${seconds.toFixed(seconds < 10 ? 2 : 1)} 秒`;
  return `${Math.floor(seconds / 60)} 分 ${(seconds % 60).toFixed(1)} 秒`;
}

function stateLabel(state: RunState) {
  return ({
    EMPTY: "等待导入",
    READING: "读取素材",
    READY: "可以生成",
    PREPARING: "生成 Evidence",
    RUNNING: "算法处理中",
    COMPLETE: "已完成",
    FAILED: "需要处理",
  } as const)[state];
}

function semanticDayStateLabel(state: X01Result["semantic_day_state"]) {
  return ({
    CHAPTER_DAY: "Chapter Day",
    HIGHLIGHT_DAY: "Highlight Day",
    EMPTY_DAY: "Empty Day",
    UNRESOLVED_DAY: "本轮内容状态未决",
  } as const)[state];
}

function deliveryStateLabel(state: X01Result["delivery_state"]) {
  return ({
    READY_PRIMARY_COPY: "模型文案已验证",
    READY_WITH_GROUNDED_COPY_FALLBACK: "已使用可靠事实兜底",
    READY_WITH_ITEM_BLOCKS: "部分入选项未能呈现",
    PIPELINE_BLOCKED: "整轮交付受阻",
    NO_GROUNDED_MEMORY: "没有合格记忆",
  } as const)[state];
}

function surfaceSourceLabel(source: X01Editorial["surface_source"]) {
  return source === "MODEL_WRITER" ? "模型文案" : "可靠事实兜底文案";
}

function timelineDisplayLabel(result: X01Result, label: string) {
  if (result.timeline_basis !== "SYNTHETIC_SEQUENCE_ONLY") return label;
  const normalized = label.trim().replace(/-/g, "–");
  return /^第\d+(?:–\d+)?项$/.test(normalized)
    ? `导入顺序${normalized}`
    : "仅按导入顺序（范围未记录）";
}

function selectedOutcomeLabel(value: string) {
  return ({
    S09_SELECTED: "S09 已入选",
    S10_MEDIA_READY: "S10 媒体已就绪",
    S10_MEDIA_BLOCKED: "S10 媒体受阻",
    MODEL_SURFACE_VERIFIED: "模型文案已验证",
    DETERMINISTIC_FALLBACK_VERIFIED: "可靠事实兜底已验证",
    COPY_BLOCKED: "文案未通过",
    NOT_ATTEMPTED: "尚未尝试文案",
    VISIBLE_PREVIEW: "已在 Preview 呈现",
    DIAGNOSTIC_ONLY: "仅保留在诊断记录",
  } as Record<string, string>)[value] || value;
}

function uniqueAssetIds(memory: X01Editorial, result: X01Result) {
  if (memory.selected_media?.length) {
    return [...new Set(memory.selected_media.map((item) => item.asset_id))];
  }
  const momentAssets = new Map(result.moments.map((moment) => [moment.id, moment.asset_ids]));
  return [...new Set(memory.moment_ids.flatMap((id) => momentAssets.get(id) || []))];
}

function formatTag(tag: string) {
  return canonicalTagLabels[tag] ? `${canonicalTagLabels[tag]} · ${tag}` : tag;
}

function publicAssetId(value: string) {
  return value.startsWith("asset_") ? value.slice(6) : value;
}

function newEvaluation(result: X01Result): HumanEvaluationV02 {
  if (!result.trace.run_id) {
    throw new Error("算法服务未返回审计 Run ID；请重启本机服务后再运行");
  }
  const now = new Date().toISOString();
  return {
    schema_version: "DIARY_ONE_HUMAN_EVALUATION_V02",
    session_id: result.session_id,
    run_id: result.trace.run_id,
    evaluation_id: crypto.randomUUID(),
    revision: 0,
    bundle_manifest_sha256: result.bundle_manifest_sha256,
    pipeline_version: result.trace.pipeline_version,
    request_id: result.trace.request_id,
    status: "DRAFT",
    created_at: now,
    updated_at: now,
    global: { rating: 0, verdict: "UNREVIEWED", issue_codes: [], notes: "" },
    reviews: [],
  };
}

function reviewKey(targetType: HumanReviewTargetType, targetId: string, aspect: HumanReviewAspect) {
  return `${targetType}:${targetId}:${aspect}`;
}

function updateReview(
  evaluation: HumanEvaluationV02,
  targetType: HumanReviewTargetType,
  targetId: string,
  parentEditorialId: string | null,
  aspect: HumanReviewAspect,
  patch: Partial<HumanReviewItemV02>,
): HumanEvaluationV02 {
  const key = reviewKey(targetType, targetId, aspect);
  const existingIndex = evaluation.reviews.findIndex((item) => (
    reviewKey(item.target_type, item.target_id, item.aspect) === key
  ));
  const existing: HumanReviewItemV02 = existingIndex >= 0
    ? evaluation.reviews[existingIndex]
    : {
      review_id: crypto.randomUUID(),
      target_type: targetType,
      target_id: targetId,
      parent_editorial_id: parentEditorialId,
      aspect,
      verdict: "UNREVIEWED",
      issue_codes: [],
      asset_ids: [],
      frame_ids: [],
      related_entity_ids: [],
      suggestion: { text: "", tags: [], action: null },
      notes: "",
    };
  const next = { ...existing, ...patch };
  const reviews = [...evaluation.reviews];
  if (existingIndex >= 0) reviews[existingIndex] = next;
  else reviews.push(next);
  return { ...evaluation, revision: evaluation.revision + 1, status: "DRAFT", updated_at: new Date().toISOString(), reviews };
}

export default function Home() {
  const [tab, setTab] = useState<Tab>("测试日");
  const [runState, setRunState] = useState<RunState>("EMPTY");
  const [assets, setAssets] = useState<TestAsset[]>([]);
  const [endpoint, setEndpoint] = useState("http://127.0.0.1:8787");
  const [token, setToken] = useState("");
  const [health, setHealth] = useState<X01Health | null>(null);
  const [result, setResult] = useState<X01Result | null>(null);
  const [manifest, setManifest] = useState<AppLibraryBundleManifest | null>(null);
  const [evidencePreviews, setEvidencePreviews] = useState<EvidencePreview[]>([]);
  const [evidenceBytes, setEvidenceBytes] = useState(0);
  const [progress, setProgress] = useState({ done: 0, total: 0, label: "" });
  const [error, setError] = useState("");
  const [evaluation, setEvaluation] = useState<HumanEvaluationV02 | null>(null);
  const [saveState, setSaveState] = useState<SaveState>("IDLE");
  const [saveError, setSaveError] = useState("");
  const [showRaw, setShowRaw] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [cloudRunElapsedMs, setCloudRunElapsedMs] = useState(0);
  const importVersion = useRef(0);
  const generationVersion = useRef(0);
  const previewAbortController = useRef<AbortController | null>(null);
  const reviewSaveQueue = useRef<Promise<void>>(Promise.resolve());
  const evidencePreviewsRef = useRef<EvidencePreview[]>([]);

  const readyAssets = assets.filter((asset) => asset.decodeStatus === "READY");
  const unsupportedAssets = assets.filter((asset) => asset.decodeStatus === "UNSUPPORTED");
  const photos = assets.filter((asset) => asset.kind === "PHOTO").length;
  const videos = assets.length - photos;
  const currentMaxAssets = health?.maxAssets ?? 240;
  const findings = useMemo<ContractFinding[]>(
    () => result ? evaluateLatestContract(result) : [],
    [result],
  );
  const assetById = useMemo(() => new Map(assets.map((asset) => [asset.id, asset])), [assets]);
  const evidenceByFrameId = useMemo(
    () => new Map(evidencePreviews.map((preview) => [preview.frameId, preview])),
    [evidencePreviews],
  );

  function replaceEvidencePreviews(next: EvidencePreview[]) {
    evidencePreviewsRef.current.forEach((preview) => URL.revokeObjectURL(preview.url));
    evidencePreviewsRef.current = next;
    setEvidencePreviews(next);
  }

  useEffect(() => () => {
    evidencePreviewsRef.current.forEach((preview) => URL.revokeObjectURL(preview.url));
    evidencePreviewsRef.current = [];
    previewAbortController.current?.abort();
  }, []);

  useEffect(() => {
    if (runState !== "RUNNING") return;
    const startedAt = Date.now();
    const updateElapsed = () => setCloudRunElapsedMs(Date.now() - startedAt);
    const timer = window.setInterval(updateElapsed, 1_000);
    return () => window.clearInterval(timer);
  }, [runState]);

  function invalidateActiveGeneration() {
    generationVersion.current += 1;
    previewAbortController.current?.abort();
    previewAbortController.current = null;
    setCloudRunElapsedMs(0);
  }

  useEffect(() => {
    if (!result || !evaluation || result.session_id !== evaluation.session_id) return;
    let cancelled = false;
    const timer = window.setTimeout(async () => {
      setSaveState("SAVING");
      setSaveError("");
      const saveOperation = reviewSaveQueue.current
        .catch(() => undefined)
        .then(async () => {
          await saveRunSidecar(endpoint, token, {
            session_id: result.session_id,
            human_review: evaluation,
          });
        });
      reviewSaveQueue.current = saveOperation.catch(() => undefined);
      try {
        await saveOperation;
        if (!cancelled) setSaveState("SAVED");
      } catch (caught) {
        if (!cancelled) {
          setSaveState("FAILED");
          setSaveError(caught instanceof Error ? caught.message : "评价暂时无法保存");
        }
      }
    }, 900);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [endpoint, evaluation, result, token]);

  useEffect(() => {
    if (!result || !evaluation || result.session_id !== evaluation.session_id) return;
    const flushLatestReview = () => {
      // A keepalive request gives the latest edit one final best-effort write when
      // the user closes or navigates away. Backend revision checks prevent an
      // older in-flight autosave from overwriting this newer revision.
      void saveRunSidecar(endpoint, token, {
        session_id: result.session_id,
        human_review: evaluation,
      }, { keepalive: true }).catch(() => undefined);
    };
    window.addEventListener("pagehide", flushLatestReview);
    return () => window.removeEventListener("pagehide", flushLatestReview);
  }, [endpoint, evaluation, result, token]);

  async function importMedia(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files || []);
    event.target.value = "";
    if (!files.length) return;
    invalidateActiveGeneration();
    const version = ++importVersion.current;
    assets.forEach((asset) => URL.revokeObjectURL(asset.url));
    replaceEvidencePreviews([]);
    setAssets([]);
    setResult(null);
    setManifest(null);
    setEvidenceBytes(0);
    setEvaluation(null);
    setSaveState("IDLE");
    setSaveError("");
    setError("");
    setHealth(null);
    setRunState("READING");
    setTab("测试日");
    const next = await inspectFiles(files);
    if (version !== importVersion.current) {
      next.forEach((asset) => URL.revokeObjectURL(asset.url));
      return;
    }
    setAssets(next);
    setRunState("READY");
  }

  function moveAsset(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= assets.length) return;
    invalidateActiveGeneration();
    setAssets((current) => {
      const next = [...current];
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
    setResult(null);
    setManifest(null);
    replaceEvidencePreviews([]);
    setEvaluation(null);
    setSaveState("IDLE");
    setRunState("READY");
  }

  function removeAsset(id: string) {
    invalidateActiveGeneration();
    const removed = assets.find((asset) => asset.id === id);
    if (removed) URL.revokeObjectURL(removed.url);
    setAssets((current) => current.filter((asset) => asset.id !== id));
    setResult(null);
    setManifest(null);
    replaceEvidencePreviews([]);
    setEvaluation(null);
    setSaveState("IDLE");
    setRunState(assets.length === 1 ? "EMPTY" : "READY");
  }

  function clearDay() {
    invalidateActiveGeneration();
    importVersion.current += 1;
    assets.forEach((asset) => URL.revokeObjectURL(asset.url));
    replaceEvidencePreviews([]);
    setAssets([]);
    setResult(null);
    setManifest(null);
    setEvidenceBytes(0);
    setEvaluation(null);
    setSaveState("IDLE");
    setSaveError("");
    setHealth(null);
    setError("");
    setRunState("EMPTY");
    setTab("测试日");
  }

  async function connectServer() {
    setError("");
    setHealth(null);
    try {
      const next = await checkResearchServer(endpoint, token);
      setHealth(next);
      if (!next.modelReady) setError("算法服务已连接，但模型凭证尚未就绪。");
      return next;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "算法服务连接失败");
      return null;
    }
  }

  async function generateMemory() {
    if (!readyAssets.length || unsupportedAssets.length) return;
    previewAbortController.current?.abort();
    const generation = ++generationVersion.current;
    setError("");
    setResult(null);
    setManifest(null);
    replaceEvidencePreviews([]);
    setEvaluation(null);
    setSaveState("IDLE");
    setSaveError("");
    try {
      const server = await connectServer();
      if (generation !== generationVersion.current) return;
      if (!server || !server.modelReady) return;
      if (readyAssets.length > server.maxAssets) {
        throw new Error(`本次有 ${readyAssets.length} 项，超过本地 X02 测试日的 ${server.maxAssets} 项安全边界。高强度日基准 186 项已经在边界内；本轮不会静默丢弃超出的素材。`);
      }
      setRunState("PREPARING");
      const bundle = await buildEvidenceBundle(readyAssets, (done, total, label) => {
        setProgress({ done, total, label });
      });
      if (generation !== generationVersion.current) return;
      const blobByFrameId = new Map(bundle.frames.map((frame) => [frame.frameId, frame.blob]));
      replaceEvidencePreviews(bundle.manifest.assets.flatMap((asset) => asset.frames.map((frame) => {
        const blob = blobByFrameId.get(frame.frame_id);
        if (!blob) throw new Error(`Evidence 预览缺失：${frame.frame_id}`);
        return {
          frameId: frame.frame_id,
          assetId: publicAssetId(asset.asset_id),
          canonicalOffsetMs: frame.canonical_offset_ms,
          windowIndex: frame.window_index,
          windowCount: frame.window_count,
          sourceTimestampMs: frame.source_timestamp_ms,
          url: URL.createObjectURL(blob),
        };
      })));
      setManifest(bundle.manifest);
      setEvidenceBytes(bundle.evidenceBytes);
      setRunState("RUNNING");
      setProgress({ done: 0, total: 0, label: "云端正在运行完整 S00–S12" });
      setCloudRunElapsedMs(0);
      const controller = new AbortController();
      previewAbortController.current = controller;
      const next = await runResearchPreview(endpoint, token, bundle, { signal: controller.signal });
      if (generation !== generationVersion.current) return;
      if (next.session_id !== bundle.manifest.session.session_id) {
        throw new Error("算法结果与当前测试日不匹配，已拒绝展示");
      }
      if (!next.decision_trace || !Array.isArray(next.trace.stage_metrics) || !next.trace.run_id) {
        throw new Error("算法服务版本过旧，缺少审计轨迹；请重启本机算法服务后重试");
      }
      if (
        next.observation_semantic_contract_version !== server.observationSemanticContractVersion
        || next.observation_semantic_contract_sha256 !== server.observationSemanticContractSHA256
        || next.field_degradation_contract_version !== server.fieldDegradationContractVersion
        || next.field_degradation_contract_sha256 !== server.fieldDegradationContractSHA256
        || next.storyline_contract_version !== server.storylineContractVersion
        || next.storyline_contract_sha256 !== server.storylineContractSHA256
        || next.writer_surface_policy_version !== server.writerSurfacePolicyVersion
        || next.chapter_media_policy_version !== server.chapterMediaPolicyVersion
        || !currentRuntimePolicies(next.decision_trace.runtime_policies)
        || !currentRuntimePolicies(server.runtimePolicies)
      ) {
        throw new Error("本轮结果使用的算法合同与连接时不一致，已拒绝展示；请重启服务后重试");
      }
      const nextEvaluation = newEvaluation(next);
      setResult(next);
      setEvaluation(nextEvaluation);
      setSaveState("IDLE");
      setRunState("COMPLETE");
      setTab("今日记忆");
    } catch (caught) {
      if (generation !== generationVersion.current) return;
      setRunState(caught instanceof ResearchPreviewCancelledError ? "READY" : "FAILED");
      setError(caught instanceof Error ? caught.message : "生成失败");
    } finally {
      if (generation === generationVersion.current) {
        previewAbortController.current = null;
      }
    }
  }

  function cancelCloudRun() {
    if (runState !== "RUNNING" || !previewAbortController.current) return;
    setProgress({ done: 0, total: 0, label: "正在取消本轮云端处理" });
    previewAbortController.current.abort();
  }

  function exportRecord() {
    if (!result || !manifest) return;
    const record = {
      contractVersion: "DIARY_ONE_WEB_REAL_MEDIA_TEST_RECORD_V02",
      createdAt: new Date().toISOString(),
      testProfile: {
        source: "PHONE_LIBRARY_DAY_TEST",
        eachImportIsOneDay: true,
        captureTimeIgnored: true,
        gpsIgnored: true,
        importOrderIsSequenceOnly: true,
        syntheticChronologyClaimed: false,
        logicalAssetDuration9000IsNormalizationOnly: true,
        wearableAccuracyClaimed: false,
        contractBasis: "CANONICAL_V1_25_S00_S13",
        executionMode: "X02_STAGED_REAL_MEDIA_PREVIEW_NOT_PRODUCTION",
        evaluationRunMode: "FRESH_FULL_RUN",
        crossRunSemanticCacheUsed: false,
        fullProductionPipelineClaimed: false,
      },
      input: {
        assets: assets.map((asset, index) => ({
          assetId: asset.id,
          sequence: index + 1,
          fileName: asset.name,
          kind: asset.kind,
          bytes: asset.size,
          width: asset.width,
          height: asset.height,
          durationMs: asset.durationMs,
        })),
        manifest,
        evidenceBytes,
      },
      result,
      latestContractFindings: findings,
      humanEvaluation: evaluation,
    };
    const blob = new Blob([JSON.stringify(record, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `diary-one-test-day-${result.session_id.slice(0, 8)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const picker = (label: string, secondary = false) => (
    <label className={`button ${secondary ? "secondary" : "primary"}`}>
      {label}
      <input
        type="file"
        accept="image/*,video/*,.heic,.heif,.mov,.m4v"
        multiple
        onChange={importMedia}
      />
    </label>
  );

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span>D1</span>
          <div><b>Diary One</b><small>Real-media Test Lab</small></div>
        </div>
        <nav>
          {tabs.map((item) => (
            <button key={item.id} className={tab === item.id ? "nav active" : "nav"} onClick={() => setTab(item.id)}>
              <span>{item.id}</span><small>{item.en}</small>
            </button>
          ))}
        </nav>
        <div className="local">
          <i className={health?.modelReady ? "online" : ""} />
          {health?.modelReady ? "算法网关已连接" : "本机研究模式"}
          <small>原始素材不上传 · 仅发送标准化 Evidence</small>
        </div>
      </aside>

      <section className="content">
        <header>
          <div>
            <p className="eyebrow">DIARY ONE · CODEX · 本页要求 Storyline V03 / Writer V02 · V1.63 完整画面与动物通用分类</p>
            <h1>{tab}</h1>
          </div>
          <span className={`status ${runState.toLowerCase()}`}><i />{stateLabel(runState)}</span>
        </header>

        {error && <div className="error-banner"><b>{runState === "FAILED" ? "暂时无法继续" : "提示"}</b><span>{error}</span><button onClick={() => setError("")}>×</button></div>}

        {tab === "测试日" && (
          <div className="test-day-layout">
            <section>
              <div className="headline">
                <div>
                  <p className="eyebrow">PHONE LIBRARY DAY TEST</p>
                  <h2>把这一批素材，当作完整的一天。</h2>
                  <p className="intro">这里先验证“理解、切分、精选和表达”。GPS 与真实拍摄时间不会参与判断。</p>
                </div>
                {assets.length ? picker("重新导入一个测试日", true) : picker("导入照片与视频")}
              </div>

              <div className="assumption-strip">
                <div><b>一天</b><span>一次导入 = 一个测试日</span></div>
                <div><b>顺序</b><span>仅按导入顺序，不代表真实时间</span></div>
                <div><b>忽略</b><span>GPS 与拍摄时间</span></div>
                <div><b>Evidence</b><span>照片 1 帧 · 视频按时长分 Window</span></div>
              </div>

              {!assets.length && runState !== "READING" && (
                <div className="empty-state">
                  <em>01</em>
                  <h3>先选择同一天的真实素材</h3>
                  <p>照片与视频可以混合，尺寸和时长不限。X02 会把完整测试日自动拆成小批 Observation，再做全天聚合。</p>
                  {picker("选择这一整天的素材")}
                  <small>推荐使用 Safari 导入 iPhone 的 HEIC / HEVC 原片；浏览器不支持的素材会明确标出。</small>
                </div>
              )}

              {runState === "READING" && <Processing title="正在读取素材" detail="只读取格式、尺寸和视频时长，不使用拍摄时间或 GPS。" />}

              {!!assets.length && (
                <>
                  <div className="day-summary">
                    <div><span>素材</span><b>{assets.length}</b><small>{photos} 张照片 · {videos} 个视频</small></div>
                    <div><span>原始体积</span><b>{bytes(assets.reduce((sum, asset) => sum + asset.size, 0))}</b><small>不会把原文件发给模型</small></div>
                    <div><span>时间信息</span><b>无真实时间</b><small>仅按下方导入顺序处理，不推算间隔或当天时长</small></div>
                    <button className="text-button danger" onClick={clearDay}>清空测试日</button>
                  </div>

                  <div className="order-note"><b>请先确认导入顺序</b><span>第 01 项到最后一项只代表本轮处理先后；可以用箭头调整，但不会被解释为真实拍摄时间或固定分钟间隔。</span></div>
                  <div className="media-list">
                    {assets.map((asset, index) => (
                      <article className={`asset-row ${asset.decodeStatus === "UNSUPPORTED" ? "unsupported" : ""}`} key={asset.id}>
                        <span className="sequence">{String(index + 1).padStart(2, "0")}</span>
                        <Media asset={asset} />
                        <div className="asset-copy">
                          <div><span className="chip">{asset.kind}</span><b>{asset.name}</b></div>
                          <p>{asset.decodeStatus === "READY"
                            ? `${asset.width} × ${asset.height} · ${duration(asset.durationMs)} · ${bytes(asset.size)}`
                            : asset.decodeMessage}</p>
                        </div>
                        <div className="asset-actions">
                          <button aria-label="向前移动" disabled={index === 0} onClick={() => moveAsset(index, -1)}>↑</button>
                          <button aria-label="向后移动" disabled={index === assets.length - 1} onClick={() => moveAsset(index, 1)}>↓</button>
                          <button aria-label="移除" onClick={() => removeAsset(asset.id)}>×</button>
                        </div>
                      </article>
                    ))}
                  </div>

                  {unsupportedAssets.length > 0 && (
                    <div className="inline-warning"><b>{unsupportedAssets.length} 项无法解码</b><span>请移除，或改用 Safari / 转成 JPEG、H.264 后再导入。算法不会静默跳过。</span></div>
                  )}
                  {assets.length > currentMaxAssets && (
                    <div className="inline-warning"><b>已超过本地测试日的 {currentMaxAssets} 项安全边界</b><span>系统不会静默丢素材。请缩小本轮样本；高强度日 186 项仍在当前边界内。</span></div>
                  )}

                  <div className="run-panel">
                    <div>
                      <p className="eyebrow">STEP 02 · GENERATE</p>
                      <h3>生成这一天的 Chapter 与 Aha</h3>
                      <p>会从原始素材重新生成 Evidence，并完整运行当前 S00–S12。丰富旅行日重点检查 2–3 条清楚的 Chapter Storyline；Aha 会同时搜索事件与生活发现。</p>
                    </div>
                    <button
                      className="button dark large"
                      disabled={!readyAssets.length || unsupportedAssets.length > 0 || ["PREPARING", "RUNNING", "READING"].includes(runState)}
                      onClick={generateMemory}
                    >
                      {runState === "PREPARING" || runState === "RUNNING" ? "正在生成…" : "开始生成记忆"}
                    </button>
                  </div>
                  {(runState === "PREPARING" || runState === "RUNNING") && (
                    <Processing
                      title={runState === "PREPARING" ? "正在生成标准化 Evidence" : "正在理解、切分和精选"}
                      detail={runState === "PREPARING"
                        ? progress.label
                        : `${progress.label} · 已等待 ${elapsed(cloudRunElapsedMs)}。当前接口不提供阶段心跳；完整分阶段耗时会在结果返回后显示。`}
                      progress={runState === "PREPARING" && progress.total ? progress.done / progress.total : undefined}
                      indeterminate={runState === "RUNNING"}
                      actionLabel={runState === "RUNNING" ? "取消本轮" : undefined}
                      onAction={runState === "RUNNING" ? cancelCloudRun : undefined}
                    />
                  )}
                </>
              )}
            </section>

            <aside className="context">
              <p className="eyebrow">这轮测试能说明什么</p>
              <h3>验证 Pipeline 的判断，不校准穿戴分布。</h3>
              <ul className="check-list">
                <li><b>可以看</b><span>语义理解、Chapter 边界、素材精选、Aha 独立性、文案与 Tag。</span></li>
                <li><b>暂时不能看</b><span>真实日均产量、两分钟自动采集覆盖率、最终成本和穿戴准确率。</span></li>
                <li><b>最大偏差</b><span>手机素材通常更主动、更精选；它不是持续的第一人称自动采集。</span></li>
                <li><b>容量</b><span>X02 每批最多 3 项，并同时限制帧数与 Evidence 体积；本地测试日默认允许 240 项，覆盖 186 项高强度日基准。</span></li>
              </ul>
              <button className="settings-toggle" onClick={() => setShowSettings((value) => !value)}>
                {showSettings ? "收起" : "打开"}算法服务设置
              </button>
              {showSettings && (
                <div className="settings">
                  <label>本机服务地址<input value={endpoint} onChange={(event) => { setEndpoint(event.target.value); setHealth(null); }} /></label>
                  <label>研究 Token（如已启用）<input type="password" value={token} onChange={(event) => { setToken(event.target.value); setHealth(null); }} /></label>
                  <button className="button secondary" onClick={connectServer}>检查连接</button>
                  {health && <small>网关已连接 · {health.provider} · {health.model} · 最多 {health.maxAssets} 项；凭证在首次生成时验证</small>}
                </div>
              )}
            </aside>
          </div>
        )}

        {tab === "今日记忆" && (
          <ResultPage
            assets={assetById}
            result={result}
            findings={findings}
            onBack={() => setTab("测试日")}
          />
        )}

        {tab === "结果评估" && (
          <EvaluationPage
            assets={assets}
            assetById={assetById}
            evidenceByFrameId={evidenceByFrameId}
            result={result}
            findings={findings}
            evaluation={evaluation}
            onChange={setEvaluation}
            saveState={saveState}
            saveError={saveError}
            onExport={exportRecord}
          />
        )}

        {tab === "决策轨迹" && (
          <DecisionTracePage
            assetById={assetById}
            evidenceByFrameId={evidenceByFrameId}
            result={result}
          />
        )}

        {tab === "运行信息" && (
          <RunInfoPage
            assets={assets}
            health={health}
            result={result}
            manifest={manifest}
            evidenceBytes={evidenceBytes}
            showRaw={showRaw}
            setShowRaw={setShowRaw}
          />
        )}
      </section>
    </main>
  );
}

function Processing({
  title,
  detail,
  progress,
  indeterminate = false,
  actionLabel,
  onAction,
}: {
  title: string;
  detail: string;
  progress?: number;
  indeterminate?: boolean;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="processing">
      <i />
      <div><b>{title}</b><p>{detail}</p>{(progress !== undefined || indeterminate) && <div className={`progress ${indeterminate ? "indeterminate" : ""}`}><span style={indeterminate ? undefined : { width: `${Math.round((progress || 0) * 100)}%` }} /></div>}</div>
      <div className="processing-actions"><span>PROCESSING</span>{actionLabel && onAction && <button type="button" onClick={onAction}>{actionLabel}</button>}</div>
    </div>
  );
}

function Media({ asset, className = "" }: { asset: TestAsset; className?: string }) {
  if (asset.decodeStatus === "UNSUPPORTED") return <div className={`media-fallback ${className}`}>无法预览</div>;
  if (asset.kind === "VIDEO") {
    // User-selected test media has no authored caption track at this research boundary.
    // eslint-disable-next-line jsx-a11y/media-has-caption
    return <video className={className} src={asset.url} controls playsInline preload="metadata" />;
  }
  // Blob URLs cannot use the framework image optimizer.
  // eslint-disable-next-line @next/next/no-img-element
  return <img className={className} src={asset.url} alt={asset.name} />;
}

function ResultPage({
  assets,
  result,
  findings,
  onBack,
}: {
  assets: Map<string, TestAsset>;
  result: X01Result | null;
  findings: ContractFinding[];
  onBack: () => void;
}) {
  if (!result) {
    return <Page eyebrow="MEMORY RESULT" title="还没有生成结果。"><Blank text="先导入一整天的素材并运行算法。" action="返回测试日" onAction={onBack} /></Page>;
  }
  const blocking = findings.filter((finding) => finding.severity === "BLOCK").length;
  const pipelineBlocked = result.delivery_state === "PIPELINE_BLOCKED";
  const itemBlocked = result.delivery_state === "READY_WITH_ITEM_BLOCKS";
  const fallbackUsed = result.delivery_state === "READY_WITH_GROUNDED_COPY_FALLBACK";
  const selectedAhas = result.selected_memory_outcomes.filter((item) => item.memory_type === "AHA");
  const hiddenAhas = selectedAhas.filter((item) => item.visibility_state === "DIAGNOSTIC_ONLY");
  const { visibleChapters, visibleAhas, diagnosticMemories } = projectV041Memories(result);
  const resultTitle = pipelineBlocked
    ? result.selected_memory_outcomes.length
      ? "素材中已有候选，但整轮交付尚未完整通过。"
      : "本轮处理在形成入选记忆前受阻，没有可交付结果。"
    : itemBlocked
      ? "这一天已有可见记忆，也有入选项未能完成交付。"
      : fallbackUsed
        ? "这一天已生成记忆，部分表达使用可靠事实兜底。"
        : result.semantic_day_state === "EMPTY_DAY"
          ? "这批素材没有形成合格记忆。"
          : "这一天，被整理成了这些记忆。";
  return (
    <Page
      eyebrow="TEST DAY · MEMORY RESULT"
      title={resultTitle}
    >
      <div className="result-summary">
        <div><span>Chapter</span><b>{visibleChapters.length}</b><small>{diagnosticMemories.some((item) => item.type === "CHAPTER") ? "另有未完成交付的诊断候选" : "日常目标 3–4，不强行凑数"}</small></div>
        <div><span>Aha</span><b>{visibleAhas.length}</b><small>{diagnosticMemories.some((item) => item.type === "AHA") ? "另有未完成交付的诊断候选" : "通常 1–2，丰富日可到 2–3，不强行凑数"}</small></div>
        <div><span>语义日状态</span><b>{semanticDayStateLabel(result.semantic_day_state)}</b><small>只说明素材中形成了什么，不代表文案是否成功交付</small></div>
        <div><span>交付状态</span><b>{deliveryStateLabel(result.delivery_state)}</b><small>{pipelineBlocked && !result.selected_memory_outcomes.length ? "整轮在 S09 入选前受阻；这里不存在候选已找到的暗示" : pipelineBlocked || itemBlocked ? "被阻断的入选项仍保留在诊断账本" : blocking ? `${blocking} 项表面合同阻断，仅供检查` : "可进入人工评价"}</small></div>
        <div><span>时间依据</span><b>{result.timeline_basis === "SYNTHETIC_SEQUENCE_ONLY" ? "仅按导入顺序" : "可靠拍摄时间"}</b><small>{result.timeline_date ? result.timeline_date : "没有真实日期、时间间隔或当天时长"}</small></div>
      </div>

      <section className="delivery-outcomes">
        <div className="section-title"><div><p className="eyebrow">SELECTED MEMORY OUTCOMES</p><h3>每个入选记忆最终去了哪里</h3></div><span>{result.selected_memory_outcomes.length} 个 S09 入选项</span></div>
        {result.selected_memory_outcomes.length ? <div className="outcome-grid">{result.selected_memory_outcomes.map((item) => (
          <article key={`${item.memory_type}-${item.memory_id}`}>
            <div><b>{item.memory_type}</b><span>{item.memory_id}</span></div>
            <small>{selectedOutcomeLabel(item.selection_state)}</small>
            <small>{selectedOutcomeLabel(item.media_state)}</small>
            <small>{selectedOutcomeLabel(item.surface_state)}</small>
            <strong className={item.visibility_state === "VISIBLE_PREVIEW" ? "visible" : "diagnostic"}>{selectedOutcomeLabel(item.visibility_state)}</strong>
          </article>
        ))}</div> : <Blank text="S09 没有选中可交付的 Chapter 或 Aha；这与 Writer 阻断不同。" />}
      </section>

      {diagnosticMemories.length > 0 && <section className="diagnostic-memories">
        <div className="section-title"><div><p className="eyebrow">DIAGNOSTIC CANDIDATES</p><h3>算法找到了，但不能当作正式结果</h3></div><span>{diagnosticMemories.length} 个</span></div>
        <p>这些候选来自识别不完整或交付受阻的运行，只用于定位问题；不会计入上方 Chapter / Aha 数量，也不会混入正式卡片。</p>
        <div className="diagnostic-memory-list">{diagnosticMemories.map(({ memory, type }) => (
          <article key={`${type}-${memory.id}`}><b>{type}</b><strong>{type === "CHAPTER" ? memory.title : memory.story}</strong><span>诊断候选 · 不可发布</span></article>
        ))}</div>
      </section>}

      <section className="memory-section">
        <div className="section-title"><div><p className="eyebrow">CHAPTERS</p><h3>完整、值得保留的经历</h3></div><span>每个标准 Chapter 3–5 个精选素材</span></div>
        {visibleChapters.length
          ? <div className="chapter-grid">{visibleChapters.map((chapter, index) => <Chapter key={chapter.id} index={index} memory={chapter} result={result} assets={assets} />)}</div>
          : <Blank text={pipelineBlocked && !result.selected_memory_outcomes.length ? "整轮在形成 S09 入选项前受阻；不能据此判断素材本身没有 Chapter。" : pipelineBlocked || itemBlocked ? "若 Chapter 已被 S09 选中但交付受阻，可在上方逐项结果中看到；它不会被误记成语义上没有 Chapter。" : "这批 Evidence 没有形成足够完整的 Chapter；这可以是合法结果。"} />}
      </section>

      <section className="memory-section aha-section">
        <div className="section-title"><div><p className="eyebrow">AHA MOMENTS</p><h3>独立、短促的精彩瞬间</h3></div><span>每个 Aha 只展示 1 个核心素材</span></div>
        {visibleAhas.length
          ? <div className="aha-grid">{visibleAhas.map((aha, index) => <Aha key={aha.id} index={index} memory={aha} result={result} assets={assets} />)}</div>
          : <Blank text={hiddenAhas.length
            ? `S09 已选中 ${hiddenAhas.length} 个 Aha，但它们没有完成媒体或文案交付；这是交付阻断，不是算法没有找到 Aha。`
            : pipelineBlocked
              ? "Aha 流程随整轮交付受阻；不能据此判断这一天没有 Aha。"
              : "没有足够独立的 Aha；不会把普通素材硬包装成高光。"} />}
      </section>

      <div className="research-boundary"><b>结果解释边界</b><p>这次使用 X02 分阶段真实素材链路：Observation、结构、候选、集合选择、媒体精选、Writer 与最终校验彼此分开。它仍是 Web Preview，不执行 S13 HQ 导出，也不代表 Production 已完成。</p></div>
    </Page>
  );
}

function Chapter({
  memory,
  result,
  assets,
  index,
}: {
  memory: X01Editorial;
  result: X01Result;
  assets: Map<string, TestAsset>;
  index: number;
}) {
  const ids = uniqueAssetIds(memory, result);
  const hero = assets.get(memory.hero_asset_id);
  const mediaSelection = result.decision_trace.s10_chapter_media.find((item) => item.candidate_id === memory.candidate_id);
  const display = mediaSelection?.display_selection;
  return (
    <article className="chapter-card">
      <div className="chapter-hero">{hero ? <Media asset={hero} /> : <div className="media-fallback">素材引用缺失</div>}<span>CHAPTER {String(index + 1).padStart(2, "0")}</span></div>
      <div className="chapter-body">
        <div className="memory-meta"><span>{timelineDisplayLabel(result, memory.time_label)}</span><b>{memory.evidence_support || "GROUNDED"} evidence support</b></div>
        <h3>{memory.title}</h3>
        <p>{memory.story}</p>
        <div className={`memory-surface ${memory.surface_source === "DETERMINISTIC_GROUNDED_FALLBACK" ? "fallback" : "model"}`}>
          <b>{surfaceSourceLabel(memory.surface_source)}</b>
          <span>{memory.surface_policy_version}</span>
        </div>
        {memory.storyline_identity && <div className="storyline-summary">
          <b>本章聚类依据</b>
          <strong>模型提出的分组</strong>
          <span>{memory.storyline_identity.thesis || "模型未提供内部主题说明；可在决策轨迹查看成员与事实。"}</span>
          <small>{storylineBasisLabels[memory.storyline_identity.storyline_basis] || memory.storyline_identity.storyline_basis} · {storylineFormLabels[memory.storyline_identity.storyline_form] || memory.storyline_identity.storyline_form} · {memory.storyline_identity.beat_map.length} 项内容证据</small>
          <small>仅结构与引用检查通过，内容关系仍需评价。</small>
        </div>}
        <div className="tags">{memory.tags.map((tag) => <span key={tag}>{formatTag(tag)}</span>)}</div>
        <div className="selected-media">
          {ids.map((id, assetIndex) => {
            const asset = assets.get(id);
            return asset ? <div key={id}><Media asset={asset} /><span>{String(assetIndex + 1).padStart(2, "0")}</span></div> : null;
          })}
        </div>
        {display && <details><summary>为什么展示这 {ids.length} 个素材</summary>
          <p>{display.selection_source === "MODEL_VISUAL_SELECTION"
            ? display.model_reason || "模型比较画面后选择；仍需你评价重复度。"
            : display.selection_source === "THREE_MEMBER_FLOOR_NO_COMPARISON_NEEDED"
              ? "本章恰好三个可用素材，全部保留。"
              : "本次视觉比较未取得可用选择，按画质保留三项；尚未确认去重效果。"}</p>
          <small>本章共有 {mediaSelection?.candidate_content_unit_count} 个候选；未展示的素材仍属于本章，原素材未删除。</small>
        </details>}
        <details><summary>查看事实依据</summary><ul>{memory.claims.map((claim, claimIndex) => <li key={claim.fact_id || claimIndex}><b>{claim.support_grade || claim.claim_type || "GROUNDED"}</b>{claim.text}</li>)}</ul></details>
      </div>
    </article>
  );
}

function AhaLengthNote({ memory, result }: { memory: X01Editorial; result: X01Result }) {
  const review = ahaLengthReview(memory, result);
  if (!review) return null;
  return <div className="aha-length-note"><b>{review.label}</b><span>{review.characters != null ? `${review.characters} 字 · ` : ""}原文保留，请在正文评价中判断是否需要精简。</span></div>;
}

function Aha({ memory, result, assets, index }: { memory: X01Editorial; result: X01Result; assets: Map<string, TestAsset>; index: number }) {
  const hero = assets.get(memory.hero_asset_id);
  return (
    <article className="aha-card">
      <div className="aha-media">{hero ? <Media asset={hero} /> : <div className="media-fallback">素材引用缺失</div>}<span>AHA {String(index + 1).padStart(2, "0")}</span></div>
      <div><p className="eyebrow">{timelineDisplayLabel(result, memory.time_label)}</p><h3>{memory.story}</h3><AhaLengthNote memory={memory} result={result} /><div className="tags">{memory.tags.map((tag) => <span key={tag}>{formatTag(tag)}</span>)}</div><div className={`memory-surface ${memory.surface_source === "DETERMINISTIC_GROUNDED_FALLBACK" ? "fallback" : "model"}`}><b>{surfaceSourceLabel(memory.surface_source)}</b><span>{memory.surface_policy_version}</span></div><small>{memory.evidence_support || "GROUNDED"} evidence support</small></div>
    </article>
  );
}

function EvaluationPage({
  assets,
  assetById,
  evidenceByFrameId,
  result,
  findings,
  evaluation,
  onChange,
  saveState,
  saveError,
  onExport,
}: {
  assets: TestAsset[];
  assetById: Map<string, TestAsset>;
  evidenceByFrameId: Map<string, EvidencePreview>;
  result: X01Result | null;
  findings: ContractFinding[];
  evaluation: HumanEvaluationV02 | null;
  onChange: (value: HumanEvaluationV02) => void;
  saveState: SaveState;
  saveError: string;
  onExport: () => void;
}) {
  if (!result || !evaluation) return <Page eyebrow="EVALUATION" title="先生成一次结果，再评价。"><Blank text="评估只绑定到同一批固定 Evidence，避免素材变化后误比较。" /></Page>;
  const updateGlobal = (patch: Partial<HumanEvaluationV02["global"]>) => onChange({
    ...evaluation,
    revision: evaluation.revision + 1,
    status: "DRAFT",
    updated_at: new Date().toISOString(),
    global: { ...evaluation.global, ...patch },
  });
  const toggleGlobalIssue = (code: HumanEvaluationIssueCodeV02) => updateGlobal({
    issue_codes: evaluation.global.issue_codes.includes(code)
      ? evaluation.global.issue_codes.filter((item) => item !== code)
      : [...evaluation.global.issue_codes, code],
  });
  const { visibleChapters, visibleAhas, diagnosticMemories } = projectV041Memories(result);
  const selectedIds = new Set<string>();
  [...visibleChapters, ...visibleAhas].forEach((item) => {
    selectedIds.add(item.hero_asset_id);
    uniqueAssetIds(item, result).forEach((id) => selectedIds.add(id));
  });
  const saveLabel = ({
    IDLE: "等待首次保存",
    SAVING: "正在自动保存…",
    SAVED: "已自动保存到本轮审计账本",
    FAILED: "自动保存失败，页面内容仍保留",
  } as const)[saveState];
  return (
    <Page eyebrow="EVALUATION · HUMAN-IN-THE-LOOP" title="把问题记录到具体结果、素材和表达。">
      <div className="collection-note"><b>只收集，暂不自动学习</b><span>这些评价会精确绑定本次 Run 并自动保存，离开页面前还会尝试最后一次保存；积累到一定数量后，再一起讨论哪些应转成算法修改。</span><small className={saveState === "FAILED" ? "save-failed" : ""}>{saveLabel}{saveError ? ` · ${saveError}` : ""}</small></div>

      <section className="evaluation-card overall-review">
        <div><p className="eyebrow">OVERALL</p><h3>整天结果</h3><p className="helper">先判断整体是否像你想留下的这一天；下面再逐项指出具体问题。</p></div>
        <div>
          <VerdictButtons value={evaluation.global.verdict} onChange={(verdict) => updateGlobal({ verdict })} />
          <div className="rating">{[1, 2, 3, 4, 5].map((value) => <button aria-label={`${value} 星`} key={value} className={value <= evaluation.global.rating ? "filled" : ""} onClick={() => updateGlobal({ rating: value as 1 | 2 | 3 | 4 | 5 })}>★</button>)}</div>
          <p className="helper">1 = 完全不可用，5 = 已接近真实想留下的 Diary</p>
          <div className="issue-grid">{globalIssueOptions.map(([code, label]) => <button className={evaluation.global.issue_codes.includes(code) ? "selected" : ""} key={code} onClick={() => toggleGlobalIssue(code)}>{label}</button>)}</div>
          <label className="notes">整体说明<textarea value={evaluation.global.notes} onChange={(event) => updateGlobal({ notes: event.target.value })} placeholder="例如：这一天的主题基本正确，但下午的一段经历被漏掉……" /></label>
        </div>
      </section>

      <section className="evaluation-card contract-review">
        <p className="eyebrow">LATEST CONTRACT CHECK</p>
        <h3>自动合同检查</h3>
        <div className="findings">{findings.map((item, index) => <div className={`finding ${item.severity.toLowerCase()}`} key={`${item.code}-${index}`}><b>{item.severity}</b><span><strong>{item.code}</strong>{item.message}</span></div>)}</div>
      </section>

      <ReviewGroup title="逐个评价 Chapter" subtitle="边界、精选素材、标题、正文与 Tag 分开记录。">
        {visibleChapters.length ? visibleChapters.map((chapter, index) => (
          <EditorialReviewCard
            key={chapter.id}
            kind="CHAPTER"
            index={index}
            memory={chapter}
            result={result}
            assetById={assetById}
            evidenceByFrameId={evidenceByFrameId}
            evaluation={evaluation}
            onChange={onChange}
          />
        )) : <Blank text="本轮没有 Chapter；可在整体问题中记录数量或遗漏。" />}
      </ReviewGroup>

      <ReviewGroup title="逐个评价 Aha" subtitle="重点判断它是否是独立小故事，以及核心素材与表达是否正确。">
        {visibleAhas.length ? visibleAhas.map((aha, index) => (
          <EditorialReviewCard
            key={aha.id}
            kind="AHA"
            index={index}
            memory={aha}
            result={result}
            assetById={assetById}
            evidenceByFrameId={evidenceByFrameId}
            evaluation={evaluation}
            onChange={onChange}
          />
        )) : <Blank text="本轮没有 Aha；如认为有遗漏，可在具体素材下标记“重要但没有使用”。" />}
      </ReviewGroup>

      {diagnosticMemories.length > 0 && <section className="diagnostic-memories">
        <div className="section-title"><div><p className="eyebrow">DIAGNOSTIC · NOT SCORED</p><h3>诊断候选不进入正式逐项评分</h3></div><span>{diagnosticMemories.length} 个</span></div>
        <p>它们只用于定位媒体或文案交付问题；不会被当作已发布 Chapter/Aha，也不会让关联素材显示为“已选中”。</p>
        <div className="diagnostic-memory-list">{diagnosticMemories.map(({ memory, type }) => (
          <article key={`evaluation-diagnostic-${type}-${memory.id}`}><b>{type}</b><strong>{type === "CHAPTER" ? memory.title : memory.story}</strong><span>诊断候选 · 不计分</span></article>
        ))}</div>
      </section>}

      <ReviewGroup title="逐张检查全部素材" subtitle="这里也保留未入选素材，便于区分“正确没选”与“算法漏选或误解”。">
        <div className="asset-review-list">{assets.map((asset, index) => {
          const observation = result.observations.find((item) => item.asset_id === asset.id);
          return <AssetReviewCard
            key={asset.id}
            asset={asset}
            index={index}
            observation={observation}
            selected={selectedIds.has(asset.id)}
            evidenceByFrameId={evidenceByFrameId}
            evaluation={evaluation}
            onChange={onChange}
          />;
        })}</div>
      </ReviewGroup>

      <div className="evaluation-actions">
        <button className="button secondary" onClick={onExport}>导出本轮结果与评价</button>
        <button className="button dark" onClick={() => onChange({ ...evaluation, revision: evaluation.revision + 1, status: "SUBMITTED", updated_at: new Date().toISOString() })}>标记本轮评价完成</button>
        <span>{evaluation.reviews.length} 条具体评价 · {evaluation.status === "SUBMITTED" ? "已完成" : "草稿"}</span>
      </div>
    </Page>
  );
}

function ReviewGroup({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return <section className="review-group"><div className="section-title"><div><h3>{title}</h3><p>{subtitle}</p></div></div><div className="review-stack">{children}</div></section>;
}

function VerdictButtons({ value, onChange }: { value: HumanReviewVerdict; onChange: (value: HumanReviewVerdict) => void }) {
  return <div className="verdict-buttons">{verdictOptions.map(([code, label]) => <button key={code} className={value === code ? "selected" : ""} onClick={() => onChange(code)}>{label}</button>)}</div>;
}

function ReviewMedia({ asset }: { asset: TestAsset }) {
  if (asset.decodeStatus === "UNSUPPORTED") return <div className="media-fallback">无法预览</div>;
  if (asset.kind === "VIDEO") {
    // Muted inline preview is intentionally non-interactive inside the review selector.
    return <video src={asset.url} muted playsInline preload="metadata" />;
  }
  // Blob URLs cannot use the framework image optimizer.
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={asset.url} alt={asset.name} />;
}

function EvidenceImage({ preview, alt }: { preview: EvidencePreview | undefined; alt: string }) {
  if (!preview) return <div className="media-fallback">Evidence 缺失</div>;
  // Generated Evidence uses an in-memory Blob URL and cannot use the image optimizer.
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={preview.url} alt={alt} />;
}

function EditorialReviewCard({
  kind,
  index,
  memory,
  result,
  assetById,
  evidenceByFrameId,
  evaluation,
  onChange,
}: {
  kind: "CHAPTER" | "AHA";
  index: number;
  memory: X01Editorial;
  result: X01Result;
  assetById: Map<string, TestAsset>;
  evidenceByFrameId: Map<string, EvidencePreview>;
  evaluation: HumanEvaluationV02;
  onChange: (value: HumanEvaluationV02) => void;
}) {
  const assetIds = kind === "CHAPTER" ? uniqueAssetIds(memory, result) : [memory.hero_asset_id];
  const assetOptions = assetIds.map((id) => assetById.get(id)).filter((asset): asset is TestAsset => Boolean(asset));
  const aspects: Array<{ id: HumanReviewAspect; label: string; current: string }> = kind === "CHAPTER"
    ? [
      { id: "BOUNDARY", label: "Chapter 边界", current: `当前包含 ${assetIds.length} 项素材` },
      { id: "MEDIA_SELECTION", label: "精选素材", current: `封面：${assetById.get(memory.hero_asset_id)?.name || memory.hero_asset_id}` },
      { id: "TITLE", label: "标题", current: memory.title },
      { id: "STORY", label: "正文表达", current: memory.story },
      { id: "TAGS", label: "Canonical Tags", current: memory.tags.join(" · ") || "无" },
    ]
    : [
      { id: "AHA_INDEPENDENCE", label: "Aha 独立性", current: "它是否与 Chapter 有不同的故事核心？" },
      { id: "MEDIA_SELECTION", label: "核心素材", current: assetById.get(memory.hero_asset_id)?.name || memory.hero_asset_id },
      { id: "STORY", label: "Aha 表达", current: memory.story },
      { id: "TAGS", label: "Canonical Tags", current: memory.tags.join(" · ") || "无" },
    ];
  return (
    <details className="editorial-review" open={index === 0}>
      <summary>
        <span>{kind} {String(index + 1).padStart(2, "0")}</span>
        <div><b>{memory.title || memory.story}</b><small>{memory.id}</small></div>
        <i>{evaluation.reviews.filter((item) => item.target_type === kind && item.target_id === memory.id).length} 条评价</i>
      </summary>
      <div className="review-current">
        <div className="review-media-strip">{assetOptions.map((asset) => <div key={asset.id}><ReviewMedia asset={asset} /><span>{asset.name}</span></div>)}</div>
        <div><b>当前表达</b><p>{memory.story}</p>{kind === "AHA" && <AhaLengthNote memory={memory} result={result} />}<small>{memory.tags.map(formatTag).join(" · ") || "没有 Tag"}</small></div>
      </div>
      <div className="aspect-list">{aspects.map((aspect) => <ReviewEditor
        key={aspect.id}
        targetType={kind}
        targetId={memory.id}
        parentEditorialId={memory.id}
        aspect={aspect.id}
        label={aspect.label}
        currentValue={aspect.current}
        defaultAssetIds={assetIds}
        defaultFrameIds={memory.evidence_frame_ids}
        assetOptions={assetOptions}
        evidenceByFrameId={evidenceByFrameId}
        evaluation={evaluation}
        onChange={onChange}
      />)}</div>
    </details>
  );
}

function AssetReviewCard({
  asset,
  index,
  observation,
  selected,
  evidenceByFrameId,
  evaluation,
  onChange,
}: {
  asset: TestAsset;
  index: number;
  observation: X01Result["observations"][number] | undefined;
  selected: boolean;
  evidenceByFrameId: Map<string, EvidencePreview>;
  evaluation: HumanEvaluationV02;
  onChange: (value: HumanEvaluationV02) => void;
}) {
  return (
    <details className="asset-review">
      <summary><span>{String(index + 1).padStart(2, "0")}</span><div className="asset-review-thumb"><ReviewMedia asset={asset} /></div><div><b>{asset.name}</b><small>{selected ? "已进入最终记忆" : "未进入最终记忆"} · {observation ? `${observation.status} · 画面可用度 ${Math.round(observation.quality_score * 100)}%` : "没有 Observation"}</small></div></summary>
      <div className="asset-observation"><b>算法观察</b><p>{observation?.facts.map((fact) => fact.text).join("；") || "没有保留下可审计的观察事实"}</p>{observation?.limitations.length ? <small>限制：{observation.limitations.join("；")}</small> : null}</div>
      <ReviewEditor
        targetType="ASSET"
        targetId={asset.id}
        parentEditorialId={null}
        aspect="ASSET_UNDERSTANDING"
        label="这张素材的理解与使用"
        currentValue={selected ? "算法选择了这张素材" : "算法没有选择这张素材"}
        defaultAssetIds={[asset.id]}
        defaultFrameIds={observation?.evidence_frame_ids || []}
        assetOptions={[asset]}
        evidenceByFrameId={evidenceByFrameId}
        evaluation={evaluation}
        onChange={onChange}
      />
    </details>
  );
}

function ReviewEditor({
  targetType,
  targetId,
  parentEditorialId,
  aspect,
  label,
  currentValue,
  defaultAssetIds,
  defaultFrameIds,
  assetOptions,
  evidenceByFrameId,
  evaluation,
  onChange,
}: {
  targetType: HumanReviewTargetType;
  targetId: string;
  parentEditorialId: string | null;
  aspect: HumanReviewAspect;
  label: string;
  currentValue: string;
  defaultAssetIds: string[];
  defaultFrameIds: string[];
  assetOptions: TestAsset[];
  evidenceByFrameId: Map<string, EvidencePreview>;
  evaluation: HumanEvaluationV02;
  onChange: (value: HumanEvaluationV02) => void;
}) {
  const review = evaluation.reviews.find((item) => reviewKey(item.target_type, item.target_id, item.aspect) === reviewKey(targetType, targetId, aspect));
  const selectedAssetIds = review?.asset_ids || [];
  const apply = (patch: Partial<HumanReviewItemV02>) => onChange(updateReview(
    evaluation,
    targetType,
    targetId,
    parentEditorialId,
    aspect,
    {
      asset_ids: review ? review.asset_ids : defaultAssetIds,
      frame_ids: review ? review.frame_ids : defaultFrameIds,
      ...patch,
    },
  ));
  const toggleIssue = (code: HumanEvaluationIssueCodeV02) => apply({
    issue_codes: review?.issue_codes.includes(code)
      ? review.issue_codes.filter((item) => item !== code)
      : [...(review?.issue_codes || []), code],
  });
  const toggleAsset = (id: string) => apply({
    asset_ids: selectedAssetIds.includes(id)
      ? selectedAssetIds.filter((item) => item !== id)
      : [...selectedAssetIds, id],
  });
  const suggestion = review?.suggestion || { text: "", tags: [], action: null };
  return (
    <details className="aspect-review">
      <summary><div><b>{label}</b><span>{currentValue}</span></div><i className={(review?.verdict || "UNREVIEWED").toLowerCase()}>{review?.verdict || "待评价"}</i></summary>
      <div className="aspect-editor">
        <VerdictButtons value={review?.verdict || "UNREVIEWED"} onChange={(verdict) => apply({ verdict })} />
        <div className="issue-grid compact">{aspectIssueOptions[aspect].map(([code, issueLabel]) => <button className={review?.issue_codes.includes(code) ? "selected" : ""} key={code} onClick={() => toggleIssue(code)}>{issueLabel}</button>)}</div>
        {assetOptions.length > 0 && <div className="review-asset-picker"><b>意见涉及哪些素材</b><div>{assetOptions.map((asset) => <button className={selectedAssetIds.includes(asset.id) ? "selected" : ""} key={asset.id} onClick={() => toggleAsset(asset.id)}><ReviewMedia asset={asset} /><span>{asset.name}</span></button>)}</div></div>}
        {defaultFrameIds.length > 0 && <div className="frame-picker"><b>涉及的 Evidence 帧（下图就是模型接收的 3:4 标准化画面）</b><div>{defaultFrameIds.map((frameId) => {
          const preview = evidenceByFrameId.get(frameId);
          return <button className={review?.frame_ids.includes(frameId) ? "selected" : ""} key={frameId} onClick={() => apply({ frame_ids: review?.frame_ids.includes(frameId) ? review.frame_ids.filter((id) => id !== frameId) : [...(review?.frame_ids || []), frameId] })}><EvidenceImage preview={preview} alt={`Evidence ${frameId}`} /><span>{preview ? `Window ${preview.windowIndex + 1}/${preview.windowCount} · ${preview.sourceTimestampMs ?? "照片"} ms` : frameId}</span></button>;
        })}</div></div>}
        <div className="suggestion-grid">
          <label>建议动作<select value={suggestion.action || ""} onChange={(event) => apply({ suggestion: { ...suggestion, action: (event.target.value || null) as HumanReviewAction | null } })}><option value="">只记录，不指定动作</option><option value="ADD">补入</option><option value="REMOVE">移除</option><option value="REPLACE">替换</option><option value="MOVE">移动</option><option value="SPLIT">拆分</option><option value="MERGE">合并</option><option value="SUPPRESS">抑制</option><option value="PROMOTE_TO_AHA">提升为 Aha</option></select></label>
          <label>具体建议<textarea value={suggestion.text} onChange={(event) => apply({ suggestion: { ...suggestion, text: event.target.value } })} placeholder="直接写希望怎样修改；例如：把第二张移出，并补入更晚出现的另一座建筑。" /></label>
          {aspect === "TAGS" && <label>建议 Tag（逗号分隔）<input value={suggestion.tags.join(", ")} onChange={(event) => apply({ suggestion: { ...suggestion, tags: event.target.value.split(",").map((item) => item.trim()).filter(Boolean) } })} /></label>}
          <label>补充依据<textarea value={review?.notes || ""} onChange={(event) => apply({ notes: event.target.value })} placeholder="为什么这样判断？可留空。" /></label>
        </div>
      </div>
    </details>
  );
}

function DecisionTracePage({
  assetById,
  evidenceByFrameId,
  result,
}: {
  assetById: Map<string, TestAsset>;
  evidenceByFrameId: Map<string, EvidencePreview>;
  result: X01Result | null;
}) {
  if (!result) return <Page eyebrow="DECISION TRACE" title="先生成一次结果，再查看判断轨迹。"><Blank text="轨迹会把 Evidence、观察、候选、Gate 与最终结果串在一起。" /></Page>;
  const trace = result.decision_trace;
  const { visibleChapters, visibleAhas, diagnosticMemories } = projectV041Memories(result);
  return (
    <Page eyebrow="AUDITABLE DECISION TRACE" title="这次算法为什么得到这些结果。">
      <div className="trace-definition"><b>这里展示的是可审计判断依据，不是模型隐藏思维</b><p>{trace.scope_note}</p><span>你可以看到它看了什么、形成了什么观察、哪些候选通过或失败，以及最终为什么入选。</span></div>

      <div className="decision-flow">
        <DecisionStep number="00" title="分阶段执行状态" summary={`${trace.stage_statuses.length} 个阶段状态；S13 会明确标为未执行`}>
          <div className="reason-codes">{trace.stage_statuses.map((item) => <span key={item.stage}>{item.stage} · {item.status}</span>)}</div>
        </DecisionStep>

        <DecisionStep number="01" title="Evidence 按素材公平进入 S04" summary={`${trace.evidence_selection.selected.length} 帧实际呈现；照片 1 帧，视频按实际时长分 1 / 2 / 4 / 6 个 Window`}>
          <div className="evidence-trace-grid">{trace.evidence_selection.selected.map((item) => {
            const asset = assetById.get(item.asset_id) || assetById.get(publicAssetId(item.source_asset_id));
            return <article key={`${item.selection_order}-${item.frame_id}`}><EvidenceImage preview={evidenceByFrameId.get(item.frame_id)} alt={`模型 Evidence · ${asset?.name || item.source_asset_id}`} /><div><b>{asset?.name || item.source_asset_id}</b><small>{item.frame_id} · {item.reason_code}</small><span>{item.media_kind} · Window {item.window_index + 1}/{item.window_count} · 原视频 {item.source_timestamp_ms ?? "照片"} ms</span></div></article>;
          })}</div>
        </DecisionStep>

        <DecisionStep number="02" title="逐素材 Observation" summary={`${trace.counts.accepted_observation_count ?? 0} 条有可用观察 · ${trace.counts.field_degraded_observation_count ?? 0} 条字段级降级 · 每项都有一个终态`}>
          <ObservationLedger candidates={trace.observation_candidates || []} assetById={assetById} />
          <div className="observation-list">{result.observations.map((observation) => {
            const asset = assetById.get(observation.asset_id);
            const role = trace.observation_roles.find((item) => item.observation_id === observation.id);
            return <article key={observation.id}><EvidenceImage preview={evidenceByFrameId.get(observation.evidence_frame_ids[0])} alt={`Observation Evidence · ${asset?.name || observation.asset_id}`} /><div><b>{asset?.name || observation.asset_id}</b><p>{observation.facts.map((fact) => fact.text).join("；") || "没有通过的事实"}</p><small>{observation.status} · {role?.role || "未分配角色"} · {observation.episode_code} · {observation.evidence_frame_ids.length} 帧依据{observation.degraded_fields.length ? ` · ${observation.degraded_fields.length} 个字段已保守降级` : ""}</small></div></article>;
          })}</div>
        </DecisionStep>

        <DecisionStep number="03" title="双向边界证据与连续 Moment" summary={`${trace.boundary_edges.length} 条相邻边 · ${result.moments.length} 个连续 Moment`}>
          <div className="candidate-ledger"><h4>Boundary Ledger<small>JOIN / SPLIT / DEFER</small></h4>{trace.boundary_edges.map((edge) => <article key={edge.edge_id}><div className="candidate-status"><b className={edge.decision === "JOIN" ? "passed" : edge.decision === "SPLIT" ? "rejected" : "pending"}>{edge.decision}</b><span>{edge.reason_code}</span></div><div><h5>{edge.left_observation_id.slice(0, 8)} → {edge.right_observation_id.slice(0, 8)}</h5><p>连续证据：{edge.continuity_evidence.join(" · ") || "无"}</p><small>边界证据：{edge.boundary_evidence.join(" · ") || "无"}</small></div></article>)}</div>
          <div className="moment-trace">{result.moments.map((moment, index) => <article key={moment.id}><span>{String(index + 1).padStart(2, "0")}</span><div><b>{timelineDisplayLabel(result, moment.time_label)} · {moment.episode_codes.join(" / ")}</b><p>{moment.asset_ids.map((id) => assetById.get(id)?.name || id).join(" · ")}</p></div><small>{moment.roles.join(" / ")}</small></article>)}</div>
        </DecisionStep>

        <DecisionStep number="04" title="S07 Storyline 候选与 S09 集合选择" summary="先判断每个 Chapter 到底在讲哪一条经历；混入另一条故事职责的素材会先被拒绝，再计算全天组合">
          <CandidateLedger title="Chapter 候选" candidates={trace.chapter_candidates} assetById={assetById} />
          <CandidateLedger title="Aha 候选" candidates={trace.aha_candidates} assetById={assetById} />
          <details><summary>查看集合选择记录</summary><pre className="raw-json">{JSON.stringify({ chapter: trace.chapter_set_selection, aha: trace.aha_set_selection }, null, 2)}</pre></details>
          <p className="metric-scope">Aha 搜索结论：{String(trace.aha_set_selection.search_outcome || "未记录")}；事件候选 {Number(trace.aha_set_selection.event_candidate_count || 0)} 个，发现候选 {Number(trace.aha_set_selection.discovery_candidate_count || 0)} 个。</p>
        </DecisionStep>

        <DecisionStep number="05" title="S10 媒体精选" summary={`${trace.s10_chapter_media.length} 个 Chapter 媒体计划 · ${trace.s10_aha_media.length} 个 Aha 媒体计划`}>
          <details><summary>查看 candidate 到最终 3–5 项媒体的映射</summary><pre className="raw-json">{JSON.stringify({ chapters: trace.s10_chapter_media, ahas: trace.s10_aha_media }, null, 2)}</pre></details>
        </DecisionStep>

        <DecisionStep number="06" title="S11 Writer 与 S12 校验" summary={`${trace.writer_items.filter((item) => item.validation_status === "PASSED").length} 条检查通过 · ${trace.writer_items.filter((item) => item.validation_status === "REJECTED").length} 条未通过（不是重试次数）`}>
          <div className="candidate-ledger">{trace.writer_items.map((item, index) => <article key={`${item.candidate_id}-${index}`}><div className="candidate-status"><b className={item.validation_status.toLowerCase()}>{item.validation_status}</b><span>{item.memory_type}</span></div><div><h5>{item.candidate_id}</h5><p>{item.detail || "格式、引用或完整事实复制检查；不等于文案语义与自然度已核实"}</p>{item.length_review_required && <p>偏长，待评价 · {item.text_visible_characters} 字</p>}</div><div className="reason-codes">{item.reason_codes.map((code) => <span key={code}>{decisionReason(code)}</span>)}</div></article>)}</div>
          {trace.blocked_memories.length ? <div className="inline-warning"><b>{trace.blocked_memories.length} 个 Memory 被对象级阻断</b><span>{trace.blocked_memories.map((item) => `${item.memory_type} · ${item.failure_owner} · ${item.reason_code}`).join("；")}</span></div> : null}
        </DecisionStep>

        <DecisionStep number="07" title="语义结果与最终交付" summary={`${semanticDayStateLabel(result.semantic_day_state)} · ${deliveryStateLabel(result.delivery_state)} · ${visibleChapters.length} 个可见 Chapter · ${visibleAhas.length} 个可见 Aha`}>
          <div className="final-trace-grid">{[
            ...visibleChapters.map((item) => ({ ...item, kind: "CHAPTER" as const })),
            ...visibleAhas.map((item) => ({ ...item, kind: "AHA" as const })),
          ].map((item) => <article key={item.id}><span>{item.kind} · {surfaceSourceLabel(item.surface_source)}</span><b>{item.title || item.story}</b><p>{item.story}</p><small>{item.claims.length} 条事实声明 · {item.evidence_frame_ids.length} 帧依据 · {item.evidence_support || "GROUNDED"} · {item.surface_policy_version}</small></article>)}</div>
          {diagnosticMemories.length > 0 && <div className="diagnostic-memory-list">{diagnosticMemories.map(({ memory, type }) => <article key={`trace-diagnostic-${type}-${memory.id}`}><b>{type}</b><strong>{memory.title || memory.story}</strong><span>诊断候选 · 不计入可见数量</span></article>)}</div>}
          <details><summary>查看所有 S09 入选项的交付终态</summary><pre className="raw-json">{JSON.stringify(result.selected_memory_outcomes, null, 2)}</pre></details>
        </DecisionStep>
      </div>
    </Page>
  );
}

function DecisionStep({ number, title, summary, children }: { number: string; title: string; summary: string; children: ReactNode }) {
  return <section className="decision-step"><header><span>{number}</span><div><h3>{title}</h3><p>{summary}</p></div></header><div>{children}</div></section>;
}

function CandidateLedger({
  title,
  candidates,
  assetById,
}: {
  title: string;
  candidates: X01Result["decision_trace"]["chapter_candidates"];
  assetById: Map<string, TestAsset>;
}) {
  return (
    <div className="candidate-ledger">
      <h4>{title}<small>{candidates.length} 个</small></h4>
      {candidates.length ? candidates.map((candidate) => (
        <article key={`${candidate.candidate_kind}-${candidate.source_index}`}>
          <div className="candidate-status"><b className={candidate.validation_status.toLowerCase()}>{candidate.validation_status}</b><span>{candidate.selection_status}</span></div>
          <div>
            <h5>{candidate.title || candidate.candidate_key || candidate.source_key || `候选 ${candidate.source_index + 1}`}</h5>
            <p>{candidate.storyline_identity
              ? candidate.storyline_identity.thesis || "模型未提供内部主题说明"
              : candidate.story || candidate.episode_code || candidate.event_kind || "候选在形成完整表达前被 Gate 拒绝"}</p>
            {candidate.model_grouping_reason && <p>模型分组说明：{candidate.model_grouping_reason}</p>}
            {candidate.storyline_identity && <small>{storylineBasisLabels[candidate.storyline_identity.storyline_basis] || candidate.storyline_identity.storyline_basis} · {storylineFormLabels[candidate.storyline_identity.storyline_form] || candidate.storyline_identity.storyline_form} · {candidate.storyline_identity.temporal_segments.length} 个导入片段（不代表真实时间）</small>}
            <small>{(candidate.source_asset_ids || (candidate.source_asset_id ? [candidate.source_asset_id] : [])).map((id) => assetById.get(publicAssetId(id))?.name || id).join(" · ") || "没有合法素材引用"}</small>
            {candidate.storyline_identity && <details className="storyline-beats"><summary>逐项查看为什么归入这条 Storyline</summary><ol>{candidate.storyline_identity.beat_map.map((beat) => {
              const index = candidate.observation_ids?.indexOf(beat.observation_id) ?? -1;
              const sourceId = index >= 0 ? candidate.source_asset_ids?.[index] : undefined;
              return <li key={beat.observation_id}><b>{sourceId ? assetById.get(publicAssetId(sourceId))?.name || sourceId : beat.observation_id.slice(0, 8)}</b><span>{beat.beat_role} · {beat.contribution}</span></li>;
            })}</ol></details>}
          </div>
          <div className="reason-codes">{candidate.reason_codes.map((code) => <span key={code}>{decisionReason(code)}</span>)}</div>
        </article>
      )) : <p className="helper">模型没有返回这类候选。</p>}
    </div>
  );
}

function ObservationLedger({
  candidates,
  assetById,
}: {
  candidates: NonNullable<X01Result["decision_trace"]["observation_candidates"]>;
  assetById: Map<string, TestAsset>;
}) {
  const rejected = candidates.filter((candidate) => candidate.validation_status === "REJECTED");
  const degraded = candidates.filter((candidate) => candidate.validation_status === "PASSED_WITH_FIELD_DEGRADATION");
  if (!rejected.length && !degraded.length) return null;
  return (
    <>
      {!!degraded.length && <div className="candidate-ledger">
        <h4>保留下来的字段降级 Observation<small>{degraded.length} 条 · 有效事实不会因单个辅助字段越界而整项消失</small></h4>
        {degraded.map((candidate) => {
          const assetName = candidate.source_asset_id
            ? assetById.get(publicAssetId(candidate.source_asset_id))?.name || candidate.source_asset_id
            : "素材引用无效";
          return <article key={`degraded-${candidate.source_index ?? candidate.observation_id}`}>
            <div className="candidate-status"><b className="pending">DEGRADED</b><span>事实已保留</span></div>
            <div><h5>{assetName}</h5><p>{candidate.degraded_fields?.map((item) => `${item.json_field_path} → ${item.action}`).join("；") || "辅助字段已使用保守值"}</p><small>{candidate.terminal_status || "PARTIAL"} · 每次降级都有规则与路径</small></div>
            <div className="reason-codes">{candidate.reason_codes.map((code) => <span key={code}>{decisionReason(code)}</span>)}</div>
          </article>;
        })}
      </div>}
      {!!rejected.length && <div className="candidate-ledger">
        <h4>被拒绝的 Observation<small>{rejected.length} 条 · 不影响其他合法结果</small></h4>
        {rejected.map((candidate) => {
          const assetName = candidate.source_asset_id
            ? assetById.get(publicAssetId(candidate.source_asset_id))?.name || candidate.source_asset_id
            : "素材引用无效";
          return (
            <article key={`observation-${candidate.source_index ?? candidate.observation_id}`}>
              <div className="candidate-status"><b className="rejected">REJECTED</b><span>未进入结果</span></div>
              <div><h5>{assetName}</h5><p>{candidate.invalid_frame_ids?.length ? `违规帧：${candidate.invalid_frame_ids.join(" · ")}` : candidate.detail || "结构或证据引用没有通过校验"}</p><small>{candidate.terminal_status || "FAILED"} · 失败仅隔离当前素材</small></div>
              <div className="reason-codes">{candidate.reason_codes.map((code) => <span key={code}>{decisionReason(code)}</span>)}</div>
            </article>
          );
        })}
      </div>}
    </>
  );
}

function RunInfoPage({
  assets,
  health,
  result,
  manifest,
  evidenceBytes,
  showRaw,
  setShowRaw,
}: {
  assets: TestAsset[];
  health: X01Health | null;
  result: X01Result | null;
  manifest: AppLibraryBundleManifest | null;
  evidenceBytes: number;
  showRaw: boolean;
  setShowRaw: (value: boolean) => void;
}) {
  const clientTrace = result?.trace.client_trace;
  const completedAt = result?.trace.completed_at
    ? new Date(result.trace.completed_at).toLocaleString("zh-CN", { hour12: false })
    : "尚未完成";
  const modelMetrics = result?.trace.stage_metrics.filter((metric) => metric.model_calls > 0) || [];
  const pricingConfigured = result
    ? modelMetrics.some((metric) => !metric.pricing_basis?.toLowerCase().includes("unconfigured"))
    : false;
  const modelCost = result && pricingConfigured
    ? `$${result.trace.estimated_cost_usd.toFixed(6)}`
    : result ? "费率未配置，无法估算" : "尚未运行";
  return (
    <Page eyebrow="RUN INFO · RESEARCH ONLY" title="这次运行到底做了什么。">
      <div className="boundary-grid">
        <div><span>产品合同</span><b>Canonical V1.25 · S00–S13</b><p>页面按最新冻结规则检查 Chapter、Aha、文案与 Tag。</p></div>
        <div><span>当前执行形态</span><b>X02 V04.1 · Delivery-safe · Fresh Full Run</b><p>每次从原始素材重新生成 Evidence，再执行当前 S00–S12；语义日状态与最终交付状态分开记录，S13 明确不执行。</p></div>
        <div><span>输入画像</span><b>PHONE LIBRARY DAY TEST</b><p>一次导入视为一天；只保留导入顺序，时间与 GPS 不参与。</p></div>
      </div>
      <div className="trace-table">
        <Row label="导入素材" value={`${assets.length} 项 · ${bytes(assets.reduce((sum, asset) => sum + asset.size, 0))}`} />
        <Row label="Evidence" value={manifest ? `${manifest.assets.reduce((sum, asset) => sum + asset.frames.length, 0)} 帧 · ${bytes(evidenceBytes)}` : "尚未生成"} />
        <Row label="正式测试方式" value={result ? `${result.evaluation_run_mode} · 跨轮语义缓存 ${result.cross_run_semantic_cache_used ? "已使用" : "未使用"}` : "每轮从原素材完整运行"} />
        <Row label="语义日状态" value={result ? semanticDayStateLabel(result.semantic_day_state) : "尚未运行"} />
        <Row label="交付状态" value={result ? deliveryStateLabel(result.delivery_state) : "尚未运行"} />
        <Row label="素材理解覆盖" value={result ? (result.coverage_status === "COMPLETE" ? "完整" : `部分失败 · ${result.unresolved_asset_ids.length} 项未解决`) : "尚未运行"} />
        <Row label="时间依据" value={result ? (result.timeline_basis === "SYNTHETIC_SEQUENCE_ONLY" ? "仅按导入顺序，不代表真实时间" : "可靠拍摄时间") : "本测试页固定只使用导入顺序"} />
        <Row label="时间日期" value={result?.timeline_date || "无；没有从导入时间伪造拍摄日期"} />
        <Row label="时间可靠性" value={result ? `拍摄时间 ${result.time_reliability.capture_time_reliable ? "可靠" : "不可靠"} · 间隔 ${result.time_reliability.interval_reliable ? "可靠" : "不可靠"} · 时区 ${result.time_reliability.timezone_reliable ? "可靠" : "不可靠"}` : "均未提供"} />
        <Row label="Evidence Profile" value={result?.trace.evidence_profile_version || "PHONE_TEST_DURATION_WINDOWS_V01"} />
        <Row label="原始文件上传" value={result ? `${result.trace.originals_uploaded} 个` : "不会上传"} />
        <Row label="服务" value={health ? `${health.provider} · ${health.model}` : "未连接"} />
        <Row label="本页目标版本" value="Storyline V03 / Writer V02 / Chapter Media V01（codex V1.37）" />
        <Row label="已连接服务版本" value={health ? `${health.storylineContractVersion} / ${health.writerSurfacePolicyVersion}` : "未连接；不代表已运行新算法"} />
        <Row label="本轮实际算法版本" value={result ? `${result.storyline_contract_version} / ${result.writer_surface_policy_version}` : "尚未运行"} />
        <Row label="已连接服务处理策略" value={health ? runtimePolicyLabel(health.runtimePolicies) : "未连接"} />
        <Row label="本轮实际处理策略" value={result ? runtimePolicyLabel(result.decision_trace.runtime_policies) : "尚未运行；页面更新不会改写旧结果"} />
        <Row label="本轮素材精选策略" value={result?.chapter_media_policy_version || "尚未运行；最低三项，不默认填满五项"} />
        <Row label="本轮分组合同指纹" value={result?.storyline_contract_sha256 || "尚未运行"} />
        <Row label="完成时间" value={completedAt} />
        <Row label="审计运行 ID" value={result?.trace.run_id || "尚未生成"} />
        <Row label="本地审计账本" value={result ? `var/x02_runs/${result.session_id}/run_audit.json` : "成功运行后自动保存（不含图片）"} />
        <Row label="模型调用" value={result ? `${result.trace.model_calls} 次 · ${result.trace.model_frame_count} 帧进入模型` : "尚未运行"} />
        <Row label="Token" value={result ? `${result.trace.input_tokens} in · ${result.trace.output_tokens} out` : "尚未运行"} />
        <Row label="模型时延" value={result ? `${result.trace.latency_seconds.toFixed(2)} 秒` : "尚未运行"} />
        <Row label="模型 API 估算成本" value={modelCost} />
        <Row label="成本估算口径" value={result ? [...new Set(modelMetrics.map((metric) => metric.pricing_basis || "未配置"))].join(" · ") || "没有模型调用" : "尚未运行"} />
        <Row label="用户等待总时长" value={clientTrace?.total_duration_ms ? elapsed(clientTrace.total_duration_ms) : "等待下一次新版本运行记录"} />
      </div>

      <section className="stage-metrics">
        <div className="section-title"><div><p className="eyebrow">TIME · TOKEN · COST</p><h3>逐流程消耗</h3><p>时间按真实测量展示；Token 与模型 API 费用只归到实际调用模型的步骤，不把一次模型调用虚构拆分。这里不等于服务器、网络、存储等生产总成本。</p></div></div>
        {result ? <div className="metric-table">
          <div className="metric-head"><span>流程</span><span>耗时</span><span>Token</span><span>成本</span><span>说明</span></div>
          {clientTrace?.stages.map((metric) => <MetricRow key={`client-${metric.stage}`} label={stageLabel(metric.stage)} durationMs={metric.duration_ms} tokens="—" cost="—" note={metric.stage === "UPLOAD_AND_SERVICE_ROUND_TRIP" ? "包含上传、云端处理与下载响应，和服务端分项时间重叠" : "Web 端实测"} />)}
          {result.trace.server_metrics?.map((metric) => <MetricRow key={`server-${metric.stage}`} label={stageLabel(metric.stage)} durationMs={metric.duration_ms} tokens="—" cost="—" note={`${bytes(metric.request_body_bytes)} 请求体在本机网关落盘并校验`} />)}
          {result.trace.stage_metrics.map((metric) => <MetricRow
            key={metric.stage}
            label={stageLabel(metric.stage)}
            durationMs={metric.duration_ms}
            tokens={metric.input_tokens || metric.output_tokens ? `${metric.input_tokens} in · ${metric.output_tokens} out` : "0"}
            cost={metric.model_calls > 0 ? (pricingConfigured ? `$${metric.estimated_cost_usd.toFixed(6)}` : "无法估算") : "未计（非模型）"}
            note={metric.model_calls > 0 ? `${metric.model_calls} 次模型调用 · ${metric.model_frame_count ?? 0} 帧；只承担该阶段职责` : "确定性本地步骤，不消耗模型 Token"}
          />)}
          <MetricRow label="服务端 X02 合计" durationMs={result.trace.total_duration_ms} tokens={`${result.trace.input_tokens + result.trace.output_tokens}`} cost={pricingConfigured ? `$${result.trace.estimated_cost_usd.toFixed(6)}` : "无法估算"} note="分阶段模型调用 + 确定性 Gate；成本仅含模型 API" total />
          {clientTrace?.total_duration_ms !== null && clientTrace?.total_duration_ms !== undefined && <MetricRow label="用户端端到端合计" durationMs={clientTrace.total_duration_ms} tokens="模型同上" cost="模型 API 同上" note="从开始生成 Evidence 到页面收到并解析结果；这是用户真实等待时间" total />}
        </div> : <Blank text="完成一次新版本运行后，这里会显示每个流程的真实时间、Token 与成本。" />}
        {result && <p className="metric-scope">{result.trace.stage_metric_scope}</p>}
      </section>

      {clientTrace?.asset_metrics.length ? <details className="asset-timing"><summary>查看每项素材的 Evidence 处理时间</summary><div>{clientTrace.asset_metrics.map((item) => <article key={item.asset_id}><b>{item.sequence.toString().padStart(2, "0")} · {item.source_display_name}</b><span>抽帧/标准化 {elapsed(item.evidence_generation_ms)}</span><span>原文件校验 {elapsed(item.source_hash_ms)}</span><span>单项合计 {elapsed(item.total_duration_ms)}</span><small>{item.evidence_frame_count} 帧 · {bytes(item.evidence_bytes)}</small></article>)}</div></details> : null}

      <button className="raw-toggle" disabled={!result} onClick={() => setShowRaw(!showRaw)}>{showRaw ? "收起" : "查看"}原始结果 JSON</button>
      {showRaw && result && <pre className="raw-json">{JSON.stringify({ manifest, result }, null, 2)}</pre>}
      <div className="capacity-note"><b>为什么现在可以超过 24 项？</b><p><strong>X02 不再把全部素材塞进一次模型调用。</strong>完整测试日先按每批最多 3 项，并同时限制帧数与 Evidence 体积来生成 Observation，再用结构化事实做全天聚合；失败批次会拆小隔离，不能把整天误报成 Empty Day。</p><ul><li>本地测试日默认安全边界为 240 项，覆盖 186 项高强度日基准。</li><li>照片只生成 1 帧；视频 ≤10 秒为 1 Window / 3 帧，10–30 秒为 2 Window / 4 帧，30–90 秒为 4 Window / 8 帧，超过 90 秒为 6 Window / 12 帧。</li><li>这只是手机素材测试 Profile，不覆盖冻结的 Auto 9 秒三帧合同。</li><li>候选可以超过 5 项；最终 Chapter 展示 3–5 项，第四、第五项须有新增展示价值。双素材例外已取消，相似素材不会从整章候选中全部删除。</li><li>当前上传仍由浏览器一次准备完整 Evidence；分批上传、断点缓存与 App 后台 Sync 属于后续工程。</li></ul></div>
      <div className="limitation"><b>手机素材对结论的影响</b><ul><li>素材会等比例缩放到 768×1024 画布内，空余位置留边；低清、抖动和模糊仍会降低理解质量。</li><li>新导入的横屏素材保留完整画面，不再居中裁切；横图缩小后的细节仍有限。旧结果不会自动重新处理，需重新导入才能使用完整画面输入。</li><li>数量会直接影响 Chapter 完整度；稀疏测试日不应强行产出 3–4 个 Chapter。</li><li>最大的偏差来自拍摄行为：手机素材更主动、更精选，无法替代第一人称、每两分钟采集的连续性校准。</li><li>没有真实时间与 GPS，本轮只按导入顺序判断相邻关系；不能验证真实间隔、当天时长、跨批次修订、地点实体、真实日界线或 Preview 触发阈值。</li></ul></div>
    </Page>
  );
}

function stageLabel(stage: string) {
  const exact = ({
    EVIDENCE_PREPARATION: "Web 生成标准化 Evidence",
    UPLOAD_AND_SERVICE_ROUND_TRIP: "Web 上传并等待服务返回",
    RESPONSE_PARSE: "Web 解析响应",
    REQUEST_MULTIPART_MATERIALIZATION: "网关接收并校验 Evidence",
    S00_S02_BUNDLE_LOAD: "S00–S02 加载并验证 Evidence Bundle",
    S04_DETERMINISTIC_VALIDATION: "S04 逐素材 Evidence Gate",
    S03_S07_DETERMINISTIC_STRUCTURE: "S03–S07 边界、Moment 与候选 Gate",
    S05_S07_STRUCTURE_PROPOSAL: "S05–S07 结构提议",
    S08_S09_SET_SELECTION: "S08–S09 全天集合选择",
    S10_MEDIA_EDITORIAL: "S10 最终媒体精选",
    S11_DETERMINISTIC_VALIDATION: "S11 Writer 输出校验",
    S12_FINAL_VALIDATION: "S12 最终合同校验",
  } as Record<string, string>)[stage];
  if (exact) return exact;
  if (stage.startsWith("S10_CHAPTER_VISUAL_SELECTION_")) return `S10 Chapter 画面比较 ${stage.slice(-2)}`;
  if (stage.startsWith("S04_PERCEPTION_BATCH_")) return `S04 小批视觉理解 ${stage.slice(-3)}`;
  if (stage.startsWith("S11_WRITER_ATTEMPT_")) return `S11 Writer 第 ${stage.slice(-1)} 次`;
  return stage;
}

function MetricRow({ label, durationMs, tokens, cost, note, total = false }: { label: string; durationMs: number; tokens: string; cost: string; note: string; total?: boolean }) {
  return <div className={total ? "metric-row total" : "metric-row"}><b>{label}</b><span>{elapsed(durationMs)}</span><span>{tokens}</span><span>{cost}</span><small>{note}</small></div>;
}

function Page({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return <section className="page"><p className="eyebrow">{eyebrow}</p><h2>{title}</h2>{children}</section>;
}

function Blank({ text, action, onAction }: { text: string; action?: string; onAction?: () => void }) {
  return <div className="blank"><span>◎</span><p>{text}</p>{action && <button className="button secondary" onClick={onAction}>{action}</button>}</div>;
}

function Row({ label, value }: { label: string; value: string }) {
  return <div><span>{label}</span><b>{value}</b></div>;
}
