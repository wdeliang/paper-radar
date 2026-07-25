# -*- coding: utf-8 -*-
"""
步骤2：用 DeepSeek 判断每篇新文章是否与 AI+教育 / 教育公平 直接相关，
或者虽属其他领域但存在可迁移的启发（transferable）。

- 输入：data/new_candidates.jsonl
- 输出：相关文章追加进 data/archive.jsonl（网站的数据源，只增不删）
        全部判定记录追加进 data/screen_log.jsonl（含不相关的，便于复盘prompt）
- 判断内容包含 relevance_type: "direct" 或 "transferable"；
  对 transferable 的文章，要求模型用一句话说清"怎么迁移"——这就是启发本身。

用法:
    python screen_new.py
    python screen_new.py --dry 20   # 试运行前20篇
"""

import json
import time
import argparse
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

import config

SYSTEM_PROMPT = """You are screening newly published papers from top journals for a researcher whose work focuses on (a) AI in education (LLMs, tutoring systems, AI-assisted learning and teaching, effects of AI on students and learning) and (b) educational equity (access, achievement gaps, socioeconomic disparities, inclusion, fairness in education).

Mark a paper RELEVANT with relevance_type "direct" if it is directly about:
- AI, LLMs, chatbots, tutoring systems, or educational technology in teaching, learning, or assessment
- effects of AI use on students, teachers, learning outcomes, or academic skills
- educational equity: disparities, access, SES/race/gender gaps, inclusion, fairness, policy affecting equity in education
- learning, instruction, or educational measurement in ways central to education research

Mark a paper RELEVANT with relevance_type "transferable" ONLY IF it is from another field BUT offers a concrete, statable idea that could transfer to AI-in-education or educational-equity research. Examples: human-AI interaction findings that predict how students will use AI; cognitive science of learning/memory/metacognition; trust in or reliance on algorithms; causal-inference or measurement methods usable on education data; findings on inequality, opportunity, or discrimination transferable to education settings; skill formation and labor-market returns to skills. The bar: you must be able to state the transfer idea in one concrete sentence. Vague possibility is NOT enough.

Mark NOT relevant: natural-science papers without human learning/behavior content (chemistry, astrophysics, cell biology, materials, clinical medicine, ecology, etc.), pure ML benchmarks or systems papers without human users or learning implications, and social-science papers with no plausible bridge to education or equity.

Respond ONLY with a JSON object:
{
  "relevant": true or false,
  "relevance_type": "direct" or "transferable" or null,
  "confidence": 0.0 to 1.0,
  "categories": ["one or more of: ai_in_education, educational_equity, learning_science, ai_and_cognition, methods_for_education_research, education_policy_society"],
  "reason": "one sentence in English; for transferable papers, state the concrete transfer idea"
}
If not relevant: relevance_type = null and categories = []. If the abstract is missing, judge from the title and lower confidence."""

USER_TEMPLATE = "Title: {title}\nJournal: {journal} ({date})\nAbstract: {abstract}"

client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)
io_lock = threading.Lock()
usage = {"in": 0, "out": 0}


def screen_one(rec):
    abstract = rec.get("abstract") or "(abstract not available - judge from title)"
    if len(abstract) > 6000:
        abstract = abstract[:6000]
    msg = USER_TEMPLATE.format(title=rec.get("title", ""),
                               journal=rec.get("journal", ""),
                               date=rec.get("date", ""), abstract=abstract)
    last_err = None
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": msg}],
                temperature=0, max_tokens=300,
                response_format={"type": "json_object"},
            )
            content = (resp.choices[0].message.content or "").strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            if not content.startswith("{"):
                s, e = content.find("{"), content.rfind("}") + 1
                if s >= 0 and e > s:
                    content = content[s:e]
            if not content:
                raise ValueError("empty response")
            if resp.usage:
                with io_lock:
                    usage["in"] += resp.usage.prompt_tokens or 0
                    usage["out"] += resp.usage.completion_tokens or 0
            data = json.loads(content)
            return {
                "relevant": bool(data.get("relevant", False)),
                "relevance_type": data.get("relevance_type"),
                "confidence": float(data.get("confidence", 0.0)),
                "categories": data.get("categories", []) or [],
                "reason": str(data.get("reason", ""))[:500],
            }, None
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 20))
    return None, str(last_err)[:300]


def main(dry=None):
    if not config.DEEPSEEK_API_KEY:
        raise SystemExit("未检测到环境变量 DEEPSEEK_API_KEY（公开仓库切勿写进代码！）")
    cand_path = Path(config.DATA_DIR) / "new_candidates.jsonl"
    if not cand_path.exists():
        print("没有 new_candidates.jsonl，请先运行 fetch_new.py")
        return
    candidates = [json.loads(l) for l in open(cand_path, encoding="utf-8")]

    log_path = Path(config.DATA_DIR) / "screen_log.jsonl"
    logged = set()
    if log_path.exists():
        for l in open(log_path, encoding="utf-8"):
            try:
                logged.add(json.loads(l)["id"])
            except (json.JSONDecodeError, KeyError):
                pass
    todo = [c for c in candidates if c["id"] not in logged]
    if dry:
        todo = todo[:dry]
    print(f"新文章 {len(candidates)} 篇，待筛 {len(todo)} 篇，"
          f"模型 {config.DEEPSEEK_MODEL}，并发 {config.MAX_WORKERS}")

    archive_path = Path(config.DATA_DIR) / "archive.jsonl"
    n_done = n_inc = n_err = 0
    t0 = time.time()
    with open(archive_path, "a", encoding="utf-8") as farch, \
            open(log_path, "a", encoding="utf-8") as flog, \
            ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as pool:
        futures = {pool.submit(screen_one, c): c for c in todo}
        for fut in as_completed(futures):
            rec = futures[fut]
            verdict, err = fut.result()
            with io_lock:
                if err:
                    n_err += 1
                    flog.write(json.dumps({"id": rec["id"], "error": err},
                                          ensure_ascii=False) + "\n")
                else:
                    flog.write(json.dumps({"id": rec["id"], **verdict},
                                          ensure_ascii=False) + "\n")
                    if verdict["relevant"] and verdict["confidence"] >= 0.5:
                        n_inc += 1
                        farch.write(json.dumps({**rec, **verdict},
                                               ensure_ascii=False) + "\n")
                farch.flush(); flog.flush()
            n_done += 1
            if n_done % 50 == 0 or n_done == len(todo):
                cost = (usage["in"] / 1e6 * config.PRICE_INPUT_PER_M
                        + usage["out"] / 1e6 * config.PRICE_OUTPUT_PER_M)
                print(f"  {n_done}/{len(todo)}  纳入 {n_inc}  失败 {n_err}  ≈${cost:.2f}")

    cost = (usage["in"] / 1e6 * config.PRICE_INPUT_PER_M
            + usage["out"] / 1e6 * config.PRICE_OUTPUT_PER_M)
    print(f"完成：筛 {n_done} 篇，纳入 {n_inc} 篇，失败 {n_err} 篇，"
          f"成本≈${cost:.2f}，用时 {time.time()-t0:.0f}s")
    if n_err:
        print("失败条目重跑本脚本会自动补筛。")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", type=int, default=None)
    args = ap.parse_args()
    main(dry=args.dry)
