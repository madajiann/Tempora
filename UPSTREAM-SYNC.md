# 上游同步指南（UPSTREAM SYNC）

Tempora fork 自 esengine/DeepSeek-Reasonix（浅克隆，起始基线为上游 v1.38.6 附近、2026-09-11 的 main）。
上游非常活跃（日均数十次提交），同步是保持 Tempora 更新的常规操作。

## 一次性配置（已完成）

```bash
# 本仓库已配置（.git/config，仅对本仓库生效，不影响全局）：
git config http.proxy  http://127.0.0.1:7897
git config https.proxy http://127.0.0.1:7897
git remote add upstream https://github.com/esengine/DeepSeek-Reasonix.git
git remote set-url --push upstream DISABLED   # 防止误推上游
```

## 常规同步流程

```bash
# 1. 补全历史（首次需要；当前是 depth=1 浅克隆）
git fetch upstream --unshallow

# 2. 取上游最新
git fetch upstream

# 3. 合并上游 main（git 的重命名检测会自动把上游对 tempora 文件的改动
#    匹配到 tempora 改名后的文件，大部分合并可以自动完成）
git merge upstream/main

# 4. 冲突处理原则：
#    - 上游新增的 Go 文件：import 路径是 "tempora/..."，需要批量替换为 "tempora/..."
#      sed -i 's|"tempora/|"tempora/|g' <新文件>
#    - 上游新增文件名/字符串里的品牌词：按 NOTICE.md 的更名规则处理
#    - CHANGELOG.md、release-notes/ 属上游历史，直接以上游版本为准
#    - desktop/build/*.svg|png|ico|icns 图标资产：保留 Tempora 版本（ours）

# 5. 验证
go build ./... && go test ./internal/... 
(cd desktop && go test .)

# 6. 同步后记得检查这些“上游专属”文件是否需要人工对齐：
#    internal/cli/upgrade.go（ghOwner/ghRepo 占位符）
#    .goreleaser.yaml、.github/workflows/*（发布目标仓库占位符 tempora-dev/Tempora）
```

## 注意

- 合并后必须重新执行品牌残留检查：
  `grep -rni --include="*.go" "tempora" internal/ cmd/ | grep -v _test | grep -v "DeepSeek-Tempora"`
- GLM 出厂预设（internal/config/config.go 的 Default()、provider_presets.go）是 Tempora 独有改动，
  上游同位置若发生变化需要手动合并这两处。
- 上游对 provider/billing 目录改动频繁，是冲突高发区，建议合并时优先保上游、再重放 Tempora 的 GLM 改动。
