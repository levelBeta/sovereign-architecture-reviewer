# Sovereign Architecture Review Agent

A local, offline AI agent that reviews cloud/AI architecture configs for security,
reliability, and vendor lock-in risks — reviewed entirely on a laptop, with zero
cloud dependency and zero outbound network calls during a review.

Built as a working demonstration of the design principles behind
[builderAnts](https://github.com/levelBeta): sovereign, zero-trust, vendor-agnostic
AI infrastructure — no vendor lock-in, no data leaving the machine.

## Why this exists

Most "AI reviews architecture" demos are a chatbot with a system prompt. That's not
defensible in front of a risk-aware panel, because an LLM can miss a real problem or
invent one that doesn't exist. This project splits responsibilities instead:

- **Detection is deterministic code.** A rules engine (`rules.py`) checks a config
  against 15 specific, auditable conditions — public storage, missing encryption,
  open ingress ports, plaintext secrets, and more. The LLM never decides what counts
  as a finding.
- **Explanation is the LLM's job.** Once a finding is identified, a small local model
  (via [Ollama](https://ollama.com)) writes a short, plain-English explanation and
  ties it to the remediation — nothing more.

This split means the system can't hallucinate a vulnerability that isn't there, and
it can't miss one that is. It also means every finding is fully traceable back to
the exact rule and evidence that triggered it.

## What it checks

15 rules across 5 resource types (storage, database, service, LLM endpoint, platform),
each mapped to:
- An **AWS Well-Architected Framework** pillar (Security, Reliability, Cost
  Optimization, Operational Excellence)
- A control area **aligned to APRA CPS 234** (not a compliance certification —
  see Limitations)
- A **zero-trust principle** (least privilege, assume breach, verify explicitly)
- Whether it's a **vendor lock-in** signal rather than a security risk

Findings are demonstrated across three synthetic configs representing a before /
partially-fixed / after state, proving the detection logic is consistent:

| Config | Findings |
|---|---|
| `flawed.json` | 17 (3 critical, 9 high, 5 medium) |
| `half_fixed.json` | 13 |
| `clean.json` | 0 |

## Architecture

1. **Config (JSON)** — the architecture being reviewed
2. → **Rules engine** (`rules.py`) — deterministic, no LLM — produces findings
3. → **Local LLM** (Ollama, `qwen2.5:3b`) — explains each finding in plain English
4. → **Streamlit UI** (`app.py`) — streams results, shows severity + control mapping
   - → **Sovereignty check** (`sovereignty.py`) — confirms 0 outbound connections
   - → **Audit log** (`audit.py`) — hash-chained, tamper-evident record of every review


## Governance features

- **Tamper-evident audit log.** Every review is appended to `audit.jsonl` with a
  SHA-256 hash chained to the previous entry. Editing any past entry breaks the
  chain from that point forward — verified automatically by `verify_chain()` in
  `audit.py`, and tested by deliberately editing a logged entry and confirming
  detection.
- **Sovereignty check.** Before and after each review, the app inspects the
  review process's own network connections and confirms zero outbound traffic —
  a precise, process-specific claim rather than a blanket "offline" assertion.

## Eval results

Run via `eval.py`, which (1) confirms the rules engine still produces the exact
expected finding counts on all three configs — a regression check — and (2) times
the same explanation across three local models on this machine (Windows 11,
Ryzen-based mini PC, CPU-only inference):

| Model | Time (cold) | Words |
|---|---|---|
| llama3.2:3b | 13.5s | 74 |
| qwen2.5:3b | 10.7s | 50 |
| qwen2.5:7b | 22.4s | 45 |

`qwen2.5:3b` was chosen as the default: fastest, most concise, and no meaningful
quality drop versus the larger model.

A full review of the flawed config (17 findings, each individually explained)
completes in ~2 minutes, entirely offline.

## Running it

Requires [Ollama](https://ollama.com) and Python 3.12+.

```bash
ollama pull qwen2.5:3b
pip install -r requirements.txt   # streamlit, requests, psutil
streamlit run app.py
```

Then select a config from the dropdown and click **Run Review**.

To run the eval / regression check directly:

```bash
python eval.py
```

## Limitations

- Findings are **mapped to** APRA CPS 234 control areas and Well-Architected
  pillars, not a compliance certification. A real deployment would need review
  by a qualified compliance professional.
- All configs are **synthetic**. No real client or production data was used
  anywhere in this project.
- Detection covers 15 rules across 5 resource types — a production system would
  need a substantially larger rule set, likely driven by a proper policy-as-code
  engine (e.g. OPA/Rego) rather than hand-written Python.
- Ingests simplified JSON, not real Terraform or CloudFormation — parsing actual
  IaC is a natural next step.
- Tested against 3-4B and 7B parameter models on CPU only; larger models or GPU
  inference were not evaluated.

## What this would look like in production

The same detection logic, containerized and deployed on Kubernetes (EKS/AKS/on-prem),
behind a real identity provider, with policy enforcement via OPA, secrets in a
managed vault, and the vector/config store swapped for a governed data platform —
the local version proves the design; production hardens it.



