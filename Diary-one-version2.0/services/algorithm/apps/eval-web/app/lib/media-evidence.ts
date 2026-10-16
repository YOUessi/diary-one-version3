import type {
  AppLibraryBundleManifest,
  ClientAssetTrace,
  ClientRunTrace,
  EvidenceBundle,
  EvidenceFrame,
  TestAsset,
  X01Health,
  X01Result,
} from "./contracts";
import { v041ResultContractConsistent } from "./result-contract";
import { currentRuntimePolicies } from "./codex-runtime-policy";
import {
  createResearchRunAbortControl,
  RESEARCH_PREVIEW_TIMEOUT_MS,
  ResearchPreviewCancelledError,
  ResearchPreviewTimeoutError,
} from "./research-run-control";

const OUTPUT_WIDTH = 768;
const OUTPUT_HEIGHT = 1024;
const PHONE_TEST_EVIDENCE_PROFILE_VERSION = "PHONE_TEST_DURATION_WINDOWS_V01" as const;
const VIDEO_METADATA_TIMEOUT_MS = 12_000;
const VIDEO_SEEK_TIMEOUT_MS = 12_000;
const VIDEO_FRAME_FALLBACK_MS = 1_500;
const RUN_SIDECAR_TIMEOUT_MS = 5_000;
const CLIENT_TRACE_SCHEMA_VERSION = "DIARY_ONE_WEB_CLIENT_TRACE_V01" as const;
const RUN_SIDECAR_SCHEMA_VERSION = "DIARY_ONE_X01_RUN_SIDECAR_V01" as const;
const V041_SEMANTIC_DAY_STATES = new Set(["CHAPTER_DAY", "HIGHLIGHT_DAY", "EMPTY_DAY", "UNRESOLVED_DAY"]);
/** Align with BFF result_admit / App deliveryAdmit (ready + honest empty). */
const V041_DELIVERY_STATES = new Set([
  "READY_PRIMARY_COPY",
  "READY_WITH_GROUNDED_COPY_FALLBACK",
  "READY_WITH_ITEM_BLOCKS",
  "STAGED_PREVIEW_DELIVERED",
  "NO_GROUNDED_MEMORY",
]);
/** Diagnostic-only — never treat as consumer-ready (AI03). */
const V041_BLOCKED_DELIVERY_STATES = new Set(["PIPELINE_BLOCKED"]);
const SHA256_ROUND_CONSTANTS = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

type ClientTraceState = {
  trace: ClientRunTrace;
  pipelineStartedMonotonicMs: number;
};

type RunSidecarPayload = {
  session_id: string;
  client_trace?: object;
  human_review?: object;
};

type RunSidecarResponse = {
  status: "saved";
  session_id: string;
  saved: Array<"client_trace" | "human_review">;
};

type ManifestAssetWithDisplayName = AppLibraryBundleManifest["assets"][number] & {
  source_display_name: string;
};

type EvidenceSamplePlan = {
  windowIndex: number;
  windowCount: 1 | 2 | 4 | 6;
  sampleRole: EvidenceFrame["sampleRole"];
  canonicalOffsetMs: EvidenceFrame["canonicalOffsetMs"];
  sourceFraction: number | null;
};

const clientTraceByBundle = new WeakMap<EvidenceBundle, ClientTraceState>();

function elapsedMs(started: number, completed = performance.now()) {
  return Math.max(0, Math.round((completed - started) * 1000) / 1000);
}

function evidencePlan(asset: TestAsset): EvidenceSamplePlan[] {
  if (asset.kind === "PHOTO") {
    return [{
      windowIndex: 0,
      windowCount: 1,
      sampleRole: "PHOTO_REPRESENTATIVE",
      canonicalOffsetMs: 4500,
      sourceFraction: null,
    }];
  }
  const durationMs = asset.durationMs ?? 0;
  const windowCount: 1 | 2 | 4 | 6 = durationMs <= 10_000
    ? 1
    : durationMs <= 30_000
      ? 2
      : durationMs <= 90_000
        ? 4
        : 6;
  const localSamples = windowCount === 1
    ? [
      { role: "WINDOW_EARLY" as const, offset: 1500 as const, fraction: 1 / 6 },
      { role: "WINDOW_MIDDLE" as const, offset: 4500 as const, fraction: 1 / 2 },
      { role: "WINDOW_LATE" as const, offset: 7500 as const, fraction: 5 / 6 },
    ]
    : [
      { role: "WINDOW_EARLY" as const, offset: 1500 as const, fraction: 1 / 6 },
      { role: "WINDOW_LATE" as const, offset: 7500 as const, fraction: 5 / 6 },
    ];
  return Array.from({ length: windowCount }, (_, windowIndex) => localSamples.map((sample) => ({
    windowIndex,
    windowCount,
    sampleRole: sample.role,
    canonicalOffsetMs: sample.offset,
    sourceFraction: (windowIndex + sample.fraction) / windowCount,
  }))).flat();
}

