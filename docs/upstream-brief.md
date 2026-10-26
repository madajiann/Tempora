# 上游变更简报（自 2026-10-22 起）

- 上游：`esengine/DeepSeek-Reasonix`（MIT © Reasonix Contributors）
- 移植要求：**保留 MIT 版权声明**，改动的源文件头部补 `Ported from DeepSeek-Reasonix (MIT)。`
- 红线复核：`docs/CUTLIST.md` 第 0 节（UI 1:1 / CodeMirror / 字体分片 / Go 内核 / yomm）

## 一、上游 Release 变更

### v2.52.0 — Reasonix CLI v2.52.0  (2026-10-26)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.52.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.52.0).
```

### studio-v2.52.0 — Reasonix Studio v2.52.0  (2026-10-26)
**判定：待评估** — 可能值得移植 · 命中 启动/cache/stream/session/mcp/model/edit/tool/agent/compact，需按 CUTLIST 红线复核

```
本版新增 Wallpaper Engine 场景壁纸、主题包的五个代码配色标记和历史竖带的展开，移除正文拖动把手与顶栏沙盒按钮，并修复压缩卡死、没有文件夹无法开会话等多处问题。

## 新增

- 壁纸可以导入 Wallpaper Engine 场景文件夹：提取主图和全部音轨循环播放，支持 DXT1/DXT3/DXT5 压缩主图，提供音量、静音和鼠标视差。关联 #14407 by @EMEEEEMMMM、#14478 by @EMEEEEMMMM。
- 主题包可以给注释、类型、运算符、标点和变量单独配色（五个可选标记），文件编辑器和对话代码块都生效；不写它们的主题外观不变。关联 #14358 fixed in #14483。
- 会话折叠设置新增独立的思考开头预览开关：收起时在标题下方单行显示，流式输出时也生效，旧的预览选择自动迁移。关联 #14139。
- 历史对话竖带里合并成一条的多轮对话，点一下展开成具体每一条再选要跳的那条；历史未全部加载时竖带顶端会提示。关联 #14468 by @imcreazy。

## 变更

- 移除正文左右两侧的拖动宽度把手，对话区不再有线条，手机端也不再误触；正文宽度用设置里的行宽预设选择。关联 #14460 fixed in #14463。
- 顶栏不再常驻「沙盒」按钮，它只是「工具与权限」的快捷入口，该入口已在图标栏和侧栏里，可在导航入口里显示或隐藏。关联 #14439。
- 把文件拖进会话时，放到会话面板的任意位置都会作为附件或引用加入，不必再精确拖到输入框；侧栏等自带拖放区的位置仍优先。关联 #14443。
- 文档：用户指南新增「提示词怎么注入」快速说明，区分聊天要求、仓库常驻指令和用户级人设及人设保存后的生效时机。关联 #13512。

## 修复

- 没有添加任何文件夹时新建会话不再提示「请先添加一个文件夹」，而是在应用自己的内置工作区里打开。关联 #14363。
- 大窗口模型下，用户消息很大的长会话不再反复报「折叠后仍不低于压缩阈值」而卡住自动压缩和 `/compact`。关联 #14434 fixed in #
```

### v2.51.0 — Reasonix CLI v2.51.0  (2026-10-24)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.51.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.51.0).
```

### studio-v2.51.0 — Reasonix Studio v2.51.0  (2026-10-24)
**判定：待评估** — 可能值得移植 · 命中 启动/cache/session/model/diff/tool/agent/context，需按 CUTLIST 红线复核

