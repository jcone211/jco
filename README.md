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
   $env:GITHUB_TOKEN = ""
   ```

3. 拉取贡献日历并启动本地预览：

   ```powershell
   npm run fetch:github
   hugo server --buildDrafts
   ```

没有 `GITHUB_TOKEN` 时，网站仍可构建，但会保留现有的贡献日历数据。Token 不应写入仓库、前端代码或 `.env` 文件。

## 发布市场宽度分析

市场宽度文章由本地 Agent 生成初稿，**必须经人工挑选和校对后才能发布**，站点不提供自动发布。

### 1. 导入草稿

以报告日期为文件名创建草稿（不是创建当天的日期）：

```powershell
hugo new content market-breadth/2026-08-05.md --kind market-breadth
```

生成的文件只有 front matter 骨架和免责声明，需要把本地生成的 Markdown 正文粘贴进去：

- 删除原文中的 H1 标题，避免与 front matter 的 `title` 重复；
- 保留顶部的免责声明引用块；
- 文件默认 `draft: true`，不会进入生产构建。

### 2. 预览与校对

```powershell
hugo server --buildDrafts --port 4174
```

访问 `http://localhost:4174/market-breadth/` 查看草稿渲染效果，校对数据、表格和表述。

### 3. 发布

确认无误后，将 front matter 中的 `draft: true` 改为 `false`（或直接删除该行）。发布动作必须由人工完成。

### Front matter 约定

| 字段          | 约定                       |
| :------------ | :------------------------- |
| `title`       | `市场宽度分析：YYYY-MM-DD` |
| `date`        | 报告日期，决定列表页排序   |
| `description` | 一句话摘要，用于列表页展示 |
| `tags`        | 固定为 `["市场宽度分析"]`  |
