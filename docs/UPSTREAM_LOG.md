# 上游内容吸收台账

> 规则：**每从上游（`esengine/DeepSeek-Reasonix`，MIT © Reasonix Contributors）移植/参考一项，先报户主拍板，再记入本表。**
> 移植要求：保留 MIT 版权声明，改动的源文件头部标注 `Ported from DeepSeek-Reasonix (MIT)`。
> 红线复核：`docs/CUTLIST.md` 第 0 节 —— UI 组件 1:1 / CodeMirror 依赖 / 中文字体分片 / Go 内核业务逻辑 / yomm.cc 中转站，一律不许动。
> 自动产出上游变更清单：`python scripts/upstream_watch.py --since YYYY-MM-DD`

| 上游版本 | 吸收日期 | 吸收了什么 |
|---|---|---|
| studio-v2.22.0 / [#11209](https://github.com/esengine/DeepSeek-Reasonix/pull/11209) | 2026-10-04 | **项目配置只能收紧**（大半）。排查发现 CLI/Secrets/Sandbox/Remote/Storage/Telemetry 的 user-global 隔离早已存在（`sandbox_scope.go` 等），真正漏的是 **Permissions**：项目 `tempora.toml` 的 `permissions.allow` / `mode="allow"` 此前直接生效。新增 `config/permission_scope.go`：mode 只能更严（deny3>ask2>allow1，未知值=0）、allow 只认用户授予、ask/deny 只做叠加、`allow_dynamic_bash` 用户关着时项目不能开；违规时给出 load warning（只报仓库新增的规则）。「总是允许」改存 `roots.Home()/config.toml`，不再写进仓库文件——否则写进去再读回来被当成仓库授予，功能直接坏。**未移植**：项目声明程序（钩子/LSP/shell 路径）首次使用前人工批准，需要前端交互与主目录信任记录 |
| studio-v2.21.0 / [#11110](https://github.com/esengine/DeepSeek-Reasonix/pull/11110) | 2026-10-04 | **本地服务默认鉴权 + 启动令牌**。内核本来就有完整 authGate（token/password），缺的只是默认不开：`serve` 与 `web` 现在都默认 `auth=token`，显式 `--auth` 与 config `auth_mode` 仍说了算；`web` 即使 config 写 none 也强制 token（它是给别人连的入口）。桌面壳生成 256 位令牌（RtlGenRandom）经临时文件交接、内核读到即删，启动页经 IPC 命令 `kernel_token` 取令牌放 URL fragment，由内核页既有引导脚本换 HttpOnly cookie。⚠️ `--token-file` 语义变了一点：读完后删除该文件（令牌只活在壳与内核内存里），supervised 判定也从「port-file+token-file」放宽为「有 token-file 即不打印明文」。⚠️ 0.1.20 曾因此翻车（authGate 拦了 `/assets/*.js`，页面拿不到 bundle 永远停在启动画面），0.1.21 补 `staticAssetPath()` 放行构建产物 |
| studio-v2.22.0 / [#11193](https://github.com/esengine/DeepSeek-Reasonix/pull/11193) | 2026-10-03 | **4 个一键服务商预设**（OpenRouter / OpenAI / Gemini / 火山方舟 Ark）。纯内核 3 文件：新增 `internal/contract/config/global_presets.go` + 测试，接入 `curatedProviderPresets`。本地改动：OpenRouter 归属头（`HTTP-Referer` / `X-OpenRouter-Title`）署名改为 Tempora，让用量算在我们头上 |
| studio-v2.23.0 / [#11258](https://github.com/esengine/DeepSeek-Reasonix/pull/11258) | 2026-10-03 | **按服务商设置流空闲超时 `idle_timeout_seconds`**。`provider.IdleTimeoutFromExtra()` + `ProviderEntry.IdleTimeoutSeconds` 字段 + 校验 + 渲染 + 三个模型实现接线。⚠️ 本地无 `provider.StreamIdleTimeout` 常量（各实现原为 120s），故**新增该常量时取 120s 而非上游 300s，默认行为零变更**，只是新增可覆盖能力 |
| 上游 commit `40c87d94c`（2026-09-28，per-model effort 地基）+ [#11422](https://github.com/esengine/DeepSeek-Reasonix/pull/11422) | 2026-10-03 | **每模型上下文窗口 / 最大输出**。先补地基再上本体，详见下表 |

### #11422 的两步落地（2026-10-03）

**背景**：`ProviderModelOverride.ContextWindow` / `MaxOutputTokens` 在 2.20.0 **就已存在且生效**
（改 `config.toml` 的 `model_overrides.<model>` 本来就能用），缺的是「按模型读写它的 API 和界面」。
所以本次补的是**暴露与管理能力**，不是新的存储能力。

**第一步 · 地基（commit `40c87d94c`，kernel 侧）** —— 纯重构 + 三个新查询，零行为变更：

| 文件 | 动作 |
|---|---|
| `internal/contract/config/model_effort.go` | 新增。抽出 `forModel()` / `modelOverrideKey()`，新增 `ModelEffortDeclaration` / `ModelReasoningProtocol` / `SetModelEffortDeclaration` / `InheritedEffortCapability` |
| `internal/contract/config/config.go` | `modelOverrideForModel` 改为复用 `modelOverrideKey`；`ResolveModel` 三处内联的 apply 序列改为 `forModel()` |
| `internal/contract/config/effort.go` | `EffectiveEffort`：存储档位不在菜单内时按 auto 读（`EffortDisplay` 已有此语义）；`normalizedModelOverrides` 复用 `modelOverrideEmpty` |
| `internal/frontend/serve/provider_model_effort.go` | 新增 `modelEffortView` / `modelEffortsOf` / `inheritedEffortsOf` / `modelProtocolsOf` / `orNilMap` / `applyModelEfforts` / `editRefusal` |
| `internal/frontend/serve/provider_edit.go` | 三处协议/档位写入合并为 `applyReasoningFields` |

**第二步 · 本体（#11422）**：

| 文件 | 动作 |
|---|---|
| `internal/contract/config/model_limits.go` | 新增 `ModelLimits` / `SetModelLimits` / `InheritedLimits`（`ErrModelContextWindowNegative`） |
| `internal/frontend/serve/provider_model_limits.go` | 新增 `modelLimitsView` / `modelLimitsOf` / `inheritedLimitsOf` / `applyModelLimits` |
| `internal/frontend/serve/providers.go` | 视图增 `modelLimits` / `inheritedLimits`（连同地基的 `modelEfforts` / `inheritedEfforts` / `modelProtocols`） |
| `internal/frontend/serve/provider_edit.go` | 编辑接口增 `modelLimits`，走 `applyModelLimits` |
| 前端 `ui/ModelLimits.tsx` + `ui/EditConn.tsx` + `port/provider.ts` + `port/port.ts` + `styles/app.css` + `i18n/en_settings.ts` | 新增「按模型设置限制」分组：留空继承、灰字显示当前继承值、填写只对该模型生效 |

**未移植**：#11422 前端里的 `ModelEfforts.tsx`（每模型推理档位 UI）。我们的前端是 2.20.0 基线，
**整层 per-model UI 都不存在**（无 `ModelEfforts.tsx`、无 `modelEfforts` 字段），
移植它等于把 effort 地基的前端一半也搬过来，牵动 EditConn 的状态机。故只做 limits，
effort UI 单列一轮。**地基的 kernel 侧已就位，届时只需补前端。**

**本地适配点（与上游不同，别照抄）**：
- 模块名 `tempora` ≠ `reasonix`
- `modelOverrideEmpty` 本地是超集（多判 `MaxOutputTokens`），替换内联条件更安全
- 单位后缀用本地既有写法 `<i>tokens</i>`（上游是 `t("窗口")` / `t("输出")`），避免中英文案不一致
- i18n 里 `"窗口"` 已存在（= Window），**不要重复添加**

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
| ~~启动等待延长到 60s、3s 后显示「正在启动」、提前退出自动重试一次~~ | studio-v2.24.0 / #11479 | 直击「打开卡死」痛点 | ✅ **已处理**：上游实现在 `desktop/electron/`，与我们 Tauri 壳无交集，按语义自研（见下节） | — |
| 输入框草稿按会话保存，刷新/重开会话后恢复 | studio-v2.22.0 / #11176 | 体验提升，纯前端 | 未核 | 低 |
| 项目「⋯」菜单新增「在文件管理器中显示」 | studio-v2.25.0 / #11533 | 与已做的原生文件夹选择框同源 | 未核 | 低 |

> 另：2026-10-05（0.1.23）处理了一个**自有问题，不是上游差距** —— 客户端发现新版本后
> 只写日志、不弹窗（shell `silent_check()` 刻意为之，历史上弹窗会变空白窗），
> 用户可见入口只有品牌区一个 7px 圆点，结果 0.1.22 发出去三天没人升级。
> 已改为侧栏整行提示 + 半小时复查，详见 `docs/GAP_ANALYSIS.md` 第 9 节。

## 已按语义自研（非代码移植，2026-10-03）

| 项 | 上游 | 为什么不算移植 | 落地 |
|---|---|---|---|
| 内核提前退出自动重试一次 + 等待放宽到 60s | #11479 (studio-v2.24.0) | 上游 5 个文件全在 `desktop/electron/{host,main,shelllog,starting}.js` + 测试，**与 Tauri 壳零交集，搬不了**；只取语义自研 | `shell/src-tauri/src/main.rs` `ensure_kernel()`：两轮循环 + `child.try_wait()` 提前退出检测；`cargo check` 通过 |
| 会话图片按 blob 存（schema 3） | studio-v2.20.2 | 上游走的是它自己的 checkpoint schema 3，我们这边超限的是 **sessionstore 的事件日志**（`sessionEventReplayMaxBytes = 128MiB`），两边结构不同源；按语义自研 | `internal/state/sessionstore/session_image_blobs.go`：data URL 按 SHA-256 落到 `<id>.blobs/`，日志与 .jsonl 只存 `tempora-blob:v1:<digest>`；写入外提、读取回填、压缩时按存活引用回收；blob 目录登记进 `store.SessionSidecarDirs` 随会话删除。**不动 schema 号**——旧版本读到引用只是丢图，不会读坏文本；**已写坏的旧会话不能自愈**（日志超限就读不回来） |

> **判定原则**：上游补丁先查改动文件路径。落在 `desktop/electron/`、`cmd/`（CLI/TUI）
> 的，对我们基本无移植价值 —— 前者我们已换 Tauri，后者我们没有终端。
> 只有落在 `internal/**`（内核）与 `desktop/frontend-next/src/**`（前端）的才值得搬。

## 明确不碰（与轻便版定位冲突或撞红线）

- 社区市场 / 账号登录 / 云端配置备份 / 插件生态（要登录、要联网审核，轻便版不需要）
- 终端命令体系（`/queue`、`/steer`、`/setup` 等十几个，我们是桌面 GUI，无终端）
- 一切 UI 外观改动（CUTLIST 第 0 节：UI 组件 1:1）
- Electron / 沙箱相关（我们已换 Tauri）

## 待补的基础设施

- ✅ **前端基线版本已确定（2026-10-03）：`studio 2.20.0`**
  证据：`kernel/release-notes/studio/` 最新为 `2.20.0.md`；`kernel/desktop/frontend-next/src`
  即 2.20.0 基线前端（433 文件），可直接与 `app/frontend/src`（435 文件）diff 出我们的全部改动。
  完整差距清单见 `docs/GAP_ANALYSIS.md`。

- ⚠️ **比对范围纠正（重要）**：上游是**两条并行线、代码不同源**
  - 2.x = `studio` 分支（**我们基于这条**，最新 2.26.0）
  - 1.x = `main-v2` 分支（v1.39.x，另一份代码）
  → 本表上半部分拿 v1.39.x 的 PR 去核我们 2.x 内核，**方向本身不成立**，那些结论不可作为依据。
  → 正确的比对范围是 **studio 2.20.1 → 2.26.0**。

- 参考副本 `G:/Tempora/reference/DeepSeek-Reasonix` 停在 **2026-09-25**（落后 8 天），
  下次做上游比对前需先更新它（`git fetch`；本机直连 github.com 不稳，必要时用
  `GET /repos/esengine/DeepSeek-Reasonix/tarball/studio` 拉归档）。
  > 注：其实**不必先更新副本** —— `kernel/desktop/frontend-next` 就是现成的 2.20.0 基线，
  > 直接 diff 更快；取上游新改动用 `GET /repos/{repo}/pulls/{n}/files` 拿 patch。

- ⚠️ **diff 前必须剥 CR**：基线前端与我们前端的行尾符不同，
  不剥会把整个文件误报成差异（`diff --strip-trailing-cr`）。
  实测 `ui/App.tsx`：不剥 = +799/-777（假），剥后 = +28/-6（真）。
