# Branches

## fix/2026-10-23-r5-21-chapter-recovery · 2026-10-23

- 目的：按用户要求，在个人仓库 `YOUessi/diary-one-version3` 新建带日期的分支，保存R5_19—R5_21累计修复并说明范围；不更新main或既有发布分支。
- 来源：`fix/version4-chapter-recovery` / `ff240a54dbfbcf5b7e3d18ce6dfae5f733900dc0`；创建时工作区干净、无未提交修改。继续使用 `Diary_one_chapter_recovery` 工作区，原分支保留。
- 更新说明：[2026-10-23-R5_21.md](releases/version4/2026-10-23-R5_21.md)。本次只新增发布说明，算法源码与ff240a5一致；推送前重跑算法1151通过/25历史素材跳过/158子测试通过，BFF203通过/7跳过。
- 尚未部署公网或重新打包；phase_10最终审核未完成，23/24结果保持。推送后的远端提交核验记录独立存放工作区 `work_logs/2026-10-23.md`。

## fix/version4-chapter-recovery · 2026-10-23

- Source: clean `fix/version4-evidence-preflight` at `5f238f542a34b6f127907d4e7d54540a61640366` (iOS Build 5).
- Isolated checkout: `/Users/youtang/Documents/Nexleap/Diary_one_chapter_recovery`; original checkout is preserved for an already-running three-group experiment. Native worktree creation was unavailable for the parent non-repository workspace, so a Git linked worktree was used.
- Purpose: correct incomplete-input delivery/admission, retry transient model transport failures with a bounded budget, and resume validated perception work without repeating successful batches. S0 FP16 v07 and content grounding requirements remain in scope as preserved constraints.
- Status at creation: implementation and regression verification pending; no deployment, iOS rebuild, remote push, or changes to main.
- Evidence and daily work records live outside source in workspace `work_logs/2026-10-23.md` and `work_logs/evidence/`.
- Local repair verification: R5_19 algorithm 1125 passed / 25 historical-fixture skips / 158 subtests passed; BFF 203 passed / 7 runtime skips. Independent review findings were reproduced and fixed. Recovery behavior and remaining deployment boundaries: [CHAPTER_RECOVERY.md](releases/version4/CHAPTER_RECOVERY.md). No mobile code, main, public deployment or current experiment runner changes.
- R5_20 follow-up: reserve the fixed 18-image budget by provisional chapter facts and their verified frames; repair chapter boundaries independently of an invalid hero while retaining full publication validation; deduplicate retained failed StageRun records. Recorded phase_10 payload and multiframed-asset regressions added. Algorithm: 1139 passed / 25 historical-fixture skips / 158 subtests passed; independent review passed. A separately pinned, single real phase_10 run is planned; its results are not implied by offline verification.

- R5_21 follow-up from clean d75fa47: safe transport diagnostics and persistent editorial-stage responses, with unchanged semantic gates and zero current usage for reused calls. Algorithm 1151 passed / 25 historical skips / 158 subtests; BFF 203 passed / 7 skips. Independent review findings reproduced and corrected. Two byte-identical S09B real calls (SYSTEM/DIRECT) returned HTTP200 and passed local structure gates, but no final full-group result was published. Aggregate remains 23/24. Evidence: work_logs/evidence/editorial-recovery-20261023/. No deployment, push, mobile build or main changes.

## feat/main-algorithms-only · 2026-10-19

- Base: origin/main `602d2cf7f60600e7a7b9d19a87eff5fb7977c84f`; clean worktree at creation.
- Purpose: retain upstream 2.0 product implementation and port only MobileCLIP-S0 FP16 v07, native evidence timing/lifecycle fixes, R5_7 cloud Chapter/Aha/scene-aware selection and necessary wire/media integration.
- Source: the working tree of `feat/integrate-v2-preserve-v07` at `782287f4ae83680d1d86bfcb96bbd7e35bc8079d`, including uncommitted algorithm fixes; old checkout is preserved.
- Upstream UI, authentication, storage, task/import implementation and player are retained. No deployment credentials or runtime datasets are copied.
- Status: scoped migration and fresh local verification completed; content quality is not accepted. Prior-branch test results are references, not evidence of this branch passing.
- Minimal upstream compatibility exception: `sha256File.ts` passes the same bytes as `Uint8Array` to Expo 57 Crypto. The unchanged main implementation passed `ArrayBuffer` and failed in the actual iOS native bridge before enqueueing an import. UI, authentication, storage and player implementations remain upstream; 153 protected files are byte-identical to the base.
- Local validation: algorithm 980 passed / 25 missing-fixture skips, BFF 71 passed, App core 39 passed, mobile targeted 45 passed, SHA-256 compatibility 6 passed; 28 strategy / 5 pixel fixtures and 10 macOS AVFoundation cases passed. Typecheck passes; lint has 0 errors and 7 warnings. These counts describe separate suites, not a unique-test grand total.
- Real cloud verification: four fresh groups (27 videos, 53 existing verified S0 frames, 85 model calls) passed HTTP, application-contract and PostgreSQL/MinIO persistence checks. Content failures remain: hero/title/body scope mismatch, missing structural fields, rigid copy and inconsistent per-claim visual judgments.
- Actual arm64 iOS simulator Release: six previously failing cycling originals were imported through Photos, decoded with AVFoundation and selected with S0 FP16 v07 into 14 frames, uploaded and processed by qwen3.8-flash; 1 Aha was persisted and survived a cold restart. Raw original/frame SHA and selected PTS were independently verified. No Chapter survived the cloud semantic/structural gates in this run, so native Chapter display and playback were not exercised. Aha uses the upstream text-only SmallMemory UI/model.
- Local cloud activation: set the server-side, non-secret `DIARY_ONE_X02_EDITOR=product_v1` to use the migrated product editor; the upstream legacy default remains available. Provider credentials belong only in the server environment. Public `eas.json` and its BFF address are unchanged; this test Release used a separate local BFF at `http://127.0.0.1:8909` with an ordinary signed-in session.
- Not verified/deployed: public infrastructure, physical iPhone/BLE, Apple/Google OAuth, TestFlight, upgrade/sandbox relocation, development hot refresh, native Chapter playback, and the normal Redis notification path (local tests exercised upstream durable PostgreSQL recovery).
- Evidence: /Users/youtang/Documents/Nexleap/work_logs/evidence/main-algorithms-only-20261019-195307

