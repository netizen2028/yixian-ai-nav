#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用站点标签写入工具 —— 让任意分类的站点都能带上「路线/标签」徽标。

用法（直接在飞牛 NAS 或本地执行，需 Pillow 仅当要抓取 favicon）：
  # 1) 按 "企业名:标签" 直接给定
  python3 set_site_tags.py <db路径> --category "量子科技国内" \
      --map "中电信量子集团:超导|国科量子:量子通讯"

  # 2) 从文件读取（每行 企业名<TAB>标签）
  python3 set_site_tags.py <db路径> --category "AI4S · 科学智能国内" --file tags.txt

说明：
  - 标签只更新该分类内 title 命中的行；不命中不改、不存在不新增。
  - 空标签 "" 表示清除该站点 tag。
  - 模板已对未知标签按文本哈希自动上色（前端 JS），无需重编译即可适配任意新路线。
"""
import sqlite3, argparse, sys


def load_map_inline(s):
    out = {}
    for pair in s.split("|"):
        if ":" not in pair:
            continue
        t, tag = pair.split(":", 1)
        out[t.strip()] = tag.strip()
    return out


def load_map_file(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "\t" not in line:
                continue
            t, tag = line.split("\t", 1)
            out[t.strip()] = tag.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db", help="webstack-go.db 路径")
    ap.add_argument("--category", required=True, help="分类标题（精确匹配）")
    ap.add_argument("--map", help="内联映射：企业A:标签A|企业B:标签B")
    ap.add_argument("--file", help="映射文件，每行 企业名<TAB>标签")
    args = ap.parse_args()

    m = {}
    if args.map:
        m.update(load_map_inline(args.map))
    if args.file:
        m.update(load_map_file(args.file))
    if not m:
        print("错误：请提供 --map 或 --file"); sys.exit(1)

    c = sqlite3.connect(args.db)
    cid = c.execute("SELECT id FROM st_category WHERE title=?", (args.category,)).fetchone()
    if not cid:
        print("错误：分类不存在 ->", args.category); sys.exit(1)
    cid = cid[0]

    cur = c.execute("SELECT title, tag FROM st_site WHERE category_id=?", (cid,)).fetchall()
    title2tag = {t: (tag or "") for t, tag in cur}
    matched, changed = 0, 0
    for title, tag in m.items():
        if title not in title2tag:
            print("  跳过(未命中):", title); continue
        matched += 1
        if title2tag[title] != tag:
            c.execute("UPDATE st_site SET tag=? WHERE category_id=? AND title=?", (tag, cid, title))
            changed += 1
            print("  更新:", title, "->", repr(tag))
        else:
            print("  已一致:", title, "->", repr(tag))
    c.commit()
    print(f"完成：命中 {matched} / 变更 {changed}；分类[{args.category}] 现有标签分布：")
    for tag, cnt in c.execute("SELECT tag, count(*) FROM st_site WHERE category_id=? GROUP BY tag ORDER BY tag", (cid,)):
        print("   ", repr(tag), cnt)
    c.close()


if __name__ == "__main__":
    main()
