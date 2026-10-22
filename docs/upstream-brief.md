# 上游变更简报（自 2026-09-22 起）

- 上游：`esengine/DeepSeek-Reasonix`（MIT © Reasonix Contributors）
- 移植要求：**保留 MIT 版权声明**，改动的源文件头部补 `Ported from DeepSeek-Reasonix (MIT)。`
- 红线复核：`docs/CUTLIST.md` 第 0 节（UI 1:1 / CodeMirror / 字体分片 / Go 内核 / yomm）

## 一、上游 Release 变更

### v2.48.0 — Reasonix CLI v2.48.0  (2026-10-22)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.48.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.48.0).
```

### studio-v2.48.0 — Reasonix Studio v2.48.0  (2026-10-22)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 chinese

```
本版大幅降低长会话和大型工作区的页面内存占用，预设模块选择支持多选，并修好记忆多进程写入互相覆盖等问题。

## 新增

- 预设模块选择支持多选、搜索、全选与内置／自定义分组，手动输入 ID 移到高级选项。关联 #13988。

## 变更

- 旧会话先显示列表，摘要与轮数在后台补全；读取未完成或失败会明确提示，后台索引会为打开会话让出资源。关联 #14086 by @SivanCola。

## 修复

- 长会话里已完成且收起的工具调用卡片不再挂载整段输出，页面节点数和内存占用大幅下降。关联 #13899。
- 工作区有几万个未提交文件时，“改动”列表只渲染一页，其余显示“还有 N 项没有显示”，可按 500 项展开。关联 #13899。
- 两个进程共用一个记忆目录时，写入不再互相覆盖，也不再出现两条生效事实、改名没存下来、回滚倒退版本或索引丢行。关联 #14100 by @chuiwenwei。
- 回滚到旧版本的记忆时，不再返回该版本从未有过的内容或报“找不到该版本”。关联 #14096 by @chuiwenwei。
- 会话历史搜索不再把宿主追加的记忆召回和执行策略块当作用户说过的话。关联 #14076 by @chuiwenwei。
- 读取 JSONL 检查点时不再跟随指向所指定会话目录之外的文件符号链接。关联 #14086 by @SivanCola。
- 恢复把右侧工作区文件树里的文件和文件夹拖入对话，作为文件引用添加。关联 #12771 fixed in #12877。
- 普通会话启动期间读取 MCP 资源时，会等待已授权的服务器连接就绪，不再因连接未完成而提前报错。关联 #14084 by @SivanCola。
- 已登录账号时，反馈贡献榜不再错误地提示先去设置里登录。关联 #14012 fixed in #14071 by @lancy69。
- `reasonix config compact-ratio 33.3` 现在写入 `0.333`，不再写成 `0.33299999999999996`。关联 #14120。
- `reas
```

### v2.47.1 — Reasonix CLI v2.47.1  (2026-10-21)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.47.1](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.47.1).
```

### v2.47.0 — Reasonix CLI v2.47.0  (2026-10-21)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.47.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.47.0).
```

### v1.39.10 — Reasonix CLI v1.39.10  (2026-10-21)
**判定：观察** — 无关键词命中，扫一眼

```
> 用 Go 1.26.10 重新构建以修复证书验证的问题，并且 OpenCode Go 连接改用官方文档里的接口地址、支持 DeepSeek V4.1 Flash。

**发布渠道：稳定版 · v1.39.10**

[English →](https://reasonix.io/changelog/v1.39.10/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.10/)

## 概览

**Reasonix v1.39.10 — Reasonix 1.39.10**

用 Go 1.26.10 重新构建以修复证书验证的问题，并且 OpenCode Go 连接改用官方文档里的接口地址、支持 DeepSeek V4.1 Flash。

发布日期：2026-10-21

**Desktop 3 · CLI 3**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **Go 工具链升级到 1.26.10，修复证书验证对不再受信任的中间证书的处理** — Go 1.26.10 修复了标准库 crypto/x509 的证书验证：遇到已知的、不再受信任的中间证书时会报错（GO-2026-6809）。Reasonix 已用它重新构建；升级之后，漏洞扫描没有再报出 Reasonix 可达的漏洞。 ([#14051](https://github.com/esengine/DeepSeek-Reasonix/pull/14051) by @esengine)
- **[Desktop · CLI]** **OpenCode Go 连接改用官方文档里的接口地址，DeepSeek V4.1 Flash 也能正常使用** — OpenCode Go 文档里新的推理接口地址和 deepseek-v4.1-flash 之前没有收录，所以 V4.1 Flash 连接可能丢失 DeepSeek 的思考和工具历史回放，新地址也缺少 Go 的客户端请求头和模型发现。现在都已支持，旧的路径继续
```

### studio-v2.47.1 — Reasonix Studio v2.47.1  (2026-10-21)
**判定：待评估** — 可能值得移植 · 命中 启动/session，需按 CUTLIST 红线复核

```
本版用 Go 1.26.10 重新构建，修复标准库证书验证对已不再受信任的中间证书的处理，并修好历史搜索读不到会话时误报“没有匹配”和多进程下会话从搜索里消失的问题。

## 修复

- 构建改用 Go 1.26.10，修复标准库证书验证 crypto/x509 对已不再受信任的中间证书的处理（GO-2026-6809）。关联 #14034。
- 会话记录读不出来时，历史搜索不再说「没有匹配」，而是先提示索引不完整，并把该会话标为损坏、稍后自动重试。关联 #14023 by @chuiwenwei。
- 两个进程共用一个历史索引时，另一个进程刚索引的会话不再被误判为「已删除」而从历史搜索里消失；只有确认文件不存在才会被标记缺失。关联 #14024 by @chuiwenwei。
- 侧栏“项目”标题行里的“+”和“更多操作”按钮悬停时现在是同一种高亮。关联 #14041 fixed in #14043 by @lancy69、#14043 by @lancy69。

## 贡献者

感谢本版本的贡献者：@chuiwenwei、@lancy69

---

<!-- lang:en -->

This release is rebuilt with Go 1.26.10, which fixes how certificate verification treats intermediate certificates that are no longer trusted, and fixes history search reporting no match for an unreadable transcript or losing a session another process had just indexed.

## Fixed

- builds now use Go 1.26.10, which fixes how crypto/x509 certificate verification treats intermediate certificates t
```

