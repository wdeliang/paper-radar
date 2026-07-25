# -*- coding: utf-8 -*-
"""
生成演示数据（papers.js），部署前先看看网站长什么样。
正式流水线跑起来后会覆盖这份数据。
用法: python make_sample_data.py
"""

import json
from pathlib import Path
from datetime import date, timedelta

import config

today = date.today()
d = lambda n: (today - timedelta(days=n)).isoformat()

SAMPLE = [
    {"id": "W_s1", "doi": "10.1073/pnas.2422633122",
     "title": "Generative AI without guardrails can harm learning: Evidence from high school mathematics",
     "date": d(1), "year": today.year, "journal": "PNAS",
     "authors": ["Hamsa Bastani", "Osbert Bastani", "Alp Sungu", "Haosen Ge", "Özge Kabakcı", "Rei Mariman"],
     "cited_by": 60, "first_seen": d(1),
     "abstract": "A field experiment with roughly 1,000 students shows that unrestricted GPT-4 access improves practice performance but harms subsequent unaided exam performance; a tutor-guarded version removes the harm.",
     "relevance_type": "direct", "confidence": 0.98,
     "categories": ["ai_in_education", "learning_science"],
     "reason": "Field-experimental evidence that unguarded LLM help during practice undermines unaided learning."},
    {"id": "W_s2", "doi": "10.1038/s41562-024-01961-1",
     "title": "When combinations of humans and AI are useful: A systematic review and meta-analysis",
     "date": d(2), "year": today.year, "journal": "Nature Human Behaviour",
     "authors": ["Michelle Vaccaro", "Abdullah Almaatouq", "Thomas Malone"],
     "cited_by": 180, "first_seen": d(2),
     "abstract": "Across 106 studies, human-AI combinations often perform below the better of the two alone, with gains concentrated in creation tasks.",
     "relevance_type": "transferable", "confidence": 0.9,
     "categories": ["ai_and_cognition"],
     "reason": "Transfer idea: student-AI 'teams' in classrooms may underperform the better partner unless the division of labor is designed deliberately."},
    {"id": "W_s3", "doi": "",
     "title": "Socioeconomic gaps in access to school-based AI tutoring (sample entry)",
     "date": d(2), "year": today.year, "journal": "Educational Researcher",
     "authors": ["Sample Author", "Second Author"],
     "cited_by": 3, "first_seen": d(2),
     "abstract": "Sample abstract: district-level analysis of which students gain access to AI tutoring programs and the implications for achievement gaps.",
     "relevance_type": "direct", "confidence": 0.95,
     "categories": ["educational_equity", "ai_in_education"],
     "reason": "Directly measures how AI tutoring access is stratified by socioeconomic status."},
    {"id": "W_s4", "doi": "",
     "title": "Retrieval practice reshapes memory consolidation during sleep (sample entry)",
     "date": d(5), "year": today.year, "journal": "Psychological Science",
     "authors": ["Sample Author"], "cited_by": 8, "first_seen": d(4),
     "abstract": "Sample abstract: testing effects interact with sleep-dependent consolidation in a week-long learning paradigm.",
     "relevance_type": "transferable", "confidence": 0.78,
     "categories": ["learning_science"],
     "reason": "Transfer idea: AI tutors that schedule retrieval practice before sleep windows could amplify retention."},
    {"id": "W_s5", "doi": "",
     "title": "Difference-in-differences with staggered adoption: a practical guide (sample entry)",
     "date": d(8), "year": today.year, "journal": "PNAS Nexus",
     "authors": ["Sample Methodologist"], "cited_by": 15, "first_seen": d(8),
     "abstract": "Sample abstract: estimator choices for staggered policy rollouts with heterogeneous effects.",
     "relevance_type": "transferable", "confidence": 0.72,
     "categories": ["methods_for_education_research"],
     "reason": "Transfer idea: directly applicable to evaluating staggered school-district rollouts of AI tools."},
    {"id": "W_s6", "doi": "",
     "title": "National trends in teacher shortages and student outcomes (sample entry)",
     "date": d(11), "year": today.year, "journal": "Educational Evaluation and Policy Analysis",
     "authors": ["Sample Economist", "Sample Sociologist"], "cited_by": 5, "first_seen": d(10),
     "abstract": "Sample abstract: links regional teacher shortages to widening achievement gaps.",
     "relevance_type": "direct", "confidence": 0.88,
     "categories": ["educational_equity", "education_policy_society"],
     "reason": "Directly documents a structural driver of educational inequality that AI tutoring is often proposed to offset."},
    {"id": "W_s7", "doi": "",
     "title": "Calibrated trust in algorithmic advice under time pressure (sample entry)",
     "date": d(13), "year": today.year, "journal": "Cognition",
     "authors": ["Sample Cognitive Scientist"], "cited_by": 2, "first_seen": d(12),
     "abstract": "Sample abstract: time pressure shifts advice-taking from calibrated to indiscriminate acceptance.",
     "relevance_type": "transferable", "confidence": 0.7,
     "categories": ["ai_and_cognition"],
     "reason": "Transfer idea: students under exam-style time pressure may accept AI answers indiscriminately - a testable classroom prediction."},
]

meta = {
    "generated": "sample data",
    "model": config.DEEPSEEK_MODEL,
    "n_papers": len(SAMPLE),
    "n_journals": len({p["journal"] for p in SAMPLE}),
    "n_journals_tracked": len(config.JOURNALS),
    "new_badge_days": config.NEW_BADGE_DAYS,
}
payload = json.dumps({"meta": meta, "papers": SAMPLE}, ensure_ascii=False).replace("</", "<\\/")
Path("papers.js").write_text("window.PAPERS_DATA = " + payload + ";\n", encoding="utf-8")
print("演示数据已写入 papers.js，用浏览器打开 index.html 预览。")
