import json, hashlib, time, os

LOG_PATH = "audit.jsonl"
GENESIS = "0" * 64

def _last_hash():
    if not os.path.exists(LOG_PATH):
        return GENESIS
    last = None
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = line
    if last is None:
        return GENESIS
    return json.loads(last)["hash"]

def record(event: dict):
    """Append one event to the audit log, chained to the previous entry."""
    prev = _last_hash()
    entry = {"ts": time.time(), "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             **event, "prev": prev}
    payload = json.dumps(entry, sort_keys=True).encode("utf-8")
    entry_hash = hashlib.sha256(payload).hexdigest()
    entry["hash"] = entry_hash
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def verify_chain():
    """Walk the whole log and confirm every hash matches. Returns (ok: bool, details: list[str])."""
    if not os.path.exists(LOG_PATH):
        return True, ["No audit log yet."]

    details = []
    expected_prev = GENESIS
    ok = True
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            stored_hash = entry.pop("hash")
            recomputed = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()

            if entry["prev"] != expected_prev:
                ok = False
                details.append(f"Entry {i}: broken chain — prev pointer does not match.")
            if recomputed != stored_hash:
                ok = False
                details.append(f"Entry {i}: hash mismatch — content was likely edited after logging.")
            if entry["prev"] == expected_prev and recomputed == stored_hash:
                details.append(f"Entry {i}: OK")

            expected_prev = recomputed

    return ok, details

if __name__ == "__main__":
    record({"action": "review", "config": "flawed.json", "findings": 17, "role": "ciso"})
    record({"action": "review", "config": "clean.json", "findings": 0, "role": "ciso"})
    ok, details = verify_chain()
    print(f"Chain valid: {ok}")
    for d in details:
        print(" -", d)