### studio-v2.47.0 — Reasonix Studio v2.47.0  (2026-10-21)
**判定：待评估** — 可能值得移植 · 命中 启动/session/terminal/mcp/provider/model/tool/agent/context，需按 CUTLIST 红线复核

```
本版新增默认关闭的 Windows 命令沙箱、定时运行、外部文字确认开关，以及工作台里 PDF、CSV 和静态 HTML 的预览（AI 文件交付卡片需在用户配置里主动启用），并修复长会话窗口内存上涨、1.x 会话导入与历史搜索、自定义预设切换过慢等一批问题。

## 新增

- 设置 → 自动化 → 定时运行：查看、预览确认后创建、暂停、续期、删除定时任务，并查看每次运行的结果。关联 #11406。
- Windows 命令沙箱（设置 > 沙箱，默认关）：不能在授权文件夹外创建或改写文件；删除、重命名、读取、联网、ssh-agent/docker 管道不受限。见 #13109。
- 设置的「工具与权限」里有「外部文字」开关，开启后照抄网页或工具结果文字的调用，Auto 和 YOLO 也先问你；默认关。关联 #13111。
- 配置项 permissions.ask_on_external_origin（默认关）：调用逐字复制了网页或工具结果里的文字时，Auto 和 YOLO 也先问你。见 #13111。
- 远程机器现在可以在侧栏里上移、下移（远程项目菜单里的“上移/下移 机器名”），整台机器连同它的项目一起移动。关联 #13958。
- 会话右键菜单有「标为已读」，未读的会话（本机或远端）不用打开就能清掉未读标记。关联 #13962。
- 打开有未读回答的会话时，在新回答开始的位置画一条分隔线；可在设置的外观里关闭。关联 #13962。
- 用户配置 tools.present_files 主动启用 AI 交付卡片；工作台直接预览 Markdown、图片、PDF、CSV/TSV 和静态 HTML。关联 #14031 by @SivanCola。
- 终端的会话选择器（/resume）里按 Ctrl+D 询问、对同一行再按一次 Ctrl+D 才永久删除该会话；当前打开的会话会被拒绝并说明原因。见 #13954。

## 变更

- 会话很长时，折叠或展开左侧会话栏不再逐帧重算整段对话的样式，动画明显更顺。关联 #13936 fixed in #13937。
- Agen
```

### v1.39.9 — Reasonix CLI v1.39.9  (2026-10-20)
**判定：观察** — 无关键词命中，扫一眼

```
> 修复只有思考内容的回复被当作完成、附加大文件让桌面服务退出、手动压缩后无法发送、流中途被截断的工具调用被当作完成、Studio 导入的会话在 1.x 里显示成多余会话、恢复出来的对话重复出现、恢复状态残留、目标模式工作时长一直为 0、! 命令找不到登录 shell 的程序、远程会话徽标，以及设置与模型实际能力不一致的问题。

**发布渠道：稳定版 · v1.39.9**

[English →](https://reasonix.io/changelog/v1.39.9/?lang=en) · [网页版完整更新日志 →](https://reasonix.io/changelog/v1.39.9/)

## 概览

**Reasonix v1.39.9 — Reasonix 1.39.9**

修复只有思考内容的回复被当作完成、附加大文件让桌面服务退出、手动压缩后无法发送、流中途被截断的工具调用被当作完成、Studio 导入的会话在 1.x 里显示成多余会话、恢复出来的对话重复出现、恢复状态残留、目标模式工作时长一直为 0、! 命令找不到登录 shell 的程序、远程会话徽标，以及设置与模型实际能力不一致的问题。

发布日期：2026-10-20

**Desktop 14 · CLI 5**

## 桌面端更新

### 重点内容

- **[Desktop · CLI]** **只有思考内容的回复现在会重试一次，仍无答案时给出明确提示** — 有些模型只输出思考过程、没有答案也没有工具调用，这一轮却显示为已完成，你只会看到一行思考。现在会再请模型给出一次答案，已经取得的工具结果保留；如果仍然没有答案，这一轮会以明确的错误结束（支持英文、简体中文、繁体中文），说明没有产生答案，不再看起来像是完成了，重新打开会话时这条错误依然在。取消和各项上限的行为不变。导出的诊断信息还会增加不含内容的简短回复摘要（结束原因、大小、工具数量），方便反馈这类问题；它们不会进入模型上下文。 ([#13966](https://github.com/esengine/DeepSeek-R
```

### v2.46.0 — Reasonix CLI v2.46.0  (2026-10-20)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.46.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.46.0).
```

### v2.45.0 — Reasonix CLI v2.45.0  (2026-10-19)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.45.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.45.0).
```

### studio-v2.46.0 — Reasonix Studio v2.46.0  (2026-10-20)
**判定：待评估** — 可能值得移植 · 命中 启动/stream/session/terminal/mcp/model/edit/tool/agent，需按 CUTLIST 红线复核

```
本版新增会话级 Agent 预设（默认关闭）、终端排队消息管理、设置里独立的“会话间消息”、项目内 `.reasonix/reasonix.toml`，长会话占用的内存明显降低，并修复公网远程误报离线、多标签页掉帧、macOS 托盘图标、1.x 会话导入等一批问题。

## 新增

- 新增会话级 Agent 预设：人设、工具和模块按会话绑定版本，在人设页管理，输入框上方的状态行里选择；默认不启用，选择器默认隐藏，可在人设页开启。关联 #13613 by @SivanCola。
- 预设只能调整 MCP 和扩展的超时，不能改写启动参数、地址或凭据；写预设和切换组合需要配置编辑授权；跨项目移动已绑定的会话会被拒绝，原会话保持不变。关联 #13613 by @SivanCola。
- 终端里排队的消息画在工作行下：↑ 选中修改，Alt+↑/↓ 调序，Enter 保存，连按两次 d 删除，r 重试，空格暂停。关联 #12144。
- 设置里的“会话间消息”成为独立的一项，可以从已添加的项目里选择放行、一键撤销。关联 #13794。
- 提问卡片的自由填写框也能“优化提示词”：点星标或按 Ctrl+Shift+E，改写只在你点“采用”后才替换。关联 #13870。
- 关联电脑到账号时多一个默认勾选的“加入贡献榜”，旁边显示将公开的名字，点“确认”才生效；终端关联后也会提示加入命令。关联 #13142。
- 发送反馈时附上各进程的内存（只有进程类型和数字），表单里能先看到，方便判断是界面还是内核占得多。关联 #13899。
- Studio 项目配置支持 `.reasonix/reasonix.toml`，仅在根目录的 `reasonix.toml` 不存在时使用，项目权限限制不变。关联 #6007 fixed in #13887 by @lancy69。

## 变更

- 长会话占用的内存更少：已完成的长输出在页面里只保留开头和结尾各 4 KB，可点“显示完整输出”取回；命令运行期间只保留最近 64 KB。关联 #13899。
- 已完成的子代理卡片收起时不再加载它的子调用
```

