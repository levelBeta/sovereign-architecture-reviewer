import json, copy

base = json.load(open("configs/flawed.json"))

half = {
 "customer-data-bucket": {"encrypted_at_rest": True, "public_access": False},
 "inference-api": {"tls": True, "ingress": [{"port": 8080, "cidr": "0.0.0.0/0"}]},
 "platform": {"audit_logging": True},
}
clean = {
 "customer-data-bucket": {"encrypted_at_rest": True, "public_access": False, "versioning": True, "region": "ap-southeast-2"},
 "customer-db": {"encrypted_at_rest": True, "publicly_accessible": False, "backups": True, "region": "ap-southeast-2"},
 "inference-api": {"tls": True, "mtls": True, "ingress": [{"port": 443, "cidr": "10.0.0.0/8"}],
                   "credentials": "workload_identity", "secrets_in_plaintext": False},
 "llm-endpoint": {"auth": "oidc", "provider_api": "portable", "abstraction_layer": True, "egress": "allowlist"},
 "platform": {"audit_logging": True},
}

for name, patch in (("half_fixed", half), ("clean", clean)):
    cfg = copy.deepcopy(base)
    cfg["name"] = base["name"].replace("FLAWED", name.upper().replace("_", "-"))
    for r in cfg["resources"]:
        r.update(patch.get(r["id"], {}))
    json.dump(cfg, open(f"configs/{name}.json", "w"), indent=2)