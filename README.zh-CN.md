<p align="center">
  <img src="docs/logo-tempora.svg" alt="Tempora" width="360"/>
</p>

<p align="center">
  <strong>Tempora</strong> — 一个为长时间自主任务而生的编码 agent。Fork 自
  <a href="https://github.com/esengine/DeepSeek-Reasonix">DeepSeek-Reasonix</a>（MIT），开箱即用 DeepSeek + 智谱 GLM 双通道。
</p>

<p align="center">
  简体中文 · <a href="README.md">English</a> · <a href="NOTICE.md">Fork 说明</a> · <a href="UPSTREAM-SYNC.md">上游同步</a> · <a href="HANDOFF.md">交接文档</a>
</p>

---

## 这是什么

Tempora（源自拉丁语 tempus，时间）：一个你可以"放着跑"的编码 agent。单一本地引擎、四种入口：

- **终端 TUI**（全屏交互界面）
- **桌面应用**（Windows / macOS / Linux）
- **本地 Web UI**（`tempora web`）
- **编辑器集成**（ACP 协议，VS Code 扩展）

围绕 DeepSeek 的 prefix-cache 稳定性设计，长时间运行 token 成本极低；同时内置智谱 GLM 通道。

## 出厂模型

| 名称 | 模型 | Provider | 环境变量 |
|---|---|---|---|
| `deepseek-flash`（默认） | deepseek-v4-flash | api.deepseek.com | `DEEPSEEK_API_KEY` |
| `deepseek-pro` | deepseek-v4-pro | api.deepseek.com | `DEEPSEEK_API_KEY` |
| `glm-flash` | glm-5.3-flash | open.bigmodel.cn | `GLM_API_KEY` |
| `glm-pro` | glm-5.3 | open.bigmodel.cn | `GLM_API_KEY` |

更多预设（z.ai 国际版、GLM Coding Plan、Kimi、MiniMax、Qwen 等）见 `tempora setup` 向导。

## 快速开始

### 构建（Go 1.26+）

```bash
go build -o bin/tempora.exe ./cmd/tempora     # Windows
go build -o bin/tempora ./cmd/tempora          # Linux / macOS
```

### 安装（Windows）

双击安装器（免管理员，自动写入用户 PATH）：

```
dist\TemporaSetup-v0.1.0.exe
```

没有现成安装包时，先构建再安装（安装器约 20MB，内含 UPX 压缩的完整 CLI）：

```bash
make windows-installer UPX=/path/to/upx.exe   # 无 UPX 也可构建，体积约 70MB
```

也可以用脚本方式直接安装 `bin\tempora.exe`：双击 `install.cmd`，或 `powershell -ExecutionPolicy Bypass -File install.ps1`。

### 运行

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."        # 或 $env:GLM_API_KEY = "..."
tempora                                  # 交互式 TUI
tempora -p "修复 login.go 里的越界 bug"  # 单次任务
tempora --model glm-flash                # 指定智谱 GLM-5.3-Flash
tempora web --no-open                    # 本地 Web UI
tempora doctor                           # 环境自检
```

## 核心特性（继承自上游）

- **长时间运行**：检查点在 git 之外，任意回合可回滚；会话可恢复
- **透明可控**：逐工具调用权限门、工作区沙箱、Plan 模式（写入需批准）
- **可扩展**：MCP 服务器、Markdown 技能、子 agent（explore / research / review / security-review）
- **多渠道**：IM 机器人网关（微信 / 飞书 / 钉钉 / QQ）、HTTP+SSE 服务模式
- **低成本**：prefix-cache 稳定性优先的请求设计

## 许可证

MIT。本项目为 DeepSeek-Reasonix 的 fork，上游版权与许可见 [LICENSE](LICENSE) 与 [NOTICE.md](NOTICE.md)。

## 致谢

感谢 [esengine](https://github.com/esengine) 与 DeepSeek-Reasonix 的全部贡献者 —— Tempora 站在他们的肩膀上。
