# -*- coding: utf-8 -*-
"""
步骤3：从累积档案 data/archive.jsonl 重新生成网站数据 papers.js（仓库根目录）。

- 按 OpenAlex ID 与 DOI 双重去重（同一篇后筛的记录覆盖先筛的）
- 网站最多保留 SITE_MAX_PAPERS 篇（按发表日期最新优先；档案文件不受影响）
- 同时写 data/last_run.json 作为每次运行的心跳（保证Actions每次都有提交，
  定时任务不会因仓库"无活动"被GitHub暂停）
"""

import json
from pathlib import Path
from datetime import datetime, timezone

import config


def main():
    archive_path = Path(config.DATA_DIR) / "archive.jsonl"
    papers_by_id = {}
    if archive_path.exists():
        for l in open(archive_path, encoding="utf-8"):
            try:
                r = json.loads(l)
                papers_by_id[r["id"]] = r
            except (json.JSONDecodeError, KeyError):
                pass

    # DOI去重（极少数情况下同一DOI有两个OpenAlex ID）
    by_doi = {}
    papers = []
    for r in papers_by_id.values():
        doi = (r.get("doi") or "").lower()
        if doi:
            if doi in by_doi:
                continue
            by_doi[doi] = True
        papers.append(r)

    papers.sort(key=lambda p: (p.get("date") or "", p.get("first_seen") or ""),
                reverse=True)
    papers = papers[: config.SITE_MAX_PAPERS]

    slim = [{
        "id": p["id"], "doi": p.get("doi", ""), "title": p.get("title", ""),
        "date": p.get("date", ""), "year": p.get("year"),
        "journal": p.get("journal", ""), "authors": p.get("authors", []),
        "cited_by": p.get("cited_by", 0), "abstract": p.get("abstract", ""),
        "first_seen": p.get("first_seen", ""),
        "relevance_type": p.get("relevance_type"),
        "confidence": round(p.get("confidence", 0), 2),
        "categories": p.get("categories", []),
        "reason": p.get("reason", ""),
    } for p in papers]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    meta = {
        "generated": now,
        "model": config.DEEPSEEK_MODEL,
        "n_papers": len(slim),
        "n_journals": len({p["journal"] for p in slim if p["journal"]}),
        "n_journals_tracked": len(config.JOURNALS),
        "new_badge_days": config.NEW_BADGE_DAYS,
    }
    payload = json.dumps({"meta": meta, "papers": slim},
                         ensure_ascii=False).replace("</", "<\\/")
    Path("papers.js").write_text("window.PAPERS_DATA = " + payload + ";\n",
                                 encoding="utf-8")

    Path(config.DATA_DIR).mkdir(exist_ok=True)
    (Path(config.DATA_DIR) / "last_run.json").write_text(
        json.dumps({"time": now, "papers_on_site": len(slim)}))

    print(f"网站数据已生成：papers.js（{len(slim)} 篇，更新于 {now}）")


if __name__ == "__main__":
    main()