### 2026-10-20 · Local failure testing and repair checkpoint

- Continued from local `c2b1e8b0429d55205af9d6a567384b0ee2e522d9`; no new branch. User selected this main-based branch for further testing. The migration checkpoint above remains historical: the subsequent targeted fixes intentionally change authentication/session recovery, cloud polling, task retries, local media paths, storage error handling and player cleanup. The earlier 153-file equality claim does not describe this checkpoint.
- S0 FP16 v07 weights/strategy and public `eas.json` are unchanged. No public deployment or GitHub push. The old integrated checkout remains a reference.
- Cloud R5_9 isolates invalid chapter boundaries, permits one scoped boundary/coverage repair, requires coverage references to actual published memories, and reconciles the final title with already selected verified cover candidates. It does not turn an invalid model response into an accepted memory or bypass visual review.
- Mobile repairs retain cloud jobs across transient polling faults, fence late authentication responses, persist immutable upload context for lost-ack retries, prevent concurrent runners and silent new revisions, rebase managed media after sandbox relocation, verify selected local media hashes, preserve the original SQLite write failure, and remove player calls from unmount cleanup. Their native UI acceptance is still pending.
- Current automated verification: algorithm 1004 passed / 25 missing-fixture skips / 158 subtests; BFF 71 passed; combined mobile tests 136 passed; 28 strategy and 5 pixel fixtures passed; 10 macOS AVFoundation boundary cases passed; 5 BFF URL cases passed. Typecheck passes; lint has 0 errors / 7 existing warnings. Separate suites and subtests must not be added as a single unique-case total.
- Live local infrastructure: 11 PostgreSQL/MinIO/Redis worker fault cases and 9 authenticated BFF request fault cases passed. Worker fault providers are explicit failure doubles, not model-generated successes. An abrupt worker loss after provider dispatch can still cause a later provider retry; exactly-once billing is not guaranteed.
- Real Bailian `qwen3.8-flash`: R5_8 ran 8 groups / 43 assets / 78 existing verified frames across 7 scene categories; R5_9 then ran 2 targeted groups / 14 assets / 26 frames. All 10 jobs passed HTTP, actual App contract validation, idempotent repeat submission and PostgreSQL/MinIO byte/hash persistence checks. These are samples, not the entire 734-video corpus, and not new iOS extraction. H0z and Wnie are Citywalk sources; zoo is the separate `tokyo_zoo__group_01`.
- Content remains unaccepted: zoo/museum chapters can be lost in final title/spatial review; one R5_9 Citywalk coverage proposal remains a rejected duplicate; some copy remains unnatural. A completed job is not content acceptance. Only two scenes were rerun on R5_9, so R5_8 outputs are not relabelled as R5_9 results.
- Both arm64 iOS simulator Release and Debug compile. Release contains the expected model hashes and patched native binary; the Debug implementation lives in the linked `DiaryOneDev.debug.dylib` (initial launcher-only marker check failed and has a separate correction report). Neither build result establishes native runtime success. Mac lock prevents new UI/import/retry/restart/playback/hot-refresh acceptance. The previous checkpoint's six-video simulator success is historical evidence only.
- Expo Doctor: 17/21 checks pass; remaining diagnostics cover inherited unsupported Android config, dynamic/static config warning (manual import is present), missing direct `expo-modules-core` peer declaration, and 11 SDK patch-version mismatches. Dependencies were not silently upgraded during testing. Android SDK, physical hardware, public server access and external OAuth/TestFlight credentials are unavailable.
- Current evidence: /Users/youtang/Documents/Nexleap/work_logs/evidence/main-full-fault-validation-20261019-235525. Raw failures and intermediate builds are preserved alongside final automated reports. All execution notes remain outside algorithm source in `work_logs/2026-10-20.md`.

### 2026-10-20 · Continued acceptance checkpoint

