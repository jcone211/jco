#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 work-assistant 市场宽度日报 txt 转换为 Hugo market-breadth 文章。

用法:
    python scripts/publish_breadth.py [path/to/breadth_analysis_MMDD.txt]

不传参数时, 自动取 BREADTH_SRC 目录 (默认为 work-assistant 的 market_breadth)
下日期最新的 breadth_analysis_*.txt。生成文件与人工校对版 (2026-08-17.md) 同格式:
frontmatter + 免责声明引用行 + 正文, 幂等覆盖。
"""
import os
import re
import sys
import datetime
from pathlib import Path

JCO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = JCO_ROOT / "content" / "market-breadth"
DEFAULT_SRC = r"D:\sundry\7-ai\agents\work-assistant\market_breadth"


def pick_source():
    if len(sys.argv) > 1:
        f = Path(sys.argv[1])
        if not f.is_file():
            sys.exit(f"ERROR: 指定文件不存在: {f}")
        return f
    src = Path(os.environ.get("BREADTH_SRC", DEFAULT_SRC))
    if not src.is_dir():
        sys.exit(f"ERROR: 源目录不存在: {src} (可用环境变量 BREADTH_SRC 覆盖)")
    cands = list(src.glob("breadth_analysis_*.txt"))
    if not cands:
        sys.exit(f"ERROR: {src} 下没有 breadth_analysis_*.txt")
    # 文件名尾部的 MMDD 数字排序, 取最新 (跨年场景仍按正文日期解析, 此处仅选文件)
    def key(p):
        m = re.search(r"(\d{3,4})\.txt$", p.name)
        return m.group(1) if m else p.name
    return sorted(cands, key=key)[-1]


def extract_date(text, stem):
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", text)
    if m:
        y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
    else:
        mf = re.search(r"(\d{2})(\d{2})$", stem)
        y = str(datetime.date.today().year)
        mo = int(mf.group(1)) if mf else 1
        d = int(mf.group(2)) if mf else 1
    return f"{y}-{mo:02d}-{d:02d}"


def strip_h1(text):
    lines = text.splitlines()
    start = 0
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("# "):
            start = i + 1
            while start < len(lines) and lines[start].strip() == "":
                start += 1
            break
    return "\n".join(lines[start:]).strip("\n")


def main():
    src_file = pick_source()
    text = src_file.read_text(encoding="utf-8-sig")
    date_str = extract_date(text, src_file.stem)
    body = strip_h1(text)
    if not body:
        sys.exit(f"ERROR: 剥离 H1 后正文为空: {src_file}")

    front_matter = (
        "---\n"
        f'title: "市场宽度分析：{date_str}"\n'
        f"date: {date_str}\n"
        "draft: false\n"
        'description: "每日市场宽度观察与复盘。"\n'
        'tags: ["市场宽度分析"]\n'
        "---\n\n"
        "> 本文由本地 Agent 生成初稿后人工校对，仅用于研究记录，不构成投资建议。\n\n"
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / f"{date_str}.md"
    out_file.write_text(front_matter + body + "\n", encoding="utf-8", newline="\n")
    print(f"PUBLISHED {out_file}")


if __name__ == "__main__":
    main()
