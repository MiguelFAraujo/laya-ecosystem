#!/usr/bin/env python3
"""Ultra-Fast DOM & Mobile UI Action Decider (inspired by browser-use/jev-ultrafast & droidrun/mobile-jev).
Decides action + element target in a single forward pass without slow selector generation.
"""

import json
import os
import sys
import urllib.request

LAYA_URL = os.environ.get("LAYA_URL", "http://127.0.0.1:8092/v1/systemone")

def decide_ui_action(goal: str, elements: list) -> dict:
    """Takes a list of indexed interactive elements [{'id': 0, 'text': 'Login', 'tag': 'button'}, ...]
    and decides the next action and target index in a single forward pass.
    """
    options_map = {}
    for el in elements[:15]:
        key = f"elem_{el.get('id', 0)}"
        desc = f"<{el.get('tag', 'btn')}> {el.get('text', '')} ({el.get('role', '')})".strip()
        options_map[key] = desc
    options_map["none"] = "Nenhum elemento corresponde ao objetivo atual"

    body = {
        "state": {
            "goal": goal,
            "elements_count": len(elements)
        },
        "questions": {
            "action_type": {
                "type": "choice",
                "instructions": "Qual a ação imediata a executar na interface?",
                "criteria": {
                    "click": "Clicar em um botão, link ou elemento interativo",
                    "type": "Digitar texto em um campo de entrada / input",
                    "scroll": "Rolar a página para encontrar mais conteúdo",
                    "done": "O objetivo já foi cumprido na tela atual"
                }
            },
            "target_element": {
                "type": "choice",
                "instructions": "Qual elemento da lista deve receber a interação?",
                "criteria": options_map
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
        return {"error": str(e)}

if __name__ == "__main__":
    sample_elements = [
        {"id": 1, "tag": "input", "text": "Pesquisar no Google", "role": "searchbox"},
        {"id": 2, "tag": "button", "text": "Pesquisa Google", "role": "button"},
        {"id": 3, "tag": "a", "text": "Gmail", "role": "link"},
        {"id": 4, "tag": "a", "text": "Imagens", "role": "link"}
    ]
    goal = sys.argv[1] if len(sys.argv) > 1 else "Buscar passagens para São Paulo"
    res = decide_ui_action(goal, sample_elements)
    print(json.dumps(res, indent=2, ensure_ascii=False))