class IncrementalSha256 {
  private state = new Uint32Array([
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ]);
  private buffer = new Uint8Array(64);
  private bufferLength = 0;
  private bytesHashed = 0;
  private words = new Uint32Array(64);

  update(input: Uint8Array) {
    this.bytesHashed += input.length;
    let position = 0;
    if (this.bufferLength) {
      const needed = Math.min(64 - this.bufferLength, input.length);
      this.buffer.set(input.subarray(0, needed), this.bufferLength);
      this.bufferLength += needed;
      position += needed;
      if (this.bufferLength === 64) {
        this.processBlock(this.buffer, 0);
        this.bufferLength = 0;
      }
    }
    while (position + 64 <= input.length) {
      this.processBlock(input, position);
      position += 64;
    }
    if (position < input.length) {
      this.buffer.set(input.subarray(position), 0);
      this.bufferLength = input.length - position;
    }
  }

  hex() {
    const totalBytes = this.bytesHashed;
    this.buffer[this.bufferLength++] = 0x80;
    if (this.bufferLength > 56) {
      this.buffer.fill(0, this.bufferLength, 64);
      this.processBlock(this.buffer, 0);
      this.bufferLength = 0;
    }
    this.buffer.fill(0, this.bufferLength, 56);
    const highBits = Math.floor(totalBytes / 0x20000000);
    const lowBits = (totalBytes * 8) >>> 0;
    this.buffer[56] = highBits >>> 24;
    this.buffer[57] = highBits >>> 16;
    this.buffer[58] = highBits >>> 8;
    this.buffer[59] = highBits;
    this.buffer[60] = lowBits >>> 24;
    this.buffer[61] = lowBits >>> 16;
    this.buffer[62] = lowBits >>> 8;
    this.buffer[63] = lowBits;
    this.processBlock(this.buffer, 0);
    return Array.from(this.state, (word) => word.toString(16).padStart(8, "0")).join("");
  }

  private processBlock(chunk: Uint8Array, offset: number) {
    const words = this.words;
    for (let index = 0; index < 16; index += 1) {
      const position = offset + index * 4;
      words[index] = (
        (chunk[position] << 24)
        | (chunk[position + 1] << 16)
        | (chunk[position + 2] << 8)
        | chunk[position + 3]
      ) >>> 0;
    }
    for (let index = 16; index < 64; index += 1) {
      const x = words[index - 15];
      const y = words[index - 2];
      const sigma0 = ((x >>> 7) | (x << 25)) ^ ((x >>> 18) | (x << 14)) ^ (x >>> 3);
      const sigma1 = ((y >>> 17) | (y << 15)) ^ ((y >>> 19) | (y << 13)) ^ (y >>> 10);
      words[index] = (words[index - 16] + sigma0 + words[index - 7] + sigma1) >>> 0;
    }
    let [a, b, c, d, e, f, g, h] = this.state;
    for (let index = 0; index < 64; index += 1) {
      const sum1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
      const choice = (e & f) ^ (~e & g);
      const temp1 = (h + sum1 + choice + SHA256_ROUND_CONSTANTS[index] + words[index]) >>> 0;
      const sum0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
      const majority = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (sum0 + majority) >>> 0;
      h = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }
    this.state[0] = (this.state[0] + a) >>> 0;
    this.state[1] = (this.state[1] + b) >>> 0;
    this.state[2] = (this.state[2] + c) >>> 0;
    this.state[3] = (this.state[3] + d) >>> 0;
    this.state[4] = (this.state[4] + e) >>> 0;
    this.state[5] = (this.state[5] + f) >>> 0;
    this.state[6] = (this.state[6] + g) >>> 0;
    this.state[7] = (this.state[7] + h) >>> 0;
  }
}

class MediaWaitTimeoutError extends Error {
  constructor(event: string, timeoutMs: number) {
    const eventLabel = event === "loadedmetadata" ? "读取视频信息" : event === "seeked" ? "定位视频画面" : event;
    super(`${eventLabel}超过 ${Math.round(timeoutMs / 1000)} 秒`);
    this.name = "MediaWaitTimeoutError";
  }
}

function waitForEvent(target: EventTarget, event: string, errorEvent = "error", timeoutMs = VIDEO_METADATA_TIMEOUT_MS) {
  return new Promise<void>((resolve, reject) => {
    const done = () => {
      cleanup();
      resolve();
    };
    const failed = () => {
      cleanup();
      reject(new Error(`无法解码该素材（${errorEvent}）`));
    };
    const timedOut = () => {
      cleanup();
      reject(new MediaWaitTimeoutError(event, timeoutMs));
    };
    const cleanup = () => {
      clearTimeout(timeoutId);
      target.removeEventListener(event, done);
      target.removeEventListener(errorEvent, failed);
    };
    const timeoutId = setTimeout(timedOut, timeoutMs);
    target.addEventListener(event, done, { once: true });
    target.addEventListener(errorEvent, failed, { once: true });
  });
}

