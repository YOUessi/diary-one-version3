import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import test from "node:test";
import ts from "typescript";

// Reuse the adjacent algorithm's existing interface fixture. No real images,
// semantic counterexamples, cloud requests, or quality scores are created here.
const algorithmRoot = fileURLToPath(new URL("../../diary-one-cloud-intelligence/", import.meta.url));
const fixture = JSON.parse(execFileSync("python3", ["-B", "-c", `
import base64
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from test_x02 import MissingAhaReferenceGateway
from test_codex_full_frame_bundle import make_x02_bundle_v04
from test_codex_x02_chapter_media import MediaGateway
import diary_one_ci.x02 as pipeline
from diary_one_ci.x02 import run_x02
from diary_one_ci.x01_server import X01RequestHandler

gateway = MediaGateway()
health = {}
handler = SimpleNamespace(
    path="/health", stage_gateway=gateway, max_assets=240,
    max_sidecar_bytes=2097152, _origin_allowed=lambda: True,
    _authorized=lambda: True, _json=lambda status, payload: health.update(payload),
)
X01RequestHandler.do_GET(handler)
recorded = json.loads(Path("tests/fixtures/codex_writer_exit_real.json").read_text())
aha_memories = [m for m in recorded["contexts"]["v151"]["memories"] if m["memory_type"] == "AHA"]
long_fact = aha_memories[1]["facts"][0]["text"]

class RecordedFactGateway(MediaGateway):
    # Transport fixture, not a claim that these frames depict the recorded fact.
    def _writer(self, context):
        output = super()._writer(context)
        by_id = {m["candidate_id"]: m for m in context["memories"]}
        for item in output["ahas"]:
            item["text"] = by_id[item["candidate_id"]]["facts"][0]["text"]
        return output

with tempfile.TemporaryDirectory(prefix="codex-web-contract-") as temporary:
    manifest_path = make_x02_bundle_v04(Path(temporary))
    manifest = json.loads(manifest_path.read_text())
    result = run_x02(manifest_path, gateway)
    plan = {index: "HISTORIC_TOWN_WALK" for index in range(5)}
    plan[3] = "CAFE_STOP"
    overrides = {3: {"fact_text": long_fact}}
    long_result = run_x02(manifest_path, RecordedFactGateway(semantic_plan=plan, observation_overrides=overrides))
    with patch.object(pipeline, "_deterministic_writer_fallback", return_value=({"chapters": [], "ahas": []}, [])):
        blocked_result = run_x02(manifest_path, MissingAhaReferenceGateway(plan, observation_overrides=overrides))
    frames = [{
        "frame_id": frame["frame_id"],
        "bytes_base64": base64.b64encode(
            (manifest_path.parent / frame["relative_path"]).read_bytes()
        ).decode(),
    } for asset in manifest["assets"] for frame in asset["frames"]]
    print(json.dumps({"health": health, "manifest": manifest, "frames": frames, "result": result,
        "long_result": long_result, "blocked_result": blocked_result,
        "tolerance_lines": [item["text"] for item in next(c for c in recorded["cases"] if c["case_id"] == "v151_attempt_2")["output"]["ahas"]]}))
`], {
  cwd: algorithmRoot,
  env: { ...process.env, PYTHONPATH: `${algorithmRoot}/src:${algorithmRoot}/tests` },
  encoding: "utf8",
  timeout: 30_000,
  maxBuffer: 4 * 1024 * 1024,
}));

async function compiledModuleUrl(name, dependencies = {}) {
  const source = await readFile(new URL(`../app/lib/${name}.ts`, import.meta.url), "utf8");
  let compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
    fileName: `${name}.ts`,
  }).outputText;
  for (const [dependency, url] of Object.entries(dependencies)) {
    compiled = compiled.replaceAll(`"./${dependency}"`, JSON.stringify(url));
  }
  return `data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`;
}

const media = await import(await compiledModuleUrl("media-evidence", {
  "result-contract": await compiledModuleUrl("result-contract"),
  "research-run-control": await compiledModuleUrl("research-run-control"),
  "codex-runtime-policy": await compiledModuleUrl("codex-runtime-policy"),
}));
const review = await import(await compiledModuleUrl("codex-writer-review"));
const findings = await import(await compiledModuleUrl("contract-findings", {
  "result-contract": await compiledModuleUrl("result-contract"),
}));
const frameBytes = new Map(fixture.frames.map((frame) => [frame.frame_id, frame.bytes_base64]));
const frames = fixture.manifest.assets.flatMap((asset) => asset.frames.map((frame) => ({
  frameId: frame.frame_id,
  canonicalOffsetMs: frame.canonical_offset_ms,
  windowIndex: frame.window_index,
  windowCount: frame.window_count,
  sampleRole: frame.sample_role,
  sourceTimestampMs: frame.source_timestamp_ms,
  relativePath: frame.relative_path,
  sha256: frame.sha256,
  blob: new Blob([Buffer.from(frameBytes.get(frame.frame_id), "base64")], { type: "image/jpeg" }),
})));
const bundle = {
  manifest: fixture.manifest,
  frames,
  evidenceBytes: frames.reduce((sum, frame) => sum + frame.blob.size, 0),
};

