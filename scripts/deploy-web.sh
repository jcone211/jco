#!/usr/bin/env bash
# 将 Hugo 构建产物 public/ 打包上传并原子替换服务器上的 snowynight.site 站点目录。
# 由 post-commit 钩子调用, 也可手动执行: bash scripts/deploy-web.sh
#
# 可覆盖的环境变量:
#   JCO_SSH_PEM     SSH 私钥路径 (默认 /c/Users/19459/.ssh/txcloud/admin.pem)
#   JCO_DEPLOY_HOST 目标主机 (默认 root@118.25.152.144)
set -uo pipefail

JCO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PEM="${JCO_SSH_PEM:-/c/Users/19459/.ssh/txcloud/admin.pem}"
HOST="${JCO_DEPLOY_HOST:-root@118.25.152.144}"
REMOTE_HTML="/usr/local/nginx/html"

PUBLIC_DIR="$JCO/public"
if [ ! -d "$PUBLIC_DIR" ]; then
  echo "ERROR: 找不到 public/, 请先 hugo 构建" >&2
  exit 1
fi
if [ ! -f "$PEM" ]; then
  echo "ERROR: 私钥不存在: $PEM" >&2
  exit 1
fi

# 用最新 market-breadth 文章日期生成包名 public-M-D.tar.gz
LATEST_MD="$(ls "$JCO"/content/market-breadth/*.md 2>/dev/null \
  | grep -E '[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$' | sort | tail -1 || true)"
if [ -n "$LATEST_MD" ]; then
  DSTR="$(basename "$LATEST_MD" .md)"
  MON=$((10#${DSTR:5:2}))
  DAY=$((10#${DSTR:8:2}))
else
  MON=$(date +%-m); DAY=$(date +%-d)
fi
TARNAME="public-${MON}-${DAY}.tar.gz"
LOCAL_TAR="$JCO/$TARNAME"

echo "[deploy] 打包 public/ -> $TARNAME"
tar czf "$LOCAL_TAR" -C "$JCO" public || { echo "ERROR: tar 失败" >&2; exit 1; }

echo "[deploy] 上传 $TARNAME 到 $HOST:$REMOTE_HTML"
# shellcheck disable=SC2086
scp -i "$PEM" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 \
  "$LOCAL_TAR" "$HOST:$REMOTE_HTML/$TARNAME" \
  || { echo "ERROR: scp 上传失败" >&2; rm -f "$LOCAL_TAR"; exit 1; }

echo "[deploy] 服务器端原子替换 snowynight.site"
# shellcheck disable=SC2086
ssh -i "$PEM" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 \
  "$HOST" 'bash -s' <<REMOTE || { echo "ERROR: 远端替换失败" >&2; rm -f "$LOCAL_TAR"; exit 1; }
set -e
cd "$REMOTE_HTML"
rm -rf .deploy-new && mkdir .deploy-new
tar xzf "$TARNAME" -C .deploy-new
if [ ! -d .deploy-new/public ]; then
  echo "ERROR: 归档内未找到 public/ 目录" >&2
  exit 1
fi
rm -rf snowynight.site.bak
[ -d snowynight.site ] && mv snowynight.site snowynight.site.bak
mv .deploy-new/public snowynight.site
rm -rf .deploy-new
# 只保留最新的 public-*.tar.gz, 清理历史包
ls -t public-*.tar.gz 2>/dev/null | tail -n +2 | xargs -r rm -f
echo "SWAP OK snowynight.site (旧版备份为 snowynight.site.bak)"
REMOTE

rm -f "$LOCAL_TAR"
echo "DEPLOY OK $TARNAME"