### studio-v2.45.0 — Reasonix Studio v2.45.0  (2026-10-19)
**判定：待评估** — 可能值得移植 · 命中 启动/cache/stream/session/plugin/终端/terminal/mcp/provider/model/edit/tool/agent/context，需按 CUTLIST 红线复核

```
本版新增定时任务、会话排序与跨项目移动、手机提醒、WSL 远程、Git 面板、反馈贡献榜、规则目录与按名称关闭工具，推理强度可在进行中的回合里切换，并修复内置浏览器页面缩放、终端卡顿、子代理识图等一批问题。

## 新增

- `reasonix schedule add|list|tick` 等命令，在终端确认后按时间只读地运行任务；需用系统计划任务调用 `schedule tick`。关联 #11406。
- Studio 打开且可见（窗口或托盘图标）时，会按计划自动运行已确认的定时任务；同一时刻只有一个内核执行。关联 #11406。
- 会话菜单里可以把会话上移或下移，也可以在会话行上按 Alt+上下键；顺序保存在内核里，重启后不变。关联 #11420。
- Linux 增加 `.AppImage` 下载（amd64 和 arm64），可直接运行；它不会自更新，新版本需重新下载。关联 #11653。
- 浏览器和工作台可以全屏查看，会话与输入框暂时收起，按 Esc 或再点一次回到分栏；有事等你决定时自动退出全屏。关联 #11721。
- 登录同一账号的手机可在有操作待批准、模型提问、一轮出错时收到提醒，通知只含类别和数量。电脑和手机两边默认都关，需分别开启。关联 #11878。
- MCP 服务器因授权范围不够拒绝调用时，模型会停下，你可在该服务器那行点“授权更多权限”，每次都会先问你。关联 #11959。
- 在“我的反馈”里可以撤回自己的反馈（命令行用 /feedback withdraw）；已登记的议题会被关闭，已有结论的反馈不能撤回。关联 #11995。
- 可选的等级提示（设置里“等级提升时通知我”，默认关）：反馈等级提高时在窗口顶部提示一次，终端 /feedback list 说一行。关联 #12025。
- 在“我的反馈”的对话里，你自己的回复旁会显示你的等级徽章，维护者的回复旁没有。关联 #12025。
- 关联账号的电脑上，“我的反馈”会列出其他已关联设备的反馈和回复；终端新增 /feedback link、unlink、links。关联 #12
```

### v2.44.0 — Reasonix CLI v2.44.0  (2026-10-18)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.44.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.44.0).
```

### v2.43.0 — Reasonix CLI v2.43.0  (2026-10-17)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.43.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.43.0).
```

### studio-v2.44.0 — Reasonix Studio v2.44.0  (2026-10-18)
**判定：待评估** — 可能值得移植 · 命中 cache/缓存/stream/session/plugin/terminal/mcp/provider/model/tool/agent，需按 CUTLIST 红线复核

```
本版新增模型读图片/视频工具、网页搜索与抓取的后端设置、会话间消息的真开关与派活、打开本地网页文件和模型接口重试次数设置，并修复子代理、MCP、侧栏、输入法与反馈回复相关的一批问题。

## 新增

- 设置 > 外观 > 大小 增加“界面文字”四档，只放大侧栏、设置、标签等处的文字，不动边距和控件；对话正文仍由“正文”单独设置。关联 #11577。
- MCP 工具定义被改动时不必每次点接受：可以对某个服务器选择「跟随」，它的改动直接采用，每次仍会通知；随时可取消。关联 #12356。
- 需要登录（401）的 MCP 服务器行上有“登录”按钮，点后等待浏览器登录；被暂挡工具旁新增“接受并以后都自动接受这个服务器的改动”，已跟随的服务器可“取消跟随”。关联 #12357。
- 「我的反馈」的等级卡片里加了一句说明，写清楚「已落地」指反馈已被修复或实现并随新版本发布。修复 #12900 fixed in #13530。
- 新增（默认关闭）：模型可把任务交给你另一个项目里的会话（dispatch_to_project），对方用户批准后才看到。关联 #13341。
- 你发过消息的会话，侧栏行和标签上会出现小图标，标明对话走到哪一步（等批准、处理中、已回复、被拒绝），点它跳到该会话。关联 #13371。
- 设置里有真正的“会话间消息”开关；被拦下的消息可“批准并记住项目”，已记住的项目在设置里一键撤销。保存后下个回合起生效。关联 #13371。
- 声明 `video_models` 和 `video_protocol` 后，`read_video` 可把 MP4 原生交给能看视频的模型（通义内联、Kimi 上传），卡片显示发给了哪个模型。关联 #13399。
- 能读图的模型多了 view_image 工具，可直接看工作区里的 PNG/JPEG/GIF/WebP 文件；不读图的模型不受影响。关联 #13540。
- 本机读不到网页时，`web_fetch` 可回退到 DeepSeek 付费抓取接口，需先在卡片上同意；内网地址绝不外发。关联 #13541。
- 免费搜索
```

### studio-v2.43.0 — Reasonix Studio v2.43.0  (2026-10-17)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 chinese