function loadImage(file: File) {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const image = new Image();
    const url = URL.createObjectURL(file);
    image.onload = () => {
      URL.revokeObjectURL(url);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("浏览器无法解码这张照片"));
    };
    image.src = url;
  });
}

async function loadVideo(file: File) {
  const video = document.createElement("video");
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";
  const url = URL.createObjectURL(file);
  try {
    const metadataReady = waitForEvent(video, "loadedmetadata", "error", VIDEO_METADATA_TIMEOUT_MS);
    video.src = url;
    video.load();
    await metadataReady;
    if (!Number.isFinite(video.duration) || video.duration <= 0) {
      throw new Error("视频时长无效");
    }
    return { video, url };
  } catch (error) {
    URL.revokeObjectURL(url);
    throw error;
  }
}

function extensionOf(name: string) {
  const dot = name.lastIndexOf(".");
  return dot >= 0 ? name.slice(dot + 1).toLowerCase() : "unknown";
}

export async function inspectFiles(files: File[]): Promise<TestAsset[]> {
  const inspected: TestAsset[] = [];
  for (const file of files) {
    const kind = file.type.startsWith("video/") || /\.(mov|mp4|m4v|webm)$/i.test(file.name)
      ? "VIDEO"
      : "PHOTO";
    const id = crypto.randomUUID();
    const url = URL.createObjectURL(file);
    try {
      if (kind === "PHOTO") {
        const image = await loadImage(file);
        inspected.push({
          id,
          file,
          name: file.name,
          kind,
          url,
          size: file.size,
          width: image.naturalWidth,
          height: image.naturalHeight,
          durationMs: null,
          decodeStatus: "READY",
        });
      } else {
        const loaded = await loadVideo(file);
        inspected.push({
          id,
          file,
          name: file.name,
          kind,
          url,
          size: file.size,
          width: loaded.video.videoWidth,
          height: loaded.video.videoHeight,
          durationMs: Math.max(1, Math.round(loaded.video.duration * 1000)),
          decodeStatus: "READY",
        });
        URL.revokeObjectURL(loaded.url);
      }
    } catch (error) {
      inspected.push({
        id,
        file,
        name: file.name,
        kind,
        url,
        size: file.size,
        width: 0,
        height: 0,
        durationMs: null,
        decodeStatus: "UNSUPPORTED",
        decodeMessage: error instanceof Error ? error.message : "浏览器无法解码该素材",
      });
    }
  }
  return inspected;
}

export function drawNormalized(source: CanvasImageSource, sourceWidth: number, sourceHeight: number) {
  if (!Number.isFinite(sourceWidth) || !Number.isFinite(sourceHeight) || sourceWidth <= 0 || sourceHeight <= 0) {
    throw new Error("素材尺寸无效，无法保留完整画面");
  }
  const canvas = document.createElement("canvas");
  canvas.width = OUTPUT_WIDTH;
  canvas.height = OUTPUT_HEIGHT;
  const context = canvas.getContext("2d", { alpha: false });
  if (!context) throw new Error("浏览器无法创建图像处理画布");
  // Fit the complete source inside the existing Evidence canvas, without cropping.
  const scale = Math.min(OUTPUT_WIDTH / sourceWidth, OUTPUT_HEIGHT / sourceHeight);
  const drawWidth = sourceWidth * scale;
  const drawHeight = sourceHeight * scale;
  context.fillStyle = "#000";
  context.fillRect(0, 0, OUTPUT_WIDTH, OUTPUT_HEIGHT);
  context.drawImage(
    source,
    (OUTPUT_WIDTH - drawWidth) / 2,
    (OUTPUT_HEIGHT - drawHeight) / 2,
    drawWidth,
    drawHeight,
  );
  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (blob) => blob ? resolve(blob) : reject(new Error("JPEG Evidence 编码失败")),
      "image/jpeg",
      0.84,
    );
  });
}

async function sha256(blob: Blob, onProgress?: (processedBytes: number, totalBytes: number) => void) {
  const hasher = new IncrementalSha256();
  const chunkBytes = 4 * 1024 * 1024;
  for (let offset = 0; offset < blob.size; offset += chunkBytes) {
    const processedBytes = Math.min(offset + chunkBytes, blob.size);
    hasher.update(new Uint8Array(await blob.slice(offset, processedBytes).arrayBuffer()));
    onProgress?.(processedBytes, blob.size);
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
  }
  return hasher.hex();
}

