# 几十～上百人内测 · 云服务器部署步骤（必做）

> **现状诚实说明**  
> 本机 **Dev Lite + trycloudflare 临时隧道** 只适合你自己 / 几个人短测。  
> **几十或上百人** 必须换成：**常开云主机（或办公室常开机）+ Docker 量产栈 + 稳定 HTTPS 域名 + 真 DashScope + SMTP OTP**。  
> 代码仓库里 compose / 配额 / OTP **已有**；缺的是 **你去买机、装 Docker、配域名、把 App 指到稳定 URL 再打 IPA**。

对照 PRD：**M2 真链路 + 多人隔离**（每人 OTP → 各自 chapter），不是 App Store 正式上架。

---

## 0. 目标架构

```text
每人 iPhone (TestFlight)
  → https://bff.你的域名  (443，稳定，不随重启变)
  → 云主机 Docker：BFF + Worker + Postgres + Redis + MinIO
  → 同机（或旁路）X02 :8787
  → 一把 DASHSCOPE_API_KEY → 通义
  → job 成功 → 各自 Diary Chapter
```

| 人数体感 | 机器建议 | Worker |
|----------|----------|--------|
| ~20–50 | 2～4 核 / 8GB+ / 80GB SSD | `WORKER_MAX_CONCURRENT=1～2` |
| ~50–100+ | 4～8 核 / 16GB+ / 盘要够 MinIO | `WORKER_MAX_CONCURRENT=2～4`，日配额别开太大 |

默认每用户每天 **8** 次 day-revision（`DAY_REVISION_DAILY_LIMIT`），超限 429，避免把机器打爆。

---

## 1. 买云主机 · 手把手（推荐阿里云）

### 1.1 去哪儿买

| 选项 | 入口 | 何时选 |
|------|------|--------|
| **推荐：阿里云 ECS** | https://www.aliyun.com → 登录 → **云服务器 ECS** → 立即购买 | 国内测试员多、和通义同生态 |
| 备选：腾讯云 CVM | https://cloud.tencent.com → 云服务器 | 你已有腾讯云账号时 |
| 不要用 | 仅「轻量应用服务器」里乱选 Windows | 本教程按 **Linux Ubuntu** |

个人/企业账号实名后才能买。没有账号：先注册并完成实名。

### 1.2 买什么规格（内测够用）

打开「自定义购买」时按下面勾（名称因页面改版可能略有出入）：

| 项 | 选什么 |
|----|--------|
| 付费 | **包年包月**（先买 1 个月即可） |
| 地域 | **华东 1（杭州）** 或离你最近；之后不要随便换地域 |
| 实例 | **计算型/通用型**，**4 vCPU / 8 GiB**（五十人左右）；上百人再升 8核16G |
| 镜像 | **Ubuntu 22.04 64 位**（公有镜像） |
| 系统盘 | **ESSD** ≥ **80 GB** |
| 带宽 | **按固定带宽 ≥ 5 Mbps**（人多改 10～20） |
| 公网 IP | **分配**（必须有，否则手机到不了） |
| 安全组 | 新建或选用；规则见下节 |
| 登录 | **密钥对**（更安全）或自定义密码；密钥下载 `.pem` 好好保存 |

结账开通后，在 ECS 控制台记下：

```text
公网 IP：______________
用户名：ubuntu（Ubuntu 镜像默认）
密钥文件路径 或 密码：______________
```

### 1.3 安全组规则（必配）

ECS → 该实例 → 安全组 → 配置规则 → **入方向** 添加：

| 端口 | 协议 | 授权对象 | 用途 |
|------|------|----------|------|
| 22 | TCP | 建议「你当前家/公司公网 IP/32」；临时可 `0.0.0.0/0` | SSH |
| 80 | TCP | `0.0.0.0/0` | HTTP（申请证书 / 跳转） |
| 443 | TCP | `0.0.0.0/0` | HTTPS（App 访问） |

**不要**对公网开放 **8790**。

### 1.4 本步完成标准（发给我继续）

你回复这 4 行即可进入「域名」下一步：

```text
厂商：阿里云 / 腾讯云
公网 IP：x.x.x.x
系统：Ubuntu 22.04
SSH：密钥已下 / 或已设密码（不要把密码发在聊天里）
```

可选折中：不买云、办公室 Windows **24h 开机** + Cloudflare Named Tunnel——仍建议先有一个域名（§2）。

---

## 2. 买域名 + 解析 · 手把手

### 2.1 去哪儿买域名

