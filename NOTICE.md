# NOTICE

Tempora 是 [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)（reasonix.io）的二次开发分支（fork），遵循 MIT 许可证发布。

- 上游项目：DeepSeek-Reasonix，Copyright (c) 2026 Reasonix Contributors
- 本分支：Tempora，Copyright (c) 2026 Tempora Contributors
- 上游的 MIT 许可证文本见 [LICENSE](LICENSE)，本分支完整保留其署名。
- 本分支的全部修改同样以 MIT 许可证发布。

## 与上游的主要差异

1. 品牌更名：Tempora → Tempora（模块名 `tempora`、二进制 `tempora`、配置目录 `~/.tempora` / `%APPDATA%\tempora`、配置文件 `tempora.toml`、环境变量前缀 `TEMPORA_`）。
2. 出厂默认模型新增智谱（Zhipu）GLM：`glm-flash`（glm-5.3-flash）与 `glm-pro`（glm-5.3），与 DeepSeek（`deepseek-flash` / `deepseek-pro`）并列开箱即用；上游预设目录（glm-cn / zai-global / 各 coding plan）中的 GLM 模型列表与默认模型同步更新。
3. 图标更换为 Tempora 沙漏主题（保留上游的品牌蓝 #0153e5 方案与资产测试约束）。
4. 自动更新 / 发布 / 遥测相关的上游基础设施（`crash.tempora.io`、`dl.tempora.io`、`tempora.io` 等域名为占位符，尚无真实后端）：CLI `tempora upgrade` 指向占位仓库 `tempora-dev/Tempora`（无发布时行为为“无可用更新”），不会回装上游产品。
5. `docs/logo-ghost-wave-effect.svg`、`CHANGELOG.md`、`release-notes/` 中保留上游名称与链接，属于上游历史记录与出处署名，非本分支品牌残留。