- Continued from `b46b9d25f8ec12c99db7daaee1e77b5479d9f4a1` on the same branch. The working tree was clean at the start. S0 FP16 v07 weights/strategy, public BFF configuration and the old integrated checkout are unchanged. No public deployment or push.
- Cloud R5_10 adds one bounded, same-image format repair for invalid spatial-verification schemas; it does not rescale coordinates or retry valid contradictory verdicts. Abstract scene/activity statements retain independent image review without requiring boxes for an entire venue. Parallel title subjects need not share a frame unless the title actually asserts a relationship. Rejected final Aha candidates no longer occupy published capacity.
- Reproduced a session-renewal race in both initial and resumed pipelines: a replacement session's resume request was lost while the old runner remained active. Recovery now waits for that runner to release ownership, preserves the original job/revision, discards pending recovery after sign-out, and avoids marking an active local build as interrupted.
- Cloud concept IDs are localized in the shared MemoryTag presentation component; canonical stored values are preserved. This is not a full translation of upstream screens. The upstream system-language English fallback is retained.
- Expo SDK 57 patch dependencies are aligned, dynamic config receives the normalized static config, the unsupported Android property is removed, and native-module imports use the public `expo` API. `expo-video-encoder` is pinned to validated 1.0.23. An intermediate build failed because an overlapping dependency update and pod install produced a mismatched module target; it was discarded and rebuilt after pinning. The shell-quote critical advisory was resolved; 28 transitive dependency advisories remain recorded, without a forced SDK downgrade.
- Automated verification: algorithm 1017 passed / 25 missing-private-replay skips / 158 subtests; BFF 71 passed; combined mobile 141 passed; macOS AVFoundation 10 passed; cloud-registry/display checks 22 passed. Typecheck passes; lint has 0 errors / 7 existing warnings. Expo Doctor 21/21 passes. Counts from distinct suites are not a unique-case grand total.
- All eight real sample groups were rerun on the same R5_10 frozen source: 43 assets, 78 existing S0 frames, seven scene categories, 157 Bailian qwen3.8-flash calls. Ten Chapters, seven nested highlights and one Aha were emitted. All jobs passed HTTP, actual App TypeScript contract validation, idempotent repeated submission, and PostgreSQL/MinIO byte/hash checks. Nine live BFF fault checks passed with zero intended provider calls. These are samples, not the full 734 corpus or new native extraction.
- Quality is still not accepted: zoo/museum chapters now survive, but the zoo title's afternoon implication lacks trustworthy capture-time evidence; some titles, covers and reduced bodies differ in emphasis, and some wording remains stiff. All model outputs and audit trails are preserved unchanged for review.
- Final arm64 iOS simulator Release and Debug builds both pass with identical source receipts and no source drift. Release model assets and native patch hashes/markers pass; Debug's linked implementation contains the patch marker. Release is installed on the test clone; existing SQLite records remain unchanged after installation. This does not establish runtime migration, import, playback or hot-refresh acceptance.
- Current blockers: Mac remains locked, so current native UI import/retry/playback/restart/Debug reload tests are pending. Android configuration generation passes but there is no Android SDK/runtime. Web export is unavailable without the upstream-absent react-dom/react-native-web dependencies. Private historical replay inputs, public access, physical phone/BLE and external OAuth/TestFlight conditions remain unavailable.
- Evidence: /Users/youtang/Documents/Nexleap/work_logs/evidence/continued-acceptance-20261020-004712. Daily log and test artifacts remain separate from algorithm code. Prepared native fault-response proxy is not activated; no pending real model jobs remain.

### 2026-10-20 · Native acceptance after unlock

- Continued from `af92cd2f8353b1703eb571188821158eda551b7e`, with a clean working tree at the start. The user unlocked the Mac and explicitly authorized the local test-account login. The earlier locked-screen checkpoint above is historical.
- Actual ordinary-session UI login, privacy gate, six original cycling imports, S0 FP16 v07 extraction (14 frames), accepted-submit acknowledgement loss, a subsequent polling 503, and same-job recovery were exercised. A real R5_10 Chapter was saved and independently reconciled across HTTP, PostgreSQL, MinIO and the installed application's SQLite, original bytes, selected frame PTS and model hashes.
- Native playback to the end, replay/pause/mute/seek, navigation away, local collage export, Chinese search, calendar empty state, Simulator Restart and Release/Debug upgrades were exercised. The existing Chapter and a manually saved `Native test` note survived later app installs and reloads. No external share was sent.
- Fixed a YourStory editor that could not open with the bottom-sheet library's default dynamic sizing, and changed the outer player toggle to describe its actual close action. Fixed interrupted-task recovery that left Today preparing and failed to persist changes before the startup persistence subscription existed; write errors still reach the existing retry screen.
- Large synchronous Base64 decoding and image resampling blocked development UI. File hashing and model/image byte reads now use Expo 57's native asynchronous `File.bytes()` API. Pillow fixed-point resampling retains the exact calculation order and yields with a short time budget; cancellation is checked before creating native tensors. Model bytes, prompt values, v07 selection policy and public `eas.json` remain unchanged.
- Three explicit developer-menu Reload actions were performed during active import processing; the first two were preceded by process samples containing ONNX compute stacks, while the third sampled preprocessing. No new native crash was found in these repetitions. This is bounded simulator evidence, not a guarantee for physical devices or every reload schedule. Automatic same-runtime refresh and native lifecycle fault tests remain separate evidence.
- Current automated mobile verification: 152 passing tests, 28 strategy cases and 5 Pillow reference tensors; typecheck passes and lint reports 0 errors / 7 existing warnings. Both final iOS simulator configurations compile from the same source snapshot. No private model keys were embedded. Earlier failures from the test harness's old filesystem adapters are retained in the work log, alongside corrected real-file adapters.
- Known product gaps remain: upstream full-screen localization, quality of some Chapter titles/body/cover choices, content coverage and independent Aha value. The seven-scene cloud results were not silently rewritten to appear correct. Public deployment, physical iPhone/BLE, Android runtime, external OAuth/TestFlight and unavailable private historical fixtures remain unverified.
- Evidence: `/Users/youtang/Documents/Nexleap/work_logs/evidence/continued-acceptance-20261020-004712/native-validation-report.html`. The controlled fault plan is disabled for the final Release generation check; that run's result is recorded separately on completion.

