# Diary One App · 当前后端接入

当前产品代码入口是本仓库的 `apps/mobile`，云端位于 `services/bff` 和 `services/algorithm/algorithm`。

| 能力 | 当前模块 | 实现边界 |
|---|---|---|
| 邮箱验证码登录 | `authRemoteService` | 公网 BFF 校验 OTP 并签发会话；已移除不使用的本地数字验证码占位实现 |
| Apple / Google | `SignInScreen` / `authRemoteService.completeOAuthLogin` | 使用原生/远端登录链路；公司账号配置与真机验收仍另行进行 |
| 上传与结果保存 | `productionCloudService`、`runPipeline` | BFF job、结果合同验证、日记与任务状态原子保存 |
| 内容算法 | `services/algorithm/algorithm` | qwen3.8-flash，R5_18；部分内容拒绝时保持部分交付提示 |
| 导出 / 删本地 | `privacyService` | 导出及本地清理流程 |
| 真设备连接 | `deviceSyncService` | 硬件 SDK 尚未接入；不伪造在线状态 |

公网入口为 `https://bff.diary.luxe`。App 不存储服务端 DashScope、SMTP 或 API_TOKEN。Consumer 构建禁用 Lab/Research；留存的实验与兼容代码不代表开放了这些产品功能。
