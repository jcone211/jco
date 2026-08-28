#!/usr/bin/env bash
# 市场宽度日报一键发布流水线 (飞书投递之后执行):
#   1. 转换最新日报 txt 为 Hugo market-breadth 文章
#   2. 更新 GitHub 贡献日历 (无 token 时保留旧数据)
#   3. hugo 构建 public/
#   4. git commit -> 触发 post-commit 钩子自动部署到服务器
#   5. git push origin main
# 手动执行: bash scripts/publish-daily.sh
set -uo pipefail

JCO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$JCO"

echo "[daily] 1/5 转换最新日报 -> Hugo 文章"
python scripts/publish_breadth.py || { echo "ERROR: 日报转换失败" >&2; exit 1; }

LATEST_MD="$(ls "$JCO"/content/market-breadth/*.md 2>/dev/null \
  | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' | sort | tail -1)"
DSTR="$(basename "$LATEST_MD" .md)"

# 若该文章已被跟踪且无改动, 视为无新日报, 跳过 (避免空提交)
if git ls-files --error-unmatch "$LATEST_MD" >/dev/null 2>&1 \
   && git diff --quiet -- "$LATEST_MD"; then
  echo "[daily] $DSTR 已是最新且无改动, 跳过构建/提交/部署"
  exit 0
fi

echo "[daily] 2/5 fetch:github"
npm run fetch:github || echo "[warn] fetch:github 失败, 继续用现有日历数据"

echo "[daily] 3/5 hugo 构建"
./.tools/hugo/hugo.exe --minify --cleanDestinationDir \
  || { echo "ERROR: hugo 构建失败" >&2; exit 1; }

echo "[daily] 4/5 git commit (将触发 post-commit 自动部署)"
git add "$LATEST_MD" data/github_contributions.json 2>/dev/null || git add "$LATEST_MD"
if git diff --cached --quiet; then
  echo "[daily] 无暂存改动, 跳过 commit"; exit 0
fi
git commit -m "feat: publish market-breadth $DSTR" \
  || { echo "ERROR: git commit 失败" >&2; exit 1; }

echo "[daily] 5/5 git push origin main"
git push origin main || echo "[warn] git push 失败 (离线/权限?), 部署仍由钩子完成"

echo "DAILY DONE $DSTR (详见 .git/deploy.log)"