- Final native result: 12 distinct cycling videos across three real uploads produced 28 selected frames, two Chapters and one Aha. The five-video job survived an in-flight app upgrade and saved under the same job ID; the last one-video run used the final time-budgeted Release and produced the train-crossing Aha. Original SHA, frame SHA/PTS, model identity, HTTP/PG/MinIO and current SQLite publication checks all pass. The final one-video selection is byte-for-byte identical to the earlier same-input run.
- The verifier initially rejected immutable sidecar URIs from the old app sandbox after upgrade. That failure is retained; verification now permits only the exact old task/bundle root proven in pre-upgrade snapshots, while current UI SQLite paths remain subject to strict current-container checks. The relocated originals are independently hashed against the uploaded manifest.
- Duplicate import through Photos correctly reported Already imported; there remain exactly three native cloud jobs. All dispatched jobs are terminal, with only the two deliberate missing-frame/SHA fault jobs failed. The final Release/Debug receipt is `c68f5d299251aa6920aa1a724a6da023bc718e2a43f0eb07a344b35d9444af5b`; final mobile 152/152, strategy/pixel parity, typecheck and lint checks pass. No public deployment or push.
- Aha text is verified in the actual Diary UI. The upstream text-only SmallMemory model still does not carry/display the cloud-selected Aha imagery. This integration/design gap, incomplete localization and misleading technical progress copy remain explicitly open, along with content quality review.


## version3.0 · 2026-10-20

- Requested publication destination: `7tiantian/diary-one-web-testbenches`, branch `version3.0`. Neither repository's `main` is a publication target.
- Created from `feat/main-algorithms-only` at `317595e276e8be8df2700a33095f6f62a8466775`; the source worktree was clean. This branch contains the current full app/BFF/algorithm snapshot and its existing history, not changes to the testbench main tree.
- This preparation adds only this branch record. MobileCLIP-S0 FP16 v07, cloud R5_10 and previously validated application code remain identical to the source commit.
- Validation evidence is the native acceptance checkpoint above: 152 App tests, Release/Debug builds, 12 distinct cycling videos / 28 frames / 2 Chapters / 1 Aha. This is not a new run or full-corpus acceptance; content quality, complete localization and Aha image UI gaps remain open.
- Historical cloud tests reported 25 skipped test cases because private run archives were absent; this is a test-case count, not 25 missing video files.
- At preparation time, target branch does not exist remotely. SSH and existing HTTPS credentials both authenticated as `YOUessi` but repository write access was denied. Publication remains pending authorized write access; no remote main or deployment was changed.

### 2026-10-20 · Publication destination update

- The user created and selected `YOUessi/diary-one-version3` as the publication repository. The requested branch remains `version3.0`; `main` is not a push target. The earlier denied testbench publication above is preserved as history.
- Prepared from the clean local `version3.0` commit `843e3b91b9e9949a7bf68ab6845de43d25d64bf9`. This update changes only this record; product code remains identical to the validated `317595e276e8be8df2700a33095f6f62a8466775`.
- Publication transport and remote commit verification are recorded in the separate workspace daily log and evidence. Publishing this branch does not deploy the cloud services or close the known product quality gaps.

### 2026-10-20 · Public acceptance repairs after b5eb611

