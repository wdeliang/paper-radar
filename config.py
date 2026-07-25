# -*- coding: utf-8 -*-
"""
Paper Radar 配置文件。

安全警告：这个仓库将是公开的（GitHub Pages要求）。
绝对不要把 DEEPSEEK_API_KEY 直接写进本文件！
- 本地运行：用环境变量  set DEEPSEEK_API_KEY=sk-xxx (Windows) / export ... (Mac)
- GitHub Actions：在仓库 Settings → Secrets 里配置（见README）
"""

import os

# ---------------------------------------------------------------
# API
# ---------------------------------------------------------------
MAILTO = "your_email@example.com"      # 改成你的邮箱（OpenAlex礼貌池）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"     # 想省钱可换 "deepseek-v4-flash"
MAX_WORKERS = 4
PRICE_INPUT_PER_M = 0.44               # 美元/百万token，仅用于成本估算
PRICE_OUTPUT_PER_M = 0.87

# ---------------------------------------------------------------
# 抓取窗口
# ---------------------------------------------------------------
LOOKBACK_DAYS = 14        # 每次运行回看多少天的新文章（重叠窗口，靠seen去重，防漏）
FIRST_RUN_DAYS = 30       # 第一次运行回填多少天（网站初始就有内容）
SITE_MAX_PAPERS = 4000    # 网站最多展示多少篇（超出后砍最老的；档案文件仍保留全部）
NEW_BADGE_DAYS = 7        # 网站上标 NEW 徽章的天数窗口

DATA_DIR = "data"

# ---------------------------------------------------------------
# 期刊清单（键=名称，值=ISSN；print或online任一即可）
# 按板块分组，不想追的板块/期刊注释掉即可。
# 提示：Nature Communications 体量大且多为自然科学，若觉得噪音大可注释掉。
# ---------------------------------------------------------------
JOURNALS = {
    # —— 综合顶刊 ——
    "Nature": "0028-0836",
    "Science": "0036-8075",
    "PNAS": "0027-8424",
    "PNAS Nexus": "2752-6542",
    "Science Advances": "2375-2548",
    "Nature Communications": "2041-1723",

    # —— Nature 系（行为·认知·AI·学习）——
    "Nature Human Behaviour": "2397-3374",
    "Nature Machine Intelligence": "2522-5839",
    "Nature Computational Science": "2662-8457",
    "Nature Reviews Psychology": "2731-0574",
    "Communications Psychology": "2731-9121",
    "npj Science of Learning": "2056-7936",

    # —— 心理学 / 认知科学顶刊 ——
    "Psychological Science": "0956-7976",
    "Trends in Cognitive Sciences": "1364-6613",
    "Behavioral and Brain Sciences": "0140-525X",
    "Psychological Review": "0033-295X",
    "Psychological Bulletin": "0033-2909",
    "Perspectives on Psychological Science": "1745-6916",
    "Current Directions in Psychological Science": "0963-7214",
    "Journal of Experimental Psychology: General": "0096-3445",
    "Cognition": "0010-0277",
    "Cognitive Science": "0364-0213",
    "Psychonomic Bulletin & Review": "1069-9384",
    "Annual Review of Psychology": "0066-4308",
    "American Psychologist": "0003-066X",

    # —— 发展心理（教育相关）——
    "Child Development": "0009-3920",
    "Developmental Psychology": "0012-1649",

    # —— 教育学顶刊 ——
    "Review of Educational Research": "0034-6543",
    "American Educational Research Journal": "0002-8312",
    "Educational Researcher": "0013-189X",
    "Journal of Educational Psychology": "0022-0663",
    "Journal of the Learning Sciences": "1050-8406",
    "Educational Psychologist": "0046-1520",
    "Educational Psychology Review": "1040-726X",
    "Contemporary Educational Psychology": "0361-476X",
    "Learning and Instruction": "0959-4752",

    # —— 教育技术 / AI+教育 ——
    "Computers & Education": "0360-1315",
    "British Journal of Educational Technology": "0007-1013",
    "Internet and Higher Education": "1096-7516",
    "International Journal of Artificial Intelligence in Education": "1560-4292",

    # —— 教育公平（政策·社会学·经济学视角）——
    "Sociology of Education": "0038-0407",
    "Economics of Education Review": "0272-7757",
    "Educational Evaluation and Policy Analysis": "0162-3737",
}
