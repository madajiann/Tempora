# Tempora 换号交接（接手人从这份开始）

> 写给接手 WorkBuddy 账号、继续 Tempora 开发的人。
> 写于 **2026-10-22**。仓库 `G:/Tempora`，`main @ b3dfefc`，本地=远端，工作区干净。
>
> **分工**：仓库全景手册是 [`docs/HANDOVER.md`](HANDOVER.md)（架构/构建/发版/服务器运维/排障，必读）。
> 本文档只写 HANDOVER 里没有的：**上一次工作的精确快照、换号影响面、悬着的事的优先级、接手自检**。
> 两份都读完再动手。

---

## 0. 三十秒速览

- **Tempora** = 桌面编码 Agent（React SPA + Tauri 壳 + Go 内核），上游 DeepSeek-Reasonix 的复制式 fork，版本 **0.1.23 已在线上**，更新第一端点 `https://tempora.yomm.cc`。
- **当前唯一未发版的改动**：输入框草稿按会话保存（上游 #11176 移植，commit `b3dfefc`），已构建、已同步 `D:/Tempora`、已真机验证，**就差走一次发版流程变成 0.1.24**。
- **发版全流程**：`~/.workbuddy/skills/tempora-release/SKILL.md`（含全部踩过的坑，本机文件不随号变）+ HANDOVER §6.2。
- **一个大坑刚踩过**：`git push` 间歇 502 时用 `scripts/push_via_api.py` 兜底，但它会用**陈旧断点**重建 commit 制造远端重复线（详见 §2.2 和 HANDOVER §6.4 的警告），事后靠 `--force-with-lease` 对齐修复。修复脚本或改文档是接手后的高优事项。

---

## 1. 接手第一步（自检清单，按顺序做）

```bash
# 1) 仓库状态核对 —— 四行输出应分别是 b3dfefc / b3dfefc / 无分叉 / 干净
cd /g/Tempora && git fetch origin
git rev-parse main origin/main
git merge-base --is-ancestor origin/main main && echo 无分叉
git status --short

# 2) 版本三处一致性（应全是 0.1.23）
grep '"version"' shell/src-tauri/tauri.conf.json
grep 'version' site-version.json

# 3) 线上通道（应返回 0.1.23）
curl -s https://tempora.yomm.cc/latest.json
curl -s https://cdn.jsdelivr.net/gh/madajiann/Tempora@main/updates/latest.json

# 4) 真机能跑
# 启动 D:/Tempora/tempora-shell.exe，主界面应正常渲染（v0.1.23，带草稿保存功能）
```

全部符合 → 状态与本文档一致，可以直接开工。不符合 → 先查 HANDOVER §7.3 症状速查表。

---

## 2. 上一次工作的精确快照（2026-10-14 完成，此后至 10-22 无任何改动）

### 2.1 已完成：输入框草稿按会话保存（上游 PR #11176 移植）

- **commit**：`b3dfefc`「feat: 输入框草稿按会话保存（移植上游 #11176）」，10 个文件，+240/-9，已推送。
- **实现**：
  - 新增 `app/frontend/src/ui/drafts.ts`：草稿存 localStorage，按「远程主机 + 工作区根 + 会话路径」三元组隔离，32KB 上限，存储前缀 `tempora-draft-v1:`（上游用 `rx-studio-draft-v1:`，刻意分开命名空间）。
  - 新增 `useDraft.ts`：250ms 防抖写入；`pagehide` 立即冲刷；**提交只有内核确认送达后才清草稿**（发送中刷新/被拒都能找回）。
  - 接线：`Composer.tsx`（draftKey prop + useDraft hook）、`Pane.tsx`（传会话键）、`App.tsx`（归档清草稿）、`Workspaces.tsx`/`RemoteHosts.tsx`（删除会话清草稿）、`roots.ts`（RUNTIME_EVENT 白名单加 `pagehide`）。
  - 测试：`drafts.test.ts` 3 个单测 + `Composer.interaction.test.tsx` 新增 6 个交互用例。
- **验证结论**：
  - `tsc --noEmit` 零错误。
  - vitest 相关 5 文件：45 过 / 1 挂。挂的是 `session-new.interaction.test.tsx > does not fall back to the first folder in the tree` —— **stash 基线比对确认是既有失败，新增失败 0**（基线比对方法见 HANDOVER §3.3）。
  - vite build 成功；已同步 `D:/Tempora/frontend-next/dist/`（内容级 `cp -rf dist/.`）；真实壳前台抓屏验证主界面渲染正常（v0.1.23，无白屏）。