- Continue on `version3.0` from clean `b5eb611`; MobileCLIP-S0 FP16 v07 weights, prompts and frame selection are unchanged.
- Chapter covers now bind playback to the moment owning the exact poster URI. Missing or conflicting matches remain static. Actual Release simulator playback confirmed that the train cover plays the railway clip and the other slide plays the grassy-path clip; existing login, diary, tasks and original-media records survived the upgrade.
- “Continue without a device” goes directly to skippable preferences. Setup completion reports a connection only for real hardware, not disconnected or internal-lab state. Photo permission copy now includes diary photo/video import; affected controls have English/Chinese strings. This does not claim full localization.
- Cloud R5_11 limits final title repair to approved sentences supported by the already selected exact frames, while retaining the remaining approved body. The recorded zoo failure was replayed: its unselected goldfish title is now rejected before another image-verification call. Independent image review and final publication gates remain enforced.
- Automatic checks: mobile core/evidence/ONNX/video suites, typecheck and lint passed; algorithm full suite 1,020 passed / 25 skipped / 158 subtests passed, followed by 18 title-repair tests; BFF 71 passed. Four additional onboarding tests passed. Missing private replay archives remain unavailable.
- Eight real scene groups (43 assets / 78 existing frames) completed fresh R5_11 public generation, App contract validation and PostgreSQL/MinIO verification: 9 Chapters, 6 nested highlights, 157 provider calls. Four jobs used the real email account; after its expected daily quota rejection, four used the existing internal lab identity, clearly separated in evidence. No quota limits or counters were changed.
- The scoped X02 source update has a server-side backup and SHA receipt; the BFF source/configuration and secrets were not changed. Deployment evidence and detailed reports are outside this source repository in workspace `work_logs/evidence/acceptance-repair-20261020-224718/`.
- Remaining gaps include some narrative wording, complete Chinese UI and Aha image presentation. Android has no implementation of the required native video-decoding module and has not passed APK/runtime acceptance. Physical iPhone, signed distribution and Apple/Google OAuth remain unverified.
- Additional single-cycling control reused three hash-verified native S0 frames from one 10,010 ms clip. Fresh public R5_11 generation and server persistence passed, but produced one Chapter and no Aha, whereas the earlier R5_10 run produced an Aha. This does not prove the title-only patch caused the classification difference; it leaves the short-clip Chapter/Aha boundary unaccepted. Total this round: 9 runs / 44 assets / 81 frames / 172 model calls / 10 Chapters / 6 nested highlights / 0 Aha. A probe filename mismatch was corrected and the same immutable cloud result revalidated; no successful model output was selected by retrying.

### 2026-10-21 — version3.0 四项验收修复（未提交工作区）

- 延续 b5eb611 上的封面精确 poster→原视频映射，缺失或冲突映射不播放其他素材；没有更换 MobileCLIP-S0 FP16 v07。
- 云端新增 `final_moment_repair.py`：只对已有图像审核锚点的 HIGHLIGHT/AHA 做一次局部补救，保护已通过字段，固定引用/选图；被否定的空间参照物作为负面改稿约束，改稿后仍独立图像复核。采用 JSON-object 兼容的 `copy: null` 放弃分支，完整保留补救审计。最终编辑器为 R5_14。
- 首次设置移除模拟搜索/连接和占位系统授权；旧恢复路由也不声称已连接。未连接可继续偏好设置，云上传同意仍独立、不会自动开启。默认新安装中文，保留旧语言设置，补齐日记/日期/播放/导入/设备/补充记忆主要文案；未声称所有帮助与偏好子页全部翻译。
- 自动回归：最终算法 1038 passed / 25 skipped / 158 subtests；App 核心 111 passed；typecheck 与 lint 通过（7 个既有警告）；原生配置 4 项。历史档案缺失仍未计通过。
- 公网 R5_12 动物园 8 视频 / 14 帧 / 33 次百炼调用，2 Chapter / 1 章节内高光 / 0 独立 Aha，通过实际 App 合同、幂等、PG/MinIO 保存核对，仍有内容拦截。额度已满后没有修改额度或创建替代身份；R5_13 局部回放 7 次调用只恢复 1 条，R5_14 对相同两条历史失败锚点作 8 次真实局部请求，2 条均通过。后者不是完整 BFF 新上传/重新分组，也不是新建两个独立 Aha。
- 服务器仅更新 X02 两个源码文件，按部署覆盖层记录 SHA/备份，BFF、服务器凭据与模型资源未改。公网完整链路和最终局部算法验证范围分别记录，不混称全量通过。
- 本轮证据在工作区 `work_logs/evidence/acceptance-repair-20261020-2350/`（与源码分离）。iOS Release 新构建与界面结果见其中 `mobile/`、`simulator/` 和 `report/`；不替代真机、Android 或 TestFlight 签名验收。没有推送 main。
- 随后完成 iOS Release 实际操作：封面火车与另一页草地各播放对应原视频，播放结束/重播、中文日记/设备/补充记忆、中英文即时切换均正常。另发现账户偏好页“取消”被浮动导航遮挡，已为该入口保留底部空间并补充按钮语义；重新构建后实际点击返回通过。最终 App 源码快照 `17930051f6a65e95e0486cc0ef9dfa963de8f738c9152f5cd00d82311c7242a1`，S0 模型/提示向量字节未变；typecheck、lint 再次通过。升级与重启后原登录、中文设置、1 Chapter、原始素材及任务记录保持一致。本轮模拟器使用已保存的骑行数据，没有把界面检查计作新云端生成。

### 2026-10-21 — R5_17 文案事实范围收紧（未提交工作区）

