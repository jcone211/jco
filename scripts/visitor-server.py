#!/usr/bin/env python3
"""轻量访客统计服务器。

记录每个访问的 时间/IP/页面/来源/UA，通过 /visitor-statistics 展示。
依赖: 仅 Python 3 stdlib

启动: python3 visitor-server.py [--port 3001] [--log-dir /path/to/data]
"""
import argparse
import json
import os
import socket
import sys
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

LOG_FILE = "visitors.jsonl"
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>访客统计</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:#f5f5f5; color:#222; padding:20px; }}
h1 {{ font-size:18px; margin-bottom:16px; color:#333; }}
.stats {{ font-size:13px; color:#666; margin-bottom:12px; }}
.summary {{ display:flex; gap:16px; margin-bottom:16px; flex-wrap:wrap; }}
.summary-card {{ background:#fff; border-radius:6px; padding:14px 20px; box-shadow:0 1px 3px rgba(0,0,0,.08); flex:1; min-width:120px; }}
.summary-card strong {{ display:block; font-size:24px; color:#2563eb; }}
.summary-card span {{ font-size:12px; color:#888; }}
table {{ width:100%; border-collapse:collapse; background:#fff; box-shadow:0 1px 3px rgba(0,0,0,.08); font-size:12px; }}
th,td {{ padding:8px 10px; text-align:left; border-bottom:1px solid #eee; white-space:nowrap; }}
th {{ background:#fafafa; font-weight:600; color:#555; position:sticky; top:0; }}
tr:hover td {{ background:#f0f7ff; }}
td:first-child {{ font-family:"SF Mono",Consolas,monospace; }}
.pagination {{ margin-top:12px; font-size:13px; }}
.pagination a {{ color:#2563eb; text-decoration:none; margin:0 4px; }}
.pagination a:hover {{ text-decoration:underline; }}
.pagination .current {{ font-weight:600; color:#222; }}
@media(max-width:640px){{ td:nth-child(3),th:nth-child(3),td:nth-child(4),th:nth-child(4),td:nth-child(5),th:nth-child(5) {{ display:none; }} }}
</style>
</head>
<body>
<h1>访客统计</h1>
<div class="summary">
<div class="summary-card"><strong>{total}</strong><span>总访问次数</span></div>
<div class="summary-card"><strong>{today_count}</strong><span>今日访问</span></div>
<div class="summary-card"><strong>{today_unique}</strong><span>今日独立 IP</span></div>
</div>
<div class="stats">每页 {per_page} 条 &middot; 第 {page}/{total_pages} 页</div>
<div class="summary">{daily_rows}</div>
<table>
<thead><tr><th>时间</th><th>IP</th><th>页面</th><th>来源</th><th>UA</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
<div class="pagination">
{pagination_links}
</div>
</body>
</html>"""

ROW_TEMPLATE = '<tr><td>{time}</td><td>{ip}</td><td>{page}</td><td>{ref}</td><td>{ua}</td></tr>'


class VisitorHandler(BaseHTTPRequestHandler):
    log_file: str = ""

    def get_client_ip(self) -> str:
        ip = self.headers.get("X-Forwarded-For", "")
        if ip:
            return ip.split(",")[0].strip()
        ip = self.headers.get("X-Real-IP", "")
        if ip:
            return ip.strip()
        return self.client_address[0]

    def do_POST(self):
        if self.path != "/api/track":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        ok = self._log_visit(body)
        self.send_response(204 if ok else 500)
        self.end_headers()

    def do_GET(self):
        if self.path == "/visitor-statistics":
            q = self._parse_query()
            self._serve_stats(q)
        else:
            self.send_error(404)

    def _parse_query(self):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        return {"page": int(qs.get("page", [1])[0]), "per_page": int(qs.get("per_page", [50])[0])}

    def _log_visit(self, body: bytes) -> bool:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        record = {
            "time": data.get("time", datetime.now().isoformat()),
            "ip": self.get_client_ip(),
            "page": data.get("page", ""),
            "ref": data.get("ref", ""),
            "ua": data.get("ua", ""),
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            return True
        except OSError:
            return False

    def _serve_stats(self, q):
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            lines = []
        total = len(lines)
        today = datetime.now().strftime("%Y-%m-%d")
        today_ips = set()
        today_count = 0
        all_days = {}
        for line in lines:
            try:
                r = json.loads(line)
                d = r.get("time", "")[:10]
                ip = r.get("ip", "")
                all_days.setdefault(d, {"visits": 0, "ips": set()})
                all_days[d]["visits"] += 1
                all_days[d]["ips"].add(ip)
                if d == today:
                    today_count += 1
                    today_ips.add(ip)
            except json.JSONDecodeError:
                continue
        today_unique = len(today_ips)

        lines.reverse()
        per_page = max(1, min(q["per_page"], 200))
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(q["page"], total_pages))
        start = (page - 1) * per_page
        batch = lines[start:start + per_page]

        rows = ""
        for line in batch:
            try:
                r = json.loads(line)
                rows += ROW_TEMPLATE.format(
                    time=r.get("time", "")[0:19],
                    ip=r.get("ip", ""),
                    page=r.get("page", ""),
                    ref=(r.get("ref", "") or "")[0:60],
                    ua=(r.get("ua", "") or "")[0:80],
                )
            except json.JSONDecodeError:
                continue

        def pagelink(p, label=None):
            return f'<a href="/visitor-statistics?page={p}&per_page={per_page}">{label or p}</a>'

        links = ""
        if total_pages > 1:
            if page > 1:
                links += pagelink(page - 1, "← 上一页") + " "
            for p in range(max(1, page - 3), min(total_pages, page + 3) + 1):
                if p == page:
                    links += f'<span class="current">{p}</span> '
                else:
                    links += pagelink(p) + " "
            if page < total_pages:
                links += pagelink(page + 1, "下一页 →")

        daily_rows = ""
        for d in sorted(all_days, reverse=True)[:30]:
            v = all_days[d]
            daily_rows += f'<div class="summary-card"><strong>{v["visits"]}</strong><span>{d} · 独立IP {len(v["ips"])}</span></div>'

        html = HTML_TEMPLATE.format(
            total=total, today_count=today_count, today_unique=today_unique,
            daily_rows=daily_rows, per_page=per_page, page=page, total_pages=total_pages,
            rows=rows, pagination_links=links,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        sys.stderr.write("[visitor-server] %s - %s\n" % (self.log_date_time_string(), format % args))


def main():
    ap = argparse.ArgumentParser(description="轻量访客统计服务器")
    ap.add_argument("--port", type=int, default=3001, help="监听端口")
    ap.add_argument("--log-dir", default=os.path.dirname(os.path.abspath(__file__)), help="日志目录")
    ap.add_argument("--bind", default="127.0.0.1", help="绑定地址")
    args = ap.parse_args()

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    VisitorHandler.log_file = str(log_dir / LOG_FILE)

    server = HTTPServer((args.bind, args.port), VisitorHandler)
    print(f"[visitor-server] 启动于 http://{args.bind}:{args.port}")
    print(f"[visitor-server] 日志文件: {VisitorHandler.log_file}")
    print(f"[visitor-server] 追踪端点: POST /api/track")
    print(f"[visitor-server] 统计页面: GET /visitor-statistics")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[visitor-server] 已停止")
        server.server_close()


if __name__ == "__main__":
    main()