```
本版新增视频壁纸、查找框的大小写与正则开关、快捷键一览和长对话分页加载，正文栏可拖得更窄，并修复多处保存、粘贴与显示问题。

## 新增

- 壁纸可以选 MP4 或 WebM 视频，作为静音循环的动态壁纸；窗口隐藏或失焦、系统减弱动效或精简效果下停在第一帧。关联 #14357。
- 对话里的查找框多了两个开关：区分大小写，以及把查询当作正则表达式。关联 #14198 by @imcreazy。
- 设置的外观页增加「快捷键」一栏，列出窗口里所有可用按键，可以搜「快捷键」「Ctrl」「Esc」等词找到。关联 #14198 by @imcreazy。
- agent 浏览器的网页可在「设置 → 外观」开启空闲休眠：15 分钟无人使用后整页收起省内存，再用时恢复为同一标签页。默认关闭。关联 #14332 by @jf200s。
- 版本列表里的下载和后台自动下载现在都可以取消；取消会停止传输，并删除这次下载留下的部分文件。关联 #14338。
- 新增可选的历史接口，按页读取正文并保留稳定的消息位置和跨页工具上下文；现有客户端继续全量读取。关联 #14048、#14087 by @SivanCola。

## 变更

- 壁纸不再有 12 MB 上限，原样使用你选的图片；上传改为边收边写入磁盘，读取支持分段，大文件不再占满内存。关联 #13980。
- 正文字宽现在可以连续拖到 640px，不再停在「适宜阅读」的 760px；按 Home 或不拖动时仍是 760px。关联 #14384。
- 阅读栏左右两侧的拖动把手平时不再显示，鼠标移到栏边缘才出现，拖动和键盘调整不变。关联 #14352 fixed in #14353。
- 移除工作台的「加宽」按钮、独立加宽模式及 Ctrl/Cmd+Shift+B；可拖动分隔条或聚焦后用方向键调宽。关联 #14324 fixed in #14335 by @lancy69。
- 轮次多的对话里，右侧提问细条会把相邻几条折成一组，悬停显示涵盖的范围；右键某条可加书签。关联 #14198 by @imcreazy。
- 「运行分析」入口变成
```

### v2.50.0 — Reasonix CLI v2.50.0  (2026-10-23)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.50.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.50.0).
```

### studio-v2.50.0 — Reasonix Studio v2.50.0  (2026-10-23)
**判定：待评估** — 可能值得移植 · 命中 启动/cache/会话/session/plugin/terminal/mcp/model/tool/agent，需按 CUTLIST 红线复核

```
本版让子代理可以在工作台里开成标签页读完整记录，设置里新增导航入口管理、计费方式和放大设置窗口，正文栏可拖宽，并修复多处卡住、显示与对齐问题。

## 新增

- 正文栏左右边线可以拖动，两侧同时等量变宽或收窄；缩到“适宜阅读”为止，放到窗口全宽为止，被挡住的侧栏按各自设定的比例让位。关联 #14198 by @imcreazy。
- 反馈表单的正文可以切到「预览」，先看 Markdown 渲染的样子；公开的议题仍把原文放在代码块里。修复 #14248 fixed in #14255。
- 设置 → 外观 →「导航入口」可隐藏或调整图标栏和侧栏里的入口，两处同步；会话、反馈、账号和设置始终保留。关联 #14236、#14190。
- 设置窗口头部多了「放大设置窗口」按钮，可铺满整个窗口、内容区同步变宽；选择会记住，下次打开保持。修复 #14272 fixed in #14271。
- 桌面端可连自己部署的远程网关（REASONIX_REMOTE_URL、REASONIX_REMOTE_GATEWAY_ID），手机网页按授权里的网关地址连接；非 wss:// 地址会被拒绝。关联 #14282。
- 从“子代理”面板打开子代理，会在工作台开成标签页，读内核记录的完整对话（运行中持续刷新），工具步骤可折叠、可同时开多个；找不到记录时仍用原对话框。关联 #13523 fixed in #14291。
- 连接编辑页可选“计费方式”（按量计费或订阅套餐），订阅套餐的用量会按所填价格折算成估算值单独显示，不计入实际花费。关联 #13276。
- 设置 → 工具与权限第二项提供「AI 文件交付卡片」开关，支持搜索并保存用户选择，重新打开会话生效。关联 #14063 by @SivanCola。

## 变更

- 侧栏会记住你折叠过的项目，重新打开界面后仍保持折叠；新项目默认展开，不替你做决定。关联 #14195 by @lancy69。
- 设置打开时，背后的内容被更深的平面遮罩压下去，设置面板更突出；没有使用实时模糊。关联 #14196 by @lancy69。
- 正文两侧的拖
```

### v2.49.0 — Reasonix CLI v2.49.0  (2026-10-22)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.49.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.49.0).
```

### v2.48.0 — Reasonix CLI v2.48.0  (2026-10-22)
**判定：观察** — 无关键词命中，扫一眼

```
CLI archives built from the Studio release [studio-v2.48.0](https://github.com/esengine/DeepSeek-Reasonix/releases/tag/studio-v2.48.0).
```

