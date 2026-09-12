# HANDOFF — Tempora 交接文档

> 最后更新：2026-09-12 下午（GitHub 仓库已建好并完成首次推送）
> 配套文档：[WORKLOG.md](WORKLOG.md)（过程日志）、[NOTICE.md](NOTICE.md)（fork 署名与差异）、[UPSTREAM-SYNC.md](UPSTREAM-SYNC.md)（上游同步手册）、[GITHUB-SETUP.md](GITHUB-SETUP.md)（建仓推送，零基础向）

## 1. 一句话现状

**Tempora v0.1.0 完整可用**：DeepSeek-Reasonix 全量 fork + 品牌更名 + 智谱 GLM 出厂接入 + 双击即装的 exe 安装器（20.3MB）。**已推送 GitHub：https://github.com/madajiann/Tempora（Private，分支 main，完整历史 6,958+ 提交）**。

## 2. 当前产物与安装状态

| 产物 | 位置 | 状态 |
|---|---|---|
| 安装器 exe | `G:\Tempora\tempora\dist\TemporaSetup-v0.1.0.exe` | **20.3MB**，双击即装，已真机验证 |
| CLI 二进制 | `G:\Tempora\tempora\bin\tempora.exe` | 19.2MB（UPX 压缩），`--version` 验证过 |
| 安装状态 | **Administrator 账户已安装**（`%LOCALAPPDATA%\Programs\tempora` + 用户 PATH） | 是我验证时装的；**如果平时用 Ly 账户，Ly 下需重新双击安装器一次**（各账户独立） |
| 卸载方式 | 删除 `AppData\Local\Programs\tempora` 目录 + 用户 PATH 里对应条目 | 安装器输出里有说明 |

实测命令（新开终端）：

```powershell
tempora doctor                          # 应显示 4 个 provider
$env:DEEPSEEK_API_KEY="sk-..."          # 或 $env:GLM_API_KEY="智谱key"
tempora --model glm-flash               # GLM-5.3-Flash 交互会话
tempora -p "单次任务"                    # 无交互模式
```

## 3. 目录布局

```
G:\Tempora\
├── tempora\                      ← 成品仓库（git 已初始化，5 个提交，分支 main-v2）
│   ├── dist\TemporaSetup-v0.1.0.exe   ← 安装器产物（gitignore，本地产物）
│   ├── bin\tempora.exe                ← CLI 构建产物（gitignore）
│   ├── cmd\tempora\                   ← CLI 入口
│   ├── internal\                      ← ~100 个功能包
│   ├── desktop\                       ← 桌面端（嵌套模块，未打包）
│   ├── sdk\go\                        ← 扩展 SDK（嵌套模块 tempora/sdk/go）
│   ├── tools\windowsinstaller\        ← 安装器源码（嵌套模块，内嵌 payload）
│   └── install.cmd / install.ps1      ← 脚本安装备选（无安装包时用）
└── reference\DeepSeek-Reasonix\  ← 上游原版克隆（只读参考，勿改）
```

## 4. 环境信息（本机）

| 项 | 值 |
|---|---|
| Go 工具链 | `C:\Users\Administrator\AppData\Local\go`（便携版 1.26.6，Git Bash 需 `export PATH="/c/Users/Administrator/AppData/Local/go/bin:$PATH"`） |
| 代理 | `http://127.0.0.1:7897`（Clash Verge；git/go/curl 都走它） |
| 本仓库 git 代理 | 已写入 `tempora/.git/config`（仅本仓库生效，不影响全局） |
| remotes | `upstream` = 上游仓库（**push 已禁用**防误推）；`origin` 待你建仓后添加 |
| UPX | 未常驻；构建时用 `make windows-installer UPX=<upx.exe 路径>`。下载：https://github.com/upx/upx/releases （upx-4.2.4-win64.zip，解压取 upx.exe） |

常用构建：

```bash
cd G:\Tempora\tempora
go build -o bin/tempora.exe ./cmd/tempora        # 快速构建
make windows-installer UPX=<upx路径>              # 出安装器（不传 UPX 也能出，约 70MB）
go test ./internal/...                            # 测试（desktop、sdk/go 是嵌套模块需进目录测）
```

## 5. 已完成工作清单

1. **调研**：上游 MIT、极活跃（日数十提交、v1.38.6 发版当日）、源码 ~70 万行 Go ✅
2. **Fork 改名**：~19,600 处品牌串、26 个文件重命名、模块 `reasonix`→`tempora`、配置 `%APPDATA%\tempora`、环境变量 `TEMPORA_`、npm 元数据；`go build ./...` 一次通过 ✅
3. **智谱 GLM**：出厂 4 provider（deepseek-flash/pro + **glm-flash=glm-5.3-flash**、**glm-pro=glm-5.3**，open.bigmodel.cn + `GLM_API_KEY`）；6 个 GLM 预设加 5.3 系列并改默认 flash；向导家族分组（GLM 家族对称 DeepSeek）✅
4. **图标**：品牌蓝 #0153e5 + 白沙漏 + 海蓝沙（SVG 母版 ×2 + 纯 Go 光栅化器 `G:\Tempora\icontool` → PNG/ICO/ICNS/Linux 全套），上游资产测试通过 ✅
5. **exe 安装器**：`tools/windowsinstaller`（嵌套 Go 模块，go:embed payload），写用户 PATH + WM_SETTINGCHANGE 广播，免管理员；UPX 后 20.3MB ✅
6. **体积优化**：UPX 69.5MB→19.2MB（27.6%），对齐上游发布体量 ✅
7. **测试**：核心包全绿（config/cli/boot/agent/tool/billing/agentpreset/doctor/桌面图标资产），3 个改名回声测试修复，golden prefix_shape 基线按新出厂模型重生成 ✅
8. **文档**：README×2、CHANGELOG、LICENSE（双版权）、NOTICE、UPSTREAM-SYNC、GITHUB-SETUP、HANDOFF、WORKLOG ✅

