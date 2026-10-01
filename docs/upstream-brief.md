# 上游变更简报（自 2026-09-01 起）

- 上游：`esengine/DeepSeek-Reasonix`（MIT © Reasonix Contributors）
- 移植要求：**保留 MIT 版权声明**，改动的源文件头部补 `Ported from DeepSeek-Reasonix (MIT)。`
- 红线复核：`docs/CUTLIST.md` 第 0 节（UI 1:1 / CodeMirror / 字体分片 / Go 内核 / yomm）

## 一、上游 Release 变更

### v1.39.1 — Reasonix CLI v1.39.1  (2026-09-26)
**判定：观察** — 无关键词命中，扫一眼

```
> 桌面端与 CLI 的稳定性修复：更新后会话「消失」、Windows 窗口打不开、旧会话导入、钩子覆盖所有工具调用处，以及记忆安全。

**发布渠道：稳定版 · v1.39.1**

[English →](https://reasonix.io/changelog/v1.39.1/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.1/)

## 概览

**Reasonix v1.39.1 — Reasonix 1.39.1**

桌面端与 CLI 的稳定性修复：更新后会话「消失」、Windows 窗口打不开、旧会话导入、钩子覆盖所有工具调用处，以及记忆安全。

发布日期：2026-09-26

**Desktop 12 · CLI 6**

## 桌面端更新

### 重点内容

- **[Desktop]** **更新后会话「消失」的问题已修复** — 从 1.38 升级后，侧栏可能一条会话都不显示；如果上次停留在一个没发过消息的新对话上，还会一启动就报错。两者都已修复，会话目录的启动修复也会找回带分支会话的列表。会话内容本身一直都在。 ([#10763](https://github.com/esengine/DeepSeek-Reasonix/pull/10763), [#10853](https://github.com/esengine/DeepSeek-Reasonix/pull/10853))
- **[Desktop]** **用过 1.38 沙箱的 Windows 电脑上窗口能正常打开了** — 1.38.8–1.38.10 的 Windows 沙箱可能在安装目录上留下一条访问权限，导致 Chromium 进程全部崩溃、窗口始终不出现。桌面端现在启动时会从自己的安装目录移除这类权限，被系统拒绝时会弹窗说明原因。 ([#10858](https://github.com/esengine/DeepSeek-Reasonix/pull/10858), [#10853](http
```

### v1.39.0 — Reasonix CLI v1.39.0  (2026-09-24)
**判定：跳过** — 与轻便版无关 · 命中 docs/

```
> 此版本改进了会话恢复、错误处理和会话管理，带来更流畅的桌面体验。

**发布渠道：稳定版 · v1.39.0**

[English →](https://reasonix.io/changelog/v1.39.0/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.0/)

## 使用攻略

- [**恢复指南**](https://github.com/esengine/DeepSeek-Reasonix/blob/438566dd6c9b39eaf0d49027576e57e7f610d0dc/docs/RECOVERY.md) — 了解 Reasonix 如何恢复被阻塞的会话并处理缺失数据。
- [**错误呈现指南**](https://github.com/esengine/DeepSeek-Reasonix/blob/438566dd6c9b39eaf0d49027576e57e7f610d0dc/docs/ERROR_PRESENTATION.md) — 了解错误如何在桌面应用中汇总和本地化。

## 概览

**Reasonix v1.39.0 — Reasonix 1.39.0**

此版本改进了会话恢复、错误处理和会话管理，带来更流畅的桌面体验。

发布日期：2026-09-24

**Desktop 5 · CLI 0**

## 桌面端更新

### 重点内容

- **[Desktop]** **更强大的会话恢复能力** — 因无效工具参数或缺失图像而阻塞的会话现在可自动恢复，并在需要用户操作时提供本地化指导。 ([#10731](https://github.com/esengine/DeepSeek-Reasonix/pull/10731))
- **[Desktop]** **更快、更清晰的供应商错误** — 普通供应商 HTTP 和网络故障不再进入长时间自动重试；应用会显示本地化错误摘要。 ([#10730](https://github.com/esengin
```

### studio-v2.20.0 — Reasonix Studio v2.20.0  (2026-09-24)
**判定：待评估** — 可能值得移植 · 命中 mcp/agent，需按 CUTLIST 红线复核

```
本版支持用手机扫码操控 Studio，MCP 服务器可设为常驻加载，Windows 更新改为只下载差异部分。

## 新增

- 同一网络下的手机扫描顶栏二维码即可配对，并在手机上操作窗口里的会话 (74f76057f, bb47cd4a7, 45b0ea470)
- 各屏幕能看到彼此发出的消息，并标明来自哪台设备 (3b5aef077, d3049d69a, f39a0f868)
- 窄屏窗口改用抽屉式侧栏，工作台占满宽度，不再横向滚动 (96ed3492f)
- MCP 服务器可设为常驻：工具每轮直接交给模型，启动时预先连接，在扩展设置里切换 (1333c04e7)
- MCP 服务器可在工具调用中途弹出表单向你询问 (38f0e3371)
- 支持 MCP 2025-11-25 与 2026-07-28 协议，旧服务器照常可用 (88b0fc139, 7dcfebbcf)
- 发送前可让当前模型润色输入框里的草稿 (de375d26a)
- 新增 `run_script` 工具，模型可用一段 Starlark 脚本连续调用多个工具 (fc902b846)
- 新增 `best_of_n`：在多个工作树中并行尝试，由评审选出结果落地 (bba7bcf51)
- 新增 `advise` 工具，任务中途可向更强的模型请教 (c76dd5182)
- 新增 locate 子代理，分四轮并行查找代码所在位置 (c7a85ffe5)
- 可选开启对外部工具返回内容的提示注入筛查，默认关闭 (d5ad1a8e5)
- 工作台以渲染形式打开 Markdown，可在阅读与编辑间切换，链接与图片按工作区解析 (0136f0427, f16172f3b)
- 代码块带标题与行号，过长时可折叠 (dd6e9436c)
- 回答的思考时长会被记录并随该轮保留 (84ab2569e)
- 可导入主题包，并能直接打开主题包所在的文件夹 (817d6806e)
- 插件包可提供 prompt 与主题，插件运行时可给 Agent 增加新工具 (2c7bde871, d318d2405)
- Win
```

### v1.38.12 — Reasonix CLI v1.38.12  (2026-09-23)
**判定：待评估** — 可能值得移植 · 命中 agent/compact，需按 CUTLIST 红线复核

