# Diary One｜完整项目 + 单次 VLM 算法整合交付

交付：2026-11-12。这里是**完整源码项目**，不是两个ZIP简单并排：已将纯算法SDK真正接入此前完整手机 App、云端 Python 算法和 BFF，保留原有 UI、路由、数据库代码以及历史测试。

## 主要目录

- source/apps/mobile/：完整 Expo/React Native App + FP16 MobileCLIP V05/V07 抽帧 + 本地3s Motion；新算法入口 src/algorithms/index.ts。
- source/services/algorithm/algorithm/：完整 Python 算法服务及原 X02 网关；已集成单次 Direct VLM。
- source/services/bff/：原有 BFF（上传、异步Job、校验和认证）。
- source/scripts/ 与各服务 tools、fixtures、contracts：项目运行和回归所需的已跟踪文件。
- baseline_v04/：上一个完整包的旧代码快照，仅用于对比，不是实际执行路径。
- ALGORITHM_INTEGRATION_MANIFEST.json：整合的文件、修改前后SHA和来源说明。
- INTEGRATION_TEST_RESULTS.md、CHECKSUMS.sha256：验收结果与文件校验。

## 这次整合实际做了什么

1. 保留手机 MobileCLIP-S0 FP16、V05端点、V07覆盖、iOS AVFoundation解码。修正V05归一化为 ASPECT_FIT_LETTERBOX，与云端Bundle验证一致。
2. 将单次 Direct VLM Python算法接入完整项目原 X02 网关（保持同一异常类型，避免替换网关导致HTTP错误处理失效）。
3. 图库最多10张/章，通常3–8张；越界、无效索引、跨来源Clip重叠、配额滥选不允许静默修图或裁图。
4. 取消隐式的第二阶段纯文本语言修复调用；正常成功时一次全JPEG多模态请求，结构或语言失败时最多完整重试一次。
5. 新增 mobile/src/oneCallMotionAdapter.ts（服务端Frame ID、PTS、本地原10s视频→3秒Motion），不覆盖原App业务数据模型。
6. 将旧版本测试断言更新为验证新合同，补齐原完整包缺失的测试fixtures和原合同。

## 测试（已真实执行）

- 完整手机TypeScript类型检查通过；手机Node测试203通过。
- 云端算法全部pytest：1362通过、25跳过（另176项子测试通过）。
- BFF全部pytest：216通过、7跳过。
- 新增模拟真实Qwen请求与BFF来源绑定集成测试：通过。

查看 INTEGRATION_TEST_RESULTS.md。

## 快速运行

~~~bash
cd source/apps/mobile
npm ci
npm run typecheck
npm run test:core

cd ../../services/algorithm/algorithm
python3 -m pip install -e .
DIARY_ONE_X02_EDITOR=staged_v041 python3 -m pytest -q tests
python3 -m pytest -q tests/test_full_onecall_sdk_integration.py

# 真正单阶段运行需要已有后端密钥和真实JPEG Bundle:
export DIARY_ONE_X02_EDITOR=direct_vlm
export DIARY_ONE_DIRECT_VLM_MODEL=qwen3.8-flash
python3 -m diary_one_ci.direct_vlm_cli /private/day/bundle.json /private/day/result.json
~~~

历史多阶段的旧测试要求环境变量 staged_v041，**只是验证旧合同**；实际新单次算法使用 direct_vlm，默认不部署生产。

## 重要限制

- 没有包含需要授权分发的 MobileCLIP image_encoder.onnx / prompts.f32.bin。根据 apps/mobile/assets/models/mobileclip-s0-fp16/manifest.json 的SHA由授权团队受控提供。
- 3秒Live是手机App内的JPG +静音MOV动态封面，尚不是写入Apple Photos的原生配对Live Photo。
- 此包是完整源码与协议集成，不是原生iOS真机、真实Qwen质量、用户素材语义正确性或生产部署的通过证明。Chapter图文语义污染仍是上线前需评测的问题。
- 原Mac工作树未覆盖，线上未更改，API密钥和原始用户照片/视频不在ZIP中。
