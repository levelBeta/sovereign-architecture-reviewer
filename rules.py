from dataclasses import dataclass
from typing import Callable, Optional

AU_REGIONS = {"ap-southeast-2", "ap-southeast-4", "australiaeast",
              "australiasoutheast", "australia-southeast1", "australia-southeast2"}

@dataclass
class Rule:
    id: str
    title: str
    severity: str          # critical / high / medium
    types: tuple            # resource types this rule applies to
    pillar: str             # Well-Architected pillar
    cps234_area: str        # CPS 234-aligned control area (mapped, not "compliant")
    zero_trust: str
    lockin: bool
    remediation: str
    check: Callable[[dict], Optional[str]]   # returns evidence string if it fails

def flag(field, bad, msg):
    return lambda r: msg if r.get(field) == bad else None

def open_ports(r):
    bad = [str(p["port"]) for p in r.get("ingress", [])
           if p.get("cidr") == "0.0.0.0/0" and p.get("port") != 443]
    return f"open to the internet on port(s) {', '.join(bad)}" if bad else None

def residency(r):
    if r.get("data_class") == "regulated" and r.get("region") not in AU_REGIONS:
        return f"regulated data hosted in {r.get('region')}"

def no_recovery(r):
    if r["type"] == "object_storage" and r.get("versioning") is False:
        return "versioning disabled"
    if r["type"] == "database" and r.get("backups") is False:
        return "backups disabled"

def lockin(r):
    if r.get("provider_api") == "proprietary_only" and r.get("abstraction_layer") is False:
        return "model access hard-coded to one provider API"

def missing_tags(r):
    tags = r.get("tags")
    if not tags:
        return "no cost/ownership tags present"
    required = {"owner", "cost_center"}
    missing = required - set(tags.keys())
    if missing:
        return f"missing tag(s): {', '.join(sorted(missing))}"

SEC, REL, COST, OPS = "Security", "Reliability", "Cost Optimization", "Operational Excellence"
IMPL, CAP, CLASS, TEST = ("Implementation of controls", "Information security capability",
                          "Information asset identification and classification",
                          "Testing control effectiveness")

RULES = [
 Rule("R01","Storage not encrypted at rest","high",("object_storage",),SEC,IMPL,"Assume breach",False,
      "Enable encryption at rest with customer-managed keys.",flag("encrypted_at_rest",False,"encryption at rest disabled")),
 Rule("R02","Storage publicly accessible","critical",("object_storage",),SEC,IMPL,"Least privilege",False,
      "Block public access; grant access via scoped identities.",flag("public_access",True,"public access enabled")),
 Rule("R03","Database not encrypted at rest","high",("database",),SEC,IMPL,"Assume breach",False,
      "Enable encryption at rest with managed keys.",flag("encrypted_at_rest",False,"encryption at rest disabled")),
 Rule("R04","Database publicly accessible","critical",("database",),SEC,IMPL,"Least privilege",False,
      "Move to a private subnet; allow only service identities.",flag("publicly_accessible",True,"reachable from the internet")),
 Rule("R05","Open ingress from the internet","high",("service",),SEC,IMPL,"Verify explicitly",False,
      "Restrict ingress to internal ranges or a gateway on 443.",open_ports),
 Rule("R06","Traffic not encrypted in transit","high",("service",),SEC,IMPL,"Assume breach",False,
      "Enforce TLS on all listeners.",flag("tls",False,"TLS disabled")),
 Rule("R07","No mutual TLS between services","medium",("service",),SEC,IMPL,"Verify explicitly",False,
      "Adopt a service mesh with mTLS.",flag("mtls",False,"mTLS not enforced")),
 Rule("R08","Shared admin credentials","high",("service",),SEC,IMPL,"Least privilege",False,
      "Use per-workload identities with least-privilege roles.",flag("credentials","shared_admin","shared admin credential in use")),
 Rule("R09","Secrets stored in plaintext","high",("service",),SEC,IMPL,"Assume breach",False,
      "Move secrets to a secrets manager or sealed secrets.",flag("secrets_in_plaintext",True,"plaintext secrets in config")),
 Rule("R10","Audit logging disabled","high",("platform",),OPS,TEST,"Verify explicitly",False,
      "Enable immutable audit logging and central retention.",flag("audit_logging",False,"audit logging off")),
 Rule("R11","Model endpoint has no authentication","critical",("llm_endpoint",),SEC,IMPL,"Verify explicitly",False,
      "Require OIDC or token auth with per-caller authorisation.",flag("auth","none","no authentication")),
 Rule("R12","Regulated data outside Australia","high",("object_storage","database"),SEC,CLASS,"Assume breach",False,
      "Host regulated data in an Australian region.",residency),
 Rule("R13","Provider lock-in on model access","medium",("llm_endpoint",),COST,CAP,"n/a",True,
      "Add an abstraction layer (OpenAI-compatible gateway) so models are swappable.",lockin),
 Rule("R14","No recovery capability","medium",("object_storage","database"),REL,CAP,"Assume breach",False,
      "Enable versioning or backups with tested restores.",no_recovery),
 Rule("R15","Unrestricted egress from model workload","medium",("llm_endpoint",),SEC,IMPL,"Assume breach",False,
      "Apply an egress allowlist.",flag("egress","unrestricted","unrestricted outbound access")),
 Rule("R18","Missing cost/ownership tags","medium",
      ("object_storage","database","service","llm_endpoint","platform"),COST,CLASS,"n/a",False,
      "Apply standard cost-center and owner tags to all resources.",missing_tags),
 Rule("R16","No multi-factor authentication on admin access","high",("platform",),SEC,IMPL,"Verify explicitly",False,
      "Require MFA for all administrative and break-glass accounts.",flag("mfa_enabled",False,"MFA not enforced on admin access")),
 Rule("R20","Monitoring and alerting disabled","high",("platform",),OPS,TEST,"Verify explicitly",False,
      "Enable centralized monitoring with alerting on key security and reliability signals.",
      flag("monitoring_enabled",False,"monitoring and alerting disabled")),
]
def evaluate(config):
    findings = []
    for res in config["resources"]:
        for rule in RULES:
            if res["type"] in rule.types:
                evidence = rule.check(res)
                if evidence:
                    findings.append({"rule": rule.id, "title": rule.title, "severity": rule.severity,
                                     "resource": res["id"], "evidence": evidence, "pillar": rule.pillar,
                                     "cps234_area": rule.cps234_area, "zero_trust": rule.zero_trust,
                                     "lockin": rule.lockin, "remediation": rule.remediation})
    order = {"critical": 0, "high": 1, "medium": 2}
    return sorted(findings, key=lambda f: order[f["severity"]])