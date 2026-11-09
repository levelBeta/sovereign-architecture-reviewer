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