async function waitForPresentedVideoFrame(video: HTMLVideoElement) {
  if (!("requestVideoFrameCallback" in video)) {
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
    return;
  }

  await new Promise<void>((resolve) => {
    let settled = false;
    const pending: {
      callbackId?: number;
      timeoutId?: ReturnType<typeof setTimeout>;
    } = {};
    const finish = (cancelPending: boolean) => {
      if (settled) return;
      settled = true;
      if (pending.timeoutId !== undefined) clearTimeout(pending.timeoutId);
      if (cancelPending && pending.callbackId !== undefined && "cancelVideoFrameCallback" in video) {
        try {
          video.cancelVideoFrameCallback(pending.callbackId);
        } catch {
          // The frame may have been delivered between the timeout and cancellation.
        }
      }
      resolve();
    };
    pending.callbackId = video.requestVideoFrameCallback(() => finish(false));
    pending.timeoutId = setTimeout(() => finish(true), VIDEO_FRAME_FALLBACK_MS);
  });
}

async function seekVideo(video: HTMLVideoElement, seconds: number) {
  const safe = Math.min(Math.max(seconds, 0), Math.max(video.duration - 0.001, 0));
  if (Math.abs(video.currentTime - safe) > 0.001) {
    const seeked = waitForEvent(video, "seeked", "error", VIDEO_SEEK_TIMEOUT_MS);
    video.currentTime = safe;
    try {
      await seeked;
    } catch (error) {
      const reachedTarget = Math.abs(video.currentTime - safe) <= 0.15;
      const frameIsUsable = reachedTarget && !video.seeking && video.readyState >= 2;
      if (!(error instanceof MediaWaitTimeoutError && frameIsUsable)) {
        throw error;
      }
    }
  }
  await waitForPresentedVideoFrame(video);
}

async function framesForAsset(
  asset: TestAsset,
  onFrameStart?: (frameNumber: number, totalFrames: number) => void,
): Promise<EvidenceFrame[]> {
  const frames: EvidenceFrame[] = [];
  const plan = evidencePlan(asset);
  if (asset.kind === "PHOTO") {
    onFrameStart?.(1, 1);
    const image = await loadImage(asset.file);
    const normalized = await drawNormalized(image, image.naturalWidth, image.naturalHeight);
    const normalizedHash = await sha256(normalized);
    const sample = plan[0];
    frames.push({
      frameId: `frame_${asset.id}_w00_${sample.canonicalOffsetMs}`,
      canonicalOffsetMs: sample.canonicalOffsetMs,
      windowIndex: sample.windowIndex,
      windowCount: sample.windowCount,
      sampleRole: sample.sampleRole,
      sourceTimestampMs: null,
      relativePath: `evidence/asset_${asset.id}/frame_w00_${sample.canonicalOffsetMs}.jpg`,
      sha256: normalizedHash,
      blob: normalized,
    });
    return frames;
  }

  const { video, url } = await loadVideo(asset.file);
  try {
    for (let index = 0; index < plan.length; index += 1) {
      const sample = plan[index];
      onFrameStart?.(index + 1, plan.length);
      const seconds = video.duration * (sample.sourceFraction ?? 0.5);
      await seekVideo(video, seconds);
      const blob = await drawNormalized(video, video.videoWidth, video.videoHeight);
      frames.push({
        frameId: `frame_${asset.id}_w${sample.windowIndex.toString().padStart(2, "0")}_${sample.canonicalOffsetMs}`,
        canonicalOffsetMs: sample.canonicalOffsetMs,
        windowIndex: sample.windowIndex,
        windowCount: sample.windowCount,
        sampleRole: sample.sampleRole,
        sourceTimestampMs: Math.round(video.currentTime * 1000),
        relativePath: `evidence/asset_${asset.id}/frame_w${sample.windowIndex.toString().padStart(2, "0")}_${sample.canonicalOffsetMs}.jpg`,
        sha256: await sha256(blob),
        blob,
      });
    }
    return frames;
  } catch (error) {
    const message = error instanceof Error ? error.message : "无法抽取视频画面";
    throw new Error(`${asset.name}：${message}。请移除该视频，或转为 H.264 MP4 后重试。`);
  } finally {
    video.removeAttribute("src");
    video.load();
    URL.revokeObjectURL(url);
  }
}

