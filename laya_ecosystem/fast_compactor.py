#!/usr/bin/env python3
"""Fast Lossless Context Compactor (inspired by tamaratran/fast-jev-compaction).
Uses local Laya System-1 (:8092) to score and prune disposable tool outputs without lossy summarization.
"""

import json
import os
import sys
import urllib.request
import urllib.error

LAYA_URL = os.environ.get("LAYA_URL", "http://127.0.0.1:8092/v1/systemone")

def evaluate_block_importance(block_text: str, block_type: str = "tool_output") -> float:
    """Returns probability (0.0 to 1.0) that the block is critical and must be retained."""
    body = {
        "state": {
            "type": block_type,
            "preview": block_text[:1200]
        },
        "questions": {
            "retain": {
                "type": "noul",
                "instructions": "Este bloco contém informações críticas permanentes (código final, erro ativo não resolvido, decisão arquitetural)?",
                "criteria": {
                    "true": "Sim, contém código fonte, decisão arquitetural ou erro ainda pendente",
                    "false": "Não, é log de progresso transitório, listagem intermediária repetitiva ou saída auxiliar"
                }
            }
        }
    }
    try:
        req = urllib.request.Request(
            LAYA_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res.get("answers", {}).get("retain", {}).get("noul", 0.5)
    except Exception:
        # Fallback safe: preserve if unable to score
        return 1.0

def compact_transcript(entries: list, threshold: float = 0.45) -> list:
    compacted = []
    for entry in entries:
        content = entry.get("content", "")
        if len(content) < 200:
            compacted.append(entry)
            continue
        
        score = evaluate_block_importance(content, entry.get("type", "step"))
        if score >= threshold:
            compacted.append(entry)
        else:
            compacted.append({
                **entry,
                "content": f"[Pruned by Laya Compactor: {len(content)} chars of transient output (retention_score: {score:.2f})]",
                "pruned": True
            })
    return compacted

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        out = compact_transcript(data if isinstance(data, list) else [data])
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print("Usage: python3 fast_compactor.py <transcript.json>")
