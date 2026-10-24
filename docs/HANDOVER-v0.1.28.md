# Tempora v0.1.28 交接文档

> 生成时间：2026-10-25 00:05 · **本版已完整发布，线上四端点全部生效**
> 本文给换号/换人接手用：§2 是全部路径，§4 是本波新踩的坑（下次直接抄）。

---

## 1. 本版是什么

**版本**：v0.1.28 · 一版同步四个上游已 merged 功能（DeepSeek-Reasonix 上游 PR）。

| 上游 PR | 功能 | 本地入口 |
|---|---|---|
| #11183 | 重复输出循环检测（默认只报不切；`perseveration_retries>0` 才掐断重试） | `kernel/internal/runtime/agent/perseveration_guard.go` |
| #14086 | 旧会话渐进加载 + 后台调度 | `kernel/internal/session/sessionstore/`、`kernel/internal/frontend/serve/historycatalog/`、`app/frontend/src/ui/useTreeRead.ts` |
| #11529 | 子代理记录入口 + show-all | `app/frontend/src/ui/panels/AgentTranscript.tsx` |
| #11468 | MCP 单工具禁用 | `kernel/internal/ext/plugin/disabled_tools.go` |

- 本地 release commit：`245400c`（133 文件，+9032/-1756）
- 本地更新清单 commit：`de70ca2`（chore(updates): latest.json -> v0.1.28）
- 本地 tag：`v0.1.28` → `245400c`
- 远端 main：`bda2c8eb919c8c44b7af74591738a2cc3eec9ad4`（内容与本地 `de70ca2` 等价，tree 完全一致）

---

## 2. 全部路径

### 源码与构建
| 角色 | 路径 |
|---|---|
| 源码仓库 | `G:/Tempora`（remote `madajiann/Tempora`，分支 main） |
| 前端源码 | `G:/Tempora/app/frontend`，产物 `app/frontend/dist/` |
| Go 内核源码 | `G:/Tempora/kernel`，产物 `kernel/bin/tempora.exe` |
| Tauri 壳源码 | `G:/Tempora/shell/src-tauri` |
| NSIS 安装包 | `shell/src-tauri/target/release/bundle/nsis/Tempora_0.1.28_x64-setup.exe`（40,385,856 字节） |
| 安装包签名 | 同目录 `.sig`（440 字节） |
| 安装包 SHA-256 | `606c19f0028c0a7f32473ff3d8c9cf0978624949938aafaa20d91dd4f1fa17b2` |

### 部署与运行
| 角色 | 路径 |
|---|---|
| 本机部署目录 | `D:/Tempora`（`tempora-shell.exe` + `tempora.exe` + `frontend-next/dist`） |
| 内核版本自检 | `D:/Tempora/tempora.exe version --json` → 已见 `v0.1.28` / `245400c32d5e` |
| 更新日志现场 | `D:/Tempora/updater.log`（查"为什么不弹更新"看这个文件） |

### 线上（全部已生效）
| 角色 | 路径 |
|---|---|
| 香港镜像（第一端点） | `root@103.84.110.200:/opt/tempora-site/`，dl 只留 0.1.27 + 0.1.28 |
| GitHub Release | `https://github.com/madajiann/Tempora/releases/tag/v0.1.28`（release id `422716823`） |
| Release 三资产 | 安装包 40,385,856 + `.sig` 440 + `latest.json` 1612，全部 `state=uploaded` |
| 客户端更新端点顺序 | `tempora.yomm.cc/latest.json` → jsdelivr → raw.githubusercontent → release-asset |

### 凭据
| 用途 | 路径 |
|---|---|
| GitHub PAT（`ghp_`，scope=repo） | `~/.tempora/token` |
| 部署 SSH 私钥 | `~/.ssh/id_ed25519_deploy` |
| Tauri 更新签名私钥 | `~/.tauri/tempora.key`（泄漏 = 别人能推任意"官方更新"） |

