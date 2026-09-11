# Changelog

All notable changes to Tempora are documented here. Tempora forked from
[DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix); the upstream
project's history lives in its own repository.

## [v0.1.0] - 2026-09-12

First Tempora release. Fork baseline: DeepSeek-Reasonix main @ 2026-09-11
(CLI v1.38.6 era), upstream commit `036c7c50c5c154f747419aee6b75667f9044c8fa`
("docs(release): 准备 v1.38.7 中英更新日志 #10151").

### Added

- Zhipu GLM out of the box: `glm-flash` (glm-5.3-flash) and `glm-pro` (glm-5.3)
  default provider entries alongside DeepSeek; curated GLM preset catalogs
  (glm-cn / zai-global / coding plans) now list glm-5.3-flash and glm-5.3 with
  glm-5.3-flash as the preset default.
- New Tempora brand icon (hourglass on the upstream brand-blue scheme):
  `desktop/build/appicon.{svg,png}`, `windows/icon.ico`, `darwin/icon.icns`,
  Linux hicolor PNGs, `docs/logo-tempora.svg` wordmark.
- `install.ps1` / `install.cmd`: user-scope Windows installer (PATH setup, no admin).
- `UPSTREAM-SYNC.md`: upstream sync playbook (proxy config, rename-aware merge rules).
- `NOTICE.md`: fork attribution and divergence list.

### Changed

- Full rebrand Reasonix → Tempora: Go module `tempora`, binary `tempora`,
  nested module `tempora/sdk/go`, config `tempora.toml`, config dirs
  (`%APPDATA%\tempora`, `~/.tempora`), env prefix `TEMPORA_`, UI strings,
  docs, site, npm wrapper metadata, release/signing configs (placeholder repo
  `tempora-dev/Tempora`).

### Security

- Telemetry/crash/update endpoints now point at placeholder `*.tempora.io`
  domains (no real backend): no data leaves the machine to upstream services.
- CLI `tempora upgrade` targets the placeholder `tempora-dev/Tempora` repo and
  cannot reinstall the upstream product.
