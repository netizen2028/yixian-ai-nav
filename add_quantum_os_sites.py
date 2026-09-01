#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补充「量子科技海外」分类（来源：微信文章《海外量子科技企业 Top 30》，2026-09）
幂等：分类按 title 去重；站点按 title 去重，已存在则跳过；自动抓取真实 favicon，失败用首字母 fallback。
用法：python3 add_quantum_os_sites.py [DB路径]
说明：文章本身不含官网外链，30 家官方域名已逐家检索核实；按文章四大赛道给每家打标签：
      量子计算硬件(17) / 量子软件与云服务(5) / 量子通信与网络安全(5) / 量子传感(3)。
      分类插入到 sort=4（量子科技国内之后），其余分类 sort>=4 自动后移。
"""
import sys, sqlite3, urllib.request, urllib.error, ssl, io, base64, hashlib, os, concurrent.futures
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont

DB = sys.argv[1] if len(sys.argv) > 1 else "storage/webstack-go.db"
CATEGORY_TITLE = "量子科技海外"
CATEGORY_ICON = "linecons-globe"
TARGET_SORT = 4  # 量子科技国内(sort=3) 之后

# (title, url, description, tag) —— 顺序即文章排名，按四大赛道分组
SITES = [
    # 一、量子计算硬件赛道（17家）
    ("IBM Quantum", "https://quantum.ibm.com",
     "超导量子计算龙头，127+ 比特 Condor/Heron 处理器与 Qiskit 开源生态", "量子计算硬件"),
    ("Google Quantum AI", "https://quantumai.google",
     "超导路线，Sycamore 量子优越性验证与 Willow 纠错芯片", "量子计算硬件"),
    ("Quantinuum", "https://quantinuum.com",
     "离子阱路线独角兽，H2 系列高保真度量子计算机", "量子计算硬件"),
    ("IonQ", "https://ionq.com",
     "离子阱上市企业，Forte 商用离子阱系统与云端接入", "量子计算硬件"),
    ("PsiQuantum", "https://psiquantum.com",
     "光量子路线，硅光子集成容错量子计算（百万比特目标）", "量子计算硬件"),
    ("Xanadu", "https://www.xanadu.ai",
     "光量子路线，可编程光量子机与 PennyLane 框架", "量子计算硬件"),
    ("Rigetti Computing", "https://www.rigetti.com",
     "超导路线上市企业，Aspen 处理器与量子云服务", "量子计算硬件"),
    ("QuEra Computing", "https://www.quera.com",
     "中性原子路线，256 原子 Aquila 模拟机（Harvard/MIT 衍生）", "量子计算硬件"),
    ("Pasqal", "https://www.pasqal.com",
     "中性原子路线，法国移动原子阵列量子处理器", "量子计算硬件"),
    ("Atom Computing", "https://www.atom-computing.com",
     "中性原子路线，1000 原子阵列与碱土金属光钟", "量子计算硬件"),
    ("D-Wave", "https://www.dwavequantum.com",
     "退火量子计算上市企业，Advantage 量子退火系统", "量子计算硬件"),
    ("Microsoft Quantum", "https://quantum.microsoft.com",
     "拓扑量子路线，Azure Quantum 云与 Majorana 研究", "量子计算硬件"),
    ("Oxford Quantum Circuits (OQC)", "https://oxfordquantumcircuits.com",
     "英国超导路线，Coaxmon 3D 架构量子处理器", "量子计算硬件"),
    ("Diraq", "https://diraq.com",
     "澳大利亚硅基自旋量子比特（硅 CMOS 工艺路线）", "量子计算硬件"),
    ("Alice & Bob", "https://alice-bob.com",
     "法国超导路线，纠错猫态（cat qubit）专用架构", "量子计算硬件"),
    ("IQM Quantum Computers", "https://www.meetiqm.com",
     "芬兰超导路线，向超算中心交付 on-premise 量子处理器", "量子计算硬件"),
    ("Infleqtion", "https://www.infleqtion.com",
     "美国冷原子（原子钟/传感器）与量子计算，前 ColdQuanta", "量子计算硬件"),

    # 二、量子软件与云服务赛道（5家）
    ("SandboxAQ", "https://www.sandboxaq.com",
     "量子软件与 SaaS，源自 Alphabet，量子安全/量子传感应用", "量子软件与云服务"),
    ("Classiq", "https://www.classiq.io",
     "量子软件，电路合成与 EDA 级量子算法设计平台", "量子软件与云服务"),
    ("Riverlane", "https://www.riverlane.com",
     "量子软件，Decoders 纠错堆栈与中性原子控制栈", "量子软件与云服务"),
    ("QC Ware", "https://qcware.com",
     "量子软件，Forge 量子算法与优化云平台", "量子软件与云服务"),
    ("Horizon Quantum Computing", "https://www.horizonquantum.com",
     "新加坡量子软件，经典代码自动量子化编译", "量子软件与云服务"),

    # 三、量子通信与网络安全赛道（5家）
    ("ID Quantique (IDQ)", "https://www.idquantique.com",
     "量子保密通信龙头，QKD 与量子随机数（瑞士）", "量子通信与网络安全"),
    ("Toshiba", "https://www.toshiba.eu/quantum/",
     "量子密钥分发（QKD）网络与量子安全技术（日本）", "量子通信与网络安全"),
    ("QNu Labs", "https://www.qnulabs.com",
     "印度量子安全，量子密钥与抗量子加密", "量子通信与网络安全"),
    ("KETS Quantum", "https://kets-quantum.com",
     "英国量子安全，芯片级 QKD 与量子随机数", "量子通信与网络安全"),
    ("QuintessenceLabs", "https://www.quintessencelabs.com",
     "澳大利亚量子安全，量子随机数与密钥管理", "量子通信与网络安全"),

    # 四、量子传感赛道（3家）
    ("Q-CTRL", "https://q-ctrl.com",
     "量子传感与控制软件，量子纠错/降噪（澳大利亚）", "量子传感"),
    ("AOSense", "https://www.aosense.com",
     "美国冷原子传感，原子干涉仪与量子惯性传感器", "量子传感"),
    ("Quspin", "https://quspin.com",
     "美国量子传感，原子钟与精密测量器件", "量子传感"),
]

SEARCH_FALLBACK = {t for t, u, _, _ in SITES if "baidu.com/s?wd=" in u}

PALETTE = [
    (61, 90, 246, 124, 140, 255), (16, 185, 129, 52, 211, 153), (245, 158, 11, 251, 191, 36),
    (239, 68, 68, 248, 113, 113), (139, 92, 246, 167, 139, 246), (6, 182, 212, 103, 232, 249),
    (236, 72, 153, 244, 114, 182), (100, 116, 139, 148, 163, 184),
]


def load_font(size):
    for fp in ["/System/Library/Fonts/STHeiti Light.ttc",
               "/System/Library/Fonts/Hiragino Sans GB.ttc",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def fallback_icon(text):
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    r1, g1, b1, r2, g2, b2 = PALETTE[h % len(PALETTE)]
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(64):
        t = i / 64
        d.line([(0, i), (64, i)], fill=(int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t),
                                        int(b1 + (b2 - b1) * t), 255))
    mask = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 64, 64], radius=14, fill=255)
    img.putalpha(mask)
    d = ImageDraw.Draw(img)
    ch = text[0]
    fs = 30 if len(ch.encode("utf-8")) > 1 else 36
    d.text((32, 33), ch, font=load_font(fs), fill=(255, 255, 255, 255), anchor="mm")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def domain_of(url):
    p = urlparse(url)
    return (p.netloc or p.path.split('/')[0]).replace('www.', '')


def to_png_b64(data):
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        if getattr(img, 'format', None) == 'ICO':
            sizes = img.info.get('sizes', [(img.width, img.height)])
            if sizes:
                biggest = max(sizes, key=lambda s: s[0] * s[1])
                try:
                    img = img.resize(biggest, Image.LANCZOS)
                except Exception:
                    pass
        img.thumbnail((64, 64), Image.LANCZOS)
        out = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        out.paste(img, ((64 - img.width) // 2, (64 - img.height) // 2), img)
        buf = io.BytesIO()
        out.save(buf, 'PNG')
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


ctx = ssl.create_default_context()
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def fetch_icon(domain, timeout=15):
    candidates = [f"https://icon.horse/icon/{domain}",
                  f"https://{domain}/favicon.ico"]
    for u in candidates:
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            data = urllib.request.urlopen(req, timeout=timeout, context=ctx).read()
            if len(data) < 100:
                continue
            b64 = to_png_b64(data)
            if b64:
                return b64, True
        except Exception:
            continue
    return None, False


def process(item):
    title, url, desc, tag = item
    if title in SEARCH_FALLBACK:
        return title, url, desc, tag, fallback_icon(title), False
    domain = domain_of(url)
    b64, ok = fetch_icon(domain)
    if not b64:
        b64 = fallback_icon(title)
    return title, url, desc, tag, b64, ok


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 1) 确保分类存在；不存在则插入到 TARGET_SORT，其余分类自动后移
    row = cur.execute("SELECT id FROM st_category WHERE title=?", (CATEGORY_TITLE,)).fetchone()
    if row:
        cat_id = row[0]
        print(f"分类已存在: id={cat_id}（直接追加站点）")
    else:
        cur.execute("UPDATE st_category SET sort = sort + 100 WHERE sort >= ?", (TARGET_SORT,))
        cur.execute("UPDATE st_category SET sort = sort - 99 WHERE sort >= ?", (TARGET_SORT + 100,))
        cur.execute("INSERT INTO st_category (parent_id, sort, title, icon, level, is_used)"
                    " VALUES (0, ?, ?, ?, 1, 1)", (TARGET_SORT, CATEGORY_TITLE, CATEGORY_ICON))
        cat_id = cur.lastrowid
        print(f"新建分类: '{CATEGORY_TITLE}' id={cat_id} sort={TARGET_SORT} icon={CATEGORY_ICON}")

    # 去重按「本分类内」做
    existing = {r[0] for r in cur.execute("SELECT title FROM st_site WHERE category_id=?", (cat_id,))}
    todos = [s for s in SITES if s[0] not in existing]
    print(f"待新增站点: {len(todos)} 家（已存在跳过: {len(SITES) - len(todos)}）")
    if not todos:
        conn.close()
        return

    max_sort = cur.execute("SELECT COALESCE(MAX(sort),0) FROM st_site WHERE category_id=?",
                           (cat_id,)).fetchone()[0]
    print("当前分类最大 sort:", max_sort)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for f in concurrent.futures.as_completed([ex.submit(process, t) for t in todos]):
            r = f.result()
            results.append(r)
            print(f"  [{'真实' if r[5] else '回退'}] {r[0]} ({r[3]})")

    results.sort(key=lambda x: [t[0] for t in todos].index(x[0]))
    for i, (title, url, desc, tag, b64, ok) in enumerate(results, 1):
        cur.execute(
            "INSERT INTO st_site (category_id,title,icon,description,url,tag,tag_color,is_used,created_at,updated_at,sort)"
            " VALUES (?,?,?,?,?,?,?,1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,?)",
            (cat_id, title, b64, desc, url, tag, '', max_sort + i))
    conn.commit()
    real = sum(1 for r in results if r[5])
    print(f"\n新增完成: {len(results)} 家（真实 logo {real} 家，首字母回退 {len(results)-real} 家）")
    print("量子科技海外 分类站点数:", cur.execute("SELECT count(*) FROM st_site WHERE category_id=?", (cat_id,)).fetchone()[0])
    print("分类总数:", cur.execute("SELECT count(*) FROM st_category").fetchone()[0])
    print("站点总数:", cur.execute("SELECT count(*) FROM st_site").fetchone()[0])
    conn.close()


if __name__ == "__main__":
    main()
