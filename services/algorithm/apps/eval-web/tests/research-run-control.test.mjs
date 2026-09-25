import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

const source = await readFile(new URL("../app/lib/research-run-control.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  fileName: "research-run-control.ts",
}).outputText;
const runControl = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`);
const {
  RESEARCH_PREVIEW_TIMEOUT_MS,
  createResearchRunAbortControl,
  ResearchPreviewCancelledError,
  ResearchPreviewTimeoutError,
} = runControl;

test("uses a 15-minute cloud deadline that leaves the normal 3–9 minute run window intact", () => {
  assert.equal(RESEARCH_PREVIEW_TIMEOUT_MS, 15 * 60 * 1000);
  assert.ok(RESEARCH_PREVIEW_TIMEOUT_MS > 9 * 60 * 1000);
});

test("records an explicit user cancellation separately from timeout", () => {
  const user = new AbortController();
  const control = createResearchRunAbortControl(user.signal, 1_000);
  user.abort("user asked to stop");
  assert.equal(control.signal.aborted, true);
  assert.equal(control.signal.reason, "user asked to stop");
  assert.equal(control.source(), "USER");
  control.cleanup();
});

test("records the bounded cloud deadline as timeout", async () => {
  const control = createResearchRunAbortControl(undefined, 10);
  await new Promise((resolve) => control.signal.addEventListener("abort", resolve, { once: true }));
  assert.equal(control.signal.aborted, true);
  assert.equal(control.source(), "TIMEOUT");
  assert.equal(control.signal.reason?.name, "TimeoutError");
  control.cleanup();
});

test("cleanup disarms the deadline after a completed request", async () => {
  const control = createResearchRunAbortControl(undefined, 10);
  control.cleanup();
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(control.signal.aborted, false);
  assert.equal(control.source(), null);
});

test("exposes distinct user-cancel and deadline errors", () => {
  const cancelled = new ResearchPreviewCancelledError();
  const timedOut = new ResearchPreviewTimeoutError(15 * 60 * 1000);
  assert.equal(cancelled.name, "ResearchPreviewCancelledError");
  assert.match(cancelled.message, /已取消/);
  assert.equal(timedOut.name, "ResearchPreviewTimeoutError");
  assert.match(timedOut.message, /15 分钟/);
});

test("rejects an invalid deadline before starting a request", () => {
  assert.throws(() => createResearchRunAbortControl(undefined, 0), /超时必须是正数/);
});
