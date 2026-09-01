#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 给「量子科技国内」30 家企业按文章技术路线写入 tag 列
# 用法: python3 add_tags.py [DB路径]
import sys, sqlite3

DB = sys.argv[1] if len(sys.argv) > 1 else "storage/webstack-go.db"

# 标题 -> 路线（与文章五大技术主线一致）
ROUTE = {
    # 一、超导路线（9家）
    "中电信量子集团": "超导", "国盾量子": "超导", "本源量子": "超导", "量旋科技": "超导",
    "逻辑比特": "超导", "相干科技": "超导", "国基量子": "超导", "矩量光启": "超导", "正元量子": "超导",
    # 二、光量子路线（6家）
    "硅臻芯片": "光量子", "玻色量子": "光量子", "图灵量子": "光量子", "正则量子": "光量子",
    "九章量子": "光量子", "灵光量子": "光量子",
    # 三、离子阱路线（4家）
    "华翊博奥": "离子阱", "幺正量子": "离子阱", "维刻量光": "离子阱", "玉盘智能": "离子阱",
    # 四、中性原子路线（9家）
    "中科酷原": "中性原子", "QUANTier": "中性原子", "两仪万象": "中性原子", "中器无量": "中性原子",
    "不筹量子": "中性原子", "太一量生": "中性原子", "纳开科技": "中性原子", "无问清芯": "中性原子", "原子矩阵": "中性原子",
    # 五、量子传感与通信（2家）
    "国仪量子": "量子传感与通信", "问天量子": "量子传感与通信",
}

conn = sqlite3.connect(DB)
cur = conn.cursor()
# 1) 加列（幂等）
cur.execute("""SELECT COUNT(*) FROM pragma_table_info('st_site') WHERE name='tag'""")
if cur.fetchone()[0] == 0:
    cur.execute("ALTER TABLE st_site ADD COLUMN tag VARCHAR(50) NOT NULL DEFAULT ''")
    print("已新增 tag 列")
else:
    print("tag 列已存在，跳过建列")

# 2) 仅给量子科技国内分类内的 30 家写 route 标签
cat = cur.execute("SELECT id FROM st_category WHERE title='量子科技国内'").fetchone()
if not cat:
    print("未找到分类 量子科技国内，退出"); conn.close(); sys.exit(1)
cat_id = cat[0]
updated = 0
miss = []
for title, route in ROUTE.items():
    n = cur.execute("UPDATE st_site SET tag=? WHERE category_id=? AND title=?",
                    (route, cat_id, title)).rowcount
    if n:
        updated += n
    else:
        miss.append(title)
conn.commit()
print(f"已写入 tag 的站点: {updated} 家")
if miss:
    print("未匹配(标题不一致)的:", miss)

# 校验
rows = cur.execute("SELECT title, tag FROM st_site WHERE category_id=? ORDER BY sort", (cat_id,)).fetchall()
print("--- 量子科技国内 全量 tag ---")
for t, r in rows:
    print(f"  {r or '(空)':<10} {t}")
conn.close()
