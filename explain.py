import requests

URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"

PROMPT_TEMPLATE = """You are writing one entry in an enterprise cloud architecture review report.
Do not invent facts. Use only the information given below.

Resource: {resource}
Finding: {title}
Evidence: {evidence}
Severity: {severity}
Well-Architected pillar: {pillar}
Mapped control area (aligned to APRA CPS 234, not a compliance certification): {cps234_area}
Zero-trust principle affected: {zero_trust}
Recommended remediation: {remediation}

Write exactly 2 sentences for a report read by a bank's architecture review board:
1) Why this specific finding matters, in plain business language.
2) Reference the remediation naturally, without just repeating it word for word.
Do not add any new claims, numbers, or regulations not listed above. Do not use headings or bullet points."""

def explain(finding, model=MODEL):
    prompt = PROMPT_TEMPLATE.format(**finding)
    r = requests.post(URL, json={
      "model": model, "prompt": prompt, "stream": False,
        "options": {"num_gpu": 0, "temperature": 0, "num_predict": 150}
    }, timeout=300)
    r.raise_for_status()
    return r.json()["response"].strip()

if __name__ == "__main__":
    test_finding = {
        "rule": "R02", "title": "Storage publicly accessible", "severity": "critical",
        "resource": "customer-data-bucket", "evidence": "public access enabled",
        "pillar": "Security", "cps234_area": "Implementation of controls",
        "zero_trust": "Least privilege", "lockin": False,
        "remediation": "Block public access; grant access via scoped identities.",
    }
    print(explain(test_finding))