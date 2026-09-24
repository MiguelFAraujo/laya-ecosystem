# Laya Ecosystem ⚡

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Model](https://img.shields.io/badge/Model-ModernBERT_/_mmBERT-orange.svg)](https://huggingface.co/convaiinnovations/laya)

**Production utilities, supervisors, lossless context compactors, and fast UI deciders for the Laya & TypeSafe Jev System-1 decision engines.**

Unlike text-generating LLMs that take seconds and generate token by token, **Laya System-1** executes typed decisions (`choice`, `score`, `noul`) with calibrated probabilities in a **single forward pass** (~33ms GPU / ~200ms CPU) with **zero hallucination**.

`laya-ecosystem` provides 4 production-grade tools built on top of this architecture:

---

## 🛠️ Core Tools

### 1. 🗜️ `idt-compactor` (Lossless Context Compactor)
*Inspired by `tamaratran/fast-jev-compaction`*
* Evaluates tool logs and conversational steps using calibrated System-1 importance scoring.
* Prunes transient noise and large repetitive outputs while **preserving source code, diffs, and critical decisions letter-for-letter**.
* Saves up to 60% of agent token costs without lossy summarization.

```bash
idt-compactor transcript.json > compacted.json
```

### 2. 🛡️ `idt-foreman` (Agent Supervisor & Safety Gate)
*Inspired by `thruwire/foreman` and `RomanSlack/jev-drone`*
* Evaluates agent execution steps, shell outputs, and exit codes in milliseconds.
* Decides next tactical action (`proceed`, `retry`, `fix`, `escalate`) and flags destructive actions requiring human-in-the-loop approval.

```bash
idt-foreman "Run database migrations" "OperationalError: table exists" 1
```

### 3. 🔍 `idt-search` (Two-Stage Semantic Search & Ranker)
*Inspired by `superagents-lab/jev-search` and `realZachi/pg-jev`*
* **Stage 1:** Fast FTS5 candidate retrieval from local databases.
* **Stage 2:** System-1 ordinal scoring (`irrelevante`, `baixa`, `moderada`, `alta`, `exata`) to re-rank results with surgical precision.

```bash
idt-search "telegram bot rate limit" 5
```

### 4. ⚡ `idt-action` (Ultra-Fast DOM & Mobile UI Decider)
*Inspired by `browser-use/jev-ultrafast` and `droidrun/mobile-jev`*
* Selects the target element and action (`click`, `type`, `scroll`, `done`) in a single forward pass without generating CSS selectors or coordinates.

```bash
idt-action "Search flights to São Paulo"
```

---

## 🚀 Quick Start

### Installation

```bash
pip install laya-ecosystem
```

### Configuration

By default, the tools connect to a local Laya daemon at `http://127.0.0.1:8092/v1/systemone` or any TypeSafe Jev endpoint:

```bash
export LAYA_URL="http://127.0.0.1:8092/v1/systemone"
```

---

## 📄 License
Apache License 2.0. See [LICENSE](LICENSE) for details.
