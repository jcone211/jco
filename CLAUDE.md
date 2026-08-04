# jcone211 Portfolio · Agent Guide

## 项目定位

这是一个基于 Hugo + Blowfish 的个人技术作品集，面向 Java 后端 / AI 应用开发岗位的招聘方。重点是用项目、GitHub 贡献日历和市场宽度分析证明工程交付能力，而不是堆砌博客文章。

## 工作约定

- 默认使用中文沟通；代码、命令、变量名、路径保持英文。
- 根字号固定为 `12px`；不新增独立无障碍功能面板，除非用户明确改变该决定。
- 不自动执行 `git commit`、`git push`、删除文件或修改 `.env`、密钥、CI/CD 配置；需要这些操作时先征求用户同意。
- 不把未完成项目写成已上线成品；市场宽度 Agent 仅展示技术说明，不提供登录体验。
- 市场宽度文章由人工挑选并校对后发布，不能自动替用户发布内容。

## 关键结构

- `config/_default/`：Hugo、语言、导航和主题参数。
- `layouts/partials/home/custom.html`：作品集首页。
- `static/css/portfolio.css`：首页样式。
- `content/projects/`：项目案例。
- `content/market-breadth/`：人工发布的市场宽度分析。
- `archetypes/market-breadth.md`：市场宽度文章模板。
- `scripts/fetch-github-contributions.mjs`：构建时获取 GitHub 贡献日历。
- `data/github_contributions.json`：日历的静态构建产物。

## 本地命令

```powershell
# 可选：更新 GitHub 贡献日历；Token 只能保存在当前终端环境变量中
$env:GITHUB_TOKEN = "your-token"
npm run fetch:github

# 预览与构建
.\.tools\hugo\hugo.exe server --buildDrafts --port 4174
hugo --minify
```

如果项目使用仓库内便携版 Hugo，则使用 `.tools\hugo\hugo.exe` 代替 `hugo`。未设置 `GITHUB_TOKEN` 时保留已有日历数据，不得将 Token 写入文件或前端。