export async function buildEvidenceBundle(
  assets: TestAsset[],
  onProgress?: (done: number, total: number, label: string) => void,
): Promise<EvidenceBundle> {
  if (!assets.length) throw new Error("请先导入素材");
  if (assets.some((asset) => asset.decodeStatus !== "READY")) {
    throw new Error("请先移除浏览器无法解码的素材");
  }
  const pipelineStartedAt = new Date().toISOString();
  const pipelineStartedMonotonicMs = performance.now();
  const evidenceStartedMonotonicMs = pipelineStartedMonotonicMs;
  const sessionId = crypto.randomUUID();
  const manifestAssets: ManifestAssetWithDisplayName[] = [];
  const allFrames: EvidenceFrame[] = [];
  const assetTraces: ClientAssetTrace[] = [];
  for (let index = 0; index < assets.length; index += 1) {
    const asset = assets[index];
    const assetStartedMonotonicMs = performance.now();
    onProgress?.(index, assets.length, `正在处理 ${asset.name}`);
    const evidenceGenerationStartedMonotonicMs = performance.now();
    const frames = await framesForAsset(asset, (frameNumber, totalFrames) => {
      const frameRatio = (frameNumber - 1) / totalFrames;
      const label = asset.kind === "VIDEO"
        ? `正在从 ${asset.name} 抽取第 ${frameNumber}/${totalFrames} 帧`
        : `正在标准化 ${asset.name}`;
      onProgress?.(index + frameRatio * 0.75, assets.length, label);
    });
    const evidenceGenerationMs = elapsedMs(evidenceGenerationStartedMonotonicMs);
    onProgress?.(index + 0.75, assets.length, `正在校验 ${asset.name} · 0%`);
    const sourceHashStartedMonotonicMs = performance.now();
    const originalHash = await sha256(asset.file, (processedBytes, totalBytes) => {
      const hashRatio = totalBytes ? processedBytes / totalBytes : 1;
      const percent = Math.min(100, Math.round(hashRatio * 100));
      onProgress?.(
        index + 0.75 + hashRatio * 0.25,
        assets.length,
        `正在校验 ${asset.name} · ${percent}%`,
      );
    });
    const sourceHashMs = elapsedMs(sourceHashStartedMonotonicMs);
    const evidenceBytes = frames.reduce((total, frame) => total + frame.blob.size, 0);
    allFrames.push(...frames);
    manifestAssets.push({
      asset_id: `asset_${asset.id}`,
      source_display_name: asset.name,
      media_kind: asset.kind,
      media_source: "PHONE_LIBRARY_DAY_TEST",
      original_file_extension: extensionOf(asset.name),
      original_sha256: originalHash,
      original_bytes: asset.size,
      original_width: asset.width,
      original_height: asset.height,
      original_duration_ms: asset.durationMs,
      original_included: false,
      // Stable import order only. Never encode it in a time-shaped field.
      sequence_index: index,
      logical_asset_duration_ms: 9000,
      materialized_video: false,
      evidence_sampling_profile: asset.kind === "PHOTO"
        ? "PHOTO_SINGLE_FRAME"
        : frames[0].windowCount === 1
          ? "VIDEO_SINGLE_WINDOW_THREE"
          : "VIDEO_MULTI_WINDOW_TWO_PER_WINDOW",
      evidence_window_count: frames[0].windowCount,
      frames: frames.map((frame) => ({
        frame_id: frame.frameId,
        window_index: frame.windowIndex,
        window_count: frame.windowCount,
        sample_role: frame.sampleRole,
        canonical_offset_ms: frame.canonicalOffsetMs,
        source_timestamp_ms: frame.sourceTimestampMs,
        relative_path: frame.relativePath,
        sha256: frame.sha256,
        width: 768,
        height: 1024,
        spatial_transform: "ASPECT_FIT_LETTERBOX",
      })),
    });
    assetTraces.push({
      asset_id: `asset_${asset.id}`,
      sequence: index + 1,
      source_display_name: asset.name,
      media_kind: asset.kind,
      original_bytes: asset.size,
      evidence_bytes: evidenceBytes,
      evidence_frame_count: frames.length,
      evidence_generation_ms: evidenceGenerationMs,
      source_hash_ms: sourceHashMs,
      total_duration_ms: elapsedMs(assetStartedMonotonicMs),
    });
  }
  onProgress?.(assets.length, assets.length, "Evidence 已准备完成");
  const manifest: AppLibraryBundleManifest = {
    bundle_version: "DIARY_ONE_APP_LIBRARY_BUNDLE_V04",
    research_only: true,
    session: {
      session_id: sessionId,
      exported_at: new Date().toISOString(),
      timezone: "TEST_DAY_NO_TIMEZONE",
    },
    device: {
      device_id: `web-test-${sessionId.slice(0, 8)}`,
      hardware_revision: "PHONE_LIBRARY_TEST",
      firmware_version: "NOT_APPLICABLE",
      sdk_version: "WEB_EVIDENCE_V04",
    },
    normalization: {
      width: 768,
      height: 1024,
      orientation: "PORTRAIT",
      aspect_ratio: "3:4",
      spatial_transform: "ASPECT_FIT_LETTERBOX",
      temporal_transform: PHONE_TEST_EVIDENCE_PROFILE_VERSION,
      canonical_frame_offsets_ms: [1500, 4500, 7500],
      evidence_profile_version: PHONE_TEST_EVIDENCE_PROFILE_VERSION,
    },
    assets: manifestAssets,
  };
  const evidenceBytes = allFrames.reduce((total, frame) => total + frame.blob.size, 0);
  const bundle: EvidenceBundle = {
    manifest,
    frames: allFrames,
    evidenceBytes,
  };
  const evidenceFinishedAt = new Date().toISOString();
  const evidenceTotalMs = elapsedMs(evidenceStartedMonotonicMs);
  const originalBytes = assets.reduce((total, asset) => total + asset.size, 0);
  clientTraceByBundle.set(bundle, {
    pipelineStartedMonotonicMs,
    trace: {
      trace_version: CLIENT_TRACE_SCHEMA_VERSION,
      session_id: sessionId,
      started_at: pipelineStartedAt,
      finished_at: null,
      total_duration_ms: null,
      asset_count: assets.length,
      original_bytes: originalBytes,
      evidence_bytes: evidenceBytes,
      evidence_frame_count: allFrames.length,
      http_status: null,
      asset_metrics: assetTraces,
      stages: [{
        stage: "EVIDENCE_PREPARATION",
        started_at: pipelineStartedAt,
        finished_at: evidenceFinishedAt,
        duration_ms: evidenceTotalMs,
        input_bytes: originalBytes,
        output_bytes: evidenceBytes,
      }],
    },
  });
  return bundle;
}