## 6. 关键决策记录（为什么这么做）

| 决策 | 理由 |
|---|---|
| 默认模型仍是 `deepseek-flash` | 引擎围绕 DeepSeek prefix-cache 稳定性设计；GLM 开箱可选（`--model glm-flash`），默认通道不动 |
| GLM 上下文窗口填 202,752 | 参照上游对 glm-5 系已知值，保守估计；可在 tempora.toml 覆盖 |
| GLM 暂不填价格 | 无权威价格不编造；billing 对缺价优雅降级。**待补录** |
| 安装器 = 自包含 Go exe，不用 NSIS/Inno | 零外部工具链，`make windows-installer` 一条命令；嵌套模块不污染主模块构建/CI |
| payload 用 UPX（69.5→19.2MB） | 对齐上游发布体量（上游 windows zip 21MB）；UPX 壳可能提高杀软误报率，遇误报出未压缩版 |
| `tempora upgrade` 指向占位仓库 `tempora-dev/Tempora` | 防止把用户机器上的 Tempora 回装成上游 reasonix；建仓后全局替换 `tempora-dev` |
| 遥测/崩溃上报域名 `*.tempora.io` 为死域名 | 静默失败 = 零数据外泄；将来删掉或换自有后端 |
| 上游 CHANGELOG/release-notes/logo 保留原名 | 历史记录与出处署名，非品牌残留（NOTICE.md 第 5 条） |
| 图标沿用 #0153e5 品牌蓝 | `desktop/appicon_asset_test.go` 逐像素断言；改色需同步改该测试 |

## 7. 接下来要做（按优先级）

1. ~~建 GitHub 仓库并推送~~ ✅ **已完成（2026-09-12）**：`origin` = https://github.com/madajiann/Tempora（Private）。占位符 `tempora-dev`→`madajiann` 已替换并提交（9b3250e，32 文件/76 处；测试长度夹具与历史文档有意保留）。推送要点：① PAT 需 `repo`+`workflow` 两个 scope；② 本 PortableGit 的 credential-helper-selector 在无界面环境会静默崩溃，非交互推送须 `-c credential.helper=` 绕过；③ 仓库原为 shallow clone，首次推送需 `git fetch upstream --unshallow` 补全历史，已完成。PAT 明文存于 `.git/config` 的 origin URL，注意保密
2. **填 key 实测**：`tempora setup` 向导或环境变量，验证 GLM/DeepSeek 真实对话与工具调用
3. GLM 定价录入（`internal/config/pricing.go` 体系）
4. 遥测去留决策（`internal/telemetry`、`internal/crashreport`、desktop/updater）
5. 可选：npm 包发布、桌面端打包、上游同步演练（`git fetch upstream --unshallow`）

## 8. 已知限制 / 风险

- **上游同步**：改名合并靠 git 重命名检测，provider/billing 是冲突高发区；GLM 出厂预设（config.go 的 Default()、provider_presets.go）是 Tempora 独有，每次同步人工确认这两处
- **多账户安装**：安装器按 Windows 用户隔离；Administrator 下已装，Ly（或其他账户）要用需各自双击安装器
- **UPX 杀软误报**：极少数杀软对 UPX 壳敏感；出未压缩版即可（Makefile 不传 UPX）
- **heartbeat 提示**里的 `https://tempora.io/changelog/` 是死链，运行时自动回退本地 `release-notes/releases.json`（上游历史），行为正常
- **未跑**：prod_test、benchmarks/e2e（需真实 API key）；`go test ./...` 全量在拿到 key 后建议补一次
- **桌面 `_*.txt` 探测文件**：2026-09-12 凌晨桌面出现的 6 个探测 TXT（WebView2/VS BuildTools/rustup 等）**不是本项目产生**——时间线与内容指向昨晚并行在机器上跑的另一个工具（当时有 vs_buildtools 安装进程在装 VS BuildTools），与 Tempora 工程无关，可自行删除

## 9. 验证记录（交付态）

- `go build ./...` PASS；GLM 接入后复验 PASS
- `go test ./internal/{config,cli,boot,agent,tool/...,skill,billing,agentpreset,doctor}` 全 PASS（config 98s / cli 98.9s / boot 154s）
- `go test ./desktop/ -run 'TestAppIcon|TestWindowsICO|TestDarwinICNS'` PASS
- 全量快照（改名后）：仅 sessioncatalog 一个时序用例在高负载下偶发，隔离复跑 PASS
- 安装器真机安装 PASS：文件落位 + 注册表用户 PATH + PowerShell 按 PATH 解析到 v0.1.0
- `bin/tempora.exe --version` → `tempora v0.1.0`；`tempora doctor` → 4 provider 就绪

## 10. git 提交历史（本仓库）

```
03e2ba2 Add Windows setup exe installer + GitHub onboarding guide
7669b0c Docs: record final verification results in HANDOFF/WORKLOG
e2b270c Fix rebrand-length test fixtures, add GLM family grouping, refresh golden baseline
279165a Tempora v0.1.0: fork DeepSeek-Reasonix, full rebrand + Zhipu GLM
036c7c5 (上游基线) docs(release): 准备 v1.38.7 中英更新日志 #10151
```