| 选项 | 入口 | 说明 |
|------|------|------|
| **阿里云万网** | https://wanwang.aliyun.com 或 控制台 → 域名 | 和 ECS 同账号最省事 |
| 腾讯云 DNSPod | https://dnspod.cloud.tencent.com | 云在腾讯时用 |
| Cloudflare Registrar | https://www.cloudflare.com | 海外域名；国内备案策略另说 |

内测建议：买一个便宜的 **`.com` / `.cn`**（例如 `diaryone-beta.com`），一年即可。  
**国内大陆机房 + 网站备案**：若只用 API（无网页），部分场景可先用 HTTPS API；正式对外网页需按当地法规备案。内测 API 常见做法：

- 域名在阿里云购买并完成实名；
- 解析到 ECS；后面用 Caddy 自动 HTTPS。

### 2.2 购买后做什么

1. 控制台 → **域名** → 你的域名 → **解析**。  
2. 添加记录（云主机 IP 用 §1 记下的公网 IP）：

| 主机记录 | 类型 | 记录值 | 说明 |
|----------|------|--------|------|
| `bff` | **A** | `你的ECS公网IP` | 得到 `bff.你的域名.com` |
| `@`（可选） | A | 同上 | 根域名，可不配 |

TTL 默认 10 分钟即可。

3. 等 5～30 分钟后，在你 **Windows 电脑** PowerShell 测：

```powershell
nslookup bff.你的域名.com
# 应看到 ECS 公网 IP
```

### 2.3 本步完成标准

```text
域名：________.com
子域：bff.________.com
nslookup 已指向公网 IP：是 / 否
```

（证书要等后面装 Caddy 再申请；现在先保证解析对。）

---

## 3. 云主机装 Docker（SSH 上机）

```bash
# Ubuntu 示例
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git curl
sudo usermod -aG docker $USER
# 重新登录 SSH 后：
docker version
docker compose version
```

---

## 4. 把 BFF 工程放到云主机

任选其一：

**A. git clone（若仓库可拉）**

```bash
cd ~
git clone <你的 diary-one 仓库 URL>
cd diary-one/services/bff
```

**B. 本机打包上传（Windows → 云）**

在你电脑：

```powershell
cd E:\AI耳机\diary-one\services\bff
# 不要上传 .env 里的旧密钥到公开处；到云上再写新 .env
```

用 scp / 宝塔 / SFTP 把 `services/bff`（含 `docker-compose.yml`、`docker-compose.quality.yml`、代码）传到云主机目录，例如 `/opt/diary-one/services/bff`。

---

## 5. 配置 `.env`（云上 · 关键）

```bash
cd /opt/diary-one/services/bff   # 按你的实际路径
cp .env.example .env
nano .env   # 或 vim
```

**必填（示例，换成你的真值）：**

```env
ALLOW_MOCK_PREVIEW=false
API_TOKEN=<本机生成的长随机串，勿用 dev-token，勿发给测试员>
EXPOSE_OTP_IN_RESPONSE=false

DASHSCOPE_API_KEY=sk-你的通义Key

SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=你的邮箱@qq.com
SMTP_PASSWORD=邮箱授权码
SMTP_FROM=你的邮箱@qq.com
SMTP_SECURITY=ssl

DAY_REVISION_DAILY_LIMIT=8
DAY_REVISION_MAX_INFLIGHT=2
WORKER_MAX_CONCURRENT=2

# compose 里 Worker 连宿主机 X02（Linux 云主机常用 host-gateway）
X02_BASE_URL=http://host.docker.internal:8787
```