- **用户侧表现**：输入框打字 → 切会话再切回 → 草稿还在；刷新/重启壳 → 草稿还在；发送成功 → 草稿清除；删除/归档会话 → 对应草稿清除。

### 2.2 推送事故记录（重要，别重蹈）

1. `git push` 连续 502（沙箱代理掐 github.com 的 CONNECT，等 1~2 分钟通常自愈——这次等了 60 秒也没好）。
2. 走 `scripts/push_via_api.py` 兜底，**它用了上次会话留下的陈旧断点 `a64382c2e9`**，把 4 个已在远端的 docs commit 又重建了一遍 → 远端出现内容重复的平行线，且脚本承诺的"自动 reset --soft 对齐"**没有生效**（本地仍指旧 commit）。
3. 处置（已验证有效的配方）：
   ```bash
   git fetch origin
   git diff --stat main origin/main        # 必须为空（树内容一致）才能强推
   git push origin main --force-with-lease
   git fetch origin && git rev-parse main origin/main   # 两个 sha 相同 = 对齐完成
   ```
4. **教训**：HANDOVER §6.4 对该脚本改进版的描述偏乐观。接手后建议：① 修脚本断点逻辑（断点必须先和远端 tip 比对，落后即弃用）；② 或者干脆把 §6.4 改写成"优先等 git push 恢复，脚本兜底后必须按上面配方核验对齐"。

### 2.3 顺带发现（未处理）

- README.md（仓库根）两处过时：① 发版命令还写着老的 `scripts/release_updater.py`（HANDOVER §6.1 已明确它与 `upload_assets.py` 冲突，现流程是 `device_publish.py` + `upload_assets.py`）；② 更新通道端点顺序没标注 `raw.githubusercontent.com` 本机被墙、靠香港镜像兜底。

---

## 3. 换号影响面（什么会丢、什么不会）

| 资产 | 位置 | 换号后 |
|---|---|---|
| 仓库 / D:/Tempora 运行目录 | `G:/Tempora`、`D:/Tempora` | ✅ 不受影响（磁盘文件） |
| SSH 密钥 / GitHub PAT / 签名私钥 | `~/.ssh/id_ed25519_deploy`、`~/.tempora/token`、`~/.tauri/tempora.key` | ✅ 不受影响（Windows 用户目录，**签名私钥泄漏=别人能推任意官方更新，务必保密**） |
| WorkBuddy 技能（含 tempora-release 发版技能） | `C:/Users/Administrator/.workbuddy/skills/` | ✅ 在 Windows 用户目录下，不随 WorkBuddy 账号变 |
| WorkBuddy 账号级长期记忆 | `~/.workbuddy/user-<uuid>/MEMORY.md` | ❌ 按账号隔离，新号读不到 → 本文档 + HANDOVER 是唯一可靠载体 |
| WorkBuddy 会话历史 / conversation_search | 服务端 | ❌ 新号搜不到旧会话 |

**给新号的建议**：接手后把本文档 §4 的用户偏好写进新号的长期记忆（用户明确要求过的规矩，见下）。

---

## 4. 用户偏好与工作纪律（多次明确要求，必须遵守）

- **直接干活，少铺垫少客套**；方案说人话，一次给一条最短路径，不要冗长多选项列表。
- **禁止猜测和反复试错**：先读现有源码对照原始实现（如 billd-desk、上游 PR patch），结果必须可验证（实车数据、逐字节比对、截图）。
- **报错与结论给硬证据**（时间戳、字节数、行数、sha），不给"我感觉/可能"。
- **完整完成承诺后再交付**，禁止部分发布；已实现的功能不能遗忘或回退。
- **会话收尾三件套**：整理文档 → 更新记忆 → 清理垃圾（临时脚本、探针文件用完即删）。
- **C 盘不留工作文件**：临时产物用完删掉；项目本体一律放 G 盘等数据盘。
- 遇到一条路反复失败，快速换路子，不要原地折腾。
- 主色/品牌色不能自己挑，从 LOGO 源文件采样（Tempora 绿：深色 `#4CC9A4` / 浅色 `#3FC09A`）。

---

## 5. 挂着的事（按优先级，接手即做）

### P0 —— 发版 0.1.24 ✅ **已完成（2026-10-22）**