function endpointBase(value: string) {
  return value.trim().replace(/\/+$/, "");
}

function authHeaders(token: string): Record<string, string> {
  return token.trim() ? { Authorization: `Bearer ${token.trim()}` } : {};
}

async function responseError(response: Response) {
  try {
    const value = await response.json() as {
      message?: string;
      error?: string;
      code?: string;
      stage?: string;
      model_call_completed?: boolean;
      failure_audit_saved?: boolean;
    };
    const message = value.message || value.error || `HTTP ${response.status}`;
    if (/invalid_api_key|incorrect api key|HTTP 401/i.test(message)) {
      return "云模型拒绝了当前凭证。请更新 Mac 钥匙串里的 DiaryOne DashScope API Key，并重启算法服务。";
    }
    if (/model_not_ready/i.test(message)) {
      return "本机算法网关已启动，但尚未配置可用的云模型凭证。";
    }
    if (value.code === "EVIDENCE_FRAME_NOT_PRESENTED_TO_MODEL" || /evidence was not presented to the model/i.test(message)) {
      return value.model_call_completed
        ? `模型引用了未实际展示的 Evidence 帧，本轮已被证据 Gate 拦截。${value.failure_audit_saved ? "失败详情、Token 与成本已经保存。" : "失败详情暂未保存。"}无需重新整理素材。`
        : "Evidence 引用没有通过校验，请重新生成。";
    }
    if (value.error === "contract_violation") {
      return value.model_call_completed
        ? `模型结果未通过证据合同校验。${value.failure_audit_saved ? "失败详情、Token 与成本已经保存。" : "失败详情暂未保存。"}无需重新整理素材。`
        : "输入或结果没有通过算法合同校验，请查看运行信息。";
    }
    if (value.error === "staged_execution_failed") {
      const stage = value.stage ? `阶段 ${value.stage}` : "当前阶段";
      return `${stage}没有完成：${message}。${value.failure_audit_saved ? "已保存本阶段之前的时间、Token 与成本记录。" : "失败审计暂未保存。"}`;
    }
    return message;
  } catch {
    return `HTTP ${response.status}`;
  }
}

