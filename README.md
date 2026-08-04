# jcone211 Portfolio

基于 [Hugo](https://gohugo.io/) 和 [Blowfish](https://blowfish.page/) 的个人技术作品集，面向 Java 后端 / AI 应用开发岗位招聘方。

## 第一版内容

- Java 后端与 AI 应用开发能力概览；
- GitHub Profile Contribution Calendar（构建时更新）；
- 同花顺问财辅助工具与市场宽度分析 Agent 的项目说明；
- 从本地 Markdown 人工挑选发布的市场宽度分析文章。

## 本地开发

1. 安装 Hugo Extended；
2. 构建前设置仅在当前终端有效的 GitHub Token：

   ```powershell
   $env:GITHUB_TOKEN = "your-token"
   ```

3. 拉取贡献日历并启动本地预览：

   ```powershell
   npm run fetch:github
   hugo server --buildDrafts
   ```

没有 `GITHUB_TOKEN` 时，网站仍可构建，但会保留现有的贡献日历数据。Token 不应写入仓库、前端代码或 `.env` 文件。

## 发布市场宽度分析

```powershell
hugo new content market-breadth/2026-08-05.md --kind market-breadth
```

粘贴并人工校对本地生成的 Markdown 后，将文章 front matter 中的 `draft` 改为 `false`。