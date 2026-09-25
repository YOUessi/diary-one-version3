# 05｜本地运行手册

## 环境

- Python 3.9+；
- Node.js 22.13+；
- Web 依赖使用 `npm ci` 安装；
- 真实模型运行需要阿里云百炼 Key；
- 本地校验、单元测试、build 和 lint 不需要调用付费模型。

## 1. 接收 Algorithm V1.75

```bash
cd algorithm
python3 handoff_support/verify_handoff.py
PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_*.py'
```

预期：`HANDOFF_VERIFIED`；333 项发现、307 通过、26 声明性跳过、0 失败。

## 2. 接收 Web V1.63

```bash
cd apps/eval-web
npm ci
npm run build
npm run lint
npm test
```

当前基线：build/lint 通过；测试 57/58。必须保留并理解握手失败，不能删除测试来制造全绿。

## 3. 启动当前本地研究测试页

终端 A：

```bash
cd algorithm
PYTHONPATH=src python3 -m diary_one_ci.x01_server \
  --adapter qwen --host 127.0.0.1 --port 8787
```

终端 B：

```bash
cd apps/eval-web
npm run dev
```

打开 `http://127.0.0.1:3000/`。

注意：这条 HTTP 默认路径不是 V1.75 的身份保证。页面结果只能按实际 health/result identity 命名。

## 4. 校验已标准化 Bundle，不调用模型

```bash
cd algorithm
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
  python3 handoff_support/run_v1_75_bundle.py /path/to/codex_manifest.json
```

## 5. 真实 V1.75 运行

只有在素材授权和数据目的地确认后才执行：

```bash
cd algorithm
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
  python3 handoff_support/run_v1_75_bundle.py \
  /path/to/codex_manifest.json \
  --live \
  --confirm-dashscope-beijing \
  --output /secure/new/path/v1_75_run.json
```

该命令会将 Evidence 与派生文字发送到 `dashscope.aliyuncs.com` 北京接口。输出含敏感派生事实，必须保存在仓库外，且命令拒绝覆盖已有文件。

## 凭据

优先使用 macOS Keychain：

- service：`DiaryOne DashScope API Key`
- account：当前 macOS 用户

CI 或非 macOS 环境可用 `DASHSCOPE_API_KEY`。真实值不得写入 `.env.example`、代码、issue、PR 或日志。