- 延续 version3.0/base b5eb611 和之前未提交修改。普通 Chapter 只允许不改变事实的轻度润色，不以目标字数扩写；写作、编辑、修复和最终核验统一约束修饰、动作、关系、情绪与静态姿态推断。
- 失败高光/Aha 的最终补救从自由文本改为程序生成的至多16组连续原文摘句；模型只能选编号或null。禁止新增词、拼接分散片段、丢失否定/不确定或改变引用；后续独立同图像核验仍必须通过。
- 原图发现 R5_16 标题空间关系被框坐标否定、正文通用yes却被复用。R5_17新增同图像/同主体参照物的未解析关系冲突否决，撤销批准缓存，不把模型yes当作事实。R5_16自动通过但内容失败的证据保留。
- 最终算法1059 passed/25 skipped（私有历史档案缺失）/158 subtests，57项针对测试通过。小熊猫旧稿局部3次真实请求最终被拦截，NO_EXTRACTIVE_CANDIDATE；没有强行补写来提高成功数。
- 新完整公网任务ddf1b20d-f92a-46bf-850b-3234028941e9：8动物园视频/14既有S0 FP16 v07帧/22百炼调用；HTTP、实际App合同、幂等、PG与MinIO字节核对、BFF恢复后会话与结果一致均通过。实际0 Chapter/0高光/3补救Aha，内容未全部通过：后续结构输出再次漏focus_fact_ids，章节没进入正常写作，Aha“背景有些活动”等文案和静态图动作/数量仍需严格核查。
- X02部署R5_17，SHA与R5_16备份见工作区evidence/strict-copy-r515-20261021-032016/algorithm-deployment-r517.json。测试临时日额度8→20→8，保留计数，BFF源码/模型未改。此次没有新手机构建、真机测试、Git提交或推送。完整结果报告在原8838下strict-copy-r517/，失败与成功范围分开呈现。

### 2026-10-21 — R5_18结构恢复、矛盾检查与部分交付状态（未提交工作区）

- 延续version3.0/base b5eb611。完整结构修复后至多补一次缺失focus_fact_ids；只允许补丁写入缺字段，不重写选图/章节，引用仍受原合同与语义编译限制。格式/语义分流与失败原因进入审计；失败不猜编号。
- 同图/同主体参照物/同关系的相反审核结论统一拒绝；不同图与不同已解析关系不连带否决。沿用R517未解析关系检查。
- App将部分交付摘要与日记原子保存；新导入/恢复均显示部分保存及未发布提示，不因已有日记把本批次警告变成全部完成。没有把重新读取旧结果包装为内容重新生成。
- 算法1067 passed/25 skipped（缺历史素材）/158 subtests；App核心119 passed，typecheck PASS，lint0错误/7既有警告。真实动物园R517及乡村骑行历史结构各一次qwen3.8-flash字段补齐，两组均编译出1章节/2章内候选、其余字段不变；这不是重看图片或新生成文案，也不计完整公网或内容验收通过。
- 已部署云端R5_18，部署前检查活动任务为0，备份R517；公网health正常，BFF源码、配置、8次日限额和模型不变。App本次仅源码和自动回归，尚未重新打包。未提交/推送。证据：工作区work_logs/evidence/engineering-r518-20261021-044134。

### 2026-10-21 — version3.0-clean（独立干净目录，尚未提交）

- 来源：旧仓库 `Diary_one_main_algorithm` 的 `version3.0` / b5eb611 加当前未提交修改，保留 R5_18 与 S0 FP16 v07。源目录未修改。
- 目录：`/Users/youtang/Documents/Nexleap/Diary_one_version3_clean`，只复制原 `Diary-one-version2.0` 有效项目内容，根目录不再保留两套 apps/services。
- 新仓库没有远端/历史提交，不冒充上游新分支。移除已核对无调用的9个旧文件；保留类型声明、协议兼容、原生依赖和历史算法工具。依赖、原生工程与构建缓存重新生成，不复制旧运行状态或凭据。
- 本轮测试、构建与安装证据存放在工作区 work_logs/evidence/rebuild-audit-20261021-045231；详情在 docs/CODE_CLEANUP.md，完成状态以后续日志为准。

- 清理后追加：157份V1.75交接文件与当前算法目录逐文件相同，移除重复副本；X02的legacy-cgi声明缺失已修复。新环境App120/BFF71/算法1067通过，25历史素材跳过；原目录1075文件SHA无变化。Release新构建进行中，尚未记作安装通过。

- 后续核对更正清理数量：追加移除未被调用的PNG压缩字节画质代理，累计10文件/715行；当前S0的真实RGBA质量计算保持。最终构建将按此最终源码重新核对，先前构建候选不用于交付。

- 最终完成：干净目录Release构建通过，App快照 `e8b802733c9b94dbe2f2d443fdfa46504d9cd04825b3800d8f6bca310d1247d1`；模拟器覆盖安装二进制一致，旧会话/中文/日记/原片/任务保持。火车与草地轮播分别播放对应视频，冷启动保持。源码与模拟器包交付在工作区deliverables/DiaryOne-version3-clean-20261021，未签名IPA/未推送/未新发云端任务。

- 发布包最终收尾：删除一处文件尾多余空行后再次构建/安装通过，最终源码快照 `771b23c6152009c3a1b6a2ca9b3be8cb311771cf9d144a8e21b6ba23bf59c15d`（前条为功能验收构建快照）。再次核对11项持久化字段及日记启动通过；未更改运行逻辑。