### studio-v2.49.0 — Reasonix Studio v2.49.0  (2026-10-22)
**判定：待评估** — 可能值得移植 · 命中 启动/stream/session/mcp/model/tool/agent/context，需按 CUTLIST 红线复核

```
本版新增用量页“今日”小时视图和 Patina 主题，辅助会话支持 Markdown 与流式进度，改过文件的回合不再默认被追问检查，并修复多处内存、卡住和显示问题。

## 新增

- 内置 Patina 主题，雾灰画布、白色浮卡与钢蓝强调色，明暗两套，需要时在设置里手动选择。关联 #14136 by @FuchaZ。
- 用量页多了“今日”范围，单日窗口按小时显示用量、花费和请求。关联 #14176 by @EMEEEEMMMM。

## 变更

- 改过文件的回合不再默认被要求先做检查、复核和签收才能结束；需要时在用户配置里设 `host_verification = "on"`。"交付"预设和 `--fail-on-unverified` 仍会要求。关联 #14154。
- 隐藏图标栏时，侧栏不再有两个打开同一个“远程”设置页的入口；底部重复的“连接与机器”已移除，顶部“运行环境”仍可进入。关联 #14187。
- 自动命名遇到关不掉思考的模型时，会明确提示“模型把输出额度花在思考上”，并建议换一个能关闭思考的命名模型。关联 #14188。
- 隐藏图标栏时，侧栏搜索行与下面的快捷入口之间不再有多余空白；两处小字提示统一使用“·”分隔。关联 #14191。

## 修复

- 配置了 TCP 方式的 DNS 服务器时，健康探测把正常应答的服务器误判为不可用，导致第一个服务器失效后不会切换到下一个。关联 #14044 by @imcreazy。
- 只打开了远程会话窗格时，直接访问本机端口（不带窗格前缀）的请求没有应答，现在会转发给远端内核；本地窗格仍然优先。关联 #14045 by @imcreazy。
- 注入的常驻上下文（技能清单、项目指令、规则、日期）不再因为「已交付」的书签而漏发。关联 #14099 by @chuiwenwei。
- 扩展拒绝、取消、折叠、回退、截断之后，都会按模型真正看到的历史重新判断。关联 #14099 by @chuiwenwei。
- 服务端新建会话（/new）的首个请求现在会带上技能清单、项目指令与日期。关联 #14099 by
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

## 二、上游 Commits（按改动域归类）

### 其他（60 条）

- `d797d79` Merge pull request #14526 from SivanCola/feature/root-task-wall-budget-14025 — **观察**
- `f781d9e` Merge pull request #14525 from imcreazy/fix/rail-run-opens-on-hover — **观察**
- `1e17cad` Share explicit wall budgets through Agent delegation — **待评估**
- `a6bb1f9` Open a folded rail run on hover, and close it on the way out — **观察**
- `829adcf` Merge pull request #14523 from SivanCola/fix/task-budget-usage-completeness-14025 — **观察**
- `2bd7687` Fix incomplete provider usage in task cost accounting — **待评估**
- `ebab571` Merge pull request #14518 from SivanCola/feature/root-task-token-budget-14025 — **观察**
- `181c8da` feat(agent): share reported token budgets through delegated runs — **待评估**
- `834b633` Merge pull request #14515 from SivanCola/fix/isolation-refusal-wording-14025 — **观察**
- `e596cef` Merge pull request #14377 from SivanCola/codex/fileview-provenance-14025 — **观察**
- `97d1b18` Merge pull request #14511 from SivanCola/test/serve-catalog-fixtures-14025 — **观察**
- `743c27f` fix(studio): word the refusals isolated tasks already emit — **观察**
- `3d27a1a` fix(builtin): bind file views to complete returned reads — **观察**
- `a4cce4e` Merge pull request #14510 from esengine/c5-rail-focus-visible — **观察**
- `632bb81` Merge pull request #14267 from lancy69/fix/14223-workspace-alignment — **观察**
- `fb76a1c` Merge pull request #14507 from imcreazy/perf/harness-serves-paged-history — **观察**
- `2a72d42` Merge pull request #14509 from esengine/chore/update-acknowledgments — **跳过**
- `eaf5fba` fix(studio): align footer avatar and workspace text — **观察**
- `2279f84` test(serve): retire shared catalogs with temporary runtime fixtures — **观察**
- `57598ed` perf(harness): serve the transcript in pages when ?paged=N is set — **观察**

