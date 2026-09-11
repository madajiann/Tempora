<p align="center">
  <img src="docs/logo-tempora.svg" alt="Tempora" width="360"/>
</p>

<p align="center">
  <strong>Tempora</strong> — a coding agent built for long-running autonomous sessions.
  Forked from <a href="https://github.com/esengine/DeepSeek-Reasonix">DeepSeek-Reasonix</a> (MIT),
  shipping DeepSeek and Zhipu GLM out of the box.
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> · English · <a href="NOTICE.md">Fork notice</a> · <a href="UPSTREAM-SYNC.md">Upstream sync</a> · <a href="HANDOFF.md">Handoff doc</a>
</p>

---

## What is this

Tempora (from *tempus*, time) is a coding agent you can leave running. One local
engine, four ways in:

- **Terminal TUI** (full-screen interactive session)
- **Desktop app** (Windows / macOS / Linux)
- **Local Web UI** (`tempora web`)
- **Editor integration** (ACP, VS Code extension)

Engineered around DeepSeek's prefix-cache stability for very low token cost on
multi-hour runs, with a built-in Zhipu GLM channel alongside.

## Out-of-the-box models

| Name | Model | Provider | Key env |
|---|---|---|---|
| `deepseek-flash` (default) | deepseek-v4-flash | api.deepseek.com | `DEEPSEEK_API_KEY` |
| `deepseek-pro` | deepseek-v4-pro | api.deepseek.com | `DEEPSEEK_API_KEY` |
| `glm-flash` | glm-5.3-flash | open.bigmodel.cn | `GLM_API_KEY` |
| `glm-pro` | glm-5.3 | open.bigmodel.cn | `GLM_API_KEY` |

More presets (Z.AI global, GLM Coding Plan, Kimi, MiniMax, Qwen, ...) are listed
in the `tempora setup` wizard.

## Quick start

### Build (Go 1.26+)

```bash
go build -o bin/tempora.exe ./cmd/tempora     # Windows
go build -o bin/tempora ./cmd/tempora         # Linux / macOS
```

### Install (Windows)

Run `install.cmd`, or:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Run

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."        # or $env:GLM_API_KEY = "..."
tempora                                  # interactive TUI
tempora -p "fix the off-by-one in login.go"
tempora --model glm-flash                # Zhipu GLM-5.3-Flash
tempora web --no-open                    # local Web UI
tempora doctor                           # environment diagnostics
```

## Highlights (inherited from upstream)

- **Long runs**: checkpoints live outside git — any turn is revertible; sessions resume
- **Transparent & safe**: per-tool-call permission gates, workspace sandbox, plan mode
- **Extensible**: MCP servers, markdown skills, subagents (explore / research / review / security-review)
- **Multi-channel**: IM bot gateway (WeChat / Feishu / DingTalk / QQ), HTTP+SSE serve mode
- **Cheap to run**: request design that keeps the provider prefix cache warm

## License

MIT. Tempora is a fork of DeepSeek-Reasonix; see [LICENSE](LICENSE) and
[NOTICE.md](NOTICE.md) for upstream attribution.

## Acknowledgements

Thanks [esengine](https://github.com/esengine) and every DeepSeek-Reasonix
contributor — Tempora stands on their shoulders.
