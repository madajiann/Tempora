# HANDOFF — Tempora 交接文档

> 最后更新：2026-09-12（通宵 fork 工程交付）
> 维护人接手前必读。配套文档：[WORKLOG.md](WORKLOG.md)（过程日志）、[NOTICE.md](NOTICE.md)（fork 署名与差异）、[UPSTREAM-SYNC.md](UPSTREAM-SYNC.md)（上游同步手册）。

## 1. 一句话现状

**Tempora 已可用**：DeepSeek-Reasonix（上游 v1.38.6 时代，commit `036c7c5`）全量 fork + 品牌更名 + 智谱 GLM 出厂接入，全库编译通过、核心测试通过、`bin/tempora.exe` 可直接安装使用。

## 2. 目录布局

```
G:\Tempora\
├── tempora\          ← 成品仓库（本项目，git 已初始化，含上游 remote）
│   ├── bin\tempora.exe        ← 最终产物（带版本号）
│   ├── install.cmd / install.ps1  ← Windows 一键安装（用户级，免管理员）
│   ├── cmd\tempora\           ← CLI 入口
│   ├── internal\              ← ~100 个功能包（agent/tool/permission/...）
│   ├── desktop\               ← 桌面端（嵌套 Go 模块 tempora/desktop）
│   ├── sdk\go\                ← 扩展 SDK（嵌套模块 tempora/sdk/go）
│   └── reference 无；上游原始克隆在 ..
└── reference\DeepSeek-Reasonix\  ← 上游原版克隆（只读参考，未改动）
```

## 3. 环境信息（本机）

| 项 | 值 |
|---|---|
| Go 工具链 | `C:\Users\Administrator\AppData\Local\go`（便携版 1.26.6，需加入 PATH） |
| 代理 | `http://127.0.0.1:7897`（Clash Verge 默认混合端口；git/go/curl 都走它） |
| 本仓库 git 代理 | 已写入 `tempora/.git/config`（仅本仓库生效） |
| 上游 remote | `upstream → https://github.com/esengine/DeepSeek-Reasonix.git`（push 已禁用） |

构建命令：

```bash
export PATH="/c/Users/Administrator/AppData/Local/go/bin:$PATH"   # Git Bash
cd G:\Tempora\tempora
go build -o bin/tempora.exe ./cmd/tempora
```

## 4. 已完成的工作（详见 WORKLOG.md）

1. **调研**：确认上游 MIT 开源、活跃度（日提交数十次、v1.38.6 发版）✅
2. **Fork 改名**：~19,600 处品牌字符串、26 个文件/目录重命名、Go 模块 `reasonix`→`tempora`、嵌套模块 `tempora/sdk/go`、配置路径 `%APPDATA%\tempora`、环境变量 `TEMPORA_`、npm 包 `tempora` ✅（`go build ./...` 一次通过）
3. **智谱 GLM 接入**：出厂默认 4 provider（deepseek-flash/pro + glm-flash=glm-5.3-flash、glm-pro=glm-5.3，open.bigmodel.cn，`GLM_API_KEY`）；6 个上游 GLM 预设目录加入 5.3 系列并改默认 glm-5.3-flash ✅（`internal/config` 测试全绿）
4. **图标**：品牌蓝 #0153e5 + 白色沙漏（时间主题），SVG 母版 ×2 + 自研纯 Go 光栅化器（`G:\Tempora\icontool`）生成 PNG/ICO/ICNS 全套，`desktop` 资产测试通过 ✅
5. **安装脚本**：install.cmd / install.ps1 ✅
6. **文档**：README ×2、CHANGELOG、LICENSE（保留上游署名）、NOTICE、UPSTREAM-SYNC、HANDOFF、WORKLOG ✅

## 5. 关键决策记录（为什么这么做）