```
> 此版本重点修复会话创建、导航和生命周期问题，提升性能，并改善整体桌面体验。

**发布渠道：稳定版 · v1.38.12**

[English →](https://reasonix.io/changelog/v1.38.12/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.12/)

## 使用攻略

- [**浏览器运行时升级**](https://github.com/esengine/DeepSeek-Reasonix/blob/ab15e65955e9031444d133e51a5a1f39b7a690ee/docs/BROWSER_RUNTIME_UPGRADE.md) — 了解升级后的浏览器运行时，包括新功能和诊断改进。
- [**编辑器控制**](https://github.com/esengine/DeepSeek-Reasonix/blob/ab15e65955e9031444d133e51a5a1f39b7a690ee/docs/COMPOSER_CONTROLS.md) — 编辑器控制文档，包括队列编辑和引导。
- [**模型设置**](https://github.com/esengine/DeepSeek-Reasonix/blob/ab15e65955e9031444d133e51a5a1f39b7a690ee/docs/MODEL_SETTINGS.md) — 模型设置、运行时验证和后台网关保留的详细信息。
- [**读取快照分页**](https://github.com/esengine/DeepSeek-Reasonix/blob/ab15e65955e9031444d133e51a5a1f39b7a690ee/docs/READ_SNAPSHOT_PAGINATION.md) — 有界读取快照如何稳定会话列表分页。
- [**Windows Agent Shell**](https://github.com/esengine/DeepSeek-Re
```

### studio-v2.19.0 — Reasonix Studio v2.19.0  (2026-09-23)
**判定：待评估** — 可能值得移植 · 命中 agent，需按 CUTLIST 红线复核

```
本版加入内置浏览器与 macOS 应用操作，改版 Studio 界面，并修复用量金额被放大数十倍的问题。

## 新增

- Agent 可按站点授权打开、阅读、操作网页，页面画在对话旁边，你能看到它看到的内容 (d1ec7b727, edd9ce180, c24306bd6)
- macOS 上 Agent 可读取并操作其他应用的窗口 (049ee1a75, 591326b98)
- Agent 截取的图片会显示在对话里，而不只发给模型 (1aefe8cf7)
- 写完网页或 SVG 后，Agent 会先看一眼渲染结果再结束本轮 (0670f6b9e)
- System One 决策工具，可接入 TypeSafe 与 Laya 后端 (b76b055a1)
- 工作台用代码编辑器打开文件，支持查找、跳转行与保存；也可在本机编辑器中打开工作区 (73b88cde9, 2807d121b)
- 外观设置新增「会话折叠」，可分别设定思考、执行过程、输出等默认展开或收起 (3b717c40b)
- 中转站可在来源编辑里声明思考参数与推理档位，推理强度菜单可直达该处 (016810261)
- 不打开窗格即可读取远端机器的会话列表，并可删除远端会话 (0e8a034ac, 7776d07f7)
- 回合结束或模型停下提问时可发出系统通知 (71a63d325)
- 选中回答中的一段文字即可引用到输入框 (6b391c1cf)
- 规则设置中可撤销「本会话允许」的授权 (3e75ad8f8)
- 新的启动动画与应用图标；窗口偏好在重启后保留 (9d34b96a9)

## 变更

- Studio 界面改版：侧栏、会话列表、输入框与设置页重新设计 (8a6a4f20d, 5b31c7322, fd413aaf7, 9a4ead5cd)
- 主题包现在覆盖浮层、代码块与语法高亮等全部界面颜色 (12855f3bf)
- 对话中的链接在内置浏览器打开，按住 Ctrl 或 ⌘ 点击则用系统浏览器打开 (b56a3d839)
- 审批卡片可直接选择「始终允许」并写入规则 (e54381d
```

### v1.38.11 — Reasonix CLI v1.38.11  (2026-09-20)
**判定：待评估** — 可能值得移植 · 命中 session，需按 CUTLIST 红线复核

```
> 此版本提升了会话迁移、接管与导出的可靠性，修复了 Windows 凭据与 Shell 问题，并完善图片附件在提交、历史记录与导出中的处理。

**发布渠道：稳定版 · v1.38.11**

[English →](https://reasonix.io/changelog/v1.38.11/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.11/)

## 使用攻略

- [**历史会话按需迁移**](https://github.com/esengine/DeepSeek-Reasonix/blob/ec82bb3251550b03b43b83418a716f73fe758ffd/docs/HISTORICAL_SESSION_MIGRATION_ON_DEMAND.md) — 了解历史会话如何按需迁移以及如何管理它们。
- [**远程会话**](https://github.com/esengine/DeepSeek-Reasonix/blob/ec82bb3251550b03b43b83418a716f73fe758ffd/docs/REMOTE_SESSIONS.md) — 了解跨端会话接管与远程会话管理。
- [**会话草稿生命周期**](https://github.com/esengine/DeepSeek-Reasonix/blob/ec82bb3251550b03b43b83418a716f73fe758ffd/docs/SESSION_DRAFT_LIFECYCLE.md) — 关于持久化本地草稿及其生命周期的详细信息。
- [**会话导出**](https://github.com/esengine/DeepSeek-Reasonix/blob/ec82bb3251550b03b43b83418a716f73fe758ffd/docs/SESSION_EXPORT.md) — 固定快照会话导出的工作原理。
- [**Windows 沙箱**](https://githu
```

### v1.38.10 — Reasonix CLI v1.38.10  (2026-09-18)
**判定：跳过** — 与轻便版无关 · 命中 electron/docs/

```
> 此版本重点提升会话可靠性、Windows 升级与 Agent 执行、文件路径处理和对话记录稳定性。

**发布渠道：稳定版 · v1.38.10**

[English →](https://reasonix.io/changelog/v1.38.10/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.10/)

## 使用攻略

- [**应用会话所有权**](https://github.com/esengine/DeepSeek-Reasonix/blob/26f1984e97d8f4403317d6d00dd27c77395a7a3d/docs/APP_SESSION_OWNERSHIP.md) — 了解会话在应用中的所有权和管理方式。
- [**独立会话**](https://github.com/esengine/DeepSeek-Reasonix/blob/26f1984e97d8f4403317d6d00dd27c77395a7a3d/docs/INDEPENDENT_SESSIONS.md) — 了解独立会话的工作原理及其生命周期。
- [**管理页面**](https://github.com/esengine/DeepSeek-Reasonix/blob/26f1984e97d8f4403317d6d00dd27c77395a7a3d/docs/MANAGEMENT_PAGES.md) — 探索会话和归档的管理页面。
- [**对话记录架构**](https://github.com/esengine/DeepSeek-Reasonix/blob/26f1984e97d8f4403317d6d00dd27c77395a7a3d/docs/TRANSCRIPT_ARCHITECTURE.md) — 对话记录架构及其组件的详细信息。
- [**Windows Agent Shell**](https://github.com/esengine/DeepSeek-Reasoni
```

