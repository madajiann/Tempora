# Tempora

为长时间自主任务而生的编码 Agent —— 轻量桌面客户端。

**Tempora = React SPA（前端） + Tauri 壳（Windows 桌面） + Go 内核（本地服务）** 三层架构，
把原本 Electron 打包的桌面端瘦身成约 38MB 的安装包：冷启动更快、内存更省、体积更小。

- 官网：<https://tempora.yomm.cc>
- 仓库：<https://github.com/madajiann/Tempora>

---

## 架构

| 层 | 目录 | 说明 |
|---|---|---|
| 前端 SPA | `app/frontend` | React + Vite，官方 UI 1:1 保留 |
| 桌面壳 | `shell/src-tauri` | Tauri 2 + WebView2，负责窗口、托盘、自动更新 |
| Go 内核 | `kernel` | 本地服务（`127.0.0.1:8787`），会话/工具/文件系统全部在这里 |

壳启动后拉起内核，前端通过 HTTP + SSE 与内核通信；关闭窗口只收托盘，不退出进程。

## 下载

Windows x64 安装包见 [Releases](https://github.com/madajiann/Tempora/releases)，
或官网 <https://tempora.yomm.cc>。应用内置自动更新（Tauri updater，签名校验后静默安装）。

## 本地构建

前置：Rust（cargo）、Node 22+、Go 1.2x。

```bash
# 1) 内核（产出 kernel/bin/tempora.exe）
cd kernel && make build

# 2) 前端（产出 app/frontend/dist）
cd app/frontend && npm install && npm run build

# 3) 桌面壳（产出 shell/src-tauri/target/release/bundle/nsis/*.exe）
cd shell && cargo tauri build
```

发版（生成 `latest.json` + 创建 GitHub Release + 上传资产）：

```bash
python scripts/release_updater.py --version 0.1.16 --notes "更新说明"
```

> 自动更新签名密钥位于 `~/.tauri/tempora.key`，**私钥永不入库**；
> 构建时通过 `TAURI_SIGNING_PRIVATE_KEY` 注入。

## 更新通道

客户端按 `tauri.conf.json` 中的端点顺序依次探测：

1. `https://tempora.yomm.cc/latest.json`（自建镜像，国内首选）
2. jsDelivr / raw.githubusercontent.com（仓库内 `updates/latest.json`）
3. GitHub Releases `latest/download/latest.json`（海外兜底）

## 上游与许可

本项目是 [`esengine/DeepSeek-Reasonix`](https://github.com/esengine/DeepSeek-Reasonix)（MIT）的衍生版本，
主要改动见 [`docs/CUTLIST.md`](docs/CUTLIST.md)：

- Electron 壳 → Tauri 壳（体积约 -140MB）
- 品牌全量改名 Reasonix → Tempora，图标与配色替换
- 内核改为 GUI 子系统 + 托盘常驻
- 接入 Tauri 官方自动更新

许可：**MIT**（见 [`LICENSE`](LICENSE)）。按 MIT 要求，上游 Reasonix Contributors 的版权声明
在根目录与 `kernel/LICENSE` 中均予保留。

红线（不改动）：UI 组件 1:1、CodeMirror 依赖、中文字体分片、Go 内核业务逻辑。

## 不开源的部分

以下刻意不入库，属于运营资产：

- Tauri 更新签名私钥（`~/.tauri/tempora.key`）
- GitHub / 对象存储的发布凭据（走环境变量或 `~/.tempora/token`）
- 官网与镜像的部署配置（`tempora.yomm.cc`）

## 安全

发现漏洞请提交 Issue 或邮件联系维护者，勿在公开 Issue 中披露细节。