### 2026-10-21 — iOS真机签名归档准备（version3.0-clean，未提交）

- 用户选择先部署iOS，安卓留后续。修复store构建的公网BFF初始化与production公共配置；preview的Bundle ID、BFF、S0 FP16 v07和R5_18不变。新安装和升级均保留云上传同意状态、用户会话和日记，不引入共享token。
- App核心126通过（新增6项）、原生配置4通过、typecheck通过、lint0错误/4原有警告。首次iphoneos arm64 Release未签名Archive编译成功，最低iOS16.4，模型/原生模块/ONNX补丁校验通过；源码快照f7ee61309390946a259996ee690a83e4bbbc117f62228c66795c60a23333b843，无构建中漂移。
- 增加Xcode本地preview环境脚本与README_build说明，写入被忽略的.xcode.env.local；幂等和实际shell环境验证通过。Xcode已打开正确工作区、签名页及Apple账号登录窗口；Team仍未选择，未创建签名IPA或提交TestFlight。签名需用户完成登录并确认有权限的开发者团队。
- 2组R5_18公网复测原始结果已保存于独立工作日志；用户随后明确停止继续公网复测，告知此前API余额不足。该余额原因属于用户提供的信息，本轮不再追加云请求或查余额；不覆盖已记录的实际成功/失败结果。
- 证据：工作区work_logs/evidence/ios-beta-20261021-1047。未签名Archive只证明真机目标编译，不替代签名、安装或真机实测；正式隐私/条款URL尚未提供。没有改服务器、改算法、选择其他模型或推送远端。


### 2026-10-21 — Gordon Xing 团队签名Archive完成（version3.0-clean，未提交）

- 用户在Xcode自行登录并选定Gordon Xing（Team ID P34R385KJ5）；Bundle ID保留com.nexleap.diaryone.dev。未把账号凭据或签名私钥写入源码，后续原生工程重新生成时仍需选择有权限的团队。
- iphoneos arm64 Release Archive已使用Apple Development签名，深度严格签名校验通过，描述文件/App身份/Apple登录权限相符；S0 FP16模型和提示资源、原生视频模块、ONNX生命周期补丁、dSYM与源码快照校验通过。当前App快照f7ee61309390946a259996ee690a83e4bbbc117f62228c66795c60a23333b843，未改变算法逻辑。
- 当前产物是开发签名的Release归档，尚未导出App Store分发IPA或上传TestFlight，不能当成任意同事iPhone可直接安装的包。正式分发须在Organizer完成相应签名导出/上传，真机运行验收与正式协议URL仍待完成。
- 本次初始命令错误地将静态Pods也设为必须签名；已撤销全局覆盖并使用各target默认签名配置后重新构建。失败日志保留，不是App源代码缺陷。全部证据保存在独立work_logs/evidence/ios-beta-20261021-1047。
- 公网复测按用户要求停止。本次不新增云调用、不提交或推送源码。后续Xcode界面由用户操作反馈，构建和产物校验由助手完成。

### 2026-10-21 — TestFlight build 2：视频导入无反馈修复（version3.0-clean，未提交）

- 用户在iPhone的build1中选中30–60秒可播放视频后相册关闭，App无提示。确认旧入口缺少错误捕获、准备阶段进度和iCloud原片下载选项；是否为用户视频的唯一根因尚未确认。
- 启用所选iCloud原片下载；增加不持久化的App内准备/检查/确认/错误面板，避免原生相册关闭期间的弹窗竞争；保留大小/时长/去重/授权限制，补取消、账号切换及重复点击边界。S0 FP16 v07、R5_18、BFF地址及服务器代码未变。
- 新增22项故障注入回归通过，App核心共148项通过；typecheck通过、lint0错误/4原有警告、原生配置4项通过。这是本地自动验证，不是新包真机通过。
- app.json buildNumber=2，重新生成原生工程，独立签名Archive构建结果与后续分发/真机状态见工作区work_logs/evidence/iphone-video-import-20261021-1250。保留build1，不自动覆盖已装TestFlight；本轮不新增云模型请求、不推送源码。

### 2026-10-21 — TestFlight build 3：照片证据尺寸修复（version3.0-clean，未提交）

- 用户真机照片导入被BFF拒绝：旧实现使用iOS不支持的Expo extent，实际比例不是3:4时仍声明768×1024；已离线复现相同错误。旧测试使用脚本标准图和原生视频测试，没有覆盖此实际照片实现。
- iOS改用ImageIO解码/方向转换、sRGB8位画布真实补边、JPEG编码与落盘回读核验；照片和视频帧共用归一化实现。JPEG截断需通过完整标记流检查，不以ImageIO部分解码成功为完整输入。原图EXIF/GPS不复制。JS对原生返回格式、尺寸和变换再次检查，取消静默拉伸兜底；S0 FP16 v07/R5_18/服务器未改。
- 旧错误包不直接重试，中文提示重新选择照片；新照片编码版本进入新导入的稳定指纹，旧保存任务仍保留原请求ID，避免不同字节碰撞旧请求。没有自动重发/更改服务器额度。
- 实际iOS模拟器运行生产编码函数，19张有效样例经像素方向/补边/尺寸检查并通过原BFF准入，5个异常按预期拒绝。使用合成图片/有效合成AI结果，未调用模型，不等于用户iPhone实测。正式App构建和最终自动回归状态见独立工作日志。
- 证据：工作区work_logs/evidence/photo-normalize-build3-20261021-1324；旧build1/build2归档保留，新build3尚待签名归档验证与用户TestFlight上传。

