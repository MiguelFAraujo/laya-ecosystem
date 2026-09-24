#!/usr/bin/env python3
"""Foreman Agent Supervisor (inspired by thruwire/foreman & RomanSlack/jev-drone).
Supervises agent tool execution, shell commands, and git diffs in ~200ms to enforce safety gates.
"""

import json
import os
import sys
import urllib.request

LAYA_URL = os.environ.get("LAYA_URL", "http://127.0.0.1:8092/v1/systemone")

def supervise_action(task_goal: str, last_output: str, exit_code: int = 0) -> dict:
    """Evaluates agent state and decides whether to continue, verify, stop, or intervene."""
    body = {
        "state": {
            "goal": task_goal,
            "exit_code": exit_code,
            "last_output": last_output[-1500:]
        },
        "questions": {
            "action": {
                "type": "choice",
                "instructions": "Qual a próxima ação operacional recomendada para o supervisor?",
                "criteria": {
                    "proceed": "A execução foi bem sucedida ou está progredindo normalmente",
                    "retry": "Ocorreu um erro transitório tratável (ex: timeout leve, lock temporário)",
                    "fix": "Ocorreu um erro de sintaxe, import ou parâmetro que exige correção imediata",
                    "escalate": "Risco de corrupção, falha de permissão grave ou loop infinito"
                }
            },
            "urgency": {
                "type": "score",
                "instructions": "Qual o grau de atenção necessária?",
                "criteria": ["baixa", "media", "alta", "critica"]
            },
            "requires_human_approval": {
                "type": "noul",
                "instructions": "A ação atual envolve risco de perda de dados ou comando destrutivo irreversível?",
                "criteria": {
                    "true": "Sim, envolve remoção de dados, alteração crítica de firewall ou quebra de produção",
                    "false": "Não, é uma operação segura e reversível"
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
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e), "action": "proceed"}

if __name__ == "__main__":
    if len(sys.argv) > 2:
        res = supervise_action(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python3 foreman_supervisor.py '<goal>' '<last_output>' [exit_code]")
