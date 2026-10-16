export const RESEARCH_PREVIEW_TIMEOUT_MS = 15 * 60 * 1000;

export type ResearchRunAbortSource = "USER" | "TIMEOUT" | null;

export type ResearchRunAbortControl = {
  signal: AbortSignal;
  source: () => ResearchRunAbortSource;
  cleanup: () => void;
};

/**
 * Combines an optional user cancellation signal with a generous cloud-run
 * deadline. The current preview endpoint has no stage heartbeat, so timeout is
 * deliberately well above the normal three-to-nine-minute run window.
 */
export function createResearchRunAbortControl(
  userSignal?: AbortSignal,
  timeoutMs = RESEARCH_PREVIEW_TIMEOUT_MS,
): ResearchRunAbortControl {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error("云端运行超时必须是正数");
  }
  const controller = new AbortController();
  let abortSource: ResearchRunAbortSource = null;
  const abortFromUser = () => {
    if (abortSource !== null) return;
    abortSource = "USER";
    controller.abort(userSignal?.reason);
  };
  if (userSignal?.aborted) abortFromUser();
  else userSignal?.addEventListener("abort", abortFromUser, { once: true });
  const timeoutId = setTimeout(() => {
    if (abortSource !== null) return;
    abortSource = "TIMEOUT";
    controller.abort(new DOMException("Cloud research preview timed out", "TimeoutError"));
  }, timeoutMs);

  return {
    signal: controller.signal,
    source: () => abortSource,
    cleanup: () => {
      clearTimeout(timeoutId);
      userSignal?.removeEventListener("abort", abortFromUser);
    },
  };
}

export class ResearchPreviewCancelledError extends Error {
  constructor() {
    super("已取消本轮云端处理。素材和已生成的 Evidence 仍保留，可以重新生成。");
    this.name = "ResearchPreviewCancelledError";
  }
}

export class ResearchPreviewTimeoutError extends Error {
  constructor(timeoutMs = RESEARCH_PREVIEW_TIMEOUT_MS) {
    super(`云端处理已超过 ${Math.round(timeoutMs / 60_000)} 分钟，系统已停止等待。素材和 Evidence 仍保留，可以重新运行。`);
    this.name = "ResearchPreviewTimeoutError";
  }
}
