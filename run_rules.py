import json, sys
from rules import evaluate

cfg = json.load(open(sys.argv[1]))
findings = evaluate(cfg)
print(f"\n{cfg['name']}: {len(findings)} findings\n")
for f in findings:
    print(f"[{f['severity'].upper():8}] {f['rule']} {f['resource']}: {f['title']} ({f['evidence']})")