# 上游变更简报（自 2026-09-26 起）

- 上游：`esengine/DeepSeek-Reasonix`（MIT © Reasonix Contributors）
- 移植要求：**保留 MIT 版权声明**，改动的源文件头部补 `Ported from DeepSeek-Reasonix (MIT)。`
- 红线复核：`docs/CUTLIST.md` 第 0 节（UI 1:1 / CodeMirror / 字体分片 / Go 内核 / yomm）

## 一、上游 Release 变更

### v1.39.7 — Reasonix CLI v1.39.7  (2026-10-02)
**判定：观察** — 无关键词命中，扫一眼

```
> 桌面端修复：会话用量统计清零、长轮次历史分页、远端会话切换、分叉会话和编辑目标，并部分修复迁移后会话消失的问题。

**发布渠道：稳定版 · v1.39.7**

[English →](https://reasonix.io/changelog/v1.39.7/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.7/)

## 概览

**Reasonix v1.39.7 — Reasonix 1.39.7**

桌面端修复：会话用量统计清零、长轮次历史分页、远端会话切换、分叉会话和编辑目标，并部分修复迁移后会话消失的问题。

发布日期：2026-10-02

**Desktop 7 · CLI 0**

## 桌面端更新

### 重点内容

- **[Desktop]** **切换会话后再切回来，用量统计不再清零** — 当前存储格式的会话没有保存用量快照，切换到别的会话再切回来后，请求数、令牌数、费用和已读文件记录都会归零。现在这些数据按会话保存，打开会话时恢复；文件缺失或损坏时回退为空，不会影响切换。 ([#11621](https://github.com/esengine/DeepSeek-Reasonix/pull/11621))
- **[Desktop]** **远端会话忙碌时切换，消息和历史不再丢失** — 远端会话处于过渡状态时提交的消息可能直接失败，忙碌时提交的消息不会立刻出现在队列里，回到访问过的会话还要等完整历史加载。现在临时过渡会在保留消息和附件的前提下重试，排队的消息立即显示，运行中的会话在后台保持连接，访问过的会话先显示已有历史，再与权威历史对账。 ([#11345](https://github.com/esengine/DeepSeek-Reasonix/pull/11345), [#11512](https://github.com/esengine/DeepSeek-Reasonix/pull/11512) by @XTLine)

### 修复

-
```

### studio-v2.26.0 — Reasonix Studio v2.26.0  (2026-10-02)
**判定：待评估** — 可能值得移植 · 命中 plugin/provider/model/diff/tool/agent，需按 CUTLIST 红线复核

```
本版让 Studio 终端界面补齐 1.x 的连接引导、排队与引导命令、设置命令和 YOLO 模式，设置里新增社区与贡献者入口，并修复已保存的默认模型不在配置里时 Studio 启动失败、DeepSeek 请求偶发连接错误、子代理状态一直显示运行中等问题。

## 新增

- 终端界面：没有可用密钥时启动即打开「配置连接」面板，随时可用 `/setup`（别名 `/auth`）再打开；支持筛选连接、掩码输入密钥、Ctrl+T 测试、Enter 保存 (#11682, #11493)
- 终端界面新增 `/queue`、`/steer`、`/takeover`、`/status`、`/export` 和 `/copy`，名称与用法同 1.x (#11683, #11493)
- 终端界面新增 14 个设置命令，名称与用法同 1.x：`/cls`、`/rename`、`/todo`、`/forget`、`/reload`、`/effort`、`/verbose` 等 (#11685, #11493)
- 终端界面的设置命令还有 `/diff-fold`、`/sandbox`、`/output-style`、`/reasoning-language`、`/theme`、`/language`、`/currency` (#11685, #11493)
- 终端界面：YOLO 加入 Shift+Tab 的模式循环，Ctrl+Y 只需按一次即生效；底栏显示 `工作区@分支`；大段粘贴自动折叠 (#11687, #11493)
- 设置的「版本」页新增「社区与贡献者」：QQ 群（群号可复制、加群按钮、二维码）、Discord、GitHub 问题页，以及可展开的贡献者列表 (#11660)
- 「版本」页在版本下方新增「作者与维护者」一行；抖音号放在社区区块最下方，二维码默认折叠 (#11660)
- 已安装插件的详情里，提示模板显示可直接输入的完整调用名，例如 `/插件名:模板名` (#11688 by @KHG420)
- 已安装插件的详情里，打包的子代理会列出数量和调用方式 (#
```