- build3最终完成：App核心167、视频链路21、原生配置4、iOS原生编码专项24通过；typecheck通过，lint0错误/4既有警告。iphoneos arm64签名Archive验证通过，快照71820f1126b39eb73ca5ac4a757b9330596c84a5270162754b58c3a789d03946，新原生照片方法/实际编码校验与中文错误已确认编入归档。交付在工作区deliverables/DiaryOne-iOS-beta-build3-20261021；未上传TestFlight、未做用户真机复测、未改服务器或新发模型请求。

### 2026-10-21 — Chapter/Aha 与全屏播放器 build4（version3.0-clean，未提交）

- 当前干净目录延续 build3 修复，增加首页摘要、对应帧的章内高光与原视频定位、历史 Aha 和缩略图、嵌套媒体持久化，以及完整比例视频预览、下方独立控制栏和系统全屏。保留 S0 FP16 v07 / 云端 R5_18。
- 用户要求重新打包；版本1.0.0、构建4。iphoneos arm64 Release Archive完成，Gordon Xing/P34R385KJ5签名、Apple登录权限、模型资源、旧导入修复、新播放器字段与内容、主App dSYM及源码稳定性均验证通过。App源码快照 b606be0d41ec0d67ffb94e2e9613a972c70a8218e8f95d2d63b57b86b6e859ca。
- 同一功能源码核心189项通过；打包阶段typecheck通过、lint0错误/4既有警告、原生配置4项和ONNX生命周期/补丁21项通过。25份本轮功能/测试文件与已测版本一致。模拟器已检查预览与全屏控制，退出保留进度由用户手动实测确认；原生拖动和旋转不作为自动化通过项。
- 证据：工作区 work_logs/evidence/ios-build4-20261021-1805；交付目录 deliverables/DiaryOne-iOS-beta-build4-20261021。依赖框架的完整dSYM仍缺失；没有新的真机安装、云端调用、服务器更新、远端推送或TestFlight上传。归档用于继续现有内部测试分发，不代表正式发布。

### 2026-10-22 — 版本4 GitHub 发布分支

- 目的：保存 1.0.0(4) 已打包源码及验证说明。来源：YOUessi/diary-one-version3 的 version3.0 / b5eb611，加 2026-10-21 干净目录已打包快照（923文件，App构建输入251文件）。原开发目录全为未提交文件，故发布副本置于独立 Diary_one_version4_github；未对原目录提交或重置。
- 功能源码逐文件匹配归档快照，只更新文档与发布验证记录；保留 S0 FP16 v07、R5_18。分支名为 `版本4`；不更新旧 version3.0 或其他分支。
- 本次提交及远端核验以 Git 历史和工作区 work_logs/2026-10-22.md 为准；不代表云端部署、TestFlight上传或新增真实手机验收。

### 2026-10-22 — fix/version4-evidence-preflight

- 从版本4/f5371df创建，创建时工作区干净。目的：共享上传证据预检、worker防御检查和App错误/恢复交互；保留版本4已打包快照。开发范围和验证结果以独立工作日志为准，尚不代表重新打包或上线。

- 本轮完成上传证据预检与worker防御、App错误协议/重试提示，BFF115和App199通过；typecheck通过，lint4既有警告。完整历史复盘见 docs/releases/version4/PROGRESS_AND_RETROSPECTIVE.md。这属于构建4之后的本地修复，不代表服务器部署或新TestFlight包。

- 2026-10-22后续：沿用此分支从4758258继续，开始时工作区干净。修复Dev Lite缺归属读取/损坏记录恢复、两套BFF输入指纹、额度幂等补偿与并发保护、暂存发布/原子写入/结果检查点恢复；App补503稳定错误与同任务重试提示。BFF170通过/7不适用运行时组合跳过，App201通过，类型检查通过，lint4既有警告；临时本机PostgreSQL16和MinIO真实服务6组通过，无公网/模型请求。部署兼容、仍需运维核对的双重故障边界见docs/releases/version4/JOB_RELIABILITY.md。未新建分支、推送、部署或打包，版本4交付分支未动。

- 2026-10-22发布阶段：用户授权将此修复部署、重新归档并推送该分支，不动main。以7c6d8fd部署BFF/Worker v4-7c6d8fd-build5-20261022，数据库迁移及源码比对通过；App构建号5，已签名归档并通过27项校验。线上5类异常上传及401鉴权通过且未扣次数/调用模型；本机直连公网TLS异常另列，不算真机通过。详情见docs/releases/version4/BUILD5.md。TestFlight未上传；版本4快照保持f5371df，远端推送提交以分支历史为准。
