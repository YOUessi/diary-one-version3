# 09｜Git 命名、评审与所有权

## 仓库和分支

权威仓库：`nexleap-tech/nexleap-diary-one`。

Codex 产生的历史交付使用 `codex/` 前缀，以免与其他代理或人工实验混淆。本交付完成后，团队日常开发用职责前缀：

| 前缀 | 用途 | 示例 |
|---|---|---|
| `ai/` | 算法、Prompt、评分、模型路由 | `ai/v176-aha-relation-contract` |
| `web/` | 测试台 UI 与前端合同 | `web/v175-identity-handshake` |
| `api/` | 后端路由、任务、数据合同 | `api/v175-versioned-preview` |
| `infra/` | 部署、存储、监控、安全 | `infra/internal-eval-environment` |
| `docs/` | 纯文档与决策记录 | `docs/v175-acceptance-evidence` |
| `fix/` | 不改变产品/算法行为的缺陷修复 | `fix/web-upload-timeout-copy` |

分支名应包含一个问题，不要把算法、Web、部署和重构混进同一分支。

## Commit

建议格式：

```text
feat(ai): ...
feat(eval-web): ...
feat(api): ...
fix(web): ...
test(ai): ...
docs(handoff): ...
chore(infra): ...
```

算法行为、Web、交接文档分开提交，方便回滚和指定 reviewer。

## Tag

只有检查点和证据一致时才创建 tag：

```text
codex-handoff-algorithm-v1.75-web-v1.63-20260921
```

当前 Pack 3 和人工质量验收未完成，先使用交付候选分支/PR，不创建 Production release。

## 所有权

建议至少四个职责：

- AI owner：模型、Prompt、算法策略和真实质量；
- Web owner：测试台输入、展示、评价和浏览器性能；
- API/Cloud owner：身份合同、任务、存储、安全和成本；
- Product owner：用户体验目标与需要感性判断的取舍。

`.github/CODEOWNERS.example` 只是模板。拿到真实 GitHub 用户名/团队名后再复制为 `CODEOWNERS`，不要使用猜测账号。

## PR 规则

- 先写真实问题证据，再写修改；
- 声明明确不修改的范围；
- 算法实现、确定性测试、真实模型质量和 Production 状态分开报告；
- 涉及用户体验定义时集中提出决策，不对每个工程细节逐项索要确认；
- 未经真实素材支持的例子只能用于解释，不能直接成为运行时规则；
- 不上传用户媒体、Evidence、模型完整请求/回复或密钥。