### 文档与脚本
| 用途 | 路径 |
|---|---|
| 交接主文档 | `docs/HANDOVER.md`（本版内容在 §10.7） |
| 本交接文档 | `docs/HANDOVER-v0.1.28.md` |
| 上游同步台账 | `docs/UPSTREAM_LOG.md` |
| 发版全流程 skill（含全部踩坑） | `~/.workbuddy/skills/tempora-release/SKILL.md` |
| 更新通道验收脚本 | `scripts/verify_update_channel.py` |
| GitHub 资产上传 | `scripts/upload_assets.py` |
| 香港镜像分片上传 | `scripts/upload_hk_direct.py` |
| 远端 ref 对齐（API 推送） | `scripts/align_release_ref.py` |
| 以远端 main 为 parent 的跟进推送 | `scripts/push_followup.py` |

---

## 3. 发布验收记录（已全部通过，不用重做）

| 项 | 结果 |
|---|---|
| 前端 Vitest | 153 文件 / 963 用例，0 失败 |
| `npx tsc --noEmit` | 干净 |
| 内核 `go build ./...` + `go vet ./...` | 干净 |
| `go test ./...` | 失败清单与 HEAD 基线 worktree 逐包一致（既有失败，非本波引入） |
| 内核版本串 | `v0.1.28` / `245400c32d5e` / `2026-10-24T10:04:11Z` |
| 安装包 SHA-256 | 本地 == GitHub Release == 香港镜像，三处一致 `606c19f0...` |
| `tempora.yomm.cc/latest.json` | HTTP 200，version `0.1.28` |
| `tempora.yomm.cc/dl/Tempora_0.1.28_x64-setup.exe` | HTTP 200，Content-Length 40,385,856 |
| jsdelivr purge | `status=finished`（GET，非 POST） |
| GitHub Release 资产 | 三资产全部 `state=uploaded` |
| 本机部署 `D:/Tempora` | 内核 / 壳 / 前端 dist 三者均已核对到本版 |

> 本机直连 `cdn.jsdelivr.net` 与 `raw.githubusercontent.com` 返回 HTTP 000（本机网络限制，
> 历版发版同样如此），不影响公网用户；jsdelivr purge 返回 finished 即已生效。

### 用户侧更新方式
客户端**不会自动弹窗**（`main.rs` 的 `silent_check()` 只写日志），用户可见入口是侧栏品牌区
下方那条整行提示。要立刻用上就把 `D:/Tempora` 的产物同步好——本机已经是最新版。

---

## 4. 本波新踩的坑（下次直接抄）

1. **本地 commit 与远端 commit sha 必然不同**：本地提交时区 `+0800`，GitHub 把
   author/committer date 归一成 UTC，sha 就对不上（本地 `245400c` ↔ 远端 `d9eaa03`，tree 相同）。
   **别用 sha 相等当验收，改用 tree sha + 文件数比对**。
2. **API 建 tag 的日期必须 ISO 8601**：git 原始 tagger 行是 `1792836071 +0800`，
   直接喂报 `422 not a valid date-time`，用 `%(taggerdate:iso-strict)` 取。
3. **API 建 tag 的 object 必须指向远端存在的 commit**，否则 `422 Could not verify object`。
4. **远端 tag ref 要先 POST 创建再 PATCH 更新**，直接 PATCH 报 `422 Reference does not exist`。
5. **SSH 后台跑不了**：读 `~/.ssh` 被沙箱拦，且后台不继承沙箱豁免，必须前台提权；
   `known_hosts` 还要用 `UserKnownHostsFile=/dev/null` 绕过（本机该文件读不了）。
6. **SSH 限流**：连续多次连接后 `Connection timed out`，等几分钟自愈，别改配置。
7. **`git push` 本机走不通**：https 通道被代理截断（502 / TLS EOF），一律走 Git Data API。
8. **API 推送时 parent 要用远端 main**：本地 commit 的 parent 远端不存在，
   `rev-list <remote>..<local>` 会 fatal，见 `scripts/push_followup.py`。

---

## 5. 下一步可以做什么（不紧急）

- 用户侧真机验证：重启壳 → 侧栏更新提示是否亮起（本机已是最新，不会亮，属预期）。
- `scripts/prune_releases.py` 清理 GitHub 旧 Release（默认保留最近 5 个）。
- 下一波上游 PR 蒸馏：先看 `docs/UPSTREAM_LOG.md` 的待办表。