### studio-v2.18.1 — Reasonix Studio v2.18.1  (2026-09-17)
**判定：待评估** — 可能值得移植 · 命中 model，需按 CUTLIST 红线复核

```
本版修复远端主机使用本机模型时报 unknown model，并移除 IM 机器人网关。

## 修复

- 远端主机使用本机模型时，新会话、模型列表和切换模型不再落到远端自己的配置，不再报 unknown model #10448
- 所选模型在本机不存在时，报错会说明缺模型的是本机，并提示如何改用远端自己的模型 (8b2a05c51)

## 移除

- `reasonix bot` 与 QQ、飞书、微信机器人网关；配置文件里已有的 `[bot]` 段原样保留，不影响 1.x (f352dfbec)

## 升级须知

- 模型来源为本机的远端主机，若内核低于 2.18.1，下次连接会自动下载并替换远端内核 (437b982b5)

---

**macOS** 已用 Developer ID 签名并公证，打开时不需要清除隔离属性。**Windows 包未签名**，SmartScreen 会告警：选「更多信息」，再选「仍要运行」。**Linux** 从 `.deb` 安装。

三个平台都能自更新：Linux 走自己的包，Windows 运行下一个安装器，macOS 替换自身 bundle。
```

### studio-v2.18.0 — Reasonix Studio v2.18.0  (2026-09-17)
**判定：跳过** — 与轻便版无关 · 命中 readme

```
本版修复 Windows 窗口打不开、读图模型误报看不到图、问题框不弹出，并精简内置文档。

## 修复

- Windows 安装目录带 AppContainer 包授权时窗口打不开；启动时自动移除这类授权 #10435
- 读图模型不再声称看不到已附加的图片 (44150b0aa)
- Goal 续跑时不再提示读图模型"无法读图" (44150b0aa)
- 切换模型、重载扩展或切换工作区后，问题框和审批框不再被吞掉 (921a04bda)

## 变更

- 内置文档除 README、使用指南、CLI 参考外只保留英文版，中文提问会检索到英文文档 (68b031ae5)

## 移除

- 内置文档检索中的版本历史，其内容停留在旧产品线的 1.24.1 (99c5360fd)

---

**macOS** 已用 Developer ID 签名并公证，打开时不需要清除隔离属性。**Windows 包未签名**，SmartScreen 会告警：选「更多信息」，再选「仍要运行」。**Linux** 从 `.deb` 安装。

三个平台都能自更新：Linux 走自己的包，Windows 运行下一个安装器，macOS 替换自身 bundle。
```

### studio-v2.17.0 — Reasonix Studio v2.17.0  (2026-09-16)
**判定：跳过** — 与轻便版无关 · 命中 electron/docs//ci

```
本版的主线是**让"检查通过"意味着它所说的那件事**：模型可用性探测此前从不发工具，于是一个只会聊天的中转站通过了验证、在第一条消息上失败，而设置面板仍标着"已验证"；一个 2024 年才有的可选字段被无条件发给每个 OpenAI 兼容端点，让不认它的网关拒掉整场会话。界面一侧，一个中文词在两处字典里有两种英文，英文窗口上的"保存"按钮读作 Transcript；补全菜单的内置动词由内核按进程语言渲染，于是中文机器上的英文窗口配一份中文菜单。另一条主线是**老外壳的退役**：Wails 那套连同它的 CGO 与 GTK/WebKitGTK 构建要求一次性移除，Studio 从此只有一个外壳；内核与控制器随之做了一轮按主题的归位。自 2.16.0 起 39 个提交，净减两万六千行。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。已安装的 2.10 及更早的 Wails 版本仍由现有的接管路径升到本版，那条路径不是 Wails 代码，未被此次退役触及。

## 修复

### 检查通过，然后第一条消息就失败

- **模型可用性探测现在带一个工具**。Reasonix 是代理，一个递不进工具的模型跑不了一回合。探测此前只发 messages 和 max_tokens，于是一个应答聊天、拒绝 tools 数组的中转站通过了验证，用户的第一条消息才失败——而那一行仍显示"已验证"。被拒时它再问一次、这次不带数组，**只有当去掉数组正是让请求答上来的那件事时**才报"tools"：结论来自第二次尝试成功，不是拒绝里的某个词。凭据错误与限流不给重试——第二次会因第一次的同一个理由被拒——所以那条"只试一次"的规则对它们原样保留。连接按钮从未声称超出它所证明的（它只列模型，它自己的注释就这么写），但"已连接，OpenAI 兼容"读起来像"可以用了"。现在那一行说得出"端点应答聊天、拒绝工具调用"，这一句话把人送去换网关，而不是送进一场注定失败的会话。
- **不再为一个 to
```

### studio-v2.16.0 — Reasonix Studio v2.16.0  (2026-09-15)
**判定：待评估** — 可能值得移植 · 命中 cache/会话/session/mcp/provider/tool，需按 CUTLIST 红线复核

```
本版的主线是**让屏幕上写着的东西与内核里的事实是同一件**：任务面板读内核发布的那份清单而不再从转录里把它猜回来，一次被拒的工具调用带着主机给它的身份而不是一句话，卡片名出内核真正跑的那个能力，能力清单在调用被花掉之前就说出它要的参数。工作台补上四件它做不到的事——会话内查找、代码块高亮、消息改写重发、能力名到卡片。回合多了一个出口：把清单交回用户，而不是被主机推着往下走。界面一侧是一轮以实测为准的整理（阅读尺寸与栏宽、等宽面、汉字下的小型大写、浅色的灰、卡片的高度成本），以及三个早已失灵的门。自 2.15.0 起 43 个提交。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。

## 新增

### 工作台：四件它做不到的事

- **会话内查找**。转录只挂载几十张卡片，所以浏览器自带的查找只看得见屏幕上那些：200 条消息时 DOM 里有 59 张卡，第一条根本找不到。查找改读行本身——`saidBy()` 对 `Item` 是穷尽的，新卡片必须回答它携带什么文本。命中用高亮注册表画，而不是包一层标签：那等于重写 React 拥有的 markdown，而那些卡片在每一个增量上重渲染。
- **代码块高亮**。rehype-highlight 像 katex 一样惰性加载，输出的是 class 而非内联颜色——自己写十六进制的高亮器会离开令牌系统、从此不跟随主题。调色板是四个新令牌，注释与标点走 `--faint` 和 `--muted`，跟随对比度档位。**没有标注语言的围栏不上色**：猜一门语法等于把散文画成代码。
- **一条消息可以改写后重发**。由内核已有的两件事组合而成：把对话回卷到那一回合，然后发送。`RewindResult` 的 TS 镜像少了 `conversationOk`，于是"动了文件但对话仍在"与"对话被截断"无从分辨——那会把消息发两次。类型补全，这一对进了 `wireparity`。
- **调用解析到的能力会到达卡片**，仅
```

