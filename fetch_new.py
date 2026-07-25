# -*- coding: utf-8 -*-
"""
步骤1：抓取各期刊最近发表的新文章（OpenAlex）。

- 第一次运行：回填最近 FIRST_RUN_DAYS 天。
- 之后每次运行：回看 LOOKBACK_DAYS 天（窗口重叠没关系，靠 data/seen_ids.json 去重）。
- 输出：data/new_candidates.jsonl（仅本次新增、待筛选的文章）

用法:
    python fetch_new.py            # 正常抓取
    python fetch_new.py --verify   # 只核对ISSN解析是否正确
"""

import json
import time
import argparse
from pathlib import Path
from datetime import date, timedelta
from collections import Counter

import requests

import config

API = "https://api.openalex.org/works"
SRC = "https://api.openalex.org/sources"
HEADERS = {"User-Agent": f"paper-radar (mailto:{config.MAILTO})"}
ISSN_CHUNK = 20
PER_PAGE = 200
SLEEP = 0.15
MAX_RETRY = 5


def req(url, params):
    params = dict(params, mailto=config.MAILTO)
    for attempt in range(MAX_RETRY):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        except requests.RequestException:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"重试{MAX_RETRY}次仍失败: {url}")


def verify_journals():
    print("ISSN → OpenAlex 期刊解析核对：")
    for name, issn in config.JOURNALS.items():
        data = req(SRC, {"filter": f"issn:{issn}", "per-page": 3})
        results = data.get("results", [])
        resolved = results[0]["display_name"] if results else "!! 未找到 !!"
        print(f"  {name:60s} -> {resolved}")
        time.sleep(SLEEP)


def reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def parse_work(w):
    src = (w.get("primary_location") or {}).get("source") or {}
    authors = [a["author"]["display_name"]
               for a in (w.get("authorships") or [])[:15]
               if (a.get("author") or {}).get("display_name")]
    return {
        "id": w.get("id", "").replace("https://openalex.org/", ""),
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": w.get("display_name") or "",
        "date": w.get("publication_date"),
        "year": w.get("publication_year"),
        "journal": src.get("display_name", ""),
        "cited_by": w.get("cited_by_count", 0),
        "authors": authors,
        "abstract": reconstruct_abstract(w.get("abstract_inverted_index")),
        "first_seen": date.today().isoformat(),
    }


def main():
    Path(config.DATA_DIR).mkdir(exist_ok=True)
    seen_path = Path(config.DATA_DIR) / "seen_ids.json"
    first_run = not seen_path.exists()
    seen = set(json.loads(seen_path.read_text()) if not first_run else [])

    days = config.FIRST_RUN_DAYS if first_run else config.LOOKBACK_DAYS
    since = (date.today() - timedelta(days=days)).isoformat()
    print(f"{'首次运行' if first_run else '增量运行'}：抓取 {since} 以来发表的文章…")

    issns = list(config.JOURNALS.values())
    chunks = [issns[i:i + ISSN_CHUNK] for i in range(0, len(issns), ISSN_CHUNK)]

    fetched = {}
    for ci, chunk in enumerate(chunks, 1):
        flt = ",".join([
            f"primary_location.source.issn:{'|'.join(chunk)}",
            f"from_publication_date:{since}",
            "type:article|review",
        ])
        cursor = "*"
        while cursor:
            data = req(API, {
                "filter": flt, "per-page": PER_PAGE, "cursor": cursor,
                "select": ("id,doi,title,display_name,publication_year,"
                           "publication_date,type,cited_by_count,"
                           "primary_location,authorships,abstract_inverted_index"),
            })
            for w in data.get("results", []):
                rec = parse_work(w)
                if rec["id"] and rec["id"] not in seen:
                    fetched[rec["id"]] = rec
            cursor = (data.get("meta") or {}).get("next_cursor")
            time.sleep(SLEEP)
        print(f"  期刊组 {ci}/{len(chunks)} 完成，累计新文章 {len(fetched)}")

    out = Path(config.DATA_DIR) / "new_candidates.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for rec in fetched.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    seen.update(fetched.keys())
    seen_path.write_text(json.dumps(sorted(seen)))

    by_journal = Counter(r["journal"] for r in fetched.values())
    print(f"\n本次新增 {len(fetched)} 篇待筛选 → {out}")
    for j, c in by_journal.most_common(15):
        print(f"  {c:5d}  {j}")
    no_abs = sum(1 for r in fetched.values() if not r["abstract"])
    if no_abs:
        print(f"（其中 {no_abs} 篇暂缺摘要，将按标题判断）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        verify_journals()
    else:
        main()
