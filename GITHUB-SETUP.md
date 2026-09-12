# GitHub 仓库搭建指南（从零开始）

> 目标：把本机的 Tempora 仓库推到你自己的 GitHub 仓库，作为正式的远程备份与发布基地。
> 仓库里已经做好了防误操作：`upstream`（上游 esengine/DeepSeek-Reasonix）的 push 已被禁用，只进不出。

## 第 1 步：注册 / 登录 GitHub

打开 https://github.com 注册账号（已有账号直接登录）。免费账号即可，私有仓库也免费。

## 第 2 步：创建空仓库

1. 登录后点右上角 **`+` → New repository**
2. Repository name 填 **`Tempora`**
3. 可见性二选一：
   - **Private（推荐起步）**：只有你能看到，随时可转 Public
   - Public：开源公开；代码本来就是 MIT，转 Public 没有法律障碍，只是完全公开
4. **不要勾选** "Add a README"、"Add .gitignore"、"Choose a license"——我们本地已经有完整历史，勾了会冲突
5. 点 **Create repository**，记下仓库地址，形如：
   `https://github.com/<你的用户名>/Tempora.git`

## 第 3 步：生成访问令牌（PAT，代替密码用）

GitHub 已不能用账号密码推送，用 Personal Access Token：

1. GitHub 右上角头像 → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. **Generate new token (classic)**，Note 随便填（如 `tempora-push`），Expiration 选 90 天或 No expiration
3. 权限只勾 **`repo`**（完整仓库控制）即可
4. 点生成，**立刻复制保存**令牌（`ghp_` 开头，只显示这一次）

## 第 4 步：替换占位符，指向你的仓库

仓库里的发布配置目前用的是占位符 `tempora-dev/Tempora`。拿到你的用户名后（下面以 `yourname` 为例），在 `G:\Tempora\tempora` 执行：

```bash
# 先看会改哪些文件
grep -rl "tempora-dev" --exclude-dir=.git . 

# 确认无误后全部替换（yourname 换成你的 GitHub 用户名）
grep -rl "tempora-dev" --exclude-dir=.git . | xargs sed -i 's/tempora-dev/yourname/g'

# 提交这次替换
git add -A && git commit -m "Point release config at yourname/Tempora"
```

## 第 5 步：推送

```bash
cd G:\Tempora\tempora

# 关联你的仓库（origin 这个名字随便起，upstream 已被上游占用）
git remote add origin https://github.com/yourname/Tempora.git

# 推送（分支名 main-v2 继承自上游；建议顺手改成 main）
git branch -M main
git push -u origin main
```

推送时会弹出登录框（或命令行提示）：
- **Username**: 你的 GitHub 用户名
- **Password**: 粘贴刚才的 **PAT 令牌**（不是账号密码！）

如果用的 PortableGit 没弹窗，就先手动登录一次浏览器再试，或改用带令牌的地址（令牌会进 .git/config，注意保密）：
`git remote set-url origin https://<用户名>:<PAT>@github.com/yourname/Tempora.git`

## 第 6 步：验证

刷新 GitHub 仓库页面，应看到全部代码 + 4+ 个提交。以后每次同步/修改：

```bash
git add -A && git commit -m "说明"
git push
```

## 常见问题

| 症状 | 处理 |
|---|---|
| push 超时 | 仓库已配 7897 代理（仅本仓库），确认 Clash 在运行 |
| `! [rejected]` | 先 `git pull --rebase origin main` 再推 |
| 403 | PAT 没勾 `repo` 权限，或用户名/令牌粘贴错误 |
| 想开源 | GitHub 仓库 Settings → 危险区 → Change visibility → Public |

## 之后（可选）：自动发布

`.github/workflows/` 里的发布流水线在替换占位符后即指向你的仓库；打 tag 推送（`git tag v0.1.1 && git push --tags`）即可触发构建发布（需要在仓库 Settings → Secrets 配置签名相关密钥，可先跳过，直接用 Actions 产物）。