Windows 上也可先跑（再把生成的 `.env` 拷到云，**建议云上重新随机 API_TOKEN**）：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\set-smtp.ps1 ...
.\scripts\set-dashscope-key.ps1
.\scripts\prepare-multiuser-beta.ps1 -HardenEnv
```

---

## 6. 启动 Docker 量产栈 + X02

### 6.1 起 BFF / Worker / PG / Redis / MinIO

```bash
cd /opt/diary-one/services/bff
docker compose -f docker-compose.yml -f docker-compose.quality.yml --env-file .env up -d --build
docker compose ps
curl -sS http://127.0.0.1:8790/health
# 必须：allow_mock_preview == false
```

若 Linux 访问 `host.docker.internal` 失败，在 compose 里给 bff/worker 加：

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

（质量 compose 若已带可跳过。）

### 6.2 同机起 X02（千问 · 统一一把 Key）

X02 不在 Docker 里时，在**宿主机**用项目既有方式起（把仓库里 `start-x02` / x01_server 对应环境迁到 Linux，或暂时在同 VPC 另一台跑）。

最低要求：

```bash
# 宿主机环境
export DASHSCOPE_API_KEY=sk-...
# 按仓库文档启动监听 :8787 的 X02（adapter=qwen）
curl -sS http://127.0.0.1:8787/health
# modelReady / provider 应为真模型，不是 fixture
```

**纪律：** 全员共用这一把 Key；**不要**写进 App / eas.json。

---

## 7. HTTPS 反代到 8790

### 方案 A · Caddy（简单）

```bash
sudo apt install -y caddy
sudo tee /etc/caddy/Caddyfile <<'EOF'
bff.你的域名 {
  reverse_proxy 127.0.0.1:8790
}
EOF
sudo systemctl reload caddy
```

### 方案 B · Cloudflare Named Tunnel（无开 80/443 也可）

1. Cloudflare Zero Trust → Tunnel → 安装 `cloudflared` 到云主机  
2. Public hostname：`bff.你的域名` → `http://127.0.0.1:8790`  
3. 隧道服务设为 systemd 常驻  

验证：

```bash
curl -sS https://bff.你的域名/health
# allow_mock_preview: false
# x02 reachable / smtp_configured 等按实现字段核对
```

---

## 8. 把 App 指到**稳定**公网 URL（再打 IPA）

编辑本机：

`E:\AI耳机\diary-one\apps\mobile\eas.json` → `build.preview.env`：

```json
"EXPO_PUBLIC_DEV_BFF_URL": "https://bff.你的域名",
"EXPO_PUBLIC_DEV_BFF_TOKEN": "",
"EXPO_PUBLIC_INTERNAL_BETA": "1"
```

**不要**再写 trycloudflare 临时域名（一变全员死）。

然后：

```powershell
cd E:\AI耳机\diary-one\apps\mobile
npx eas-cli login
npx eas-cli init
npx eas-cli build --profile preview --platform ios
# ASC 填 ascAppId 后
npx eas-cli submit --profile preview --platform ios
```

域名以后若改了 → 必须 **重新 eas build**。

---

## 9. 上线前自检清单（几十人放行）

```text
□ https://bff.域名/health → allow_mock_preview=false
□ SMTP 任意测试邮箱能收到 OTP
□ 邮箱 A / B 各 Import 一次 → 各有自己的 Chapter，互不覆盖
□ 同一账号连传超日限 → 429，机器不卡死
□ API_TOKEN 未发进测试群；测试员只用 OTP
□ 云主机磁盘监控（MinIO 素材）
□ X02 / Docker compose 设开机自启（systemd / restart: always）
```

---

## 10. 和「本机临时隧道」对比（为什么你觉得还没完成）

| | 本机 Dev Lite + trycloudflare | 本方案（云 / Named Tunnel） |
|--|-------------------------------|----------------------------|
| 人数 | 几人、短窗口 | 几十～上百（配合配额） |
| URL | **每次变** → 要重打 IPA | **固定域名** |
| 关机 | 全员挂 | 云主机常开 |
| 数据 | 本机文件态 | Postgres + Redis + MinIO |
| 并发 | 弱 | Worker 可调 |

仓库脚本入口：

```powershell
cd E:\AI耳机\diary-one\services\bff
.\scripts\prepare-multiuser-beta.ps1 -HardenEnv   # 生成/硬化 .env
.\scripts\prepare-multiuser-beta.ps1 -Up          # 本机 Docker（需 Desktop Running）
# 云上等价：docker compose -f docker-compose.yml -f docker-compose.quality.yml --env-file .env up -d --build
```

更多原设计说明：`docs/INTERNAL_BETA_FULL_GUIDE.md` 阶段 C；`services/bff/docs/DEPLOY.md`。

---

## 11. 你今天建议怎么排期

| 时段 | 做什么 |
|------|--------|
| 1h | 买云主机 + 安全组 + SSH 通 |
| 1h | 域名 DNS + Caddy/Tunnel HTTPS |
| 1–2h | 上传 bff、写 `.env`、compose up、起 X02、health 绿 |
| 30min | 本机改 `eas.json` 稳定 URL → `eas build` |
| 之后 | TestFlight 加人；用 2 个邮箱验收隔离 |

**没有云主机时**：只能继续「办公室 PC 常开 + Named Tunnel 固定域名」——步骤同 §7B + §5–6（Docker 在 Windows + WSL2），**不要**用会变的 quick tunnel 发几十人包。
