# 开源策略决策记录

> 结论先写：**客户端全量源码以 MIT 开源，闭源只留「密钥 + 凭据 + 服务端运营」三样。**
> 决策日期：2026-09-30

## 一、为什么是开源，而不是闭源

| 因素 | 说明 |
|---|---|
| 上游许可 | 衍生自 `esengine/DeepSeek-Reasonix`（MIT）。MIT **允许**闭源再分发，但**强制**保留上游版权声明。所以闭源合法，开源也合法 —— 不是法律问题，是收益问题 |
| 既成事实 | 仓库自 2026-09-26 起已 public，13 次提交。再转私有挡不住已存在的克隆与存档，属于「自欺式闭源」 |
| 分发成本 | 自动更新端点依赖 `raw.githubusercontent.com` / `cdn.jsdelivr.net` / GitHub Releases。转私有后这三条全部失效，只剩自建镜像单点 |
| 收益 | 可收 PR/Issue、可被索引、可被信任（闭源客户端+自动下载安装天然被杀软与用户警惕） |

**结论：开源。**

## 二、开源范围

| 目录 | 状态 | 理由 |
|---|---|---|
| `app/frontend` | ✅ 开源 | React SPA，本来就是上游公开的 UI |
| `shell/src-tauri` | ✅ 开源 | Tauri 壳，无竞争力（谁都能写一个壳） |
| `kernel` | ✅ 开源 | 上游 MIT，必须保留版权声明；本地运行的 Agent 内核，价值在体验不在代码 |
| `scripts/` | ✅ 开源 | 发版工具，便于复现构建 |
| `docs/` | ✅ 开源 | 瘦身/上游追踪记录 |

## 三、闭源范围（永不入库）

| 项 | 位置 | 处理方式 |
|---|---|---|
| Tauri 更新签名私钥 | `~/.tauri/tempora.key` | 仅本地，构建时用 `TAURI_SIGNING_PRIVATE_KEY` 注入；`.gitignore` 已拦 `*.key` |
| GitHub / 对象存储凭据 | `~/.tempora/token` | 仅本地，脚本按 `--token > 环境变量 > 文件` 优先级读取 |
| 官网与镜像部署配置 | `tempora.yomm.cc` | 不在本仓库，独立运维 |
| 运营态 `latest*.json` | 仓库根 | 已加入 `.gitignore`，只把 `updates/latest.json` 作为发布产物提交 |
| 用户会话/工作区数据 | `%LOCALAPPDATA%` | 天然不入库 |

> 签名私钥一旦泄漏 = 攻击者可推送任意"官方更新"到所有已装客户端。
> 这是本项目**唯一真正需要保密的资产**。

## 四、合规必做项（已完成）

1. 根 `LICENSE` —— MIT，双版权行（上游 Reasonix Contributors + 本 fork Tempora Contributors）
2. `kernel/LICENSE` —— 恢复上游版权行（此前被误改为单一 Tempora 版权，违反 MIT）
3. 根 `README.md` —— 明确标注上游来源、改动清单、许可
4. `.gitignore` —— 拦 `*.key` / `*.zip` / `*.sig` / `.env` / `dist.old*`

## 五、待办

- [ ] 清理上游遗留：`.github/sponsor/wechat-pay.jpg`（他人收款码）、`kernel/workers/*/wrangler.toml` 中的他人邮箱
- [ ] Release 瘦身：16 个版本 → 保留最近 5 个，删除 v0.1.0 ~ v0.1.10
- [ ] 如后续要加收费能力（账号/订阅），那部分单独建私有仓库，本仓库只放客户端