```
本版新增会话间消息（实验）、跨项目的对话正文搜索、模型读视频、更新方式“自动下载”和可选起始分支的独立工作目录，并修复多个会话同时开着时的界面卡死、停止无效，以及一批界面和英文界面问题。

## 新增

- 设置里新增“会话间消息（实验）”：可查看本机别的会话、给它们发文字；收到的文字在输入框上方等你批准，批准后才交给模型。默认关闭。关联 #11376。
- 开启“会话间消息”后，模型多了 list_peers 和 send_peer_message 两个工具；发送前先问你（卡片显示收件会话和全文），对方的用户批准后才交给它的模型。关联 #11376。
- 侧栏搜索除了按名称筛选，停顿后还会搜所有项目里对话的正文，列出命中的对话和片段，点一下就打开。关联 #11942。
- 在 Windows 缩放 100% 的宽屏（2400 像素以上）上，首次使用会问一次“界面是不是偏小”，可一键放大并可恢复，不会擅自改动。关联 #11962。
- 模型来源列表的小圆点会记住上一次测试：失败是红点、悬停可见原因，通过是空心圈，换了地址或密钥就清掉。关联 #12040。
- 工具调用跑了 10 秒还没结束时，卡片上出现“只停止这一条调用”，点了只结束这一条，本轮继续，模型会被告知该调用是被你停止的。关联 #12254。
- 对话里的图片也能从你授权给当前工作区的文件夹（设置 → 沙盒 → 额外文件夹）里显示，文件夹之外的本地图片仍显示为占位框。关联 #13125。
- 新会话的分支入口升级为“配置工作目录”：可选起始分支，首次发送时创建独立的 worktree；已有对话仍可切换分支。关联 #13264 fixed in #13273 by @SivanCola。
- 设置 › 版本 › 更新方式新增“自动下载”（默认关）：后台下载并校验新版本，空闲时提示“重启并更新”，不会自动安装或重启。关联 #13291。
- 任务运行时，输入框上方的状态条会写出本轮已运行多久（如“read_file · 1m 6s”），不用回到对话区看计时。关联 #13346、#13253。
- 反馈窗口里添加的
```

### v2.42.0 — Reasonix CLI v2.42.0  (2026-10-16)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.42.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.42.0).
```

### v2.41.0 — Reasonix CLI v2.41.0  (2026-10-15)
**判定：待评估** — 可能值得移植 · 命中 session/terminal/mcp/model/tool/agent/context，需按 CUTLIST 红线复核

```
CLI archives built from the Studio release [studio-v2.41.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.41.0).

This release adds side questions, keeping a long paste as a file, optional session-row buttons and a sandbox device allowlist, and fixes narrow-window layout, contrast, memory recall and remote-control compatibility.

## New

- Settings → Model preferences gains an independent naming model and per-role reasoning effort, so titles can use their own model and each role its own effort. Refs #11851.
- New side questions: ask a read-only question beside the main conversation; read-only tools, never in the main transcript, dropped on close. Refs #12927, #13128.
- Each class in the context details can be opened to its largest items (sizes and tool names only, never message text). Refs #13052, #13143.
- When an MCP server puts `ttlMs` on its tool list, the cata
```

### studio-v2.42.0 — Reasonix Studio v2.42.0  (2026-10-16)
**判定：待评估** — 可能值得移植 · 命中 cache/缓存/stream/session/plugin/终端/terminal/mcp/provider/model/edit/tool/agent/context，需按 CUTLIST 红线复核

```
本版本新增会话概览、从源文件夹更新技能、更新提醒、按模型填写价格、子代理乐观写入范围和从分支创建独立工作区副本，并修复停止卡住、后台任务状态、同仓库项目互相等待写入、压缩恢复和一批界面问题。

## 新增

- 「我的反馈」新增「账号关联」：登录后可手动把这台电脑关联到账号，随时解除；默认关闭、不改变额度，网页账号页之后据此显示反馈等级。关联 #13141。
- 会话右键菜单新增“从最近回复分叉”，会话还在执行时也能从最近一个已完成的回复分叉；旧回复下的分叉按钮执行中同样可用。关联 #13177。
- 新增：侧边栏会话右键菜单加入“自动命名”，一步生成并保存标题，无需先打开重命名，关联 #13195 fixed in #13199
- 新增：设置 › 会话折叠 › 思考过程新增「收起并预览首句」，收起的思考在同一行后面显示首句（超长以 … 截断）。默认不变。关联 #13212。
- 新增：网页版 Studio 页面开着不关、内核升级后，会提示“这个页面不是最新版”并给出刷新按钮，不再出现 n.filter 之类的报错，关联 #13213 fixed in #13218
- 新增：删除带有恢复副本的会话时，确认框可以选择“连同 N 份副本删除”，不用再一个一个删，关联 #13221 fixed in #13225
- 新增：文件窗口里可以用“用其他程序打开项目”菜单，在 VS Code、终端等已安装的程序中打开当前项目，关联 #13227
- 新增：内置浏览器的页签可以双击重命名，不再只能显示网址，关联 #13228 fixed in #13267
- 新增：Windows 上可以给「指定一个可执行文件」填写启动参数（例如 wsl.exe -d 发行版 -- /bin/bash），保存前带着参数实际运行验证，无法运行则不保存。关联 #13247。
- 新增：右侧文件窗口的工具栏加了“在系统文件管理器中显示此文件”按钮，不用再去文件列表里右键，关联 #13255
- 新增：回复反馈时可以附上截图（粘贴或选择，最多 3 张），只发给维护者，由维护者决定是否公开。关联 #132
```

### studio-v2.41.0 — Reasonix Studio v2.41.0  (2026-10-15)
**判定：待评估** — 可能值得移植 · 命中 cache/stream/session/plugin/terminal/mcp/model/tool/agent/context，需按 CUTLIST 红线复核

```
本版本新增辅助会话、按需保存长粘贴、会话行快捷按钮、沙盒设备白名单等功能，并修复窄窗口布局、对比度、记忆召回和远控兼容等一批问题。

## 新增

