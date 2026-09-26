# CUTLIST — Tempora 轻便版 Reasonix 瘦身记录

> 规则：**每砍/每改一项，必须先报户主拍板，再记入本表。功能零损失是底线。**
> 上游：`esengine/DeepSeek-Reasonix`（MIT），参考源码只读于 `G:\Tempora\reference\DeepSeek-Reasonix`

## 0. 不可动的红线（不许砍，也不许偷偷改）

| 项 | 位置 | 为什么不能动 |
|---|---|---|
| UI 组件全量 | `src/ui/**`（2.2MB） | 户主要求 **1:1 一模一样**，砍一块就不是了 |
| CodeMirror 18 个包 | `package.json` 依赖 | 代码高亮是 Reasonix 的本体，砍了就不像代码工具 |
| 中文字体分片 | `tokens.css` 的 `unicode-range` | 官方已有按需加载设计，正确实现，动了会退化 |
| Go 内核业务逻辑 | `internal/**` | 戸主口径「不要影响功能」 |
| yomm.cc 中转站 | 服务器 Docker:8080 | **绝对红线**，与本项目无关 |

## 1. 已执行的瘦身项

### S1 — 换壳：Electron → Tauri
- **砍了什么**：官方 Electron 壳（`desktop/electron/`）
- **为什么砍**：Electron 运行时是 150MB+ 体积与启动慢的唯一根因，户主核心痛点就是「打开慢、打包慢、上传慢」
- **省了多少**：安装包约 **-140MB**，运行时内存与冷启动大幅下降（实测待补）
- **怎么恢复**：保留 `reference/DeepSeek-Reasonix/desktop/electron/` 原样不动，随时可切回
- **功能影响**：**零**。官方 React SPA 只走 127.0.0.1 HTTP+SSE，不依赖 Electron API

### S2 — 7.5MB 字体分片化
- **改了什么**：`src/styles/studio.css` 里 `@font-face "Noto Studio"`（引用 `noto-studio.woff2` 7.5MB）
- **为什么改**：该声明**没有** `unicode-range`，且 `font-weight: 100 900` 全量可变 —— 页面一用就整包 7.5MB 全量下载，是体积头号杀手
- **怎么改的**：按 unicode 区段切成多片声明，浏览器按需取片（**所有字符仍可显示**，不是删字形）
- **省了多少**：首屏常驻体积大幅下降（具体数字实测后回填）；总字符集**一个不删**
- **怎么恢复**：`studio.css` 保留官方原写法，改回单行 `src: url("/fonts/noto-studio.woff2")` 即可
- **功能影响**：**零**，且未删除任何字形

### S2' — 字体：评估后**决定不动**（重要，避免误伤）

- **查到了什么**：`noto-studio.woff2` = **Noto Sans SC 全量可变字体**，31036 字形 / 30890 码位 / `wght 100-900` / **7.42MB**，且 `studio.css` 里该字体族**没有** `unicode-range`（页面一显示中文就整包下载）
- **本可以怎么用**：按 unicode-range 切成 4~5 片
- **为什么不切**：实测权衡后 **无损方案对"包体积"收益为零甚至为负**（分片后压缩字典不再共享，总体积不降反升约 5~15%），启动解析变快但包不变小 —— 与户主"包小、上传快"的核心诉求不吻合
- **另一种诱惑（已排除）**：子集化到常用 3500/6763 字，可砍到 2~3MB，但**生僻字会变豆腐块**，属于功能降级，违反"不要影响功能"底线
- **结论**：原样保留。中文界面的 CJK 全量字体是刚需，删不得
- **CSS 引入顺序（已核实）**：`main.tsx` → `tokens.css` → `app.css` → `studio.css`。studio.css 最后加载，其 `:root` 的 `--ui`/`--mono` 覆盖 tokens 同名变量，故实际生效的是 `"Inter Studio" + "Noto Studio" + "Studio Mono"` 这套

### S3 — 主色替换（户主指定）
- **改了什么**：官方琥珀金 `#DDA144` → 我方 mint-teal 绿
  - 深色主题：`--accent: #4CC9A4`、`--accent-fg: #04342C`、`--accent-wash: #0F3A2E`
  - 浅色主题：`--accent: oklch(72.8% .125 169.4)`、`--accent-fg: oklch(28% .058 170)`、`--accent-wash: #E6F7F1`
  - 另替换 `app.css` 徽章底色、选中圆点、`--accent-ink`
- **配色来源**：深色 **#4CC9A4** / 浅色 **#3FC09A**，采样自我方图标（户主既定色，**非自选**）；已用 sRGB→OKLCH 公式精确换算成官方同款色彩体系
- **共改 8 处**：`tokens.css` 6 处 + `app.css` 2 处，**扫描残留官方主色 0 处**
- **中性色不动**：`--text/--muted/--border` 等灰阶令牌一律保留，保证 1:1 结构不变
- **功能影响**：零，纯视觉

### S4 — 应用图标替换
- **改了什么**：Tauri 打包图标从 Reasonix 官方 `icon.ico/png` 换成户主提供的原版 Tempora LOGO
- **处理过程**：LOGO 右下角有第三方水印 → 用"上方最近干净像素整片替换"方案去除（27523 像素，保留背景渐变，主体零损伤）；再由 1024px 原图生成 icon.ico / icon.png / 128x128 / 32x32 全套
- **效果**：窗口标题栏、任务栏均为户主 LOGO（已截图验证）
- **功能影响**：零，仅视觉

