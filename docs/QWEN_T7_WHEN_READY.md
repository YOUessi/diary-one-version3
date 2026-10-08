# 真算法 T7 · 何时开跑

Expo Go **内测主链不依赖**百炼 Key。要验收真实 V1.75 记忆质量时再做下列步骤。

## 前置

1. 阿里云百炼控制台创建 API Key（华北2 北京）
2. 本机写入用户环境变量（勿提交 Git）：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-dashscope-key.ps1 -Key "sk-你的密钥"
```

3. **关掉 mock**，用 qwen 起栈：

```powershell
.\scripts\stop-dev-lite.ps1
.\scripts\start-dev-lite.ps1 -Adapter qwen
# 不要用 start-dev-lite-background（后台脚本固定 fixture+mock）
```

4. health：`mode=dev_lite`，X02 `provider`/`model` 应非 fixture。
5. 手机 Lab Demo → 人工抽查章节文案与证据（`TEST_PLAN` T7）。

## 当前状态（2026-10-02）

- 本机 `DASHSCOPE_API_KEY`：**未配置**
- 因此 T7：**⏸ 阻塞在你侧账号**，不是代码缺口