### v1.38.8 — Reasonix CLI v1.38.8  (2026-09-14)
**判定：待评估** — 可能值得移植 · 命中 会话/session，需按 CUTLIST 红线复核

```
> 桌面端可靠性与易用性改进，包括统一会话持久化、目标生命周期修复和安装程序更新。

**发布渠道：稳定版 · v1.38.8**

[English →](https://reasonix.io/changelog/v1.38.8/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.8/)

## 使用攻略

- [**会话存储 v4**](https://github.com/esengine/DeepSeek-Reasonix/blob/42868fe65121ffbe72200726b54cd47c384ce509/docs/session-storage-v4.md) — 了解新的会话存储格式和迁移。
- [**会话 v4 实现报告**](https://github.com/esengine/DeepSeek-Reasonix/blob/42868fe65121ffbe72200726b54cd47c384ce509/docs/session-v4-implementation-report.md) — 会话 v4 的详细实现报告。

## 概览

**Reasonix v1.38.8 — Reasonix 1.38.8**

桌面端可靠性与易用性改进，包括统一会话持久化、目标生命周期修复和安装程序更新。

发布日期：2026-09-14

**Desktop 21 · CLI 10**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **统一会话持久化并支持大会话恢复** — 会话现在使用规范存储服务和新的 v4 格式，支持大会话恢复，不再受之前 128 MiB 重放上限限制。 ([#10257](https://github.com/esengine/DeepSeek-Reasonix/pull/10257))
- **[Desktop · CLI]** **修复目标生命周期恢复与宿主控制** — 恢复后的目标会在续跑轮次中保留原有任务内容，并拒
```

### studio-v2.15.0 — Reasonix Studio v2.15.0  (2026-09-14)
**判定：待评估** — 可能值得移植 · 命中 session/mcp/provider/edit/context，需按 CUTLIST 红线复核

```
本版的主线是**把"谁有权决定"和"谁有权改写"各自收回一处**：只有人能拍板的工具成为一条声明而不是三处分支，会话授权按它被问到的那个主体记录，委派运行需要越过写入围栏时向人发问而不是向派它出来的模型发问；同时一个会话被另一个窗口占用时改为只读打开——租约保护的从来是写回，不是阅读。供应商一侧，DeepSeek 目录、视觉能力与官方价格各自收敛为一份声明，九个逐厂商手写的迁移函数随之退役。界面一侧是一轮以实测为准的整理：阅读列、任务页、导航树的键盘可达、上下文折叠点说出是哪条界限并在读到它的地方修改。自 2.14.1 起 67 个提交。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。DeepSeek 的 flash 模型 id 改为 `deepseek-flash`，已安装的配置由升级改写而非弃置，价格、推理强度等以旧 id 为键的设置随之迁移。此前"只能由人批准"的会话授权若以裸工具名记录，会在下一次遇到时再问一遍——那条规则不是你给出的答案，是记录它的代码替你放宽的。

## 新增

### 权限：只有人能决定的事，是一条声明

- **三处声明合一，并因此补上了前一次修复漏掉的那一半**。"这个工具的授权要读它的主体"此前写在三个地方：`subjectRequiresHuman` 的分支、`subjectScopedTools` 表、以及测试里的一份副本。合并后暴露出一条更早的路径：`install_source` 的 `apply` 拿到 `high:...` 计划时，分级判定返回 Ask，而 Approver 为 nil 时 `unattendedAsk` 直接放行——YOLO 正是以 nil approver 构建的，**高风险自我扩展计划（常驻进程、生命周期钩子、外部服务）在该档下被静默批准，没有人看到过那张计划**。现在成员资格一处声明同时承载三个后果，加第四个工具只是一条表项。
- **「不再询问」只对它被问到的那个主体生效**。`Sessio
```

### v1.38.7 — Reasonix CLI v1.38.7  (2026-09-11)
**判定：待评估** — 可能值得移植 · 命中 compact，需按 CUTLIST 红线复核

```
> 桌面端可靠性与易用性改进，包括 Windows 启动修复、浏览器控制以及聊天记录布局修正。

**发布渠道：稳定版 · v1.38.7**