test("normalization keeps every source edge for the real run's source dimensions", async (t) => {
  // Dimensions from the Sep 4 pack-2 manifest. No fabricated image semantics.
  const sizes = [[2276,1280], [1440,960], [4624,2600], [2600,4624], [720,1280], [721,1280], [3840,2160]];
  let draw;
  const canvas = {
    width: 0, height: 0,
    getContext: () => ({ fillRect() {}, drawImage(...args) { draw = args; } }),
    toBlob(callback) { callback(new Blob(["transport-only"])); },
  };
  const previousDocument = Object.getOwnPropertyDescriptor(globalThis, "document");
  Object.defineProperty(globalThis, "document", { value: { createElement: () => canvas }, configurable: true });
  t.after(() => {
    if (previousDocument) Object.defineProperty(globalThis, "document", previousDocument);
    else delete globalThis.document;
  });
  for (const [width, height] of sizes) {
    const source = {};
    await media.drawNormalized(source, width, height);
    assert.equal(draw.length, 5, "draw the entire source, without a crop rectangle");
    assert.equal(draw[0], source);
    const [, x, y, w, h] = draw;
    assert.ok(x >= -1e-8 && y >= -1e-8);
    assert.ok(x + w <= 768 + 1e-8 && y + h <= 1024 + 1e-8);
    assert.ok(Math.abs(w / h - width / height) < 1e-8);
    assert.ok(Math.abs(2*x+w-768) < 1e-8 && Math.abs(2*y+h-1024) < 1e-8);
    assert.ok(Math.abs(w-768) < 1e-8 || Math.abs(h-1024) < 1e-8);
  }
  assert.throws(() => media.drawNormalized({}, 0, 1280), /尺寸无效/);
});

function respondWith(t, payload) {
  return t.mock.method(globalThis, "fetch", async () => Response.json(payload));
}

test("current server health passes the Web version handshake; old versions do not", async (t) => {
  const fetch = respondWith(t, fixture.health);
  assert.equal((await media.checkResearchServer("http://127.0.0.1:8787", "")).storylineContractVersion,
    "DIARY_ONE_X02_STORYLINE_V03");
  for (const staleVersion of [
    { supportedAppLibraryBundleVersions: ["DIARY_ONE_APP_LIBRARY_BUNDLE_V03"] },
    { phoneTestSpatialTransforms: ["CENTER_CROP_ASPECT_FILL"] },
    { storylineContractVersion: "DIARY_ONE_X02_STORYLINE_V02" },
    { writerSurfacePolicyVersion: "DIARY_ONE_X02_WRITER_SURFACE_V01" },
    { chapterMediaPolicyVersion: undefined },
    { runtimePolicies: undefined },
    ...Object.keys(fixture.health.runtimePolicies).map((key) => ({
      runtimePolicies: { ...fixture.health.runtimePolicies, [key]: "OLD_POLICY" },
    })),
  ]) {
    fetch.mock.mockImplementation(async () => Response.json({ ...fixture.health, ...staleVersion }));
    await assert.rejects(media.checkResearchServer("http://127.0.0.1:8787", ""), /Storyline V03 \/ Writer V02/);
  }
});

test("current Python pipeline output passes the real Web response path with empty optional focus", async (t) => {
  const fetch = respondWith(t, fixture.result);
  assert.ok(fixture.result.chapters.length > 0, "the interface test must cover a Chapter, not only an empty result");
  assert.equal(fixture.result.chapters[0].storyline_identity.focus_code, "");
  assert.equal(fixture.result.chapters[0].selected_media.length, 3);
  assert.equal(fixture.result.chapter_media_policy_version, "DIARY_ONE_X02_CHAPTER_MEDIA_V01");
  const result = await media.runResearchPreview("http://127.0.0.1:8787", "", bundle);
  assert.deepEqual(result, fixture.result);
  const [url, request] = fetch.mock.calls[0].arguments;
  assert.equal(url, "http://127.0.0.1:8787/x02/v0.4.1/preview");
  assert.equal(request.method, "POST");
  assert.equal([...request.body.keys()].length, frames.length + 1);
});

