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