- 设置 → 模型偏好新增「命名模型」和按角色的推理强度：可以单独指定用哪个模型给会话起标题，并分别设置各角色的推理强度。关联 #11851 by @Guan0923。
- 新增「辅助会话」：在主对话旁边问一个只读的小问题，用只读工具回答，不写进主对话、不改文件，关闭即丢弃。关联 #12927 fixed in #13128、#13128。
- 上下文详情里每一类占用可以展开，看最大的几项（只显示大小和工具名，不含消息内容）。关联 #13052、#13143。
- MCP 服务器在工具列表响应里给出 `ttlMs` 时，工具目录会在到期后自动重读（限制在 30 秒到 1 小时之间），不再只靠变更通知。关联 #13108。
- 技能的 `allowed-tools` 现在也接受开放标准写法（空格分隔，如 `Bash(git add:*) Read`），原来的逗号分隔照常可用；括号内的分隔符属于同一条规则。关联 #13110。
- `reasonix doctor` 现在会提示技能的名称、描述不符合 Agent Skills 开放标准（大写、连字符、超长、与目录名不一致），这些技能仍会正常加载。关联 #13110。
- 设置 → 外观新增「会话行快捷按钮」：打开后，鼠标移到侧栏会话行上会显示「归档」「删除」按钮；默认关闭，两个操作仍在右键菜单里。关联 #13132。
- 压缩被拒时，提示现在列出候选内容的构成（固定前缀、被保护的消息、摘要、最近回合各占多少），不再只说「候选仍高于触发线」。关联 #13148。
- 反馈对话框新增「想法与讨论」入口，建议和想法可以发到 GitHub 讨论区，bug 和错误仍用发送。关联 #13141、#13155。
- 新增 `[sandbox] allow_devices`：Linux 命令沙盒默认看不到宿主的设备节点（如显卡），现在可在用户级配置里用 `/dev/nvidia*` 这类白名单放
```

### v2.40.0 — Reasonix CLI v2.40.0  (2026-10-14)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 chinese

```
CLI archives built from the Studio release [studio-v2.40.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.40.0).

This release fixes the unclickable workspace "+" button, adds a turn-narration setting, and lets the changelog switch between Chinese and English.

## New

- The feedback dialog gains "Capture this window": it takes one picture of the app window only when you click, adds it as a removable thumbnail, and never sends it on its own. Refs #11965.
- The session tree now carries each conversation's last-activity time, so a list can sort by recency or show a relative time. Refs #12011.
- A sub-agent queued behind another's write claim now says whose claim it waits on, and whether neither declared write_paths (each treated as writing the whole workspace). Refs #12052.
- Theme packs gain `shadowFloat`, the shadow menus, popovers and dialogs cast; unset keeps the
```

### v2.39.0 — Reasonix CLI v2.39.0  (2026-10-14)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 chinese

```
CLI archives built from the Studio release [studio-v2.39.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.39.0).


## Changes in 2.39.0

This release adds double-click rename for sessions, starting without any model service, a low-disk-space warning and maps and dashboards in extension surfaces, and tidies the sidebar and conversation display.

## New