export async function checkResearchServer(endpoint: string, token: string): Promise<X01Health> {
  let response: Response;
  try {
    response = await fetch(`${endpointBase(endpoint)}/health`, {
      headers: { Accept: "application/json", ...authHeaders(token) },
      cache: "no-store",
    });
  } catch {
    throw new Error("无法连接本机算法服务。请确认服务已启动，并允许当前 Web 地址访问。 ");
  }
  if (!response.ok) throw new Error(await responseError(response));
  const health = await response.json() as X01Health;
  if (health.status !== "ok" || health.schemaVersion !== "DIARY_ONE_X02_STAGED_PREVIEW_V04_1") {
    throw new Error("算法服务仍不是 V04.1 交付状态版本，请重启本机算法服务");
  }
  if (
    !health.runAuditEnabled
    || health.pipelineVersion !== "X02_STAGED_REAL_MEDIA_PREVIEW_V04_1"
    || health.previewPath !== "/x02/v0.4.1/preview"
    || health.runSidecarPath !== "/x02/v0.4.1/run-sidecar"
  ) {
    throw new Error("算法服务仍是旧版兼容桥；请重启本机算法服务以启用 X02 分阶段审计与评价保存");
  }
  if (
    !health.stagedRealMediaPreviewImplemented
    || !health.granularObservationValidation
    || !health.fieldLevelObservationDegradation
    || !health.durationAwarePhoneTestEvidence
    || !health.storylineSegmentationImplemented
    || health.storylineContractVersion !== "DIARY_ONE_X02_STORYLINE_V03"
    || health.writerSurfacePolicyVersion !== "DIARY_ONE_X02_WRITER_SURFACE_V02"
    || health.chapterMediaPolicyVersion !== "DIARY_ONE_X02_CHAPTER_MEDIA_V01"
    || !currentRuntimePolicies(health.runtimePolicies)
    || health.evaluationRunMode !== "FRESH_FULL_RUN"
    || health.crossRunSemanticCacheUsed !== false
    || health.appLibraryBundleVersion !== "DIARY_ONE_APP_LIBRARY_BUNDLE_V03"
    || !health.supportedAppLibraryBundleVersions?.includes("DIARY_ONE_APP_LIBRARY_BUNDLE_V04")
    || !health.phoneTestSpatialTransforms?.includes("ASPECT_FIT_LETTERBOX")
    || health.perceptionBatchMaxAssets !== 3
    || health.perceptionBatchMaxFrames !== 18
    || health.perceptionBatchMaxEvidenceBytes !== 4194304
    || health.perceptionSingleAssetRetryLimit !== 1
    || !health.observationSemanticContractVersion
    || !health.observationSemanticContractSHA256
    || !health.fieldDegradationContractVersion
    || !health.fieldDegradationContractSHA256
    || !health.storylineContractSHA256
  ) {
    throw new Error("算法服务尚未匹配本页要求的 Storyline V03 / Writer V02 / 完整画面 V04 与动物通用分类 V02 策略，请重启本机算法服务后重新连接");
  }
  return health;
}

export async function saveRunSidecar(
  endpoint: string,
  token: string,
  payload: RunSidecarPayload,
  options: { keepalive?: boolean } = {},
): Promise<RunSidecarResponse> {
  if (!payload.client_trace && !payload.human_review) {
    throw new Error("运行 Sidecar 至少需要客户端追踪或人工评价");
  }
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), RUN_SIDECAR_TIMEOUT_MS);
  let response: Response;
  try {
    response = await fetch(`${endpointBase(endpoint)}/x02/v0.4.1/run-sidecar`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...authHeaders(token),
      },
      body: JSON.stringify({
        schema_version: RUN_SIDECAR_SCHEMA_VERSION,
        ...payload,
      }),
      keepalive: options.keepalive,
      signal: controller.signal,
    });
  } catch {
    throw new Error("主结果保持有效，但运行补充记录暂时无法保存");
  } finally {
    clearTimeout(timeoutId);
  }
  if (!response.ok) throw new Error(await responseError(response));
  const saved = await response.json() as RunSidecarResponse;
  if (saved.status !== "saved" || saved.session_id !== payload.session_id) {
    throw new Error("运行 Sidecar 保存响应与当前测试日不匹配");
  }
  return saved;
}

