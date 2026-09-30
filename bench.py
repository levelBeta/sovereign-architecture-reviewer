import time, requests, psutil

MODELS = ["llama3.2:3b", "qwen2.5:3b", "qwen2.5:7b"]
URL = "http://localhost:11434/api/generate"
PROMPT = ("You are a cloud security reviewer at a bank. In about 120 words, explain why "
          "a storage bucket without encryption at rest is a risk, map it to a "
          "Well-Architected security principle, and give one remediation step.")

def ollama_rss_gb():
    total = 0
    for p in psutil.process_iter(["name", "memory_info"]):
        if p.info["name"] and "ollama" in p.info["name"].lower():
            total += p.info["memory_info"].rss
    return total / 1e9

def run(model):
    t0 = time.time()
    r = requests.post(URL, json={
        "model": model, "prompt": PROMPT, "stream": False,
        "options": {"num_gpu": 0, "num_predict": 200, "temperature": 0}
    }, timeout=900)
    r.raise_for_status()
    d = r.json()
    return {
        "wall_s": time.time() - t0,
        "load_s": d.get("load_duration", 0) / 1e9,
        "tok_per_s": d["eval_count"] / (d["eval_duration"] / 1e9),
        "tokens": d["eval_count"],
        "ram_gb": ollama_rss_gb(),
        "text": d["response"],
    }

print(f"System RAM: {psutil.virtual_memory().total/1e9:.1f} GB\n")
for m in MODELS:
    print(f"=== {m} ===")
    for label in ("cold", "warm"):
        r = run(m)
        print(f"{label}: wall {r['wall_s']:.1f}s | load {r['load_s']:.1f}s | "
              f"{r['tok_per_s']:.1f} tok/s | {r['tokens']} tokens | ollama RAM {r['ram_gb']:.1f} GB")
    print("\nSample output:\n", r["text"][:600], "\n")