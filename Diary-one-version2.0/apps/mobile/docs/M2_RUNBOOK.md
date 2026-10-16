# M2 联调手册 · App + BFF + X02

目标：手机一次 **相册导入 → Production BFF → Worker → X02 → Diary 刷新**。

## 1. 起基础设施与后端

```powershell
cd E:\AI耳机\diary-one-server
copy .env.example .env
docker compose up -d --build
docker compose run --rm bff python -m shared.db_init
```

确认：

- `http://localhost:8790/health` → `{"status":"ok",...}`
- PC 上 X02 研究服务已监听 **8787**（`nexleap-diary-one` handoff runbook）

## 2. 配置手机 App

开发包（`__DEV__`）：

1. **Account → Evidence pipeline lab**
2. **Cloud processing target** → **Production BFF**
3. **Production API** → `http://<电脑局域网IP>:8790`
4. **Token** → `dev-token`（与 server `.env` 的 `API_TOKEN` 一致）
5. （可选）Research API 仍可用于绕过 BFF 直连 X02 对比

## 3. 跑一条记忆

1. **Import from photo library** 选 1+ 张图/短视频  
2. 回到 **Diary** → 看 **Cloud processing** 横幅  
3. 等待 Worker 调 X02（可能 **3–9 分钟**）  
4. 成功：Today 更新、出现新 Chapter / Small Memory  
5. 失败：任务列表错误 + Today 可能 **PARTIAL**（不伪装空日）

## 4. Device 页自检

**Services** 卡片：

- Production API → Reachable（若 BFF 已起）
- Research API → 仅在你配置了 8787 时 Reachable

## 5. 常见问题

| 现象 | 处理 |
|------|------|
| 401 on day-revisions | App Token 与 `API_TOKEN` 不一致 |
| Job 一直 pending | Worker 未起：`docker compose logs worker` |
| X02 connection refused | `.env` 里 `X02_BASE_URL`；Docker Worker 用 `host.docker.internal:8787` |
| 手机连不上 8790 | 防火墙放行；URL 用局域网 IP 非 localhost |

## 6. 仓库对照

- 前端：`diary-one-app/`
- 后端：`diary-one-server/`
- 算法：`nexleap-diary-one/`
