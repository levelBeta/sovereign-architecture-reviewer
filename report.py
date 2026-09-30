import json, sys, time
from rules import evaluate
from explain import explain

def build_report(config_path):
    cfg = json.load(open(config_path))
    findings = evaluate(cfg)

    counts = {"critical": 0, "high": 0, "medium": 0}
    for f in findings:
        counts[f["severity"]] += 1

    lines = []
    lines.append(f"# Architecture Review: {cfg['name']}\n")
    lines.append(f"Reviewed offline, no data leaves this machine. "
                 f"Findings mapped to AWS Well-Architected pillars, zero-trust principles, "
                 f"and control areas aligned to APRA CPS 234 (not a compliance certification).\n")
    lines.append(f"**Summary:** {len(findings)} findings — "
                 f"{counts['critical']} critical, {counts['high']} high, {counts['medium']} medium.\n")

    lockin_findings = [f for f in findings if f["lockin"]]
    if lockin_findings:
        lines.append(f"**Portability note:** {len(lockin_findings)} finding(s) indicate vendor lock-in risk, "
                     f"not a security risk on their own.\n")

    if not findings:
        lines.append("No findings. This configuration passes all 15 checks in this review.\n")
    else:
        lines.append("## Findings\n")
        for i, f in enumerate(findings, 1):
            print(f"  Explaining finding {i}/{len(findings)}: {f['rule']}...")
            narrative = explain(f)
            lines.append(f"### {i}. [{f['severity'].upper()}] {f['title']} — `{f['resource']}`\n")
            lines.append(f"- **Evidence:** {f['evidence']}")
            lines.append(f"- **Well-Architected pillar:** {f['pillar']}")
            lines.append(f"- **CPS 234-aligned area:** {f['cps234_area']}")
            lines.append(f"- **Zero-trust principle:** {f['zero_trust']}")
            lines.append(f"- **Remediation:** {f['remediation']}")
            lines.append(f"\n{narrative}\n")

    return "\n".join(lines)

if __name__ == "__main__":
    t0 = time.time()
    report = build_report(sys.argv[1])
    elapsed = time.time() - t0

    out_path = sys.argv[1].replace("configs\\", "").replace("configs/", "").replace(".json", "_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nDone in {elapsed:.1f}s. Report saved to {out_path}")