[English →](https://reasonix.io/changelog/v1.38.7/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.7/)

## 使用攻略

- [**Windows 应用身份**](https://github.com/esengine/DeepSeek-Reasonix/blob/0c35021eb330f38cadde7831a8bb561d5988a970/docs/WINDOWS_APP_IDENTITY.md) — Reasonix 桌面端如何隔离其 Windows 任务栏身份与 Studio，并管理快捷方式。
- [**Windows 启动恢复**](https://github.com/esengine/DeepSeek-Reasonix/blob/0c35021eb330f38cadde7831a8bb561d5988a970/docs/WINDOWS_STARTUP_RECOVERY.md) — Windows 上从失效桌面壳恢复的设计与验收标准。
- [**桌面浏览器**](https://github.com/esengine/DeepSeek-Reasonix/blob/0c35021eb330f38cadde7831a8bb561d5988a970/docs/DESKTOP_BROWSER.md) — 内置浏览器控制设置与 Chrome 登录状态导入。
- [**聊天记录投影**](https://github.com/esengine/DeepSeek-Reasonix/blob/0c35021eb330f38cadde7831a8bb561d5988a970/docs/TRANSCRIPT_PROJECTION.md) — 聊天记录的历史快照与实时事件统一投影。
- [**检查点**](
```

### studio-v2.14.1 — Reasonix Studio v2.14.1  (2026-09-11)
**判定：观察** — 无关键词命中，扫一眼

```
本版修三处「界面没有说话」：按需加载的设置页取件失败时不再带走整个窗口，弹出菜单不再被正文的卡片盖住，以及一次仍在执行的调用会报出它已经跑了多久。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。

## 新增

- **仍在执行的调用报出已运行时长**。此前一次调用跑着的时候，屏幕上唯一在动的是 `sympulse`——一枚 14px 符号 1.9 秒一次呼吸，而脉冲在第 2 秒与第 2 分钟完全相同。逐卡片采样：四次 600ms 以内的调用整个生命周期各只有 1 种文本，7.4 秒的那一次只有 4 种（0.41 次变化/秒），所以一条跑半分钟的命令就是一行字不动半分钟。读数落在已完成时长原本占用的槽位，调用结束时数字停住而非在别处出现新值；一秒以内不绘制，那一档调用从未显得停滞；运行期间不绘制长度条，长度条是相对已知时长的量度，而此刻无人知道总长。内核的 `startedAt` 未被采用：它是内核所在机器的 unix 毫秒，远程会话中与窗口不是同一个时钟，相减会把时钟偏差计为耗时。计时只走窗口自身的时钟，自窗口观察到该调用运行时起算。改动后同一次回合复测：7.4 秒的调用由 4 种文本增至 11 种，四次短调用仍各为 1 种。
  
  同期确认线程一侧无需改动：18 秒的回合中主线程仅出现 1 次 131ms 的长任务，运行期间切换视图连续六次响应均在 62–71ms。

## 修复

- **按需加载取件失败时丢失的是面板，不是窗口**。2.14.0 将设置页拆为独立 chunk。自更新会在窗口仍然打开时替换这些文件（Linux 的 `.deb` 由 dpkg 直接替换 SPA 目录），该窗口持有的文档所请求的 chunk 名已不存在，被拒绝的导入在渲染期抛出，而其上没有错误边界：React 卸载整棵树，界面变为空白。转录正文以同样方式按需加载，其调用处一直包裹 `Boundary`，一次抛出至多让一条消息退回纯文本；设置页此前只有 `Suspense`，其
```

### studio-v2.14.0 — Reasonix Studio v2.14.0  (2026-09-11)
**判定：待评估** — 可能值得移植 · 命中 会话/compact，需按 CUTLIST 红线复核

```
本版的主线是**「这个界面能做什么」从一份名单变成一个可以验证的集合**：每个可交互的控件写上身份，一套读源码结构的普查判定哪些输入会写宿主，其中十六条不变量在 CI 里拦着——一个被证明会写、却没有名字的输入不能进主干。同期把「一个回合」收成一条边界：回合从哪条消息开始、一次调用是谁要的、一份轨迹覆盖了会话的多少，都由宿主记录，而不是留给读者按位置去猜。压缩这一侧则是先有账单再有决定：一次折叠报的是它真正发生的调用，`/compact` 不再因为问了两遍就买两次摘要。自 2.13.0 起 89 个提交。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。

## 新增

### 这个界面能做什么，是一个可以验证的集合

- **一百三十二个动作 id，一份注册表**。身份是产品自己的：一个 id 写成 `<界面>.<意图>`，在控件上写一次、在 `actions.ts` 里再写一次，于是两边可以不一致并且会被抓住——共用一个常量只会让检查拿一个值和它自己比。属性只承载归属，是哪一条记录由 `data-target` 说，给的是哪个答案由 `data-value` 说，所以一行渲染七十次仍然是一份契约，「取消」永远不会变成一个身份。
- **一套普查读结构，不读措辞**。426 个交互根，每一条判定要么带着一个正面证据，要么带着挡住它的那条开放边。十六条不变量在 CI 里跑，`UNDECLARED_MUTATION == 0` 是它存在的理由，并且已经在真实缺陷下重新亮红过三次——一个藏住 prop 链的 memo 别名、一个藏住另一条的 JSX 展开，都不是装饰性的绿灯。
- **一次写入需要一个有人刻意做出的手势**。重命名会话、移动压缩起点、重命名面板此前只在失焦时保存，而失焦会因为没人瞄准的原因触发——点到别处、按 Tab、窗口消失、元素被移除。回车现在提交并带上身份；失焦仍然保存，因为点开确实是一种回答。
- **什么东西证明一个值是 Promise，在 `
```

### v1.38.6 — Reasonix CLI v1.38.6  (2026-09-11)
**判定：跳过** — 与轻便版无关 · 命中 electron

```
> 修复了导致官方桌面安装包无法启动的构建不匹配问题。

**发布渠道：稳定版 · v1.38.6**

[English →](https://reasonix.io/changelog/v1.38.6/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.6/)

## 概览

**Reasonix v1.38.6 — 修复桌面端无法启动**

修复了导致官方桌面安装包无法启动的构建不匹配问题。

发布日期：2026-09-11

**Desktop 4 · CLI 1**

## 桌面端更新

### 重点内容

- **[Desktop]** **官方桌面安装包可正常启动** — 修复 v1.38.5 在全新安装或升级后出现 build_mismatch、无法打开的问题。桌面壳与内置服务现在使用一致的发布版本信息。 ([#10089](https://github.com/esengine/DeepSeek-Reasonix/pull/10089))

### 修复

- **[Desktop]** **发布前验证正式包启动** — Windows、macOS 和 Linux 发布检查现在以正式模式启动打包应用，要求服务握手、界面到服务的实际调用及正常退出全部成功。构建信息缺失或无效时仍会报错。 ([#10089](https://github.com/esengine/DeepSeek-Reasonix/pull/10089))

## CLI 端更新

此板块没有功能或修复条目；相关说明请查看下方升级提醒和风险提示。

## 升级提醒

- **[Desktop]** **安装完整包恢复启动** — 如果 v1.38.5 无法打开，请下载并安装 v1.38.6 完整包，无需清理配置或会话数据。从 v1.38.3 或更早 Wails 版本首次升级到 Electron 时，也需要手动安装完整包；旧版更新器无法安装新的目录结构。 ([#10089](https://github.com/esen
```

### v1.38.5 — Reasonix CLI v1.38.5  (2026-09-10)
**判定：跳过** — 与轻便版无关 · 命中 electron/docs/

```
> Reasonix 桌面端迁移至 Electron，新增 DeepSeek V4.1 Flash 图片输入、OpenCode Go 提供商预设、持久工具恢复和独立 dock 标签。本版本包含 v1.38.3 以来的改动、macOS 签名与公证修复，以及 Windows 扩展关闭稳定性修复；v1.38.4 未公开发布。

**发布渠道：稳定版 · v1.38.5**

[English →](https://reasonix.io/changelog/v1.38.5/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.5/)

## 使用攻略

- [**工具恢复**](https://github.com/esengine/DeepSeek-Reasonix/blob/645c156cdc14d577b9c9592e468e1d1530f29d5d/docs/TOOL_RECOVERY.md) — 了解如何在桌面和远程会话中恢复中断的工具执行。
- [**读取证据生命周期**](https://github.com/esengine/DeepSeek-Reasonix/blob/645c156cdc14d577b9c9592e468e1d1530f29d5d/docs/READ_EVIDENCE_LIFECYCLE.md) — 了解读取覆盖与写入守卫如何解耦，以避免重复工作。
- [**输入区控件**](https://github.com/esengine/DeepSeek-Reasonix/blob/645c156cdc14d577b9c9592e468e1d1530f29d5d/docs/COMPOSER_CONTROLS.md) — 关于输入区实时读数和回合指标准确性改进的详细信息。

## 概览

**Reasonix v1.38.5 — Reasonix v1.38.5**

Reasonix 桌面端迁移至 Electron，新增 DeepSeek V4.1 Flash 图片输入、Op
```

### v1.38.3 — Reasonix CLI v1.38.3  (2026-09-09)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> 此版本改进了模型设置持久化、运行时状态一致性、读取证据处理以及桌面界面优化，并修复了关闭、设置布局和技能诊断等问题。

**发布渠道：稳定版 · v1.38.3**

[English →](https://reasonix.io/changelog/v1.38.3/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.3/)

## 使用攻略

- [**模型设置**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/MODEL_SETTINGS.md) — 了解模型偏好和供应商连接的保存与生效时机。
- [**运行时状态**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/RUNTIME_STATE.md) — 了解本地和远程会话状态如何统一。
- [**本轮结果**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/TURN_RESULTS.md) — 查看每轮记录的文件改动、检查结果及其证据。
- [**输入栏控件**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/COMPOSER_CONTROLS.md) — 探索优化后的输入栏控件和反馈。
- [**能力诊断**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b57
```

### v1.38.2 — Reasonix CLI v1.38.2  (2026-09-08)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> 此版本提升了会话可靠性、模型服务配置和桌面性能。引入了仅追加会话日志与版本 head、独立网页搜索模型分配、统一图片理解，并修复了导航、取消和 CI 稳定性等多项问题。

**发布渠道：稳定版 · v1.38.2**

[English →](https://reasonix.io/changelog/v1.38.2/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.2/)

## 概览

**Reasonix v1.38.2 — Reasonix 1.38.2**

此版本提升了会话可靠性、模型服务配置和桌面性能。引入了仅追加会话日志与版本 head、独立网页搜索模型分配、统一图片理解，并修复了导航、取消和 CI 稳定性等多项问题。

发布日期：2026-09-08

**Desktop 46 · CLI 6**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **仅追加会话日志与版本 head** — 会话现在使用仅追加 DAG 日志（schema 2），将每次更改记录为版本 head。分叉、回退和版本选择均在同一日志内完成，不再创建单独文件，提高了可靠性并支持并发写入。 ([#9908](https://github.com/esengine/DeepSeek-Reasonix/pull/9908), [#9910](https://github.com/esengine/DeepSeek-Reasonix/pull/9910), [#9912](https://github.com/esengine/DeepSeek-Reasonix/pull/9912), [#9913](https://github.com/esengine/DeepSeek-Reasonix/pull/9913), [#9916](https://github.com/esengine/DeepSeek-Reasonix/pull/9916), [#9917](https:/
```

### desktop-v1.38.3 — Reasonix Desktop v1.38.3  (2026-09-09)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> 此版本改进了模型设置持久化、运行时状态一致性、读取证据处理以及桌面界面优化，并修复了关闭、设置布局和技能诊断等问题。

**发布渠道：稳定版 · v1.38.3**

[English →](https://reasonix.io/changelog/v1.38.3/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.3/)

## 使用攻略

- [**模型设置**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/MODEL_SETTINGS.md) — 了解模型偏好和供应商连接的保存与生效时机。
- [**运行时状态**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/RUNTIME_STATE.md) — 了解本地和远程会话状态如何统一。
- [**本轮结果**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/TURN_RESULTS.md) — 查看每轮记录的文件改动、检查结果及其证据。
- [**输入栏控件**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937d7431ffb2b5760feeef46ccf35eecab/docs/COMPOSER_CONTROLS.md) — 探索优化后的输入栏控件和反馈。
- [**能力诊断**](https://github.com/esengine/DeepSeek-Reasonix/blob/27a409937
```

### v1.38.1 — Reasonix CLI v1.38.1  (2026-09-06)
**判定：待评估** — 可能值得移植 · 命中 会话/mcp，需按 CUTLIST 红线复核

```
> 此版本恢复了提问提交与恢复流程，隔离了过期的桌面会话状态，统一了 Ask 与决策弹窗，并修复了 DeepSeek 周末计费。

**发布渠道：稳定版 · v1.38.1**

[English →](https://reasonix.io/changelog/v1.38.1/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.1/)

## 使用攻略

- [**桌面提示身份**](https://github.com/esengine/DeepSeek-Reasonix/blob/a4ae5ff6b98a37aaf9c212454cd0cc3ed5008559/docs/DESKTOP_PROMPT_IDENTITY.md) — 桌面提示卡片如何跨轮次、运行时和重连进行标识与隔离。
- [**会话恢复与并行**](https://github.com/esengine/DeepSeek-Reasonix/blob/a4ae5ff6b98a37aaf9c212454cd0cc3ed5008559/docs/SESSION_RECOVERY_AND_PARALLELISM.md) — Go 重写中统一的会话恢复与并行工作生命周期契约。
- [**工具契约**](https://github.com/esengine/DeepSeek-Reasonix/blob/a4ae5ff6b98a37aaf9c212454cd0cc3ed5008559/docs/TOOL_CONTRACT.md) — 关于工具参数验证、能力恢复、软收敛、兼容性和缓存影响的双语指南。

## 概览

**Reasonix v1.38.1 — 桌面稳定性与恢复修复**

此版本恢复了提问提交与恢复流程，隔离了过期的桌面会话状态，统一了 Ask 与决策弹窗，并修复了 DeepSeek 周末计费。

发布日期：2026-09-06

**Desktop 18 · CLI 4**

## 桌面端更新

### 重点内容

- **[D
```

### studio-v2.13.0 — Reasonix Studio v2.13.0  (2026-09-06)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
本版的主线是**委派与运行图不再靠"边跑边累加"来知道发生过什么**：一次委派在能够动作之前先落盘，运行图从这些持久事实重建而不是从事件流累积，于是一次崩溃留下的是可读的证据而不是一段无人认领的空白。同期把拒绝从"服务器写的句子"改成宿主自己的代码，并给这个界面里"一个人能做什么"编了一份有名字的清单。自 2.12.0 起 98 个提交。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。

## 新增

### 委派：先记录，再动作

- **一次委派在运行前就是持久的**。此前记录发生在运行之后，所以被中断的那一次不在任何地方——既不在运行图里，也不在恢复能看到的地方。现在顺序反过来：先落盘，再交给调度器。
- **运行图从持久事实重建**，而不是把增量流折进一个状态。快照因此并入编号流而不是另开一支，读者拿到的是权威而不是一段需要自己重放的历史。
- **执行身份不再是父调用的**。一次委派、一次采纳、一个被调度器拒绝而排队的条目，各自记录自己是什么：谁的答案被复用、扇出声明过的顺序、调度器从未接纳的那一次欠存储什么——都不再由调用方的身份代答。
- **被调用方停下的运行不是失败的运行**。两者此前记同一个结局。

### 裁决：问一个人之前先写下来

- **屏障先于问题成立**。此前是先问、后记，于是崩在中间时，一个人被问过一件宿主没有任何记录说自己欠着的事。现在注册即是它可被回答的前提；写不下去就不问。
- **下一个请求被告知死掉的运行在等什么**，后继回合继承它被交给的那次中断——中断是宿主的状态，不是让模型去猜的下游症状。

### 拒绝：代码，不是句子

- **HTTP 状态在它变成一句话的那一刻就不再是数字**。插件与 MCP 的失败此前把传输状态当成领域身份，把服务器自己的措辞当成分类；一台写不进磁盘的机器因此被报成"你的请求有错"。
- **每一条 inbox 拒绝以代码到达前端**，一条拒绝路径而不是二十五条各自为政。
- **一个服务
```

### v1.38.0 — Reasonix CLI v1.38.0  (2026-09-05)
**判定：待评估** — 可能值得移植 · 命中 mcp/context，需按 CUTLIST 红线复核

```
> 此版本将网络搜索与主对话分离，增强协议恢复可靠性，并统一桌面管理页面。同时改进了链接菜单、更新重启稳定性、模型图像能力处理以及会话操作。

**发布渠道：稳定版 · v1.38.0**

[English →](https://reasonix.io/changelog/v1.38.0/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.38.0/)

## 使用攻略

- [**管理页面**](https://github.com/esengine/DeepSeek-Reasonix/blob/94ded620594fa0a6d25f65cd3de94fec1e56eca6/docs/MANAGEMENT_PAGES.md) — 了解如何使用统一的设置、回收站和自动化管理页面。
- [**模型能力**](https://github.com/esengine/DeepSeek-Reasonix/blob/94ded620594fa0a6d25f65cd3de94fec1e56eca6/docs/MODEL_CAPABILITIES.md) — 了解模型能力的发现与覆盖方式。
- [**模型设置**](https://github.com/esengine/DeepSeek-Reasonix/blob/94ded620594fa0a6d25f65cd3de94fec1e56eca6/docs/MODEL_SETTINGS.md) — 使用新编辑器配置提供程序和模型设置。
- [**网络搜索**](https://github.com/esengine/DeepSeek-Reasonix/blob/94ded620594fa0a6d25f65cd3de94fec1e56eca6/docs/WEB_SEARCH.md) — 独立网络搜索功能的详细信息。

## 概览

**Reasonix v1.38.0 — Reasonix 1.38：独立搜索、可靠恢复与统一桌面工作区**

此版本将网络搜索与主对话分
```

### v1.37.0 — Reasonix CLI v1.37.0  (2026-09-04)
**判定：待评估** — 可能值得移植 · 命中 agent/context/compact，需按 CUTLIST 红线复核

```
> 此版本简化了 Agent 核心，改进了提供商能力处理，稳定了桌面滚动，并新增 ModelScope 提供商预设。

**发布渠道：稳定版 · v1.37.0**

[English →](https://reasonix.io/changelog/v1.37.0/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.37.0/)

## 使用攻略

- [**Agent 核心简化**](https://github.com/esengine/DeepSeek-Reasonix/blob/a2a89ee61852d828dbc7a84d8a24f8f1ca070afd/docs/AGENT_CORE_SIMPLIFICATION.md) — 了解简化的 Agent 循环、显式的 planner 和 continuation 策略，以及新的确定性完成流程。
- [**模型能力**](https://github.com/esengine/DeepSeek-Reasonix/blob/a2a89ee61852d828dbc7a84d8a24f8f1ca070afd/docs/MODEL_CAPABILITIES.md) — 关于模型级视觉能力和新能力元数据契约的详细信息。
- [**推理提供商**](https://github.com/esengine/DeepSeek-Reasonix/blob/a2a89ee61852d828dbc7a84d8a24f8f1ca070afd/docs/REASONING_PROVIDERS.md) — 针对 OpenAI 兼容提供商的推理回放和恢复行为更新。

## 概览

**Reasonix v1.37.0 — Reasonix 1.37.0**

此版本简化了 Agent 核心，改进了提供商能力处理，稳定了桌面滚动，并新增 ModelScope 提供商预设。

发布日期：2026-09-04

**Desktop 20 · CLI 6**

## 桌面端更新

#
```

### studio-v2.12.0 — Reasonix Studio v2.12.0  (2026-09-04)
**判定：待评估** — 可能值得移植 · 命中 cache/mcp/provider/agent，需按 CUTLIST 红线复核

```
本版的主线是**远程工作区第一次真正可用**：此前这条线没有发布过远端能装的内核，所以「在另一台机器上开工作区」在任何配置下都装不上东西，而失败会报成一个与真因无关的错误码。同期把项目自身状态移出跨项目共享的缓存前缀（首轮缓存命中率实测 4.2% → 54.7%），并把 Controller 按生命周期拆成协作者。自 2.11.0 起 56 个提交。

**升级路径**：无需人工步骤。三平台照旧自更新——Linux 走 `.deb`，Windows 运行下一个安装器，macOS 替换自身 bundle。

## 新增

### 远程工作区：这条线现在会发布远端要装的内核

- **发布 CLI 归档**。此前 studio 线只发桌面包，而远端安装的三条路里有两条要按版本名去取一个 release。它们取的地址不存在（tag 是 `studio-v2.11.0`，取的却是 `/download/v2.11.0/`），于是双双在发网络请求之前就被拒，只剩 npm 一条——而 npm 上那个包属于 1.x 线，装下来低于开工作区所需的内核版本。现在每次发布同时产出六个平台的 `reasonix-<os>-<arch>` 归档与 `SHA256SUMS`，`releaseasset.Line` 表达 tag 命名空间（它是 tag 前缀，不是 `update.Line` 那种安装布局——一个类型同时回答两件事，就会让 tag 前缀去决定 `.deb` 装到哪）。
- **内核声明自己的版本**。打包脚本此前不注入版本，于是发布出去的内核自称 `dev`，而按版本取 release 的两条路都拒绝一个非发布版本。顺带修好了一个从未生效的门：`ParseVersion` 读不了 `studio-v2.11.0`（它在第一个连字符处断开），版本因此为空，而「没说版本」按设计是放行的——所以内核版本下限对整条 studio 线从来没有真正生效过。注入的是 `v2.12.0` 这种 semver 而非完整 tag，门才成立。
- **取过一次的发布不再取第二次**。为一台够不到 rel
```

### v1.36.0 — Reasonix CLI v1.36.0  (2026-09-02)
**判定：待评估** — 可能值得移植 · 命中 session，需按 CUTLIST 红线复核

```
> 此版本为桌面端新增粘性上下文文件固定，为桌面端与 CLI 新增协作式会话接管，并强制完成长文件读取。同时带来大量 CLI 与桌面端的稳定性与性能修复。

**发布渠道：稳定版 · v1.36.0**

[English →](https://reasonix.io/changelog/v1.36.0/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.36.0/)

## 使用攻略

- [**会话所有权**](https://github.com/esengine/DeepSeek-Reasonix/blob/403acc1128a3367108d8c8f7d0ace54c83f368b2/docs/SESSION_OWNERSHIP.md) — 了解协作式会话接管与取回如何在桌面端与 CLI 之间工作。
- [**会话所有权（中文）**](https://github.com/esengine/DeepSeek-Reasonix/blob/403acc1128a3367108d8c8f7d0ace54c83f368b2/docs/SESSION_OWNERSHIP.zh-CN.md) — 协作式会话接管与取回在桌面端和 CLI 中工作方式的中文指南。

## 概览

**Reasonix v1.36.0 — Reasonix 1.36：粘性上下文固定、会话接管与长文件读取强制**

此版本为桌面端新增粘性上下文文件固定，为桌面端与 CLI 新增协作式会话接管，并强制完成长文件读取。同时带来大量 CLI 与桌面端的稳定性与性能修复。

发布日期：2026-09-02

**Desktop 14 · CLI 16**

## 桌面端更新

### 重点内容

- **[Desktop]** **粘性上下文文件固定** — 将会话中的工作区文件固定，使其在上下文压缩后仍可逐字保留。固定文件在下一次接受的轮次前以仅追加的用户角色修订形式传递，不会重写系统提示或使提示缓存失效。 ([#9689](https
```

### studio-v2.11.0 — Reasonix Studio v2.11.0  (2026-09-01)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 updater/nsis

```
本版把 Studio 的外壳从 Wails 换成 Electron：窗口、打包、发布线、三平台自更新与全部 OS 能力都重新落到内核与传输层上，两个外壳跑同一份前端。另有三条主线：Plan 生命周期成为带授权世代的宿主态，`ask` 成为回合屏障；沙盒把外网与宿主授权拆成两轴，凭据文件对 bash 也拒绝；上下文维护改由经济边界触发，长回合内可反复折叠，`recall` 可检索已折叠区。自 2.10.0 起 131 个提交。

**升级路径**：Windows 安装器改为按用户安装，并在安装时接管旧的 Wails 全机安装（会弹一次卸载确认，拒绝也不影响本次安装）；Linux 的 `.deb` 与旧包同名，`dpkg` 按升级处理；macOS 替换自身 bundle。

## 新增

### Studio 改由 Electron 承载

- 控制面首次落到真实 socket 上。此前 Wails 的资源服务器把 `hub.Handler()` 挂成进程内中间件——没有端口、没有 CORS、没有第二条传输，独立进程的渲染器够不到。现在 hub 跑在 loopback HTTP 上，`NewLoopbackGate` 是随之必须存在的边界：策略来自打开监听的宿主而非配置，请求必须发往本监听、必须以本监听为 origin 才能改动、必须携带本次启动铸出的凭据。无 origin 的读放行（顶层导航不发 origin），无 origin 的写拒绝。四类拒绝各有独立错误码。凭据只走 cookie（query token 会落进请求行、历史与 referrer），由宿主设置，页面 JS 读不到。
- Electron 外壳：内核由外壳派生，stdout 传一行版本化 JSON 握手（版本不认识就拒绝启动，日志一律走 stderr），stdin 是租约（父进程一端关闭即内核排空，覆盖崩溃与退出，三平台无信号参与）。页面落在 `/_studio/`，一条前缀规则即完成路由——反过来「枚举内核所有路由、其余落到页面」是资源服务器逼出来的形状，内核每加一个端点就要改一次。渲染器沙盒化、con
```

## 二、上游 Commits（按改动域归类）

### 其他（60 条）

- `21722a2` Merge pull request #10867 from esengine/fix/studio-provider-protocol-hint-wrap — **待评估**
- `19dee62` fix(studio): put the protocol hint below its switcher in a service's detail — **观察**
- `d96ca54` Merge pull request #10861 from esengine/fix/studio-explorer-refresh — **观察**
- `1674279` Merge pull request #10859 from esengine/fix/studio-running-step-visible — **观察**
- `39d5317` fix(studio): a running step moves on its own row, and step rows lose their blank column — **观察**
- `0b99a61` fix(studio): re-read the explorer tree when the window is looked at again — **观察**
- `61953d1` Merge pull request #10855 from esengine/fix/studio-10851-cjk-step-label — **观察**
- `c2ce043` fix(studio): keep the receipt label on one line beside a long command — **观察**
- `53c5683` Merge pull request #10854 from esengine/fix/studio-10792-multi-edit-all-failures — **待评估**
- `f0a0474` feat(tools): multi_edit reports every failing step in one call — **观察**
- `76ae0ee` Merge pull request #10850 from esengine/fix/studio-review-untrusted-checkout — **观察**
- `ae4ab51` fix(cli): reasonix review ignores tools and skills the reviewed checkout configures — **观察**
- `144e6e9` Merge pull request #10846 from esengine/fix/studio-hooks-planner-guardian-review — **观察**
- `c4ea325` fix(hooks): run configured tool hooks in subagents, the planner, the guardian and reasonix review — **待评估**
- `40de19b` Merge pull request #10838 from c020627/docs-studio-wails-residue — **观察**
- `7ee4bbb` ci(release): studio publishes the CLI to npm and Homebrew only when told to — **跳过**
- `040a4b5` Merge pull request #10841 from esengine/chore/ack-token-studio — **跳过**
- `ac2bc07` ci(acknowledgments): open the weekly PR with a token that triggers CI — **跳过**
- `578c134` Merge pull request #10828 from onionviolet/codex/studio-version-empty-fallback — **观察**
- `9a999f7` docs: port the retired-Wails wording cleanup to studio — **观察**

