from rules import evaluate


def rule_ids(resources):
    return [f["rule"] for f in evaluate({"resources": resources})]


def test_r01_flags_unencrypted_storage():
    res = {"id": "syn-bucket", "type": "object_storage", "encrypted_at_rest": False}
    found = [f for f in evaluate({"resources": [res]}) if f["rule"] == "R01"]
    assert len(found) == 1
    assert found[0]["evidence"] == "encryption at rest disabled"


def test_r01_passes_encrypted_storage():
    res = {"id": "syn-bucket", "type": "object_storage", "encrypted_at_rest": True}
    assert "R01" not in rule_ids([res])


def test_r01_ignores_missing_field():
    res = {"id": "syn-bucket", "type": "object_storage"}
    assert "R01" not in rule_ids([res])


def test_r02_flags_public_storage():
    res = {"id": "syn-bucket", "type": "object_storage", "public_access": True}
    found = [f for f in evaluate({"resources": [res]}) if f["rule"] == "R02"]
    assert len(found) == 1
    assert found[0]["evidence"] == "public access enabled"


def test_r02_passes_private_storage():
    res = {"id": "syn-bucket", "type": "object_storage", "public_access": False}
    assert "R02" not in rule_ids([res])


def test_r02_ignores_missing_field():
    res = {"id": "syn-bucket", "type": "object_storage"}
    assert "R02" not in rule_ids([res])


def test_r02_does_not_apply_to_databases():
    res = {"id": "syn-db", "type": "database", "public_access": True}
    assert "R02" not in rule_ids([res])


def test_r03_flags_unencrypted_database():
    res = {"id": "syn-db", "type": "database", "encrypted_at_rest": False}
    found = [f for f in evaluate({"resources": [res]}) if f["rule"] == "R03"]
    assert len(found) == 1
    assert found[0]["evidence"] == "encryption at rest disabled"


def test_r03_passes_encrypted_database():
    res = {"id": "syn-db", "type": "database", "encrypted_at_rest": True}
    assert "R03" not in rule_ids([res])


def test_r03_ignores_missing_field():
    res = {"id": "syn-db", "type": "database"}
    assert "R03" not in rule_ids([res])


def test_r03_does_not_apply_to_storage():
    res = {"id": "syn-bucket", "type": "object_storage", "encrypted_at_rest": False}
    assert "R03" not in rule_ids([res])


def test_r04_flags_public_database():
    res = {"id": "syn-db", "type": "database", "publicly_accessible": True}
    found = [f for f in evaluate({"resources": [res]}) if f["rule"] == "R04"]
    assert len(found) == 1
    assert found[0]["evidence"] == "reachable from the internet"


def test_r04_passes_private_database():
    res = {"id": "syn-db", "type": "database", "publicly_accessible": False}
    assert "R04" not in rule_ids([res])


def test_r04_ignores_missing_field():
    res = {"id": "syn-db", "type": "database"}
    assert "R04" not in rule_ids([res])


def test_r04_ignores_storage_field_name():
    res = {"id": "syn-db", "type": "database", "public_access": True}
    assert "R04" not in rule_ids([res])


def test_r04_does_not_apply_to_storage():
    res = {"id": "syn-bucket", "type": "object_storage", "publicly_accessible": True}
    assert "R04" not in rule_ids([res])


def svc(ingress):
    return {"id": "syn-svc", "type": "service", "ingress": ingress}


def r05(res):
    return [f for f in evaluate({"resources": [res]}) if f["rule"] == "R05"]


def test_r05_flags_open_port():
    found = r05(svc([{"port": 22, "cidr": "0.0.0.0/0"}]))
    assert [f["evidence"] for f in found] == ["open to the internet on port(s) 22"]


def test_r05_exempts_port_443():
    assert r05(svc([{"port": 443, "cidr": "0.0.0.0/0"}])) == []


def test_r05_ignores_private_cidr():
    assert r05(svc([{"port": 22, "cidr": "10.0.0.0/8"}])) == []


def test_r05_ignores_missing_ingress():
    assert r05({"id": "syn-svc", "type": "service"}) == []


def test_r05_boundary_around_443():
    found = r05(svc([{"port": 442, "cidr": "0.0.0.0/0"},
                     {"port": 443, "cidr": "0.0.0.0/0"},
                     {"port": 444, "cidr": "0.0.0.0/0"}]))
    assert [f["evidence"] for f in found] == ["open to the internet on port(s) 442, 444"]


def test_r05_lookalike_cidr_not_flagged():
    assert r05(svc([{"port": 22, "cidr": "0.0.0.0/1"}])) == []


def test_r05_lists_every_open_port():
    found = r05(svc([{"port": 22, "cidr": "0.0.0.0/0"},
                     {"port": 8080, "cidr": "0.0.0.0/0"}]))
    assert [f["evidence"] for f in found] == ["open to the internet on port(s) 22, 8080"]


def test_r05_mixed_private_and_open():
    found = r05(svc([{"port": 22, "cidr": "10.0.0.0/8"},
                     {"port": 8080, "cidr": "0.0.0.0/0"}]))
    assert [f["evidence"] for f in found] == ["open to the internet on port(s) 8080"]


def test_r05_flags_entry_with_no_port():
    found = r05(svc([{"cidr": "0.0.0.0/0"}]))
    assert [f["evidence"] for f in found] == ["open to the internet on port(s) not specified"]


def test_r05_no_port_listed_after_known_port():
    found = r05(svc([{"port": 22, "cidr": "0.0.0.0/0"}, {"cidr": "0.0.0.0/0"}]))
    assert [f["evidence"] for f in found] == ["open to the internet on port(s) 22, not specified"]


def test_r06_flags_service_without_tls():
    res = {"id": "syn-svc", "type": "service", "tls": False}
    found = [f for f in evaluate({"resources": [res]}) if f["rule"] == "R06"]
    assert len(found) == 1
    assert found[0]["evidence"] == "TLS disabled"


def test_r06_passes_service_with_tls():
    res = {"id": "syn-svc", "type": "service", "tls": True}
    assert "R06" not in rule_ids([res])


def test_r06_ignores_missing_field():
    res = {"id": "syn-svc", "type": "service"}
    assert "R06" not in rule_ids([res])


def test_r06_does_not_apply_to_databases():
    res = {"id": "syn-db", "type": "database", "tls": False}
    assert "R06" not in rule_ids([res])
