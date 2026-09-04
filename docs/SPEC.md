# SPEC：jcone211 个人技术作品集 V1

- **版本**：1.0
- **状态**：第一版技术规范
- **日期**：2026-08-04

## 1. 技术选型

| 层级 | 方案 | 责任 |
| --- | --- | --- |
| 静态站点生成 | Hugo Extended | 解析 Markdown、数据文件和模板，输出静态页面。 |
| 主题 | Blowfish | 提供导航、主题切换、搜索和文章页能力。 |
| 首页实现 | Hugo 自定义 partial + CSS | 以作品集信息架构替换主题默认首页布局。 |
| 构建时数据获取 | Node.js 原生 `fetch` + GitHub GraphQL | 生成 Contribution Calendar JSON。 |
| 内容格式 | Markdown + TOML front matter | 管理项目页与市场宽度文章。 |
| 本地工具 | Hugo Extended、Node.js | 构建和执行日历拉取脚本。 |

## 2. 当前目录结构

```text
.
├─ CLAUDE.md
├─ README.md
├─ package.json
├─ archetypes/
│  └─ market-breadth.md
├─ config/_default/
│  ├─ hugo.toml
│  ├─ languages.zh-cn.toml
│  ├─ markup.toml
│  ├─ menus.zh-cn.toml
│  └─ params.toml
├─ content/
│  ├─ projects/
│  │  ├─ _index.md
│  │  ├─ market-breadth-agent.md
│  │  └─ wencai-monitor.md
│  └─ market-breadth/
│     └─ _index.md
├─ data/
│  └─ github_contributions.json
├─ docs/
│  ├─ PRD.md
│  └─ SPEC.md
├─ layouts/partials/
│  ├─ extend-head.html
│  └─ home/custom.html
├─ scripts/
│  └─ fetch-github-contributions.mjs
├─ static/
│  ├─ css/portfolio.css
│  └─ images/projects/
└─ themes/blowfish/
```

## 3. Hugo 配置规范

### 3.1 核心配置

`config/_default/hugo.toml` 定义：

- `baseURL = "https://snowynight.site/"`；发布到其他域名时必须同步修改。
- 默认语言为 `zh-cn`，地区为 `zh-CN`。
- 时区为 `Asia/Shanghai`。
- 使用 `blowfish` 主题。
- 首页输出 HTML、RSS 和 JSON。
- 分类体系仅使用 `tags` 与 `categories`。

### 3.2 主题参数

`config/_default/params.toml` 约束：

- 使用 `ocean` 色板，默认浅色并允许自动切换。
- 首页布局必须为 `custom`，由自定义 `home/custom.html` 接管。
- 启用搜索、代码复制、结构化面包屑；`enableA11y = false`，不渲染主题的无障碍功能面板。
- 文章展示作者、阅读时长、目录和分类标签。

### 3.3 导航

`config/_default/menus.zh-cn.toml` 保持四项主导航：

1. 首页：`/`
2. 项目：`/projects/`
3. 市场宽度分析：`/market-breadth/`
4. GitHub：`https://github.com/jcone211`，新窗口打开。

## 4. 页面与路由规范

| 路由 | 来源 | 用途 |
| --- | --- | --- |
| `/` | `layouts/partials/home/custom.html` | 招聘方导向的作品集首页。 |
| `/projects/` | `content/projects/_index.md` | 项目列表。 |
| `/projects/wencai-monitor/` | `content/projects/wencai-monitor.md` | 同花顺问财辅助工具。 |
| `/projects/market-breadth-agent/` | `content/projects/market-breadth-agent.md` | 市场宽度分析 Agent 说明。 |
| `/projects/extreme-risk-averse-stock-agent/` | `content/projects/extreme-risk-averse-stock-agent.md` | 极端风险厌恶型选股策略 Agent。 |
| `/market-breadth/` | `content/market-breadth/_index.md` | 市场宽度分析文章列表。 |
| `/market-breadth/<slug>/` | 后续 Markdown 文件 | 人工审核后的每日分析文章。 |

## 5. 首页实现规范

`layouts/partials/home/custom.html` 必须按以下顺序渲染：

1. **Hero**：岗位方向、个人价值主张、项目/GitHub CTA、能力统计。
2. **GitHub Activity**：贡献总数、更新时间、日历网格、GitHub Profile 链接。
3. **Selected Work**：同花顺问财辅助工具和极端风险厌恶型选股策略 Agent。
4. **Market Notes**：最近最多 3 篇已发布市场宽度文章；无文章时展示空状态。
5. **What’s Next**：说明 Dify 等探索仍需完成和验证。

`static/css/portfolio.css` 负责首页样式，要求：

