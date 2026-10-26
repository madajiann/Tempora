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
| 只思考无答案 → 重试一次（含 `answeringRecovery`） | [#13966](https://github.com/esengine/DeepSeek-Reasonix/pull/13966)（**PR base=main-v2，1.x 线**） | 1.x 线在「只思考就结束」时强制续答一次 | 2.x 线（studio）现行 2.48 仍保留 `reasoningOnlyFinishHonoured`（**有意**「只思考就 honor stop」防反复空转）且无 `answeringRecovery`——PR base 决定适用性，**2.x 不算差距** | 不移植（其 `emptyFinalRetryMessage` 文案改进属低风险可选项，留待顺手吸收） |

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

## 2026-10-22 上游蒸馏（studio 2.20.1 → 2.48.0，两周一发的爆发期）

> 原始简报：`docs/upstream-brief.md`（upstream_watch.py 自动产出，40 releases + 60 commits）。
> 本节是人工筛选后的结论。**判定原则不变**：只搬 `internal/**` 与 `desktop/frontend-next/src/**`；
> `desktop/electron/`、`cmd/`（CLI/TUI）、账号/反馈/云端一律不碰。按规则，**动手前逐项拍板**。

### 一、上游这两周的主线（六条）

| 主线 | 代表 PR | 对我们的价值 |
|---|---|---|
| 长会话/大工作区内存 | #13899 #14117 #14086（工具卡懒挂载、长输出只留头尾、改动列表分页、旧会话先列表后补摘要） | ★★★ 我们定位就是「长时间自主任务」，长会话内存是真痛点。但前端基线漂移 28 个小版本，移植成本高，要单独排期 |
| 记忆/历史索引稳定性 | #14100 #14096 #14076 #14023 #14024（多进程写入互覆、回滚取回错版本、历史搜索误判） | ★★ 需先核对我们的 sessionstore/记忆是否同构，再定搬不搬 |
| 安全 | #14086（JSONL 检查点跟随 symlink 逃逸会话目录）+ Go 1.26.10 证书修复（GO-2026-6809，#14034） | ★★★ 核对后能搬就搬；Go 重建是纯工具链升级，不动源码 |
| Agent 能力 | #13613（会话级 Agent 预设）、#12927/#13128（辅助会话/侧问，只读）、#11406（定时任务）、#13966（只思考无答案→重试一次）、#13341（跨项目派活） | ★★★ 突出 agent 定位的核心素材 |
| 交互体验 | #11533（在文件管理器显示）、#11577（界面文字四档）、#12977（双击重命名）、#13195（自动命名）、#13962（未读标记）、#11420（会话排序）、#12770（从任意回复分叉）、#12300（项目拖动排序） | ★★ 多为纯前端小改，多数落在 GAP_ANALYSIS P1 |
| 工具生态 | #13540（view_image）、#13399（read_video）、#13541（web_fetch 抓取回退）、#12829/#12597（MCP 工具定义变更审批/固定）、#11468（MCP 单工具禁用） | ★★ 与 GAP P1 的 MCP 单工具禁用同域 |

### 二、建议移植清单（待户主拍板，按优先级）

| 序 | 项 | 来源 | 成本 | 备注 |
|---|---|---|---|---|
| 1 | Go 1.26.10 重建内核（证书修复 GO-2026-6809） | #14034 | 低 | 纯工具链升级，源码零改动；本地 tools/go 是 1.26.8，**没有**这个修复 |
| 2 | JSONL 检查点 symlink 逃逸检查 | #14086 | 低~中 | 先核对 load 路径是否跟随符号链接 |
| 3 | 对话内 Ctrl+F | #11236 | 低 | ✅ 已移植，随 0.1.25 发版 |
| 4 | 项目「在文件管理器中显示」 | #11533 | 低 | ✅ 已移植（内核一步式 reveal，见下节），随 0.1.25 发版 |
| 5 | 界面文字四档（UI 字号独立于正文） | #11577 | 低 | ✅ 已按语义落地（--fs-scale token 体系），随 0.1.25 发版 |
| 6 | 只思考无答案 → 重试一次 + 明确报错 | #13966 | 中 | ❌ **不移植**（1.x 线专属，见「已核对」新行），结论已出 |
| 7 | 工具卡懒挂载/长输出截断 | #13899 系列 | 高 | 值得但单独排期（前端大改） |
| 8 | 多轮无进展/重复输出提示 | #11160 #11183 | 中 | GAP P1 既列 |

### 三、明确不移植（记录在案，别再翻）

- **终端/TUI 全家**：schedule CLI、/resume、终端排队消息、终端按键 —— 我们无终端
- **账号/反馈/贡献榜/手机提醒/云端备份/社区市场/插件生态** —— 撞红线
- **Electron/外壳类**（自动下载更新 #13291、Windows 更新助手等）—— 我们自有 Tauri 更新链
- **Linux 包**（AppImage/rpm）、**1.x 会话导入** —— 不适用
- **SendWithRetry 类补丁**（1.x 线）—— 前次已核对天然免疫，见上文「已核对 · 本地已覆盖 · 不移植」
- **一切 UI 外观跟随**（主题包 shadowFloat、浅色层次重调、图标栏布局挪动等）—— CUTLIST 第 0 节
  （注：**字体清晰度**是户主明示要改的自有需求，属 0.1.24 自研改动，不算上游移植、不进本表）

### 四、自有问题（别记到上游头上）

- 0.1.23 更新提示条（已做）；草稿保存 #11176 已移植，随 0.1.24 发版
- push_via_api 陈旧断点、README 过时两处 —— TAKEOVER §5 P1 文档债，仍挂着

## 2026-10-22 第一波功能同步（0.1.25 发版）

> 户主指令：「按你的想法去执行，首先保证功能同步上游」。本节是执行记录。补丁原文落档 `build/patches/pr_*.patch.txt`。

| 项 | 来源 | 落地 | 本地适配点 |
|---|---|---|---|
| 对话内 Ctrl+F 查找 | #11236 | `ui/windowkeys.ts`（新建，快捷键框架）+ `keys.ts`（pressedChord/typingElsewhere）+ `usefind.ts`（nth 多命中）+ `findpaint.ts`/`findland.ts`（重写）+ Transcript/Find/Chrome/Sidebar/Composer 接线；上游 7 用例全量移植 **7/7 通过** | 当前命中用 `::highlight(rx-find-now)` accent 高亮；AltGr 排除、IME composing 守卫 |
| 会话双击重命名 | #12977 | `ui/Workspaces.tsx` 会话行 `onDoubleClick`（避开 input/button/[role=menu]） | — |
| 会话自动命名 | #13199（简报记 #13195 有误） | 内核 `sessionstore.UserMessagesTitleSource`（全部用户消息后 300 rune）+ `hub_tree.go` `POST /tree/sessions/auto-name` + 前端会话菜单项 | 2.20 内核已有完整标题子系统（generateTitle/titleProv/titlecache），只缺端点与标题源 |
| 在文件管理器中显示 | #11533 | 内核 `hub_locate.go` `POST /host/workspaces/reveal`（`revealFolder` 复用 themes_install.go 的 explorer.exe 调用）+ `Workspaces.tsx` 工作区菜单项 | **偏离上游两步式**（locate→shell open）：走内核一步式 reveal，免 Rust 壳重编 |
| 界面文字四档 | #11577/#13580 语义（#13575 全量重构不搬） | `tokens.css` `--fs-*` 六档套 `--fs-scale` calc；studio.css/app.css 244 处硬编码字号批量 calc 包裹；`look.ts` TEXT_STEPS 四档（0.9/1/1.15/1.3）+ `Appearance.tsx`「界面文字」seg；内核 `AppearanceConfig.TextSize` 持久化 | 上游靠全量重构才有 --fs-scale；我们用确定性正则批量包裹实现同等效果。中文字体分片红线未动 |
| 停止单个工具调用 | #13391 | 内核 `call_stop.go`（callStops + `Agent.CancelToolCall` + `stoppedByUser`→`tool.Refusal{Code: tool.cancelled_by_user}`）+ `tool_calls.go` `POST /tool-calls/{id}/cancel`（409 `tool_call.not_running`）+ 控制层 `ToolCallStopper`；前端 `StopCall.tsx`（10 秒后出现）+ ToolCard/Transcript/Pane 穿 `onStopCall` + `port.stopToolCall` | 上游 Transcript 走 `port` prop；本地走 `onStopCall` 回调（与 onPrepareFileRevert 同构）。`.stop-call` 样式入 studio.css（本地无 waitnote.css），`--dim`→`--ghost` 对齐本地 token |

**顺手修掉的自有欠账**：i18n 目录守卫 23 条中文键无英文对照（HEAD 就缺，Pane/WorkspaceFoot/Workspaces 计量栏与工作区菜单文案）——补齐后 `i18n.test.ts` 5/5 转绿。

## 2026-10-23 第二波功能同步（0.1.27 发版）

> 户主指令不变：「首先保证功能同步上游」。本波主线是**上游的 agent 自监控能力** ——
> 回合跑着跑着没有可观察进展时，宿主替用户发现并说出来。这是「长时间自主任务」定位
> 的核心配套：用户不在旁边盯着时，机器得自己承认卡住了。

### 一、本波移植（上游 PR #11160 `feat(studio): say when a run stops producing observable progress`）

| 项 | 上游 | 本地落地 | 本地适配点 |
|---|---|---|---|
| 无进展判定内核 | `internal/runtime/agent/progress_watch.go`(+138) | 同名新建 | 上游用 `a.observeRoot`；本地无此字段，**新增 `Options.ObserveRoot` + `observeRoot()` 方法**（回落 `WriteWorkspaceRoot`，与上游同语义） |
| 效果观测器 | `internal/safety/evidence/effect_watch.go`(+140) | 同名新建 | 本地 `evidence.Receipt` 字段、`IsDeliveryVerificationCommand`/`VerificationIdentity`/`NormalizePath`、`shellparse.ParseBash`/`StaticWord` **全部已具备**，零改动直接可用 |
| 配置节 | `internal/contract/config/progress_watch.go`(+67) | 同名新建 | `[progress_watch]` 用户全局节；项目 `tempora.toml` **不能**设置（load.go 合并后强制还原用户值） |
| 事件与线协议 | `contract/event/progress_watch.go` / `eventwire/progress_watch.go` | 同名新建 + `event.go`/`wire.go` 接线 | 新增 `ProgressWatchEvent` kind（插在 `KindCount` 前保持序号稳定）+ `TurnOutcomeNoProgress` |
| 控制层与路由 | `session/control/progress_watch_settings.go` / `frontend/serve/progress_watch_settings.go` | 同名新建 | `SessionAPI.Settings` 子接口加两个方法；`GET/POST /progress-watch`，越界返回 400 `progress_watch.out_of_range` |
| 运行循环接线 | `run_loop.go`（mark→settle）、`turnruntime.go`（`watch` 字段）、`errors.go`（`PauseClass`/`InspectRunPause`） | 同步 | `settleProgressRound` 返回 `noProgressPause`，走**可续跑**的停止（与预算耗尽同一条路） |
| 前端状态折叠 | `state/stall.ts`(+47) | 同名新建 | `foldStall` 折 `progress_watch` 帧；静音/关闭是本地手势；`turn_done` 落一条 info notice |
| 停顿提示条 | `ui/StallBar.tsx`(+35) | 同名新建 | 挂在 `RuntimeBar` 里（本地上游把 `RuntimeBar` 做窄了，本地照上游加 `watch`/`onStall` 两个 prop） |
| 设置面板 | `ui/ProgressWatch.tsx`(+116) | 同名新建 | 挂在「会话」段 `session-dir` 之前；prefsnav 目录加 `progress-watch` 条目（`scope: machine` / `apply: immediate`） |
| 动作声明 | `actions.ts` +7 条 | 同步 | `progress-watch.pause/rounds/token-multiple`（kernel-mutation）+ `stall.stop/continue/mute/dismiss` |
| 文案 | `en.ts` +9、`en_settings.ts` +12、`en_kernel.ts` +2、`kernel.ts` +2 | 同步 | 中英对照齐全，i18n 目录守卫通过 |

**行为要点（移植后核对无误）**：
- 判定只看**宿主可观察的效果**（文件改动 / 检查结果变化 / 任务步骤推进 / 读到新内容 /
  子代理返回），不看命令内容；不向模型发送任何内容，也不拒绝任何调用。
- 默认参数：`rounds = 20`、`token_multiple = 8`，**提示默认开、暂停默认关**。
- 提示永远说；只有用户打开「长时间无进展时暂停任务」开关，达标才暂停（已完成的工作保留，
  发一条消息即继续，计数清零）。
- 设置**无需重建**：控制器把新值直接交给运行中的 executor，下一轮生效。

### 二、本波同时修掉的实质问题（不是移植，是核对时发现的真 bug）

| 问题 | 症状 | 处理 |
|---|---|---|
| `eventwire/wire_test.go` 读的是**上游基线副本** `kernel/desktop/frontend-next/src/port/wire.ts`，不是我们发货的 `app/frontend/src/port/wire.ts` | 线协议一致性测试一直在校验上游，没校验我们 | 路径改指产品前端；改完复跑仍绿，说明本地前端与 Go 侧本来就一致 |
| 蒸馏台账把 **#14086** 记成「JSONL 检查点 symlink 逃逸检查」 | 该 PR 实际是 `fix(history): progressive legacy discovery and background scheduling`（旧会话渐进加载与后台调度，+2590/-344，53 文件） | 台账纠正；symlink 那条**另找 PR**，本波不做 |
| 台账里的 **#11420**（会话排序） | GitHub API 返回 **404**，该 PR 号不存在 | 结论作废，本波不做；要会话排序得重新找上游 PR |

### 三、Go 工具链升级（独立于移植的低风险项）

- 本地 `tools/go` 是 **1.26.8**，缺 **GO-2026-6809**（Go 1.26.10 证书修复，上游 #14034）。
- 升级到 **go1.26.10** 后重建内核：纯工具链变更，源码零改动。

### 四、留到下一波（明确不丢）

- **#11183 重复输出循环检测 + 提醒后重试一次**（perseveration_guard，+3451 行）：依赖 #11160
  的 `progress_watch.go`，本波已铺好地基，下一波做。
- #14086 旧会话渐进加载（+2590 行，前端基线漂移 28 个小版本）：单独排期。
- 会话排序、子代理记录入口（#11529）、MCP 单工具禁用（#11468）、定时任务（#11406）。


## 2026-10-24 第三波功能同步（0.1.28 发版）

> 户主指令不变：「首先保证功能同步上游」。本波把上一波台账里「留到下一波」的四条一次性做完，
> **一版发四个功能**，不再一版挤一个。

### 一、本波移植（四个上游 PR，全部是上游已 merged 的正式功能）

| 项 | 上游 | 本地落地 | 本地适配点 |
|---|---|---|---|
| 重复输出循环检测 | **#11183** `feat(studio): cut a perseveration loop and retry once`（perseveration_guard，+3451 行，49 文件） | `internal/runtime/agent/perseveration_guard.go`(357) 新建 + 运行时接线 | 上游 module 名 `reasonix` → 本地 `tempora`；上游 TUI 版 `internal/frontend/tui/progress_watch.go` **本地无 TUI 目录**，跳过；上游 `progress_watch_effect_test.go` 依赖的 `approveWorkspace` 助手本地没有 → 改用 `Options.WorkspaceRoot` + 不设 `Options.Home` |
| 旧会话渐进加载 | **#14086** `fix(history): progressive legacy discovery and background scheduling`（+2590/-344，53 文件） | `historycatalog/root_scan.go`、`serve/hub_legacy_listings.go`、`serve/hub_progressive_test.go`、`base/backgroundwork/`、前端 `useTreeRead.ts` + `ListingProgress.tsx` | 前端基线比上游漂移 28 个小版本，按本地 `useTreeRead`/`ListingProgress` 结构接，未硬套上游组件 |
| 子代理记录入口 | **#11529** 子代理 transcript 入口 + 截断输出 show-all（+257/-22，10 文件） | `ui/panels/AgentTranscript.tsx` 新建；改 `DeckChips.tsx`、`cards/ToolCard.tsx`、`cards/ToolOutput.tsx`、`actions.ts`、`i18n/en_window.ts`、`styles/studio.css` | 上游 `desktop/frontend-next/src/` → 本地 `app/frontend/src/`；本地 `actions.ts` 有 action census 棘轮上限，新增 action 须同步登记 |
| MCP 单工具禁用 | **#11468** 单个 MCP 工具级禁用（8 文件） | `ext/plugin/disabled_tools.go` 新建 + `contract/config/{mcpjson,plugin_entry,render_plugin}.go` + `session/control/mcp*.go` + `assembly/boot/mcp_registration.go` | 本地 MCP 注册在 `boot/mcp_registration.go`（上游在别处），禁用逻辑落在本地注册路径上 |

### 二、判定与行为要点（移植后核对）

- **#11183 重复输出检测**：默认**只报不切**（检测到死循环 → 走 progress-watch 通道提示）；
  `[progress_watch].perseveration_retries` 设成 >0 才**切流 + 提醒重试**，重试预算用尽则以
  `perseveration` 暂停（可续跑）。检测只看**输出文本的重复形态**（最小周期块 × 8 次以上），
  不看命令内容；思考流与回答流**各用独立缓冲**，避免交织打断周期性判定。
  死循环尾巴会折叠成「短语 + 最后一次重复」再交给模型，transcript 与存储一致。
- **#11183 敏感度是刻意保守的**：最小周期 128 字节、最大 2048 字节、需 8 次重复，
  扫描按 1024 字节节奏摊销。宁可晚触发、极少误报。
- **#11183 三层配置**：全局 `[progress_watch].perseveration_retries` → provider 级
  `perseveration_retries` 覆盖 → 负值关闭守卫。不设置 = 只报不切。

### 三、本波核对时发现并修掉的实质问题

| 问题 | 症状 | 处理 |
|---|---|---|
| **本地工作区 2088 个文件是 CRLF，但仓库配了 `attr/text eol=lf`** | `internal/contract/tool` 的 `TestBuiltinToolContractDocumentation` 在**本地工作区**失败（`docs/TOOL_CONTRACT.md has no tool table to generate into`），在干净 checkout 的基线 worktree 里**通过** | 已用 `git stash` 推掉全部改动**在同一工作区复现**同一失败，确认为**既有环境问题**（工作区行尾未规范化），与本波无关。本波**未**擅自批量改行尾（2088 文件的机械改动会污染 diff），仅记录 |
| 上游 `progress_watch_effect_test.go` 依赖 `approveWorkspace` 助手 | 本地没有该助手，测试直接编译不过 | 改用本地既有的 `Options.WorkspaceRoot` + `Options.SessionDir`；**且不能设 `Options.Home`**——`Options.Home` 会把这份 assembly 绑到工作区配置，导致用户的 `[progress_watch]` 读不到、退回默认值（探针实测 `rounds=20 mult=8`，应为 `rounds=1000 mult=1`） |
| 上游测试写 `reasonix.toml` | 本地项目配置文件名是 `tempora.toml`，上游文件不生效 → 测试误连真实 deepseek（HTTP 401） | 全部改为 `tempora.toml` |
| 上游 testdata `.cost`/`.fixed` 提取时丢末尾换行 | `TestPerseverationGuardEvidence` 5 个子用例全部失败 | 15 个 testdata 文件**全部改用上游 GitHub API 原版字节**（`merge_commit_sha=6038a6fb`），不手工补换行 |

### 四、遗留失败（基线比对确认，与本波无关）

`cmd/e2ebench`、`cmd/signpath-contract`（仓库缺 `.signpath/` 目录）、`internal/contract/tool`
（见上，CRLF）、`internal/ext/extension/{conformance,protocol,protocolgen}`（缺 SDK fixture）、
`internal/frontend/serve`（3 个守卫读旧前端副本）、`internal/platform/update`、
`internal/tools/productdocs`、`internal/assembly/boot` 的 `TestGoldenBaselineNoExtensions`
（`SystemHash` 与上游 golden 不同）——**逐包用 HEAD 基线 worktree 实跑对比，全部一致复现**。

### 五、留到下一波

- 会话排序（台账里的 #11420 已作废，PR 号不存在，需重新找上游 PR）。