export async function runResearchPreview(
  endpoint: string,
  token: string,
  bundle: EvidenceBundle,
  options: { signal?: AbortSignal; timeoutMs?: number } = {},
): Promise<X01Result> {
  const form = new FormData();
  form.append(
    "manifest",
    new Blob([JSON.stringify(bundle.manifest)], { type: "application/json" }),
    "bundle.json",
  );
  for (const frame of bundle.frames) {
    form.append(frame.frameId, frame.blob, frame.relativePath.split("/").at(-1) || `${frame.frameId}.jpg`);
  }
  const requestStartedAt = new Date().toISOString();
  const requestStartedMonotonicMs = performance.now();
  const timeoutMs = options.timeoutMs ?? RESEARCH_PREVIEW_TIMEOUT_MS;
  const abortControl = createResearchRunAbortControl(options.signal, timeoutMs);
  let response: Response | undefined;
  let result!: X01Result;
  let responseHeadersAt = "";
  let responseHeadersMonotonicMs = 0;
  let responseParsedAt = "";
  let responseParsedMonotonicMs = 0;
  try {
    response = await fetch(`${endpointBase(endpoint)}/x02/v0.4.1/preview`, {
      method: "POST",
      headers: authHeaders(token),
      body: form,
      signal: abortControl.signal,
    });
    responseHeadersAt = new Date().toISOString();
    responseHeadersMonotonicMs = performance.now();
    if (!response.ok) throw new Error(await responseError(response));
    result = await response.json() as X01Result;
    responseParsedAt = new Date().toISOString();
    responseParsedMonotonicMs = performance.now();
  } catch (caught) {
    if (abortControl.source() === "USER") throw new ResearchPreviewCancelledError();
    if (abortControl.source() === "TIMEOUT") throw new ResearchPreviewTimeoutError(timeoutMs);
    if (response) throw caught;
    throw new Error("Evidence 已生成，但无法送达本机算法服务");
  } finally {
    abortControl.cleanup();
  }
  if (!response) throw new Error("Evidence 已生成，但未收到算法服务响应");
  const unresolvedAssetCount = Array.isArray(result.unresolved_asset_ids)
    ? result.unresolved_asset_ids.length
    : -1;
  const coverageStateConsistent = result.coverage_status === "PARTIAL_UNRESOLVED"
    ? result.semantic_day_state === "UNRESOLVED_DAY" && unresolvedAssetCount > 0
    : result.coverage_status === "COMPLETE"
      && result.semantic_day_state !== "UNRESOLVED_DAY"
      && unresolvedAssetCount === 0;
  if (
    result.schema_version !== "DIARY_ONE_X02_STAGED_PREVIEW_V04_1"
    || result.validation_scope !== "STAGED_PREVIEW_ONLY"
    || result.storyline_contract_version !== "DIARY_ONE_X02_STORYLINE_V03"
    || result.writer_surface_policy_version !== "DIARY_ONE_X02_WRITER_SURFACE_V02"
    || result.chapter_media_policy_version !== "DIARY_ONE_X02_CHAPTER_MEDIA_V01"
    || !currentRuntimePolicies(result.decision_trace?.runtime_policies)
    || result.evaluation_run_mode !== "FRESH_FULL_RUN"
    || result.cross_run_semantic_cache_used !== false
    || result.trace?.input_bundle_version !== bundle.manifest.bundle_version
    || !V041_SEMANTIC_DAY_STATES.has(String(result.semantic_day_state))
    || V041_BLOCKED_DELIVERY_STATES.has(String(result.delivery_state))
    || !V041_DELIVERY_STATES.has(String(result.delivery_state))
    || (result as { _publish?: { publish_admit?: boolean } })._publish?.publish_admit === false
    || (result.coverage_status !== "COMPLETE" && result.coverage_status !== "PARTIAL_UNRESOLVED")
    || !Array.isArray(result.unresolved_asset_ids)
    || !coverageStateConsistent
    || result.timeline_basis !== "SYNTHETIC_SEQUENCE_ONLY"
    || result.timeline_date !== null
    || result.time_reliability?.capture_time_reliable !== false
    || result.time_reliability?.interval_reliable !== false
    || result.time_reliability?.timezone_reliable !== false
    || !Array.isArray(result.selected_memory_outcomes)
    || !Array.isArray(result.chapters)
    || !Array.isArray(result.ahas)
    || result.chapters.some((chapter) => (
      chapter.storyline_identity?.contract_version !== result.storyline_contract_version
      || !Array.isArray(chapter.selected_media)
      || chapter.selected_media.length < 3 || chapter.selected_media.length > 5
      || chapter.storyline_identity.one_story_gate?.validation_scope
        !== "STRUCTURE_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION"
    ))
    || !(await v041ResultContractConsistent(result, bundle))
  ) {
    throw new Error("算法结果版本不匹配");
  }
  const traceState = clientTraceByBundle.get(bundle);
  if (traceState) {
    traceState.trace.finished_at = responseParsedAt;
    traceState.trace.total_duration_ms = elapsedMs(
      traceState.pipelineStartedMonotonicMs,
      responseParsedMonotonicMs,
    );
    traceState.trace.http_status = response.status;
    traceState.trace.stages.push({
      stage: "UPLOAD_AND_SERVICE_ROUND_TRIP",
      started_at: requestStartedAt,
      finished_at: responseHeadersAt,
      duration_ms: elapsedMs(
        requestStartedMonotonicMs,
        responseHeadersMonotonicMs,
      ),
      input_bytes: bundle.evidenceBytes,
      output_bytes: null,
    });
    traceState.trace.stages.push({
      stage: "RESPONSE_PARSE",
      started_at: responseHeadersAt,
      finished_at: responseParsedAt,
      duration_ms: elapsedMs(responseHeadersMonotonicMs, responseParsedMonotonicMs),
      input_bytes: null,
      output_bytes: null,
    });
    const completedTrace = traceState.trace as ClientRunTrace;
    completedTrace.run_id = result.trace.run_id;
    bundle.clientTrace = completedTrace;
    result.trace.client_trace = completedTrace;
    void saveRunSidecar(endpoint, token, {
      session_id: result.session_id,
      client_trace: completedTrace,
    }).catch((error) => {
      console.warn(
        "Diary One run sidecar was not saved; the generated result remains valid.",
        error,
      );
    });
  }
  return result;
}
