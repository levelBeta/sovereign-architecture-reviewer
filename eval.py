import json, time
from rules import evaluate
from explain import explain

EXPECTED = {
    "configs/flawed.json": 17,
    "configs/half_fixed.json": 13,
    "configs/clean.json": 0,
}

MODELS = ["llama3.2:3b", "qwen2.5:3b", "qwen2.5:7b"]

def check_regression():
    print("=== Regression check: rules engine ===\n")
    all_ok = True
    for path, expected_count in EXPECTED.items():
        cfg = json.load(open(path))
        findings = evaluate(cfg)
        actual = len(findings)
        status = "PASS" if actual == expected_count else "FAIL"
        if actual != expected_count:
            all_ok = False
        print(f"[{status}] {path}: expected {expected_count}, got {actual}")
    print()
    return all_ok

def compare_models():
    print("=== Model comparison: speed on one finding ===\n")
    cfg = json.load(open("configs/flawed.json"))
    findings = evaluate(cfg)
    sample = findings[0]

    results = []
    for model in MODELS:
        t0 = time.time()
        text = explain(sample, model=model)
        elapsed = time.time() - t0
        word_count = len(text.split())
        results.append({"model": model, "seconds": elapsed, "words": word_count})
        print(f"{model:16} {elapsed:5.1f}s   {word_count} words")
        print(f"   -> {text[:150]}...\n")

    return results

if __name__ == "__main__":
    regression_ok = check_regression()
    model_results = compare_models()

    print("=== Summary ===")
    print(f"Regression check: {'PASS' if regression_ok else 'FAIL - see above'}")
    print("\nModel speed comparison:")
    for r in model_results:
        print(f"  {r['model']:16} {r['seconds']:.1f}s")