# jcone211 Portfolio · Agent Guide

## 项目定位

这是一个基于 Hugo + Blowfish 的个人技术作品集，面向 Java 后端 / AI 应用开发岗位的招聘方。重点是用项目、GitHub 贡献日历和市场宽度分析证明工程交付能力，而不是堆砌博客文章。

## 工作约定

- 默认使用中文沟通；代码、命令、变量名、路径保持英文。
- 根字号固定为 `12px`；不新增独立无障碍功能面板，除非用户明确改变该决定。
- 除「市场宽度日报自动化」（见下文《日报自动部署》）外，不自动执行 `git commit`、`git push`、删除文件或修改 `.env`、密钥、CI/CD 配置；需要这些操作时先征求用户同意。
- 每次提交代码前，先运行 `npm run fetch:github` 更新贡献日历后再提交。
- 不把未完成项目写成已上线成品；市场宽度 Agent 仅展示技术说明，不提供登录体验。
- 市场宽度**日报**可由 `scripts/publish-daily.sh` 流水线自动发布、提交并部署（这是用户明确放行的每日自动化流程）；其余内容（项目案例、普通博客等）仍须人工挑选并校对后发布。

## 关键结构

- `config/_default/`：Hugo、语言、导航和主题参数。
- `layouts/partials/home/custom.html`：作品集首页。
- `static/css/portfolio.css`：首页样式。
- `content/projects/`：项目案例。
- `content/market-breadth/`：市场宽度分析文章（日报由流水线自动发布，历史文章经人工校对）。
- `archetypes/market-breadth.md`：市场宽度文章模板。
- `scripts/fetch-github-contributions.mjs`：构建时获取 GitHub 贡献日历。
- `data/github_contributions.json`：日历的静态构建产物。
- `scripts/publish_breadth.py`：将 work-assistant 的市场宽度日报 txt 转成本目录文章格式（frontmatter + 免责声明引用行 + 正文），幂等覆盖。
- `scripts/deploy-web.sh`：把 `public/` 打包成 `public-M-D.tar.gz`，scp 上传服务器后原子替换 `snowynight.site`（旧版备份为 `snowynight.site.bak`）。
- `scripts/publish-daily.sh`：日报一键流水线入口（转换 → fetch:github → hugo 构建 → git commit → git push）。
- `.git/hooks/post-commit`：每次 commit 后自动执行 `deploy-web.sh`；部署失败仅记 `.git/deploy.log`，不影响 commit。

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

## 日报自动部署

```bash
# 一键：转换最新日报 → 构建 → 提交(触发钩子部署) → 推送 GitHub
bash scripts/publish-daily.sh

# 仅部署已构建的 public/（不提交），例如手动改内容后想上线
bash scripts/deploy-web.sh
```

- 部署目标：`root@118.25.152.144`，站点根 `/usr/local/nginx/html/snowynight.site`（docker nginx 挂载，静态替换即时生效、无需 reload）。
- SSH 私钥默认 `/c/Users/19459/.ssh/txcloud/admin.pem`，可用环境变量 `JCO_SSH_PEM` 覆盖；目标主机可用 `JCO_DEPLOY_HOST` 覆盖。密钥仅本地引用，绝不入库。
- 因已装 `post-commit` 钩子，**任何** `git commit`（含手动提交）都会触发一次部署；如需临时禁用，删除或重命名 `.git/hooks/post-commit`。
- 每次部署后旧站保留为 `snowynight.site.bak`，可手动 `mv` 回滚；服务器仅保留最新的 `public-*.tar.gz`。
- 部署明细见 `.git/deploy.log`。
