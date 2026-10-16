# 01｜版本矩阵

## 当前固定身份

| 版本轴 | 当前值 | 说明 |
|---|---|---|
| 产品算法总流程 | Canonical V1.25 / S00–S13 | 产品层端到端定义 |
| Algorithm Candidate | Codex V1.75 | 未覆盖事实审查与 Experience Editor 候选 |
| V1.75 Candidate SHA-256 | `70442cf035a4f2f1416606b13b4b70caff41b810ed9b63be6442c08a432f127f` | 冻结运行源码收据 |
| Web Test Lab | V1.63 | 完整画面与通用主体策略时代的测试页面 |
| Web 输入 | App Library Bundle V04 | 手机素材测试输入；无可靠拍摄时间/GPS |
| HTTP 预览接口 | X02 V04.1 | 研究 Preview/Sidecar 路由 |
| Storyline Contract | V03 | Chapter 故事结构合同 |
| Web Writer Surface | V02 | V1.63 页面合同 |
| V1.75 Writer Exit | V03 | V1.75 研究档案内部出口 |
| Production | 未完成 | 不具备正式发布证据 |

## 最重要的兼容结论

`Web V1.63 + HTTP X02 V04.1` 不能自动推出 `Algorithm V1.75`。

当前 Web 仍按五项旧策略检查后端；V1.75 又增加了新的运行策略。现有后端允许加法字段，但旧测试把所有字段都当成强依赖，因此出现 1 项握手失败。正确方向是建立三层身份：

1. `algorithm_identity`：必须精确一致；
2. `required_contracts`：Web 真正依赖的合同必须兼容；
3. `capabilities`：允许向后兼容地增加。

## 状态声明词汇

| 词汇 | 含义 |
|---|---|
| `IMPLEMENTED` | 代码已经存在 |
| `TESTED` | 确定性测试通过 |
| `REAL_CHAIN_RETURNED` | 真实模型完整链有返回 |
| `HUMAN_ACCEPTED` | 逐项人工内容评价通过 |
| `INTEGRATED` | Web/API/Algorithm 身份与合同已接通 |
| `PRODUCTION_READY` | 还需独立的安全、容量、存储、SLA、设备与发布证据 |

这些状态必须分别记录，不得用一个“完成”替代。

## 升级规则

- 行为变化必须新建版本或策略 ID；
- Schema、Prompt、模型路由、输出合同变化必须有新检查点；
- 已接受历史只允许被 supersede，不得静默覆盖；
- Web 页面目标、服务 health、本轮 result 和 run audit 必须显示同源身份；
- 英文和其他海外语言需要独立文案合同，不能机械沿用中文字符上限。
