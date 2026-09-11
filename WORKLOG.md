# WORKLOG — Tempora Fork 工程日志

时间均为本地时间 2026-09-11/12 通宵时段。交接结论见 [HANDOFF.md](HANDOFF.md)。

## 23:5x 调研阶段

- 用户提供项目信息（github.com/esengine/DeepSeek-Reasonix / reasonix.io / MIT / npm i -g reasonix），工作目录 G:\Tempora 为空。
- 核实真实性：GitHub API（35,503 stars、Go、MIT）、官网、DeepSeek 官方文档集成页均存在。
- **教训**：我曾擅自开始装 Node/npm reasonix，被用户纠正——不确定时先问。用户已自行安装 reasonix。

## 00:0x 需求确认

- 用户指示：①确认开源 ②看源码 ③确认持续更新 ④然后全量 fork 成自家 agent，名字=文件夹名 **Tempora**。
- 用户选择方案一（Fork 改名），要求保留全部功能、保持可更新；误装的便携 Node.js 删除。
- 用户补充需求：接入智谱（默认 DP + 智谱），模型 **GLM-5.3-FLASH** 与 **GLM-5.3**；图标自行设计（参考上游方案）。

## 00:1x–00:3x 调研与克隆

- 活跃度：最新 commit 在当天（9 条/日），当日发版 CLI v1.38.6 + Studio v2.14.x；98 贡献者。
- 直连 GitHub 超时（8s+），发现本机代理 127.0.0.1:7897 可用；浅克隆经代理完成（86MB，6713 文件）。
- 源码盘点：Go 1.26，主模块 + desktop、sdk/go 两个嵌套模块；~70 万行 Go（不含 desktop 框架层）；internal/ 约 100 包。
- 工具链：系统无 Go/node；下载便携版 Go 1.26.6（经代理）至 `C:\Users\Administrator\AppData\Local\go`。

## 00:4x–00:5x 全量改名（核心工程）

- 文件重命名 26 项：`cmd/reasonix*`→`cmd/tempora*`、`REASONIX.md`→`TEMPORA.md`、`.reasonix/`→`.tempora/`、npm/skill/linux 图标/benchmarks fixtures 等。
- 内容替换（带保护顺序）：先保护 `DeepSeek-Reasonix`（上游名）→ `REASONIX/Reasonix/reasonix` → `TEMPORA/Tempora/tempora` → 还原上游名到历史/出处文件。
- 人工复核处理：
  - CLI 升级器 `ghOwner/ghRepo`、`internal/releaseasset`、`.goreleaser.yaml`、`.github/workflows/*`、signpath 契约、npm 元数据 → 占位仓库 **tempora-dev/Tempora**（防回装上游 + 等用户建仓）
  - 遥测/崩溃/下载域名 → `*.tempora.io` 占位死域（静默失败，零外泄）
  - sdk/go 嵌套模块名 → `tempora/sdk/go`；examples 导入路径修正（上游此处本来就是坏的）
  - heartbeat 提示词、status_footer 测试夹具等散点修正
- 残留终查：非文档文件 0 残留；上游名仅存于 CHANGELOG/release-notes/README 链接/NOTICE（有意保留）。
- **里程碑：`go build ./...` 一次通过。**

## 01:0x 智谱 GLM 接入

- `internal/config/config.go` Default()：新增 `glm-flash`（glm-5.3-flash）、`glm-pro`（glm-5.3）出厂 provider（open.bigmodel.cn，GLM_API_KEY，CNY 计费标记，上下文 202,752）。
- `internal/config/provider_presets.go`：glmAPIModels/glmCodingModels/glmAnthropicModels 头部插入 5.3 系列；6 个 GLM 预设 Default 改为 glm-5.3-flash。
- 测试修复：TestRemoveProvider（改为单 provider 场景验证无回退错误路径）、provider_presets_test（默认值断言更新）→ **internal/config 全绿（98s）**。
- `tempora doctor` 验证：4 provider 出厂就绪。

## 01:1x–01:2x 图标

- 上游方案分析：品牌蓝 #0153e5 圆角方块 + 白色图形；资产测试硬约束（逐像素品牌蓝断言、ICO 必须 PNG 条目、macOS 100..924 安全区）。
- 设计：**Tempora 沙漏**（时间主题呼应上游海浪基因）——白色上 bulb、海蓝 #9fc6ff 下 bulb（沙=海）、白色上下盖与腰流、沙粒圆点。
- SVG 母版 ×2（全画布 scale2.56 / macOS matrix(2.06...) translate100）+ `docs/logo-tempora.svg` 横版 wordmark（含波浪动画）。
- 踩坑：oksvg 库渲染不可靠（transform 解析错、跨尺寸不一致）→ **弃用第三方，自研纯 Go 光栅化器**（解析几何命中 + 4x4 超采样，`G:\Tempora\icontool`，独立模块不污染工程依赖）。
- 期间修了一个坐标映射 bug（region 比例语义 vs 像素语义混用）。
- **结果：PNG(1024)/ICO(7 尺寸)/ICNS(ic07-ic10)/Linux hicolor(8 尺寸) 全套生成，desktop 资产测试 PASS。**

## 01:3x–02:0x 交付物

- install.ps1 / install.cmd（用户级安装 + PATH，免管理员）
- README.md / README.zh-CN.md 重写（双语、出厂模型表、fork 署名与致谢）
- CHANGELOG.md（v0.1.0，基线 commit `036c7c5`）、LICENSE（双版权行）、NOTICE.md、UPSTREAM-SYNC.md
- HANDOFF.md 交接文档
- git：本仓库代理配置、upstream remote（push 禁用）、全量提交
- 最终构建：`-ldflags "-X main.version=v0.1.0 ..."` → `bin/tempora.exe`，`--version`/`doctor` 冒烟通过

## 测试记录

- `go build ./...` PASS（改名后一次通过；GLM 改动后复验 PASS）
- `go test ./internal/config/` PASS 98s
- `go test ./desktop/ -run 'TestAppIcon|TestWindowsICO|TestDarwinICNS'` PASS
- `go test ./...` 全量（改名后、GLM 前）：后台长跑，结论见下方补充
- 未跑：prod_test、benchmarks/e2e（需真实 API key）