- Double-click a session row in the sidebar to rename it in place; the rename dialog can generate a title on request (#12977, #11591 by @Guan0923)
- Reasonix starts without any model service configured and opens the connection guide directly (#12966)
- A warning appears when the disk holding a project or session is nearly full; on by default, it only warns and never deletes files (#12960)
- The terminal UI reports working, waiting-for-you and finished states to the terminal (#12976)
- A finished session can stay in t
```

### studio-v2.40.0 — Reasonix Studio v2.40.0  (2026-10-14)
**判定：已落地** — Tempora 已自行实现（壳/图标/更新链）· 命中 chinese

```
本版本修复工作区「+」无法点击等问题，新增回合叙述设置，并让更新日志支持中英文切换。

## 新增

- 反馈对话框新增「截取当前窗口」：只在你点按钮时截一次，截图以可删除的缩略图加入附件，不会自动发送。关联 #11965 fixed in #13033。
- 侧边栏的会话列表数据现在带「最后活动时间」，可按最近使用排序或显示相对时间。关联 #12011 fixed in #12995。
- 子代理因另一个子代理占着要写的路径而排队时，现在会说明在等谁、是否因为双方都没声明 write_paths（按整个工作区处理）。关联 #12052。
- 主题包新增 `shadowFloat`，可改菜单、弹出层和对话框的投影；不设则保持内置阴影。关联 #12063 fixed in #12996。
- 图表在数据不多时，会在柱顶和折线数据点旁直接标出数值；数据多到放不下时自动不画，悬停读数仍然可用。关联 #12291。
- 侧栏里的项目现在可以拖动排序：按住项目行拖到目标位置，上沿或下沿的线指示落点；顺序保存在内核里。关联 #12300。
- 每轮结束时的「耗时」行现在同时写出这一轮的开始时间（当天只显示时分，其他日子带日期），重新载入会话后仍然保留。关联 #12728 fixed in #12994。
- 设置 > 账号新增「导出与导入配置」：无需账号，加密导出成文件、换机器时逐项导入；密钥默认不导出，必须设口令。关联 #12736。
- 设置 → 会话新增「回合间叙述」：选「详细」后，模型会在每批工具调用之间用三四行说明拿到了什么、下一步做什么；默认「简短」，行为不变。关联 #12788 fixed in #13101。
- 项目右键菜单新增「用 … 打开」：文件管理器之外，可用本机已安装的 VS Code、Cursor、IntelliJ IDEA、系统终端打开项目文件夹。关联 #12858。
- 工作台文件面板里新增「提交历史」：展开后按提交图谱列出所有分支最近的提交，带分支和标签。关联 #12913 fixed in #13028。
- 设置 → 外观新增「1.x 旧会话」
```

### studio-v2.39.0 — Reasonix Studio v2.39.0  (2026-10-14)
**判定：待评估** — 可能值得移植 · 命中 cache/session/plugin/terminal/mcp/provider/model/edit/tool/agent/context/compact，需按 CUTLIST 红线复核

```
本版加入会话行双击重命名、没有模型服务也能启动、磁盘空间不足提醒和扩展界面的地图与仪表盘，并整理侧边栏与对话的显示细节。

## 新增

- 双击侧边栏会话行就地重命名；重命名对话框可以按需自动起标题 (#12977, #11591 by @Guan0923)
- 没有配置任何模型服务也能启动，直接打开连接引导 (#12966)
- 项目或会话所在磁盘快满时发出提醒，默认开启，只提醒不清理文件 (#12960)
- 终端界面向终端报告工作中、等待你、已完成的状态 (#12976)
- 已完成的会话可以在「进行中」列表里多留一段时间，默认关闭 (#12957)
- 侧边栏标出保存在 1.x 里的会话，终端恢复列表标出未查看的会话 (#12405 by @keeyangyy, #12587)
- 用 / 调用技能时显示为紧凑的技能块；工具调用的 JSON 输入带语法着色 (#12972, #12969)
- 变更列表里可以暂存和取消暂存文件 (#12923)
- 应用图标显示未读的任务完成数，并换成扁平的新图标 (#12922 by @KHG420, #12897)
- 新增「清白蓝」「茶绿」配色，主题包可以声明密度和圆角 (#12932 by @SivanCola, #12513 by @f1shsmell)
- 图标栏有新建会话按钮；点标题栏的文件夹标记可以打开项目文件夹 (#12891, #12857, #12288 by @keeyangyy)
- 对话里的文件链接可以在工作台打开；文件菜单可以把文件或文件夹加入对话 (#12910 by @KHG420, #12877)
- 远程机器收进一个可折叠的行，会话树各层级更容易分清 (#12878, #12905)
- 第二次按 Esc 才会停止正在运行的回合 (#12859)
- 扩展界面支持样式字段、可编辑草稿、地图对比仪表盘和非阻塞动作 (#12830, #12854, #12876, #12896)
- 已安装的包可以按功能搜索、显示贡献类型、复制调用方式，安装预览显示解析出的提交 (#12065 by @KHG
```

### v2.38.0 — Reasonix CLI v2.38.0  (2026-10-13)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.38.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.38.0).
```

### studio-v2.38.0 — Reasonix Studio v2.38.0  (2026-10-13)
**判定：待评估** — 可能值得移植 · 命中 session/plugin/mcp/provider/model/tool/context/compact，需按 CUTLIST 红线复核

```
本版加入从任意回复分支会话、会话批量操作、模型显示别名和 MCP 工具定义变更审批，并修复长对话里拖选文字卡死、重载后丢失撤销入口等问题。

## 新增

- 可以从任意一条回复分支出一个独立的新会话 (#12770)
- 会话行上有快速归档和删除；可以多选本地会话做批量操作 (#12775, #12807)
- 把文件夹拖到侧边栏即可添加为项目，项目右键菜单可以打开项目操作 (#12776, #12324 by @KHG420)
- 从上下文环和检查器就能压缩上下文 (#12777)
- 对话导航旁显示当前计划 (#12803)
- 浏览器面板新增宽屏模式，打开时仍能看到对话；浏览器页面可以逐个或批量关闭 (#11762, #12806)
- 文件面板右键增加「复制路径」和「复制引用」，名称里含冒号或以反斜杠结尾而无法表示成引用时会禁用后者 (#12818, #12842 by @XTLine)
- 可以给每个模型设置显示别名；添加来源前可以批量检测模型 (#12821, #12835)
- 模型偏好里可以设置联网搜索使用的模型 (#11761)
- MCP 服务器的工具定义变更后，需要重新批准才会启用 (#12829)
- 回退之后对话顶部显示持久的撤销提示，可以关闭，重载后仍在 (#12831, #12559 by @XTLine)
- 可以在右键菜单里引用选中的回复文字 (#12836)
- 发送快捷键成为统一的偏好设置 (#12837)
- 反馈表单里可以直接打开日志文件夹；反馈对话折叠显示并保留未读状态 (#12768, #12802)
- 正在使用的版本被撤回时，应用会告知用户 (#12769)
- 工作台「+」按钮会显示启动器，从导航打开聚焦会话的文件 (#12826 by @XTLine, #12832)

## 变更

- 会话标签页改为按需开启 (#12841)
- 项目里置顶的会话排在最前并带标记 (#12845)
- 默认浅色主题的层次重新调整；视图标签与页面色调一致 (#12793, #12782)
- 对话壁纸下的文字光晕可以配置 (#12
```

### v2.37.0 — Reasonix CLI v2.37.0  (2026-10-12)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.37.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.37.0).
```

### studio-v2.37.0 — Reasonix Studio v2.37.0  (2026-10-12)
**判定：待评估** — 可能值得移植 · 命中 mcp/provider/model/tool，需按 CUTLIST 红线复核

```
本版加入常用服务预设库和主题包删除，并修复严格网关回放无参数工具调用时的 HTTP 400、卡住的外壳探测拖住内核等问题。

## 新增

- 添加模型服务时可以从内核维护的常用预设开始：可搜索、按域名分组，选中后整条预设（模型目录、识图模型、窗口、思考档）原样写入，名称重复由内核判断 (#12645)
- 外观里可以删除已安装的主题包，需要点两次确认，内置主题没有删除入口 (#12623)

## 变更

- 删除模型服务时会说明哪些角色改用了其他服务、哪些被清空，并从 `provider_access` 里去掉该服务 (#12589)
- 带密钥的供应商请求（聊天、探测、余额、决策协议）不再跟随跨主机的重定向；被拒时说明被重定向到了哪里，聊天也不再重试十次。如果你的中转站会重定向，把 base URL 改成它重定向到的地址即可 (#12570)
- 每天的第一个回合会告诉模型当天日期，只放在回合末尾，不改变缓存前缀 (#12598)
- `reasonix upgrade` 遇到由 npm 或 Homebrew 安装的程序，会提示用对应的包管理器升级，不再自己替换文件 (#12578)
- 检查通过之后才写入的文档不再要求再验证一次；有工具钩子或边车介入时仍然要求验证 (#12560)

## 修复

- 严格的网关在回放无参数的工具调用时返回 HTTP 400「arguments must be valid JSON」：空参数现在发送 `{}`，已保存的会话保持原样 (#12745)
- 外壳探测整体有时限，一次卡住的探测不再拖住内核，也不会反复重新启动 (#12615)
- 本地 `.mcp.json` 等清单有大小上限，安装被拒时会写明具体原因 (#12641)
- 内部：Windows 更新助手移除、配置迁移合并为一次读取、启动输入显式绑定、测试稳定性 (#12594, #12592, #12555, #12742)

## What's Changed
* fix(providers): keep key-carrying provider request
```

### v2.36.0 — Reasonix CLI v2.36.0  (2026-10-11)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.36.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.36.0).
```

### v2.35.0 — Reasonix CLI v2.35.0  (2026-10-11)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.35.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.35.0).
```

### studio-v2.36.0 — Reasonix Studio v2.36.0  (2026-10-11)
**判定：待评估** — 可能值得移植 · 命中 session/plugin/mcp/model/tool/agent/context，需按 CUTLIST 红线复核

```
本版加入提问等待超时、可选提示音、可选的折叠中间过程、每回合运行时长、改动文件条、工作区额外文件夹设置和编辑连接时更改协议，回执卡改为默认隐藏，并修复 1M 窗口每轮 400、存储迁移卡在校验、滚轮抖动、模型切换被后台任务挡住、Linux 与 Windows 更新等问题。

## 新增

- 新增可选的提问等待超时（默认关闭）：设置的会话页、`[agent] ask_timeout_seconds` 或终端 `/ask-timeout` 开启后，无人回答的提问超时即跳过，并告诉模型这是超时而非你的回答 (#12661)
- 每个回合结束后显示它运行了多久，重新载入历史后仍能看到；失败或被取消的回合不显示，旧会话也不补造 (#12656)
- 输入框上方新增改动文件条，显示「N 个文件已更改 +x -y」，点击打开工作台文件列表；默认开启，可在会话设置里关闭，非 git 工作区不显示 (#12668)
- 外观的行宽新增「整宽，输入框也铺满」，默认不变，需要时自己选；手机宽度不受影响 (#12703)
- 设置的「工具与权限」里新增「此项目的额外文件夹」：可添加、移除让 agent 额外可写的文件夹，只对本项目生效，拒绝时给出带代码的原因，默认没有；「完全放行」只决定是否询问，不会扩大可写范围 (#12640, #12715)
- 新增可选的提示音（默认关闭）：设置的通知里打开后，回合结束、等待批准、模型提问和反馈回复时放一声短提示，不依赖系统通知，窗口在后台也会响 (#12702)
- 新增可选的「折叠中间过程」（默认关闭，`[ui] fold_turn_work`）：已结束的一轮只留最后一句，中间的工具调用、思考和中间文字收成一行，点开展开，运行中的一轮始终展开 (#12714)
- 设置的版本页新增「日志与异常退出记录」：显示日志目录和异常退出留下的文件，不上传任何东西 (#12719)
- 编辑连接时可以更改协议，不必删掉重建；决策来源不显示该选项，已固定请求地址的连接会被拒绝并说明原因 (#12618)
- 界面字体与代码字体的建议列表大幅扩充，在 Window
```

### studio-v2.35.0 — Reasonix Studio v2.35.0  (2026-10-11)
**判定：待评估** — 可能值得移植 · 命中 session/plugin/mcp/tool/agent，需按 CUTLIST 红线复核

```
本版加入 Linux 的 rpm 安装包、MCP 工具定义固定与变更扣留、闲置会话自动归档、硬件加速开关和反馈回复通知，并修复信任库无限增长、新会话默认模型被跳过时无提示等问题。

## 新增

- 新增 Linux 的 `.rpm` 安装包（`ReasonixStudio-linux-*.rpm`），本版是首个含 rpm 的版本；用 minisign 校验，无 GPG 签名；rpm 安装的版本暂不自动更新 (#12608)
- MCP 工具定义在你批准时被固定：之后有变化或新增的工具会被扣住，不进入模型请求，调用会被明确拒绝，直到用 `reasonix mcp trust <名称> --digest <摘要>` 批准；桌面端目前只显示通知 (#12597)
- 设置的外观页新增「图形」：可关闭硬件加速（下次启动生效），并显示当前窗口的绘制方式；窗口无法绘制时，可用环境变量 `REASONIX_DISABLE_GPU=1` 或参数 `--disable-gpu` 仅关闭这一次 (#12451)
- 设置新增可选的闲置会话自动归档（默认关闭，默认 30 天，范围 1 到 3650）；已置顶、正在运行、有待回答事项或有未读完成的会话不会被归档，归档可恢复 (#11535)
- 反馈的未读角标在应用打开期间自动刷新，窗口不在前台时有新回复会弹出通知；通知设置里新增「反馈有回复时」开关，在总开关打开时默认开启 (#11538)
- 设置的「关于」页新增「支持项目」入口，含 PayPal 链接以及默认折叠的微信、支付宝收款码 (#11709)

## 变更

- 提交接口 `POST /submit` 只在提交确实被丢弃时返回 409；已受理并立刻结束的回合、排在结束中回合之后的提交现在返回 202 (#12596)
- 电脑操作返回给模型的应用名和窗口标题现在限长并转义，包含换行或不可见字符的名称不再能伪造快照行 (#12585)
- 安装 skill 或本地插件时，复制的来源若是指向目录的别名现在可以安装；批准之后来源别名被改指向别处，会被拒绝而不会复制 (#12112 by
```

### v2.34.0 — Reasonix CLI v2.34.0  (2026-10-10)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.34.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.34.0).
```

### studio-v2.34.0 — Reasonix Studio v2.34.0  (2026-10-10)
**判定：待评估** — 可能值得移植 · 命中 session/mcp/model/edit/tool，需按 CUTLIST 红线复核

```
本版让输入框可以直接切换工作区的本地分支，界面缩放改用统一范围并支持 Ctrl/Cmd +/-/0，电脑操作能判断每一步是否生效，并修复回退冲突、旧版会话导入、模型切换、GLM 思考参数和多处终端界面的问题。

## 新增

- 输入框的分支标签读取真实的 git 状态，并可直接把工作区切换到另一个本地分支；有进行中的回合、后台任务或未提交改动时会明确拒绝并说明原因 (#12092 by @XTLine, #12171 by @XTLine)
- 界面缩放只有一个声明范围 0.8 到 1.8（步长 0.05），滑块显示的值就是实际保存的值，并可用 Ctrl/Cmd 加 `+`、`-`、`0` 调整 (#12035)
- 电脑操作的每一步会标明效果是否可信，并带上占住输入的模态对话框；Windows 上输入文字会读回确认，被错误框挡住时不再假装成功 (#12541, #12542)
- 自动压缩因上次摘要失败而被暂缓时，界面和终端界面会显示一条中英文提示，不再静默 (#12083)
- 终端界面输入框为空时按回车，回到最新输出并继续跟随，与 1.x 一致；`Ctrl+Z` 把终端界面挂起到命令行，`fg` 后恢复 (#12510 by @xxoingr, #12511 by @xxoingr)
- 思考参数面板按协议声明的字段命名，Responses 协议的服务商不再显示成只支持 Chat (#12498)

## 变更

- 侧栏底部的用量、反馈、账号和设置，在图标栏可见时不再重复显示；图标栏隐藏、仅折叠时显示或窄窗口下仍保留 (#12482 by @SivanCola)
- 显式声明 `glm` 协议的服务，glm-5.2、glm-5.3、glm-5.3-flash 的请求现在带 `reasoning_effort`：5.2 选 high 真发 high，选 none 真关思考；5.3 的「关闭」发 `thinking=enabled` 加 low (#12552)
- 决策来源不再出现在输入框的模型切换器里，选它会得到明确错误，而不是不可预期的失败 (#12553)
```

### v2.33.0 — Reasonix CLI v2.33.0  (2026-10-09)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.33.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.33.0).
```

### studio-v2.33.0 — Reasonix Studio v2.33.0  (2026-10-09)
**判定：待评估** — 可能值得移植 · 命中 session/mcp/model/edit，需按 CUTLIST 红线复核

```
本版把图标栏移到窗口最左侧并加入反馈入口与三档显示方式，新增模型选择器搜索与分组、HTML 文件页面预览和「视觉效果」节能档，补齐终端界面的多个按键，并修复队列编辑、回退重发、反馈截图和带天空主题包长时间占用显卡的问题。

## 新增

- 图标栏移到窗口最左边，底部新增带未读角标的「发送反馈」入口；外观页「图标栏」改为始终显示（默认）／仅侧栏折叠时显示／从不显示，立即生效 (#12428)
- 输入框的模型选择器带搜索框（输入即过滤，回车选第一项，Esc 关闭），按服务商分组并固定显示分组标题，条目改为单行，当前模型保留勾选，声明可读图的模型带「读图」标记 (#12442)
- 工作台文件浏览器里打开 `.html`/`.htm` 文件时，标签页新增「预览」视图（默认）：按网页打开，同目录的样式、脚本、图片照常加载，文件变化后自动刷新，未保存的草稿不会被覆盖 (#12443)
- 设置的外观页「高级外观」新增「视觉效果」：完整（默认）／节能。节能档去掉磨砂玻璃、动态天空和颗粒，布局不变；只作用于本机，立即生效 (#12448)
- 终端界面的工具审批和计划审批卡片支持用 `j`/`k` 和 `Ctrl+N`/`Ctrl+P` 移动光标 (#12419 by @xxoingr)
- 终端界面的提问卡片支持 `j`/`k` 上下移动、`h`/`l` 在问题之间左右切换 (#12420 by @xxoingr)
- 终端界面的 `/mcp` 面板支持 `l`/右方向键进入服务的工具列表，`h`/左方向键返回或关闭面板，`q` 直接关闭 (#12421 by @xxoingr)
- 终端界面在开启应用内鼠标捕获时，没有选中文字的右键会粘贴剪贴板里的文字，与 1.x 一致，通过 SSH 连接时仍显示原有提示；输入框隐藏时不粘贴 (#12436 by @xxoingr)
- 终端界面在回合运行中按 `Ctrl+Enter`，把输入框内容作为引导发送，效果与 `Ctrl+S` 相同，在下一个工具边界送达；空闲时按它不做任何事，不会把想换行的草稿提交出去 (#12437 by @xx
```

### v2.32.0 — Reasonix CLI v2.32.0  (2026-10-08)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.32.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.32.0).
```

### v2.31.0 — Reasonix CLI v2.31.0  (2026-10-08)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.31.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.31.0).
```

## 二、上游 Commits（按改动域归类）

### 其他（60 条）

- `a708a88` Merge pull request #14130 from esengine/docs/release-notes-2.48.0 — **跳过**
- `07af85d` docs(release): studio 2.48.0 notes — **观察**
- `c0c7d9c` Merge pull request #14128 from esengine/fix/session-menu-fits-short-window — **待评估**
- `32782ef` docs(release): note the project menu fix — **观察**
- `ffb01d5` fix(desktop): keep a project's context menu inside a short window — **待评估**
- `69b6927` Merge pull request #14124 from esengine/fix/changes-list-row-cap — **观察**
- `f7777b4` fix(desktop): draw a page of the changes list, not every row — **观察**
- `7a46cde` Merge pull request #14047 from imcreazy/fix/undefined-bg-property — **观察**
- `692e669` Merge pull request #14123 from esengine/fix/machine-dir-must-exist — **观察**
- `17cb9e2` Merge pull request #14121 from esengine/fix/compact-ratio-float-noise — **待评估**
- `cb441be` Merge pull request #14117 from esengine/fix/tool-card-lazy-body — **待评估**
- `296e066` chore(desktop): drop scratch fixtures that were committed by mistake — **跳过**
- `b6bbcb3` fix(cli): only convert a percentage exactly when it is in range — **观察**
- `482441e` fix(cli): refuse a machine --dir that is not a directory — **观察**
- `ed969ae` test(desktop): open the card before the output-cap guard reads what it left out — **观察**
- `49959f6` fix(cli): save the compact ratio as the decimal the user typed — **待评估**
- `450f3e5` fix(desktop): do not mount the body of a finished, closed tool card — **待评估**
- `8d6523d` Merge pull request #14111 from xxoingr/docs/guide-terminal-keys-mcp — **待评估**
- `006f8e7` Merge pull request #14109 from xxoingr/docs/guide-zh-wsl-remote — **跳过**
- `9e271a2` Merge pull request #14107 from xxoingr/fix/price-source-format-chars — **跳过**