| 决策 | 理由 |
|---|---|
| 默认模型仍是 `deepseek-flash` | 上游整个引擎围绕 DeepSeek prefix-cache 稳定性设计；GLM 开箱可选（`--model glm-flash`），但默认通道不动 |
| GLM 上下文窗口填 202,752 | 参照上游对 glm-5 系的已知值（qwenModelContextOverrides），保守估计；可在 tempora.toml 覆盖 |
| GLM 不填价格 | 无权威价格数据，不编造；billing 对缺价模型优雅降级。**待办：补 `internal/config/pricing.go` 体系下的 GLM 定价** |
| `tempora upgrade` 指向占位仓库 `tempora-dev/Tempora` | 不能让它把用户机器上的 Tempora 回装成上游 reasonix；等你建了 GitHub 仓库后一键替换占位符 |
| 遥测/崩溃上报域名 `*.tempora.io` 为死域名 | 网络层静默失败 = 零数据外泄；将来若不要遥测可直接删，或换自己的后端 |
| 上游 CHANGELOG/release-notes/logo 保留原名 | 历史记录与出处，不属于品牌残留（见 NOTICE.md 第 5 条） |
| 图标沿用 #0153e5 品牌蓝 | `desktop/appicon_asset_test.go` 逐像素断言品牌蓝 + 安全区；改色需同步改该测试 |

## 6. 马上要做的事（接手清单）

- [ ] **建 GitHub 仓库**（如 `tempora-dev/Tempora`），全局替换占位符 `tempora-dev` / `tempora-dev/Tempora`（约 30 个文件，`grep -rl "tempora-dev" .`）
- [ ] 设置 `DEEPSEEK_API_KEY` / `GLM_API_KEY` 真实 key，实测 `tempora --model glm-flash` 对话与工具调用
- [ ] GLM 定价录入（billing 目录）
- [ ] 决定遥测：删掉 or 自建后端（`internal/telemetry`、`internal/crashreport`、desktop/updater）
- [ ] （可选）发布 npm 包 `tempora`（npm/tempora/ 已就绪，`npm/build.mjs` 构建分发壳）
- [ ] （可选）桌面端打包（Wails/CI 流程在 .github/workflows/release-desktop.yml，占位仓库需替换）
- [ ] （可选）上游同步演练：`git fetch upstream --unshallow` 后按 UPSTREAM-SYNC.md 走一遍

## 7. 已知限制 / 风险

- **上游同步**：改名后 merge 主要靠 git 重命名检测，provider/billing 是冲突高发区（上游迭代极快）；GLM 出厂预设为 Tempora 独有，每次同步需人工确认这两处。
- **sdk/go 嵌套模块**：上游的 examples 导入路径本来就是坏的（指向上游 URL 而非模块名），Tempora 已修为 `tempora/sdk/go`；同步时留意。
- **heartbeat i18n 提示**里写的更新页 `https://tempora.io/changelog/` 是死链，运行时会自动回退到本地 `release-notes/releases.json`（上游历史），行为正常但内容是上游日志。
- **site/ 官网源码**与 `docs/index.html` 已换占位链接但未部署；`esengine.github.io/DeepSeek-Reasonix` 上游站点保持原样（出处链接）。
- `prod_test/`、`benchmarks/e2e/` 未在本机跑（需要真实 API key / 长时运行），CI 环境才完整执行。

## 8. 验证记录（交付时的状态）

- `go build ./...`：PASS（全模块，改名后一次通过；GLM 接入后复验通过）
- `go test ./internal/config/`：PASS（98s，含 GLM 出厂与预设改动）
- `go test ./internal/cli/`：PASS（98.9s 全包，修复 3 个改名/GLM 回声测试后）
- `go test ./internal/boot/`：PASS（154s，golden prefix_shape 基线已按新出厂模型重生成）
- `go test ./internal/agent/ ./internal/tool/... ./internal/skill/ ./internal/billing/ ./internal/agentpreset/ ./internal/doctor/`：PASS
- `go test ./desktop/ -run 'TestAppIcon|TestWindowsICO|TestDarwinICNS'`：PASS
- `go test ./...`（改名后全量快照）：除 sessioncatalog 一个时序敏感用例在系统高负载下偶发外全部通过（隔离复跑 PASS）；该快照不含后续 GLM/cli 修复，受影响包均已单独复验
- `bin/tempora.exe --version` → `tempora v0.1.0 (279165…→e2b270c 最终构建)`；`tempora doctor` → 4 provider 就绪
- 未跑：prod_test、benchmarks/e2e（需真实 API key）；sessioncatalog 全包复跑建议拿到 key 后补一次
