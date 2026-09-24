#!/usr/bin/env python3
"""Two-Stage JEV/Laya Semantic Search & Ranking (inspired by superagents-lab/jev-search & pg-jev).
Retrieves candidate documents from Cortex FTS5 database and ranks them using Laya System-1 in ~200ms.
"""

import json
import os
import sqlite3
import sys
import urllib.request

LAYA_URL = os.environ.get("LAYA_URL", "http://127.0.0.1:8092/v1/systemone")
DB_PATH = "/mnt/storage/cortex-curator/cognitive.db"

def search_candidates(query: str, limit: int = 15) -> list:
    """Stage 1: Fast keyword & FTS retrieval from Cortex DB."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Simple search over documents
    try:
        cur.execute(
            "SELECT id, source_file, substr(text_original, 1, 800) FROM documents WHERE text_original LIKE ? LIMIT ?",
            (f"%{query}%", limit)
        )
        rows = cur.fetchall()
        return [{"id": r[0], "source": r[1], "snippet": r[2]} for r in rows]
    except Exception:
        return []
    finally:
        conn.close()

def rank_candidates(query: str, candidates: list) -> list:
    """Stage 2: Score candidates for semantic relevance using Laya System-1."""
    if not candidates:
        return []
    
    ranked = []
    for cand in candidates:
        body = {
            "state": {
                "query": query,
                "document": cand["snippet"]
            },
            "questions": {
                "relevance": {
                    "type": "score",
                    "instructions": "Quão relevante e útil é este documento para responder à busca?",
                    "criteria": ["irrelevante", "baixa", "moderada", "alta", "exata"]
                }
            }
        }
        try:
            req = urllib.request.Request(
                LAYA_URL,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                score = res.get("answers", {}).get("relevance", {}).get("score", 0.0)
                ranked.append({**cand, "relevance_score": score})
        except Exception:
            ranked.append({**cand, "relevance_score": 1.0})
    
    # Sort descending by relevance score
    ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
    return ranked

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cortex_jev_search.py '<query>' [limit]")
        return
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    candidates = search_candidates(query, limit=limit * 2)
    results = rank_candidates(query, candidates)[:limit]
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