test("Web rejects a stale result or stale Chapter contract instead of relabelling it as current", async (t) => {
  const fetch = respondWith(t, fixture.result);
  for (const change of [
    (result) => { result.storyline_contract_version = "DIARY_ONE_X02_STORYLINE_V02"; },
    (result) => { result.trace.input_bundle_version = "DIARY_ONE_APP_LIBRARY_BUNDLE_V03"; },
    (result) => { result.writer_surface_policy_version = "DIARY_ONE_X02_WRITER_SURFACE_V01"; },
    (result) => { delete result.chapter_media_policy_version; },
    (result) => { delete result.decision_trace.runtime_policies; },
    (result) => { delete result.decision_trace.runtime_policies.subject_granularity; },
    (result) => { result.decision_trace.runtime_policies.writer_exit = "DIARY_ONE_X02_WRITER_EXIT_V01"; },
    (result) => { result.chapters[0].selected_media = result.chapters[0].selected_media.slice(0, 2); },
    (result) => { result.chapters[0].storyline_identity.contract_version = "DIARY_ONE_X02_STORYLINE_V02"; },
    (result) => { delete result.chapters[0].storyline_identity.one_story_gate.validation_scope; },
  ]) {
    const stale = structuredClone(fixture.result);
    change(stale);
    fetch.mock.mockImplementation(async () => Response.json(stale));
    await assert.rejects(media.runResearchPreview("http://127.0.0.1:8787", "", bundle), /算法结果版本不匹配/);
  }
});

test("actual Python long-copy result remains visible with review, not a length block", async (t) => {
  respondWith(t, fixture.long_result);
  const result = await media.runResearchPreview("http://127.0.0.1:8787", "", bundle);
  assert.ok(result.ahas.length > 0);
  const original = structuredClone(result);
  for (const aha of result.ahas) {
    assert.ok(findings.visibleLength(aha.story) > 24);
    assert.equal(review.ahaLengthReview(aha, result)?.label, "偏长，待评价");
  }
  const checked = findings.evaluateLatestContract(result);
  assert.ok(checked.some((item) => item.code === "AHA_LENGTH_OVER_TOLERANCE_REVIEW" && item.severity === "REVIEW"));
  assert.ok(!checked.some((item) => item.code === "AHA_MOMENT_LINE_LENGTH"));
  assert.deepEqual(result, original, "rendering/review must not edit the returned prose");
});

test("new single-pass Writer failure stays diagnostic instead of becoming an invalid response", async (t) => {
  respondWith(t, fixture.blocked_result);
  const result = await media.runResearchPreview("http://127.0.0.1:8787", "", bundle);
  assert.equal(result.delivery_state, "READY_WITH_ITEM_BLOCKS");
  assert.equal(result.ahas.length, 0);
  assert.ok(result.decision_trace.blocked_memories.some((item) =>
    item.reason_code === "NO_VALID_WRITER_OUTPUT_AFTER_SINGLE_PASS_AND_LOCAL_FALLBACK"));
});

test("recorded 20/20/24-character lines have no current length warning; old results retain old policy", () => {
  assert.deepEqual(fixture.tolerance_lines.map(findings.visibleLength), [20, 20, 24]);
  for (const line of fixture.tolerance_lines) {
    const result = structuredClone(fixture.long_result);
    result.ahas[0].story = line;
    const checked = findings.evaluateLatestContract(result);
    assert.ok(!checked.some((item) => ["AHA_MOMENT_LINE_LENGTH", "AHA_LENGTH_OVER_TOLERANCE_REVIEW"].includes(item.code)));
  }
  const old = structuredClone(fixture.long_result);
  old.ahas[0].story = fixture.tolerance_lines[2];
  delete old.decision_trace.runtime_policies;
  assert.ok(findings.evaluateLatestContract(old).some((item) => item.code === "AHA_MOMENT_LINE_LENGTH" && item.severity === "BLOCK"));
  assert.equal(findings.visibleLength(" 木 质 \n"), 2);
});

test("Aha note never attaches a rejected draft, another candidate, or another surface source", () => {
  const result = structuredClone(fixture.long_result);
  const aha = result.ahas[0];
  const final = result.decision_trace.writer_items.find((item) => item.candidate_id === aha.candidate_id
    && item.validation_status === "PASSED" && item.validation_scope);
  assert.ok(final);
  for (const wrong of [
    { ...final, validation_status: "REJECTED" },
    { ...final, candidate_id: "another-candidate" },
    { ...final, surface_source: "DETERMINISTIC_GROUNDED_FALLBACK" },
    { ...final, validation_scope: undefined },
    { ...final, writer_exit_policy_version: "DIARY_ONE_X02_WRITER_EXIT_V01" },
  ]) {
    result.decision_trace.writer_items = [wrong];
    assert.equal(review.ahaLengthReview(aha, result), null);
  }
  result.decision_trace.writer_items = [final, { ...final, validation_status: "REJECTED" }];
  assert.equal(review.ahaLengthReview(aha, result)?.label, "偏长，待评价");
  result.decision_trace.writer_items = [{ ...final, length_review_required: false, length_status: "WITHIN_TOLERANCE", quality_flags: [] }];
  assert.equal(review.ahaLengthReview(aha, result), null);
});