**实际发版内容**：草稿保存（b3dfefc）+ **字体清晰度修复**（户主 10-22 明示的自研改动：字号全档上调、中文字重修真、默认对比度 normal，详见 commit `7e6d9f3` 与 HANDOVER §10.5）+ 上游蒸馏台账（UPSTREAM_LOG 末章，8 项移植待拍板）。
发版结果：`main @ 7e6d9f3` 已推；HK/ GitHub 双端点 0.1.24 生效（sha256 三方一致 `529c105c…3898a3d`）；jsdelivr 已 purge；真机 v0.1.24 验证通过。原文步骤存档如下：

草稿功能已在仓库和 `D:/Tempora`，但线上通道还是 0.1.23，老用户拿不到。步骤照 HANDOVER §6.2 走，要点：

1. 版本号三处：`tauri.conf.json`、`Cargo.toml`、`site-version.json` → **0.1.24**。
2. `site-version.json` 的 notes 建议文案（会进客户端更新提示，写人话）：
   `"会话输入框的草稿现在按会话保存：切换会话、刷新甚至重启后，没发出去的字都还在；只有真正发送成功才会清掉。"`
3. 三件套构建（内核本次**没改**，可跳过内核重编，但壳和前端必须重出）→ HK 镜像 + GitHub Release + GET 刷 jsdelivr → 四端点验证 → 真机截图 → 清旧包。
4. 发版技能：`~/.workbuddy/skills/tempora-release/SKILL.md`（含每一步的坑）。

### P1 —— 文档与脚本债

| 项 | 说明 |
|---|---|
| 修 `scripts/push_via_api.py` 断点逻辑 | 见 §2.2，断点必须先与远端 tip 比对 |
| 更新 HANDOVER §6.4 | 把脚本描述改悲观 + 写入 force-with-lease 对齐配方（§2.2 已验证） |
| README 两处过时 | 见 §2.3 |

### P2 —— 待拍板（HANDOVER §11.2 原样悬着）

- #11209 残余：项目声明程序（钩子/LSP/shell 路径）首次批准弹窗（要前端交互 + 主目录信任记录）
- 内核 3 处硬编码 `crash.tempora.io`：开源发布前决定换不换域名
- 约 115 处文档死链（低优先）

### P3 —— P1 体验项（HANDOVER §11.1，草稿项已完成✅，剩余）

对话内 Ctrl+F、项目「在文件管理器中显示」、多轮无进展提示、子代理记录入口、内置浏览器工具开关、模型服务可排序、应用内反馈、MCP 单工具禁用。

---

## 6. 红线（HANDOVER §2.2 原样重抄，一条都不能破）

1. UI 组件 1:1 保留，不做外观改动。
2. CodeMirror 依赖、中文字体分片，不替换。
3. Go 内核业务逻辑只做安全/稳定性补丁，不重构。
4. LICENSE 双版权行不能删。

**另有工程纪律**（HANDOVER §3.3 / §13.2，血泪换来的）：
- 测试有既有失败基线，判断回归**唯一**可靠方法 = stash 改动跑基线比对，新增失败必须为 0。
- 同一文件不要在同一条消息里并发多个编辑；改完必须 Read 复核，别信"Successfully edited"。
- Go 编译/测试前台 + 脱离沙箱；Python 用 `binaries/python/embed/python.exe`（托管版缺标准库）。
- 改白名单/鉴权相关代码必须真机启动验证（0.1.20 卡启动画面的教训）。

---

## 7. 常用入口

| 什么 | 哪里 |
|---|---|
| 仓库全景手册 | `G:/Tempora/docs/HANDOVER.md` |
| 发版技能 | `~/.workbuddy/skills/tempora-release/SKILL.md` |
| 差距分析 / 上游台账 / 瘦身记录 | `docs/GAP_ANALYSIS.md` / `docs/UPSTREAM_LOG.md` / `docs/CUTLIST.md` |
| 上游参考副本 | `G:/Tempora/reference/DeepSeek-Reasonix/`（会过期，别当唯一依据） |
| 前端基线 diff | `kernel/desktop/frontend-next/src`（2.20.0）vs `app/frontend/src`，diff 加 `--strip-trailing-cr` |
| 官网 / 仓库 | https://tempora.yomm.cc · https://github.com/madajiann/Tempora |
| 香港服务器 | `root@103.84.110.200`（Caddy 不是 nginx，`/opt/tempora-site`，ssh 参数见 HANDOVER §8） |
