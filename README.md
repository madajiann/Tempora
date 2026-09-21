<p align="center">
  <img src="docs/logo-tempora.svg" alt="Tempora" width="360"/>
</p>

<p align="center">
  <strong>Tempora</strong> — a coding agent built for long-running autonomous sessions.
  Forked from <a href="https://github.com/esengine/DeepSeek-Reasonix">DeepSeek-Tempora</a> (MIT),
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

#### CLI

The CLI build requires **Go 1.26+**. The module pins a `toolchain` directive;
keep `GOTOOLCHAIN=auto` so Go downloads the pinned toolchain, or install it.

```bash
go build -o bin/tempora.exe ./cmd/tempora     # Windows
go build -o bin/tempora ./cmd/tempora         # Linux / macOS
```

#### Desktop

The desktop build additionally requires **Node 24+ and pnpm 10**
(`npm install -g pnpm@10`) for the frontend and the Electron shell:

```bash
scripts/desktop-build.sh darwin/arm64 v0.0.0-dev   # one platform per run
```

No platform webview dependencies are needed — the shell ships its own
Chromium. See the [desktop build guide](desktop/README.md#prerequisites).

### Install (Windows)

Double-click the setup executable (per-user install, no admin, PATH handled):

```
dist\TemporaSetup-v0.1.0.exe
```

To build the installer yourself (~20MB with a UPX-packed payload):

```bash
make windows-installer UPX=/path/to/upx.exe   # builds without UPX too, at ~70MB
```

Alternatively install `bin\tempora.exe` via script: run `install.cmd`, or
`powershell -ExecutionPolicy Bypass -File install.ps1`.

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

MIT. Tempora is a fork of DeepSeek-Tempora; see [LICENSE](LICENSE) and
[NOTICE.md](NOTICE.md) for upstream attribution.

## Acknowledgements

Thanks [esengine](https://github.com/esengine) and every DeepSeek-Tempora
contributor — Tempora stands on their shoulders.