### S5 — 壳入口路径修正（bug 修复，非瘦身）
- **问题**：壳窗口永远卡在"正在连接内核…"，React 不启动
- **根因**：两层 ① 壳 URL 配了 `/_studio/` 前缀，而前端构建 `base: "./"`、内核 `withPage` 用 `_studio/assets/xxx` 在 dist 里 stat 找不到文件 → 全部回落内核兜底返回 index.html → JS module 因 MIME `text/html` 拒载；② 内核自动发现前端的路径是 `<exe目录>/frontend-next/dist`，之前不存在
- **修复**：壳 URL 改为 `http://127.0.0.1:8787/`（根路由，官方设计意图）；前端产物复制到 `build/frontend-next/dist`，**内核免参数自动发现**
- **验证**：`/assets/index-*.js` 返回 `text/javascript` 593576B（真实 JS）；壳内主界面完整渲染，底部状态栏带真实会话数据
- **功能影响**：零（这正是官方桌面壳的预期工作方式）

## 2. 评估中 / 待户主拍板

（暂无。保持空表，任何新提议先填这里再动手。）

## 3. 实测数据台账（2026-09-26 凌晨实测）

| 指标 | 官方 Electron 版 | Tauri 本版 | 备注 |
|---|---|---|---|
| 壳 exe 体积 | ~150MB（Electron 运行时，官方参考值） | **14.1MB**（14,750,208 B） | release 优化编译 |
| Go 内核 exe | 同源 | 61.5MB（64,480,256 B） | 同一个内核，无差别 |
| 前端 dist | 14MB | 14MB | 1:1 未砍 |
| 部署总体积 | — | **~90MB**（build 目录 83M） | Electron 光运行时就超 |
| 运行内存（壳进程） | 300MB+ 量级（Electron 多进程，参考值） | **64MB**（WebView2 渲染子进程另计，共享系统组件） | tasklist 实测 |
| 运行内存（内核） | 同源 | 51MB | tasklist 实测 |
| 冷启动 | 上任版本"打开非常慢" | 首次连接到主界面渲染秒级（截图链路验证） | 正式对比待户主体感 |
| 打包/上传 | 上任版本"特别慢" | 待首次 nsis/msi 打包后回填 | |

> 交付物：`G:\Tempora\shell\src-tauri\target\release\tempora-shell.exe`（14.1MB）+ `G:\Tempora\build\`（内核+前端，免参数启动）
> 验收截图：`G:\Tempora\build\shell_shot2.png`（深色欢迎屏）、`G:\Tempora\build\final_release.png`（release 首次设置向导）

## 2026-09-26 中午：三项修复
1. **图标四角漏白** — 根因：图标 alpha 全 255（不透明白底），圆角卡四角显白。
   修复：flood-fill 挖白 + 边缘羽化（`_icon_transparent.py`），icon.png/128x128/32x32/icon.ico 四文件验证四角 alpha=0。
2. **黑色控制台窗口** — 真凶：桌面快捷方式指向 `D:/Tempora/tempora-shell.exe`（旧编译，PE subsystem=3 CONSOLE）。
   G 盘新版早已是 GUI subsystem=2 但没同步。已把带托盘的新壳覆盖 D 盘，硬验证 subsystem=2。
   壳的 build.rs 加 `/SUBSYSTEM:WINDOWS`（Rust 侧根修）；内核 tempora.exe 直接 patch PE 头 3→2（机器无 Go SDK 无法重编，备份 `.subsysbak`）。
3. **点关闭→托盘** — main.rs 原本 7 行无托盘。新增：`tray-icon` feature + system tray
   （左键显隐切换 / 右键菜单「显示主窗口」「退出 Tempora」/ `CloseRequested` 拦截 → `hide()`）。
   关闭不再退出，托盘右键退出才是真退出。
4. 安装包重打：`G:/Tempora/Tempora_0.1.0_x64-setup.exe`（13,144,236 字节，含以上全部 + 装完自动跳完成页 hooks）。

## 2026-09-26 中午：三项修复（用户验收前三项反馈）
1. **图标四角漏白** — 根因：icons 全套 alpha=255 不透明，圆角卡四角是白底 (254,254,254)。
   修复：`_icon_transparent.py` flood-fill 从四角挖白 + 边界羽化，icon.png/128x128/32x32/icon.ico 四文件四角 alpha=0（PIL 硬验证）；ico 重嵌 7 尺寸。
2. **黑色控制台窗口** — 真凶：桌面快捷方式指向 `D:/Tempora/tempora-shell.exe`（旧编译 14,879,232 字节，PE subsystem=3 CONSOLE）。G 盘新版 (14,781,440, subsystem=2) 没同步过去。已把新壳覆盖 D 盘并验证 subsystem=2；G 盘壳 build.rs 此前已加 /SUBSYSTEM:WINDOWS 根修。
3. **点关闭→托盘** — main.rs 原本 7 行无托盘。新增 `tray-icon` feature：左键显隐切换 / 右键菜单「显示主窗口」「退出 Tempora」/ `CloseRequested` 拦截 → `hide()`。关闭不再退出，托盘右键退出才是真退出。
4. **安装包重打**：`G:/Tempora/Tempora_0.1.0_x64-setup.exe`（13,144,236 字节，含以上全部 + 装完自动跳完成页 hooks）。僵尸安装器 PID 46156 占锁导致首次 bundle 拒绝访问，Stop-Process 后用 tauri 自带 makensis 直打成功（exit=0）。