### v1.39.6 — Reasonix CLI v1.39.6  (2026-10-01)
**判定：观察** — 无关键词命中，扫一眼

```
> 修复升级后清不掉的配置告警、停顿后连接已断导致的请求失败、Windows 上的 shell 命令问题，以及多处桌面端会话与侧边栏问题。

**发布渠道：稳定版 · v1.39.6**

[English →](https://reasonix.io/changelog/v1.39.6/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.6/)

## 概览

**Reasonix v1.39.6 — Reasonix 1.39.6**

修复升级后清不掉的配置告警、停顿后连接已断导致的请求失败、Windows 上的 shell 命令问题，以及多处桌面端会话与侧边栏问题。

发布日期：2026-10-01

**Desktop 18 · CLI 7**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **升级后不再残留清不掉的配置告警** — 从 1.38 升级到 1.39.5 后，旧版本写入的项目权限规则，以及同一个 Windows 文件夹的不同写法，会一直弹出配置有问题的提示，尽管对话本身正常。现在已有授权覆盖的规则会被识别，尚未批准的项目声明会保留供查看，不再被当作配置失败。项目设置仍然不能授予权限，也不能恢复已撤销的授权。 ([#11431](https://github.com/esengine/DeepSeek-Reasonix/pull/11431) by @SivanCola)
- **[Desktop · CLI]** **连接在空闲时已断开，不再让下一轮对话失败** — 停顿一段时间后，下一轮对话可能因 `unexpected EOF` 失败，原因是请求走了已被对端断开的复用空闲连接；自 1.39.0 起请求只发送一次，所以这个失败直接暴露给了用户。现在只有在请求使用了复用的空闲连接、且没有收到任何响应字节时，才会在新连接上重发一次；其他失败、超时和取消不会重发。 ([#11271](https://github.com/esengine/
```

### studio-v2.25.0 — Reasonix Studio v2.25.0  (2026-10-02)
**判定：待评估** — 可能值得移植 · 命中 cache/session/插件/plugin/mcp/model/diff/edit/agent/context，需按 CUTLIST 红线复核

```
本版加入子代理记录入口、文件管理器菜单与经同意的 URL 征询，并修复 Windows 远端打不开项目、存储迁移丢项目清单、引导按钮点不到、远端用 nvm 装的 npm 找不到、模型因上下文提示提前停手、底部栏数字跳动等问题。

## 新增

- 右下角的子代理读数在委派结束后保留，可点开完整记录；嵌套输出被截断时可「显示全部」 (#11529, #11505)
- 项目「⋯」菜单新增「在文件管理器中显示」 (#11533, #11524)
- MCP 服务器要用户去浏览器完成外部步骤时，改为经同意的 URL 征询，回环与私有地址会警告 (#11475 by @KHG420)
- 手动调整的项目顺序会被保存，并且不改变启动时打开的项目 (#11458 by @KHG420)
- 无头 `reasonix run` 在未信任目录里被拒绝时，会说明原因与补救办法 (#11494, #11493)
- 指南新增「Hooks」一节，说明事件、settings.json 写法、退出码与限制 (#11562)
- 没有本机文件夹选择器的浏览器/无头部署，「打开项目」改为弹出路径输入框，按内核所在机器上的路径添加工作区 (#11613 by @Harbor404, #11574 fixed in #11613 by @Harbor404)
- 新增会话开始时注入上下文的作者示例包 (#11590 by @KHG420)

## 变更

- 输入框右键的编辑菜单（剪切、复制、粘贴等）跟随界面语言 (#11530, #11524)
- 用户自己取消的回合不再画成错误卡，输入框显示「已取消」 (#11551, #11559)
- 上下文预算与「引导未生效」提示按界面语言显示，终端对用户原文做清洗并限长 (#11552, #11524)
- 排队暂停的原因按界面语言显示，不再出现英文内核原文 (#11555)
- 用户跳过提问后，排队的引导按原顺序继续派发；停止、报错、超时仍保持暂停 (#11563)
- 启动时不再同步整理会话历史，改为后台进行，历史很多的机器冷启动更快 (#11488)

```

