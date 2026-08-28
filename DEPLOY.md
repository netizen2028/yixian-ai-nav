# 壹线 AI应用企业导航 — 部署指南

> 基于 [webstack-go](https://github.com/ch3nnn/webstack-go)（Golang + SQLite）定制，
> 前端 WebStackPage 风格导航 + 光年后台管理。品牌「壹线 AI应用企业导航」。

## 架构速览

| 模块 | 说明 |
|---|---|
| 后端 | Go (Gin) + SQLite（零外部依赖，单二进制） |
| 前端 | WebStackPage 风格首页（内嵌模板，编译进二进制） |
| 后台 | `/login` 登录，默认账号 `admin / admin` |
| 数据 | `storage/webstack-go.db`（分类、站点、站点配置全在库里） |
| 图标 | 企业 Logo 为 base64 PNG 存库；分类图标为 linecons 图标类 |

## 当前已预置数据

- 7 大分类：AI4S·科学智能 / AI 视频生成 / AI 音频与语音 / AI 智能体平台 / 大模型与对话 / AI 搜索与知识 / AI 办公与效率
- 63 家企业：AI4S 海外 Top 20（来源：壹线产业观察《海外 AI for Science 企业 Top 20》）+ 视频/音频/智能体/搜索/办公赛道头部企业
- 品牌：站点标题、Logo、favicon、关于页均已替换为「壹线」品牌

## 一、本地运行

```bash
# 已编译好：bin/server
./bin/server -conf config/prod.yml
# 访问 http://localhost:8000（前台）
# 访问 http://localhost:8000/login（后台，admin / admin）
```

重新编译（改了 Go 代码或模板后）：

```bash
export GOPROXY="https://goproxy.cn,direct"
go build -o bin/server ./cmd/server
```

> 注意：模板和静态资源是 `go:embed` 编译进二进制的，改模板必须重新编译。

## 二、上传 GitHub

```bash
cd webstack-go-master   # 建议改名为 yixian-ai-nav
git init
git add .
git commit -m "feat: 壹线 AI应用企业导航（webstack-go 定制版）"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

`.gitignore` 已忽略 `bin/`、`logs/`、`deploy/docker-compose/data`。
**注意：`storage/webstack-go.db` 会随仓库一起提交**——里面预置了 7 分类 63 家企业的初始数据，部署后开箱即用；如需重置，删除该文件重启服务即可自动重建。

## 三、Cloudflare 上线（两种方案）

### 方案 A：Cloudflare 免费版（静态演示，适合先跑通）

本项目是 Go 后端（Gin + SQLite），**无法直接部署到 Cloudflare Pages（仅支持静态/JS）**。免费跑通的替代路径：

1. **本地起服务 + Cloudflare Tunnel（推荐，零成本）**：本机 `cloudflared tunnel --url http://localhost:8000` 即可拿到公网 HTTPS 域名，适合演示
2. **Go → WebAssembly 编译为 Cloudflare Workers**：用 [syumai/workers](https://github.com/syumai/workers) 把 `cmd/server` 编译为 WASM 部署到 Workers（注意 SQLite 需换为 Workers KV / D1），改造工作量较大

日常生产建议直接用**方案 B（VPS + Cloudflare 代理）**或**方案 C（Docker）**。

### 方案 B：任意 VPS / 云主机 + Cloudflare 代理（推荐）

1. 在云服务器（腾讯云/阿里云轻量即可）安装 Go 或直接上传编译好的二进制：
   - 本地交叉编译 Linux 版：
     ```bash
     GOOS=linux GOARCH=amd64 go build -o webstack-go ./cmd/server
     ```
2. 上传 `webstack-go` 二进制 + `config/` 目录到服务器，执行：
   ```bash
   ./webstack-go -conf config/prod.yml
   ```
   （建议用 `systemd` 或 `nohup` 保活，监听 8000 端口）
3. Cloudflare 添加域名 → DNS 记录 A 指向服务器 IP，开启橙色云朵代理
4. Cloudflare SSL 设为 Full，域名即生效

### 方案 C：Docker（最省心）

项目自带 Dockerfile：

```bash
docker build -t yixian-ai-nav .
docker run -d -p 8000:8000 --name yixian-ai-nav -v $(pwd)/storage:/app/storage yixian-ai-nav
```

> 挂载 `storage/` 持久化数据库，避免容器重建丢数据。

## 四、后台使用

1. 访问 `/login`，账号 `admin` 密码 `admin`（**首次登录后务必在「修改密码」处改掉**）
2. **网站管理 → 网站分类**：增删分类、排序、换 linecons 图标
3. **网站管理 → 网站列表**：增删企业、上传/自动生成 Logo、编辑描述与跳转链接
4. **系统管理 → 站点配置**：改标题、关键词、Logo、favicon、备案信息、关于页

## 五、数据维护

批量更新可用 `seed_nav.py` 思路直接写 SQLite（停服后操作），或在后台逐条添加。
企业 Logo 如需换成真实 favicon：下载 favicon → 转 base64 → 后台编辑站点图标字段。