- 不覆盖 Blowfish 全局基础布局。
- 根字号固定为 `12px`；桌面端项目卡片为双列，680px 以下收敛为单列。
- 贡献日历允许横向滚动，避免窄屏压缩为不可辨识的小方块。
- 可在系统深色模式下保持文字、边框和卡片对比度。

## 6. GitHub Contribution Calendar 数据流程

### 6.1 数据契约

`data/github_contributions.json` 的结构：

```json
{
  "username": "jcone211",
  "totalContributions": 204,
  "generatedAt": "2026/08/04 22:30:00",
  "weeks": [
    {
      "days": [
        { "date": "2026-08-03", "count": 3, "color": "#40c463" }
      ]
    }
  ]
}
```

- `username`：GitHub 登录名。
- `totalContributions`：`contributionCalendar.totalContributions`。
- `generatedAt`：脚本完成拉取时的 Asia/Shanghai 时间。
- `weeks[].days[]`：按 GitHub 返回的周序和日序保存；首页不应自行重排。
- `color`：按 GitHub 返回的颜色用于单元格展示。

### 6.2 拉取脚本

脚本：`scripts/fetch-github-contributions.mjs`

输入：

| 环境变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `GITHUB_TOKEN` | 是（仅刷新时） | 无 | 仅在当前构建进程中使用。 |
| `GITHUB_USERNAME` | 否 | `jcone211` | 要读取贡献日历的 Profile。 |

处理流程：

1. 读取环境变量。
2. 未设置 `GITHUB_TOKEN` 时只输出警告，并保留现有 `data/github_contributions.json`。
3. 调用 GitHub GraphQL 的 `user.contributionsCollection.contributionCalendar`。
4. 将贡献总数、日期、贡献数和颜色转换为 JSON。
5. 原子性要求：后续优化时应先写临时文件，再替换正式 JSON，避免构建中断产生半截文件。
6. 脚本不得打印 Token，也不得把 Token 写入任何文件。

### 6.3 构建命令

```powershell
$env:GITHUB_TOKEN = "your-token"
npm run fetch:github
hugo --minify
```

`package.json` 中的 `build` 脚本组合拉取与构建；运行环境必须确保 `hugo` 已在 PATH。若使用项目便携版，执行：

```powershell
npm run fetch:github
& .\.tools\hugo\hugo.exe --minify
```

## 7. 内容规范\n\n> 站点不应硬编码工作年限。个人简历将由用户后续上传为 Markdown，并在确认字段和展示位置后接入。

### 7.1 项目文章

项目页至少应包含：

- 项目背景与待解决的问题；
- 当前可验证的能力；
- 技术栈/实现说明；
- 状态（进行中、已发布、仅技术说明等）；
- 外部仓库或服务链接；
- 若有 UI，使用已获授权的截图。

禁止：

- 将进行中项目称为“已完成”或“生产可用”；
- 泄露内部地址、账号、Token 或商业敏感数据；
- 对市场分析作收益承诺。

### 7.2 市场宽度文章

创建命令：

```powershell
hugo new content market-breadth/YYYY-MM-DD.md --kind market-breadth
```

流程：

1. 从本地 Agent 输出复制 Markdown。
2. 人工核对标题、数据口径、结论和风险表述。
3. 保留“仅用于研究记录，不构成投资建议”的声明。
4. 将 `draft: true` 改为 `draft: false` 后构建发布。

## 8. 安全与发布边界

- 禁止提交 `.env`、Token、证书、私有网络地址或内部服务登录信息。
- GitHub 日历只在构建环境访问 API；访客浏览器不发送 GitHub API 请求。
- 市场宽度 Agent 只能展示技术描述与经人工审核的内容；不开放登录或执行入口。
- 当前仓库尚未定义自动部署工作流。新增 GitHub Actions、Pages 配置或其他 CI/CD 文件前必须先得到用户确认。

## 9. 验证规范

每次修改后至少执行：

```powershell
& .\.tools\hugo\hugo.exe --minify
```

涉及首页、导航、项目或 CSS 时，还应：

1. 启动 `hugo server` 并确认首页标题、主导航、项目卡片、市场宽度栏目存在。
2. 确认项目截图在生成产物中存在。
3. 扫描生成 HTML 中的本地页面与资源引用，确认无断链。
4. 若调整 GitHub 脚本，分别验证：未设置 Token 时保留现有数据；设置 Token 时能更新 JSON。

## 10. 已知限制与后续演进

- V1 的日历刷新依赖构建时环境变量，尚未配置定时刷新。
- 站点没有 CMS，内容编辑仍是本地 Markdown 流程。
- 未完成 Dify Agent/工作流仅在后续经过稳定性和展示材料验证后加入。
- 当前主题目录是已下载依赖；在准备首次正式提交前，应由用户决定是否改为 Git submodule 或供应商化源码，并保持仓库策略一致。