### studio-v2.24.0 — Reasonix Studio v2.24.0  (2026-10-01)
**判定：待评估** — 可能值得移植 · 命中 plugin/mcp/provider/model/diff/agent/context，需按 CUTLIST 红线复核

```
本版加入应用内反馈和每个模型单独的上下文设置，并修复重启后首次启动误报、远程中转断线原因不明等问题。

## 新增

- 应用内反馈：可附截图和昵称，得到受理编号，并在「我的反馈」里查看进度、维护者回复和追问 (#11432 by @esengine, #11435 by @esengine, #11445 by @esengine, #11446 by @esengine)
- 终端支持 `/feedback`，可提交反馈、查看进度并回复 (#11432 by @esengine, #11445 by @esengine)
- 每个模型可单独设置上下文窗口和最大输出，未设置的沿用服务商的值 (#11422 by @esengine)
- 技能支持 `disable-model-invocation`（禁止模型调用）和 `user-invocable`（不出现在斜杠列表） (#11439 by @esengine)
- MCP 服务器可单独禁用其中的某个工具 (#11468 by @KHG420)
- 市场插件可以来自 GitHub 仓库的子目录 (#11449 by @KHG420)
- 终端问答在答完最后一题时可自动提交，默认关闭 (#11357 by @BuGlessRB)

## 变更

- 远程中转连接失败时分别提示来源被拒、被限流、离线、网关不可达等具体原因 (#11438 by @esengine)
- 启动等待延长到 60 秒，3 秒后显示「正在启动」窗口，提前退出时自动重试一次 (#11479 by @esengine)
- 市场读取失败可重试，并在重试后保持焦点 (#11442 by @KHG420, #11444 by @KHG420, #11465 by @KHG420)
- 安装信任披露按界面语言显示，自动化事件名称也一样 (#11453 by @KHG420, #11454 by @KHG420)
- 更新或安装进行中，对应的行和设置导航会被锁定，避免并发操作 (#11450 by @KHG420, #11460 by @KHG420, #1
```

### studio-v2.23.0 — Reasonix Studio v2.23.0  (2026-09-30)
**判定：待评估** — 可能值得移植 · 命中 sse/stream/session/plugin/terminal/mcp/provider/model/diff/agent/context/compact，需按 CUTLIST 红线复核

```
本版让终端能把 diff 排成可读的差异视图，市场可以在明确信任后安装未固定版本的已批准包，更新优先走镜像并支持续传，并补上模型服务空闲超时。

## 新增

- 终端里的 diff 或 patch 代码块、以及整段输出就是 diff 的命令结果，会渲染成差异视图，也可用 `[cli].diff_formatter` 指定外部格式化命令 (#11201 by @BuGlessRB)
- 可以为每个模型服务单独设置流空闲超时 `idle_timeout_seconds`，超时后中止等待 (#11258 by @BuGlessRB)
- 市场里已批准但未固定版本的包，在你明确表示信任后可以安装 (#11317 by @esengine)
- 市场优先展示可安装的条目，并标出已安装的能力 (#11292 by @KHG420)
- 新会话默认使用的沙盒与终端姿态取决于沙盒声明和文件夹信任 (#11298 by @esengine, #11256 by @esengine)
- 对话内查找改为 Ctrl+F 能真正触发 (#11236 by @esengine)
- 可以在「记住的规则」里撤销项目规则 (#11177 by @KHG420)
- 可以在模型服务设置里给服务改显示名，不影响它的标识和已有会话 (023f20e97)
- 技能名称支持 Unicode，MCP 标识不受影响 (42e9c7ce2)

## 变更

- 更新下载优先走镜像，镜像不可用时才回退 GitHub (#11322 by @esengine)
- 完整安装包下载可以断点续传，增量更新文件放在另一个磁盘卷时也能正常使用 (#11325 by @esengine)
- 市场信任徽章的文案更清楚，翻页不再出现重复条目 (#11335 by @KHG420, #11337 by @KHG420)
- 终端里以 ! 开头的命令只在本地运行，不再触发一轮模型对话 (#11262 by @esengine)

## 修复

- 打开 1.x 写的会话不再丢掉它的上下文压缩摘要 (ac30722a7)
- 命令实
```

