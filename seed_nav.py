# -*- coding: utf-8 -*-
import sqlite3, base64, hashlib
from PIL import Image, ImageDraw, ImageFont
import os

DB = "/Users/wangguanglong/Documents/2026-08-28-10-50-29/nav-framework/webstack-go-master/storage/webstack-go.db"

def load_font(size):
    for fp in ["/System/Library/Fonts/STHeiti Light.ttc",
               "/System/Library/Fonts/Hiragino Sans GB.ttc"]:
        if os.path.exists(fp):
            try: return ImageFont.truetype(fp, size)
            except Exception: pass
    return ImageFont.load_default()

PALETTE = [
    (61,90,246,124,140,255), (16,185,129,52,211,153), (245,158,11,251,191,36),
    (239,68,68,248,113,113), (139,92,246,167,139,246), (6,182,212,103,232,249),
    (236,72,153,244,114,182), (100,116,139,148,163,184),
]
def make_icon(text):
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    r1,g1,b1,r2,g2,b2 = PALETTE[h % len(PALETTE)]
    img = Image.new("RGBA", (64,64), (0,0,0,0))
    d = ImageDraw.Draw(img)
    for i in range(64):
        t = i/64
        d.line([(0,i),(64,i)], fill=(int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t), 255))
    mask = Image.new("L", (64,64), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,64,64], radius=14, fill=255)
    img.putalpha(mask)
    d = ImageDraw.Draw(img)
    ch = text[0].upper()
    fs = 34 if len(ch.encode("utf-8")) > 1 else 36
    d.text((32,33), ch, font=load_font(fs), fill=(255,255,255,255), anchor="mm")
    import io
    buf = io.BytesIO(); img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ---------- 数据 ----------
CATEGORIES = [
    (1, "AI4S · 科学智能", "linecons-beaker"),
    (2, "AI 视频生成", "linecons-videocam"),
    (3, "AI 音频与语音", "linecons-music"),
    (4, "AI 智能体平台", "linecons-cog"),
    (5, "大模型与对话", "linecons-comment"),
    (6, "AI 搜索与知识", "linecons-search"),
    (7, "AI 办公与效率", "linecons-doc"),
]

