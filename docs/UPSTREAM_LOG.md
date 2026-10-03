# 上游内容吸收台账

> 规则：**每从上游（`esengine/DeepSeek-Reasonix`，MIT © Reasonix Contributors）移植/参考一项，先报户主拍板，再记入本表。**
> 移植要求：保留 MIT 版权声明，改动的源文件头部标注 `Ported from DeepSeek-Reasonix (MIT)`。
> 红线复核：`docs/CUTLIST.md` 第 0 节 —— UI 组件 1:1 / CodeMirror 依赖 / 中文字体分片 / Go 内核业务逻辑 / yomm.cc 中转站，一律不许动。
> 自动产出上游变更清单：`python scripts/upstream_watch.py --since YYYY-MM-DD`

| 上游版本 | 吸收日期 | 吸收了什么 |
|---|---|---|
| — | — | （尚未移植任何上游内容） |

## 已核对 · 本地已覆盖 · 不移植（2026-10-03 核对）

上游自 1.39.0 起把 `SendWithRetry` 改成「只发一次」，我们保留的是更早的重试循环，
所以上游后来为这个改动打的补丁，对我们**天然不适用**。逐项记录，避免下次重查。

| 上游修复 | PR | 上游改法 | 本地实际情况 | 结论 |
|---|---|---|---|---|
| 空闲复用连接被对端断开 → 下一轮 `unexpected EOF` | [#11271](https://github.com/esengine/DeepSeek-Reasonix/pull/11271) (v1.39.6) | 用 `httptrace` 探测「走了复用空闲连接 + 零响应字节」，仅在此时重发一次 | `internal/contract/provider/retry.go` 是 `for attempt <= retryLimit` 循环，`httpClient.Do` 失败即 `continue` 重试，**本就覆盖** | 不移植 |
| 上下文整理（compact）无限等待 | [#11171](https://github.com/esengine/DeepSeek-Reasonix/pull/11171) (v1.39.5) | 统一 5 分钟上限；摘要失败保留最后一次确认的上下文 | `internal/runtime/agent/compact.go` 有 `summaryTimeout = 90 * time.Second`，**比上游更严** | 不移植 |
| 启动时同步整理会话历史拖慢冷启动 | [#11488](https://github.com/esengine/DeepSeek-Reasonix/pull/11488) (studio-v2.25.0) | 新增 `session_sweep.go`，启动改后台 | `internal/assembly/boot/isolation.go:53` 已是 `go store.SweepExpired(...)` 异步 goroutine | 不移植 |

## 待户主拍板（2026-10-03 提出）

| 项 | 上游版本 / PR | 为什么值得 | 本地现状 | 风险 |
|---|---|---|---|---|
| 启动等待延长到 60s、3s 后显示「正在启动」、提前退出自动重试一次 | studio-v2.24.0 / #11479 | 直击「打开卡死」痛点 | 有 `public/boot.html`（含启动动画），但内核侧未搜到等待/重试逻辑 | 中（要动启动链路，需回归） |
| 输入框草稿按会话保存，刷新/重开会话后恢复 | studio-v2.22.0 / #11176 | 体验提升，纯前端 | 未核 | 低 |
| 项目「⋯」菜单新增「在文件管理器中显示」 | studio-v2.25.0 / #11533 | 与已做的原生文件夹选择框同源 | 未核 | 低 |

## 明确不碰（与轻便版定位冲突或撞红线）

- 社区市场 / 账号登录 / 云端配置备份 / 插件生态（要登录、要联网审核，轻便版不需要）
- 终端命令体系（`/queue`、`/steer`、`/setup` 等十几个，我们是桌面 GUI，无终端）
- 一切 UI 外观改动（CUTLIST 第 0 节：UI 组件 1:1）
- Electron / 沙箱相关（我们已换 Tauri）

## 待补的基础设施

- **前端基线版本未知**：`app/frontend/package.json` 未标、`CUTLIST.md` 未记，
  导致无法判断前端相对上游落后多少。下次复制上游代码时应记录对应的上游 tag。
- 参考副本 `G:/Tempora/reference/DeepSeek-Reasonix` 停在 **2026-09-25**（落后 8 天），
  下次做上游比对前需先更新它（`git fetch`；本机直连 github.com 不稳，必要时用
  `GET /repos/esengine/DeepSeek-Reasonix/tarball/studio` 拉归档）。