### v1.39.5 — Reasonix CLI v1.39.5  (2026-09-29)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> 项目配置与沙盒的安全加固、上下文整理不再无限等待，以及若干桌面端修复。

**发布渠道：稳定版 · v1.39.5**

[English →](https://reasonix.io/changelog/v1.39.5/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.5/)

## 概览

**Reasonix v1.39.5 — Reasonix 1.39.5**

项目配置与沙盒的安全加固、上下文整理不再无限等待，以及若干桌面端修复。

发布日期：2026-09-29

**Desktop 13 · CLI 8**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **项目配置只能收紧你的设置** — 仓库里的 reasonix.toml 和 .reasonix/settings.json 不能再放宽沙盒、权限和审批设置，只能让它们更严格。项目声明的程序（钩子、语言服务器、模型服务商、shell、ripgrep 和浏览器路径）首次使用前需要你批准，声明或相关文件变化后会再次询问。在项目里选择的「总是允许」改为保存在你的 Reasonix 主目录，而不是写进仓库。 ([#11209](https://github.com/esengine/DeepSeek-Reasonix/pull/11209) by @esengine)
- **[Desktop · CLI]** **上下文整理有时间上限，失败时保留原有上下文** — 接近上限的对话在整理时可能无限等待，因为服务端心跳一直让请求保持活跃。现在每次整理有统一的五分钟上限；摘要失败时保留最后一次确认的上下文，不再退回有损截断。 ([#11171](https://github.com/esengine/DeepSeek-Reasonix/pull/11171) by @SivanCola)

### 改进

- **[Desktop]** **保存权限规则时拒绝未知工具名** — 桌面设置不再保存像 
```

### studio-v2.22.0 — Reasonix Studio v2.22.0  (2026-09-29)
**判定：待评估** — 可能值得移植 · 命中 stream/会话/session/mcp/model/tool/agent，需按 CUTLIST 红线复核

```
本版加强了项目配置的安全边界：仓库自带的配置只能收紧你的设置，项目声明的程序首次使用前需要你批准。同时新增 OpenAI Pro 模式、更完整的推理档位、四个一键服务商预设、长时间无进展提示和输入框草稿保存。

## 新增

- 在 GPT-5.6、GPT-6（OpenAI Responses 接口）上可以在推理强度菜单里打开 Pro 模式，只对当前会话生效，会消耗更多 token (#11194 by @esengine)
- 推理档位覆盖 GPT-5.6、GPT-6 和通义 Qwen3.8 的完整档位，菜单里选的档位会原样发给模型 (#11166 fixed in #11189 by @esengine)
- 新增 OpenRouter、OpenAI、Gemini 和火山方舟 Coding Plan 四个一键服务商预设 (#11193 by @esengine)
- 连续多轮没有可观察的进展时，输入框上方会给出提示，可以直接停止；阈值在「设置 → 会话」里调整 (#11160 by @esengine)
- 模型反复输出同一段文字时，输入框上方会给出提示，默认不打断也不改动对话 (#11183 by @BuGlessRB)
- 输入框里没发出去的文字会按会话保存，刷新页面或重新打开会话后恢复 (#9580 fixed in #11176 by @KHG420)
- 可以在用户配置 `[tools.shell.env]` 里为 bash 工具预设环境变量 (#11163 by @BuGlessRB)
- 新增技能编写指南 `docs/SKILLS.md` (#11191 by @esengine)
- 模型服务设置里可以按模型单独设置推理档位，同一个中转接入下不同厂商的模型各用各的档位 (#11192 fixed in #11197 by @esengine)
- 命令行界面可以在用户配置里设置 `ui.commandmode = "vi"`，开启 vi 命令模式 (#11074 by @BuGlessRB)
- 工作台资源管理器新增「显示隐藏文件」按钮，默认关闭；版
```

### v1.39.4 — Reasonix CLI v1.39.4  (2026-09-28)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> CLI 与桌面端修复：/mcp 重试不再卡住对话、审查子代理不再被 8 轮上限打断、更换密钥保留原变量名、远程标签页显示上下文。

**发布渠道：稳定版 · v1.39.4**

[English →](https://reasonix.io/changelog/v1.39.4/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.4/)

## 概览

**Reasonix v1.39.4 — Reasonix 1.39.4**

CLI 与桌面端修复：/mcp 重试不再卡住对话、审查子代理不再被 8 轮上限打断、更换密钥保留原变量名、远程标签页显示上下文。

发布日期：2026-09-28

**Desktop 6 · CLI 4**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **审查类子代理不再在 8 轮后被停下** — review、security-review、team-architect 子代理在 8 轮工具调用后就会暂停，并提示调大 max_steps，但没有任何设置能调到。现在它们与其他子代理使用相同的步数预算。 ([#11093](https://github.com/esengine/DeepSeek-Reasonix/pull/11093) by @esengine)

### 改进

- **[Desktop · CLI]** **提示匹配不到任何工具的权限规则** — 写成裸命令的规则（例如 deny = ["rm"]）能被解析，但永远匹配不到任何工具调用。现在启动时会指出这类规则，并给出应写成的 Bash(...) 形式；匹配语义不变。 ([#10949](https://github.com/esengine/DeepSeek-Reasonix/pull/10949) by @boscocp)

### 修复

- **[Desktop · CLI]** **保存新密钥时保留你设置的变量名** — 当某个模型服务的密钥存放
```

### v1.39.3 — Reasonix CLI v1.39.3  (2026-09-28)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> 项目配置、serve 审批、宿主 git 与沙盒的安全加固，以及远程 SSH 会话恢复正常加载与发送。

**发布渠道：稳定版 · v1.39.3**

[English →](https://reasonix.io/changelog/v1.39.3/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.3/)

## 概览

**Reasonix v1.39.3 — Reasonix 1.39.3**

项目配置、serve 审批、宿主 git 与沙盒的安全加固，以及远程 SSH 会话恢复正常加载与发送。

发布日期：2026-09-28

**Desktop 2 · CLI 2**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **项目配置、serve 审批、宿主 git 与沙盒的安全加固** — 项目声明的 MCP 服务在启动前会先征得你的同意，项目也不能再设置状态栏命令；通过 serve 进行的修改与审批需要本次启动的令牌；Reasonix 自己执行的 git 命令不再运行仓库配置的程序；在 bash 沙盒内，仓库的 git 配置与钩子保持只读。 ([#11114](https://github.com/esengine/DeepSeek-Reasonix/pull/11114) by @esengine)
- **[Desktop]** **远程 SSH 会话恢复正常加载与发送** — 在远端打开过一次旧的历史会话后，之后的连接会报 "transcript v2 is required" 或 "Transcript v2 is not synchronized"，无法加载也无法发送。现在远端 Serve 会始终如实声明它支持的能力。更新后重连一次，桌面端会自动重启远端 Serve 并替换其程序。 ([#11124](https://github.com/esengine/DeepSeek-Reasonix/pull/11124) by @esen
```

### studio-v2.21.0 — Reasonix Studio v2.21.0  (2026-09-28)
**判定：待评估** — 可能值得移植 · 命中 session/插件/mcp/model/tool/agent/compact，需按 CUTLIST 红线复核

```
本版开始建设 Studio 的扩展生态：设置里新增社区市场，可以浏览、安装和发布技能、插件、MCP 服务器与主题；登录账号后还能把配置备份到云端。同时加强了本地服务、宿主 git 和沙盒的安全边界。

## 新增

- 设置 → 扩展新增「发现」页，可浏览社区市场并安装技能、插件和 MCP 服务器；只安装经过审核、绑定了内容摘要的版本，内容与审核时不一致会拒绝安装 (#11107 by @esengine)
- 登录后可以从 Studio 直接发布技能、插件、MCP 服务器和主题到社区市场，并查看每次提交的审核状态 (#11112 by @esengine)
- 发布时可选「仅自己可见」：私有包不进入公开列表，发布者本人无需等待审核即可安装自己的包 (#11135 by @esengine)
- 市场支持赞和踩，每人每个包各一次；列表按下载、赞踩等综合权重推荐排序 (#11128 by @esengine, #11129 by @esengine, #11130 by @esengine)
- 登录账号后可选择把配置备份到云端，并在其他电脑上恢复；可按类别勾选设置、扩展、记忆和自动化，API 密钥默认不备份；未登录时不提供此功能 (#11109 by @esengine)
- 备份用你设置的口令加密后才上传，服务器读不到内容；恢复时会运行程序的条目需你逐项同意，审批模式、权限和沙盒设置不会被恢复 (#11109 by @esengine)
- 在输入框里选择技能或子代理会插入标签，而不是纯文本；行中任意位置输入 `/` 都能唤出菜单 (#11149 by @esengine)

## 变更

- 市场列表每行最多两行，窄屏下截断而不溢出；新增「只看可安装」筛选 (#11126 by @esengine)
- 本地服务默认要求身份验证，审批等改变状态的请求必须带启动令牌；`[serve]` 设置只从用户级配置读取 (#11110 by @esengine)
- 宿主自己运行的 git 命令不再执行仓库配置的程序；沙盒内的命令不能改写工作区仓库的 `.git/config`
```

### v1.39.2 — Reasonix CLI v1.39.2  (2026-09-27)
**判定：待评估** — 可能值得移植 · 命中 mcp，需按 CUTLIST 红线复核

```
> 桌面端与 CLI 修复：打不开或归档不掉的会话、切换会话后的实时流式显示、手动调用技能、设置向导的 API Key 变量名，以及中文 Windows 上的输出乱码。

**发布渠道：稳定版 · v1.39.2**

[English →](https://reasonix.io/changelog/v1.39.2/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.2/)

## 概览

**Reasonix v1.39.2 — Reasonix 1.39.2**

桌面端与 CLI 修复：打不开或归档不掉的会话、切换会话后的实时流式显示、手动调用技能、设置向导的 API Key 变量名，以及中文 Windows 上的输出乱码。

发布日期：2026-09-27

**Desktop 25 · CLI 14**

## 桌面端更新

### 重点内容

- **[Desktop]** **打不开、也删不掉的会话恢复正常** — 历史里同一条消息被记录两次的会话会打不开，也无法移到废纸篓，只提示一个笼统的错误。现在这类会话可以正常打开（以第一条为准，磁盘上的文件不会被改写）；文件损坏的会话也总能移到废纸篓，并给出明确提示；新的写入也不会再产生重复消息。 ([#10893](https://github.com/esengine/DeepSeek-Reasonix/pull/10893) by @esengine)
- **[Desktop]** **归档的旧会话会从侧栏消失** — 归档 1.38 留下的「已恢复」旧会话时，会一次归档它的所有恢复副本，不会再归档一条又冒出下一条；被列在错误工作区下的旧会话（带分支标记的、或以原始文件名为标题的）也不会再卡在侧栏、既删不掉又不能置顶/重命名/打开。归档的内容都可以在归档列表里恢复。 ([#10883](https://github.com/esengine/DeepSeek-Reasonix/pull/10883) by @esengine, [#1
```

### studio-v2.20.4 — Reasonix Studio v2.20.4  (2026-09-27)
**判定：待评估** — 可能值得移植 · 命中 cache/session/provider/model/edit/tool/agent/context，需按 CUTLIST 红线复核

```
本版正式打通 Web Studio 与桌面 Studio：手机或其他浏览器可通过同一账号安全连接家中电脑，看到并操作同一套会话；桌面端会明确显示谁正在远程控制，并可随时断开。

## 新增

- Web Studio 现在使用完整的 Studio 界面，通过端到端加密的远程通道访问电脑上的同一内核、工作区、会话与模型配置，不再是另一套简化控制页 (#11054 by @esengine, #11053 by @esengine)
- 桌面端顶部新增统一的「设备访问」状态：显示互联网远程设备数量、稳定的设备编号、Web Studio 在线状态，以及连接和离开提示 (#11058 by @esengine)
- 桌面端可对互联网远程设备执行两步确认断开；中转服务只允许同账号的电脑端关闭对应控制连接 (#11057 by @esengine, #11058 by @esengine)
- ACP 客户端可收到上下文用量和会话费用 (#11083 by @esengine)
- 发往模型服务的请求带上 `Reasonix/<版本>` 标识 (#11063 by @esengine)

## 变更

- 从 Web Studio 发出的消息在桌面端标注「来自 设备 N」，两端看到同一条会话和回复，便于确认当前操作来源 (#11058 by @esengine)
- 即使没有开启局域网手机访问，桌面端仍会持续显示互联网远程设备状态；局域网开关不会影响同账号 Web Studio (#11058 by @esengine)
- 远程请求超时、连接断开和身份校验错误改为中文可操作提示；请求错误固定在右下角悬浮显示，主动断开后提供「重新连接」入口 (#11058 by @esengine)
- 只有完成端到端加密握手的 Web Studio 才会出现在桌面设备列表；中转服务只转发密文，无法读取会话和文件内容 (#11054 by @esengine, #11058 by @esengine)
- 断开命令由本机窗口发起，并同时校验账号和单次连接标识，不能跨账号关闭其他人的连接 (#110
```

### studio-v2.20.3 — Reasonix Studio v2.20.3  (2026-09-27)
**判定：待评估** — 可能值得移植 · 命中 model/agent，需按 CUTLIST 红线复核

```
本版让内置浏览器工具有了独立开关，工作台能用满宽屏，模型服务可调整顺序，并修复行内技能调用发给模型的内容。

## 新增

- 设置 → 工具新增「内置浏览器」开关，由 `[tools] browser_tools` 决定，未设置时开启；项目配置覆盖时显示实际生效的值 (#10898 by @esengine)
- 模型服务可在设置中调整顺序，输入框的模型菜单和模型偏好按同样顺序列出；聚焦某一行时可用 Alt+↑/↓ 移动 (#10864 by @par73e)

## 变更

- 宽屏窗口中右侧工作台最宽可拉到 1600px；窗口变窄时暂时收窄，再变宽时恢复你拖出的宽度 (#10990 by @KHG420)
- 模型用 `python -c` 等临时脚本自检时，会被告知这为何不算验证，并列出可认的验证命令 (#11001 by @esengine)
- 后来的计划删掉已接受的验证命令时，交由你审批，不再由规划器自行决定 (#11024 by @esengine)
- 发布页为引用的合并请求注明作者、为问题注明修复它的合并请求，并在末尾列出贡献者 (#10984 by @esengine)

## 修复

- 只输入 `/技能名` 或只放一个技能标签时，技能以与模型调用相同的形式发出，不再作为原始技能正文夹在你的消息里 (#11008 by @esengine)
- 行内调用技能后，不再把技能正文里提到的其他技能当作必须调用，记忆检索按你输入的任务而非技能正文进行 (#11020 by @KHG420)
- 只把待办标记为完成、没有其他动作的回合，完成回执不再显示为「完成」 (#11014 by @esengine)
- 前台子代理用 `sed -i` 等命令改动的文件能被识别，不再留下无法消除的未证实改动 (#11009 by @esengine, #11013 by @esengine)

## 升级须知

- 内置浏览器工具不再读取与 1.x 共用的 `[browser] enabled`：1.x 写入的 `enabled = false` 不会再关掉 Stud
```

### studio-v2.20.2 — Reasonix Studio v2.20.2  (2026-09-27)
**判定：观察** — 无关键词命中，扫一眼

```
这一版修复了三处会直接影响数据可信度和长会话可靠性的问题：Studio 终于拥有独立于 1.x Desktop 与 CLI 的匿名遥测；带大量图片的会话不再把事件日志撑到自身无法读取；评测报告会保留导致分歧的宿主义务类型。自 2.20.1 起 3 个合并变更。

## 修复

- **Studio 使用量此前没有被统计。** 2.20.0 与 2.20.1 没有启动遥测报告器，服务端看到的 Desktop 数据因此主要来自 1.x，不能代表整个 Reasonix。Studio 现在使用独立的 `studio` 表面标识，启动量和汇总指标分别遵守现有的遥测、指标隐私开关，也继续支持 `DO_NOT_TRACK` 与 `REASONIX_TELEMETRY` 退出方式。Studio、1.x Desktop 与 CLI 在服务端分表统计，不再互相混入。
- **图片较多的会话不会再把自己写坏。** 图片原先以内联 data URL 反复写进事件日志；日志超过 128 MiB 后，读取器会拒绝它，后续保存也随之永久失败。图片现在按内容哈希存放在会话的 blob 目录，事件日志只保存引用；缺失或损坏的 blob 会优先从检查点恢复，并在无法恢复时保留文本与明确的不可用记录。旧的超限会话可以重新打开，并在下次保存时迁移。
- **评测分歧不再只显示笼统的 `obligation.outstanding`。** 报告现在携带不含内容的宿主义务类型，使一次运行结束后仍能判断是哪类未完成义务导致分歧。

## 兼容性与隐私

- 带图片的新格式会话使用 schema 3。旧版 Studio 与 1.x 会明确拒绝打开，而不会在不理解图片引用的情况下保存并造成数据丢失；纯文本会话保持原格式。
- Studio 遥测不上传对话、项目文件、提示词、账号邮箱或模型内容。启动统计使用匿名安装标识按天去重；可选指标只保存按版本、系统和信号分桶的汇总计数。

## 验证

- Linux、Windows、Intel macOS 与 Apple Silicon macOS 构建全部通过。
- macOS
```

### studio-v2.20.1 — Reasonix Studio v2.20.1  (2026-09-27)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 chinese

```
本次更新集中补齐统一登录、可信执行证据链、长任务与多模型稳定性，并包含 Studio、CLI、TUI、远程连接和供应商兼容性修复。下面列出 2.20.0 到 2.20.1 的全部合并 PR 与贡献者。

## What's Changed
* fix(pricing): bill Chinese public holidays as DeepSeek off-peak (studio) by @nanami-0713 in https://github.com/esengine/DeepSeek-Reasonix/pull/10758
* fix(cli): keep fatal crash output of the CLI for the next start by @esengine in https://github.com/esengine/DeepSeek-Reasonix/pull/10790
* fix(tui): history recall keeps the draft it replaced by @esengine in https://github.com/esengine/DeepSeek-Reasonix/pull/10789
* fix(cli): an ambiguous --resume query names its candidates by @esengine in https://github.com/esengine/DeepSeek-Reasonix/pull/10787
* fix(goaleval): read the verdict a thinking model leaves in reasoning by @esengine in https://github.com/esengine/DeepSeek-Reasonix/pull/10785
* ci: pin every third-party action to a full-length commit SHA by @esengine in https
```

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

## 二、上游 Commits（按改动域归类）

### 其他（60 条）

- `cc5d768` Merge pull request #11803 from esengine/feat/fix-prev-resp — **观察**
- `aee132a` Merge pull request #11780 from esengine/feat/fix-11776 — **观察**
- `3c0a655` fix(responses): keep continuation after an expired response id — **观察**
- `813e693` fix(evidence): require every mutated path to be a prose path inside the observed root — **观察**
- `11a4734` Merge pull request #11504 from Harbor404/fix/powershell-shell-probe — **观察**
- `6ec0de9` fix(responses): fall back to full history when a relay rejects previous_response_id — **观察**
- `35c8104` Merge pull request #11546 from Harbor404/feat/effort-model-same-switch-fastpath — **待评估**
- `0ef669e` style(agent): use the shared receiver name for the prose scan check — **待评估**
- `83f13a3` Merge branch 'studio' of https://github.com/esengine/DeepSeek-Reasonix into HEAD — **观察**
- `93c5419` test(evidence): make the prose-only tests independent of fixture files and filesystem case — **观察**
- `93bb4eb` Revert "fix(cli): align plugin doctor root diagnostics" — **待评估**
- `791eca3` Revert "fix(cli): align plugin doctor root diagnostics" — **待评估**
- `7d5bcfd` Merge pull request #11790 from esengine/feat/studio-red — **观察**
- `b8af495` fix(cli): print package warnings before plugin doctor rejects an agent root — **待评估**
- `41eeae6` fix(cli): align plugin doctor root diagnostics — **待评估**
- `fa5816d` chore(merge): sync with latest studio — **跳过**
- `73431b6` fix(cli): align plugin doctor root diagnostics — **待评估**
- `38def5a` chore(merge): sync with latest studio — **跳过**
- `9d4f5ab` test(evidence): cover prose-only waiver edge cases through boot.Build — **观察**
- `3068d41` Merge pull request #11566 from KHG420/codex/studio-market-version-draft — **观察**