SITES = {
1: [
 ("Google DeepMind", "https://deepmind.google", "AlphaFold 蛋白质结构预测，2024 诺贝尔化学奖，AI4S 绝对标杆"),
 ("Isomorphic Labs", "https://www.isomorphiclabs.com", "DeepMind 分拆，AlphaFold 药物设计引擎，与礼来诺华合作近 30 亿美元"),
 ("EvolutionaryScale", "https://www.evolutionaryscale.ai", "ESM 蛋白质大模型，AI 生物学最大 A 轮 5.4 亿美元"),
 ("Recursion", "https://www.recursion.com", "NASDAQ: RXRX，Recursion OS 表型筛选，并购 Exscientia"),
 ("Schrödinger", "https://www.schrodinger.com", "NASDAQ: SCHR，物理建模+机器学习，2025 营收 2.56 亿美元"),
 ("Generate:Biomedicines", "https://generatebiomedicines.com", "NASDAQ: GENB，生成式 AI 从零设计蛋白质疗法"),
 ("Insitro", "https://www.insitro.com", "Daphne Koller 创立，机器学习+自动化湿实验室，融资超 10 亿美元"),
 ("Cradle", "https://cradle.bio", "AI 蛋白质设计 SaaS，服务全球前 25 大药企中 6 家"),
 ("Atomwise", "https://www.atomwise.com", "AtomNet 深度学习结构药物设计，3 万亿化合物 AI 搜索"),
 ("BenevolentAI", "https://www.benevolent.com", "伦敦上市，生物医学知识图谱驱动药物发现"),
 ("Orbital Materials", "https://www.orbitalmaterials.com", "LINUS 材料基础模型，碳捕获材料性能提升 10 倍"),
 ("CuspAI", "https://www.cuspai.com", "物质世界搜索引擎，Hinton/LeCun 任顾问"),
 ("Periodic Labs", "https://periodiclabs.com", "前 OpenAI/DeepMind 团队，3 亿美元融资攻高温超导体"),
 ("Radical AI", "https://radical.ai", "AI 物理实验室，高超音速高熵合金，空军 D2P2 合同"),
 ("Deep Genomics", "https://www.deepgenomics.com", "AI RNA 靶向疗法，基因序列到药物候选全链条"),
 ("NVIDIA BioNeMo", "https://www.nvidia.com/en-us/clara/bionemo/", "BioNeMo/Apollo 科学模型，AI4S 最大战略投资方"),
 ("Microsoft AI4Science", "https://www.microsoft.com/en-us/research/lab/microsoft-research-ai4science/", "MatterGen/MatterSim，减锂 70% 电池材料"),
 ("Benchling", "https://www.benchling.com", "生命科学研发云平台，Claude for Life Sciences 合作方"),
 ("Lila Sciences", "https://www.lila.ai", "Flagship 孵化，5.5 亿美元，科学超智能 AI 工厂"),
 ("Anthropic 生命科学", "https://www.anthropic.com", "Claude for Life Sciences，调用实验数据生成研究假设"),
],
2: [
 ("Runway", "https://runwayml.com", "Gen 系列视频生成模型，专业影视创作工具链"),
 ("Luma AI", "https://lumalabs.ai", "Dream Machine 视频生成与 3D 重建"),
 ("Pika", "https://pika.art", "创意视频生成社区，特效玩法出圈"),
 ("快手可灵 AI", "https://klingai.com", "Kling 视频生成，物理真实感与时长领先"),
 ("生数 Vidu", "https://www.vidu.cn", "清华系 Vidu，长时长高一致性视频生成"),
 ("MiniMax 海螺", "https://hailuoai.com", "海螺 AI 视频，动态表现与人物一致性强"),
 ("即梦 AI", "https://jimeng.jianying.com", "字节旗下图像视频一站式创作平台"),
 ("HeyGen", "https://www.heygen.com", "AI 数字人口播视频，多语言翻译出海爆款"),
],
3: [
 ("ElevenLabs", "https://elevenlabs.io", "语音合成与克隆标杆，多语种配音"),
 ("Suno", "https://suno.com", "文生音乐标杆，3 分钟完整歌曲"),
 ("Udio", "https://www.udio.com", "高保真 AI 音乐生成，风格覆盖广"),
 ("Speechify", "https://speechify.com", "文本转语音阅读助手，学习场景"),
 ("科大讯飞", "https://www.iflytek.com", "星火大模型，语音识别合成龙头"),
 ("火山语音", "https://www.volcengine.com/product/speech", "字节语音技术，TTS/ASR 全家桶"),
],
4: [
 ("OpenAI Agents", "https://openai.com", "Agents SDK 与 Operator，智能体范式定义者"),
 ("LangChain", "https://www.langchain.com", "最流行 LLM 应用与 Agent 编排框架"),
 ("Dify", "https://dify.ai", "开源 LLM 应用平台，可视化 Agent 工作流"),
 ("扣子 Coze", "https://www.coze.cn", "字节零代码智能体平台，插件生态丰富"),
 ("Manus", "https://manus.im", "通用 AI Agent，自主完成复杂任务"),
 ("CrewAI", "https://www.crewai.com", "多智能体协作编排框架"),
 ("MetaGPT", "https://github.com/geekan/MetaGPT", "多角色软件公司模拟，开源明星项目"),
 ("AutoGPT", "https://agpt.co", "自主目标驱动 Agent 先驱"),
],
5: [
 ("ChatGPT", "https://chatgpt.com", "OpenAI 对话助手，定义 AI 时代交互"),
 ("Claude", "https://claude.ai", "Anthropic 大模型，长上下文与安全对齐标杆"),
 ("Gemini", "https://gemini.google.com", "Google 原生多模态大模型"),
 ("DeepSeek", "https://chat.deepseek.com", "开源推理之王，API 价格亲民"),
 ("Kimi", "https://kimi.moonshot.cn", "月之暗面，超长上下文与深度推理"),
 ("智谱 AI", "https://bigmodel.cn", "GLM 系列基座模型开放平台"),
 ("豆包", "https://www.doubao.com", "字节国民级 AI 助手"),
 ("文心一言", "https://yiyan.baidu.com", "百度文心大模型，中文理解深厚"),
 ("Grok", "https://grok.com", "xAI 大模型，实时信息整合"),
 ("Mistral", "https://mistral.ai", "欧洲开源大模型先锋"),
],
6: [
 ("Perplexity", "https://www.perplexity.ai", "对话式 AI 答案引擎，带来源引用"),
 ("秘塔 AI 搜索", "https://metaso.cn", "中文 AI 搜索标杆，无广告溯源清晰"),
 ("You.com", "https://you.com", "可对话可编程的 AI 搜索工作台"),
 ("夸克", "https://www.quark.cn", "阿里智能搜索与 AI 助手"),
 ("Bing", "https://www.bing.com", "微软搜索，Copilot 加持"),
],
7: [
 ("Microsoft Copilot", "https://copilot.microsoft.com", "Office 全家桶 AI，重塑工作方式"),
 ("Notion AI", "https://www.notion.so", "文档知识库与 AI 深度整合"),
 ("WPS AI", "https://ai.wps.cn", "金山办公 AI，覆盖文档表格演示"),
 ("Gamma", "https://gamma.app", "AI 一键生成 PPT 与网页"),
 ("Canva", "https://www.canva.com", "Magic Studio 设计 AI 全家桶"),
 ("Grammarly", "https://www.grammarly.com", "英语写作纠错润色标杆"),
],
}

con = sqlite3.connect(DB)
cur = con.cursor()
# 清空旧分类/站点（幂等）
cur.execute("DELETE FROM st_site")
cur.execute("DELETE FROM st_category")
for cid, title, icon in CATEGORIES:
    cur.execute("INSERT INTO st_category (id,parent_id,sort,title,icon,level,is_used,created_at,updated_at) VALUES (?,?,?,?,?,1,1,datetime('now'),datetime('now'))", (cid,0,cid,title,icon))
for cid, sites in SITES.items():
    for i,(t,u,desc) in enumerate(sites, start=1):
        icon = make_icon(t)
        cur.execute("INSERT INTO st_site (category_id,title,icon,description,url,is_used,created_at,updated_at,sort) VALUES (?,?,?,?,?,1,datetime('now'),datetime('now'),?)", (cid,t,icon,desc,u,i))
con.commit()
n_cat = cur.execute("SELECT COUNT(*) FROM st_category").fetchone()[0]
n_site = cur.execute("SELECT COUNT(*) FROM st_site").fetchone()[0]
con.close()
print(f"seeded: {n_cat} categories, {n_site} sites")
