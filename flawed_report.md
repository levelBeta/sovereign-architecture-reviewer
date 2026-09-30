# Architecture Review: Synthetic AI platform - FLAWED

Reviewed offline, no data leaves this machine. Findings mapped to AWS Well-Architected pillars, zero-trust principles, and control areas aligned to APRA CPS 234 (not a compliance certification).

**Summary:** 17 findings — 3 critical, 9 high, 5 medium.

**Portability note:** 1 finding(s) indicate vendor lock-in risk, not a security risk on their own.

## Findings

### 1. [CRITICAL] Storage publicly accessible — `customer-data-bucket`

- **Evidence:** public access enabled
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Least privilege
- **Remediation:** Block public access; grant access via scoped identities.

This specific finding is concerning because enabling public access to the customer-data-bucket could expose sensitive customer information to unauthorized users, potentially leading to data breaches and loss of trust from customers. To address this, we recommend blocking public access and granting access only via scoped identities to ensure least privilege and enhance security.

### 2. [CRITICAL] Database publicly accessible — `customer-db`

- **Evidence:** reachable from the internet
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Least privilege
- **Remediation:** Move to a private subnet; allow only service identities.

This specific finding is concerning because a publicly accessible database could expose sensitive customer data to unauthorized access from the internet, which could lead to data breaches and loss of trust from customers. To address this, we recommend moving the database to a private subnet and allowing access only to service identities, which aligns with the least privilege principle and enhances security.

### 3. [CRITICAL] Model endpoint has no authentication — `llm-endpoint`

- **Evidence:** no authentication
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Require OIDC or token auth with per-caller authorisation.

This specific finding is critical because without authentication on the model endpoint, sensitive data could potentially be accessed by unauthorized users, posing a significant risk to the bank's data security and compliance. To address this, we recommend requiring OIDC or token authentication with per-caller authorization to ensure only authorized users can access the endpoint.

### 4. [HIGH] Storage not encrypted at rest — `customer-data-bucket`

- **Evidence:** encryption at rest disabled
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable encryption at rest with customer-managed keys.

This specific finding is critical because without encryption at rest, customer data stored in the customer-data-bucket is vulnerable to unauthorized access, potentially exposing sensitive information. To address this, we recommend enabling encryption at rest with customer-managed keys to enhance security and protect data integrity.

### 5. [HIGH] Regulated data outside Australia — `customer-data-bucket`

- **Evidence:** regulated data hosted in us-east-1
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Information asset identification and classification
- **Zero-trust principle:** Assume breach
- **Remediation:** Host regulated data in an Australian region.

This specific finding matters because storing regulated data in the US-East-1 region outside Australia could compromise compliance with regulatory requirements, potentially leading to penalties and reputational damage. To address this, we recommend moving the regulated data to an Australian region to align with the zero-trust principle and ensure data security and compliance.

### 6. [HIGH] Database not encrypted at rest — `customer-db`

- **Evidence:** encryption at rest disabled
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable encryption at rest with managed keys.

The database not encrypted at rest poses a significant risk as it exposes customer data to potential unauthorized access, especially given the zero-trust principle, which assumes breach. To mitigate this risk, enabling encryption at rest with managed keys is recommended.

### 7. [HIGH] Regulated data outside Australia — `customer-db`

- **Evidence:** regulated data hosted in us-east-1
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Information asset identification and classification
- **Zero-trust principle:** Assume breach
- **Remediation:** Host regulated data in an Australian region.

This specific finding matters because regulated data hosted in the US-East-1 region outside Australia could compromise compliance with regulatory requirements, potentially leading to fines and reputational damage. To address this, we recommend moving the regulated data to an Australian region to align with the zero-trust principle and ensure compliance.

### 8. [HIGH] Open ingress from the internet — `inference-api`

- **Evidence:** open to the internet on port(s) 22, 8080
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Restrict ingress to internal ranges or a gateway on 443.

This specific finding is concerning because it exposes the inference-api service to the internet on ports 22 and 8080, which could potentially allow unauthorized access and pose a security risk. To mitigate this, we recommend restricting ingress to internal ranges or a gateway on port 443, aligning with the zero-trust principle.

### 9. [HIGH] Traffic not encrypted in transit — `inference-api`

- **Evidence:** TLS disabled
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Enforce TLS on all listeners.

This specific finding is concerning because it exposes our inference-api service to potential eavesdropping during data transmission, which could lead to sensitive information being intercepted. To address this, we need to enforce TLS on all listeners to ensure all traffic is encrypted in transit, thereby enhancing our security posture and aligning with our zero-trust principle.

### 10. [HIGH] Shared admin credentials — `inference-api`

- **Evidence:** shared admin credential in use
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Least privilege
- **Remediation:** Use per-workload identities with least-privilege roles.

This specific finding about shared admin credentials in the inference-api service poses a significant risk because it could lead to unauthorized access and compromise of sensitive data, potentially violating least privilege principles. To address this, we recommend implementing per-workload identities with least-privilege roles to enhance security and align with the zero-trust principle.

### 11. [HIGH] Secrets stored in plaintext — `inference-api`

- **Evidence:** plaintext secrets in config
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Move secrets to a secrets manager or sealed secrets.

This specific finding is concerning because the inference-api uses plaintext for storing secrets, which could expose sensitive information if accessed improperly. To address this, we recommend moving the secrets to a secrets manager or using sealed secrets to enhance security.

### 12. [HIGH] Audit logging disabled — `platform`

- **Evidence:** audit logging off
- **Well-Architected pillar:** Operational Excellence
- **CPS 234-aligned area:** Testing control effectiveness
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Enable immutable audit logging and central retention.

This specific finding about audit logging being disabled is critical because it leaves the bank vulnerable to potential security breaches and unauthorized access, as audit logs are crucial for detecting and responding to such incidents promptly. To address this, we recommend enabling immutable audit logging and central retention to ensure robust security controls are in place.

### 13. [MEDIUM] No recovery capability — `customer-data-bucket`

- **Evidence:** versioning disabled
- **Well-Architected pillar:** Reliability
- **CPS 234-aligned area:** Information security capability
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable versioning or backups with tested restores.

The absence of recovery capability for the customer-data-bucket, specifically due to versioning being disabled, poses a risk as it lacks the ability to recover from data loss or corruption. To address this, enabling versioning or implementing backups with tested restores is recommended to ensure data integrity and reliability.

### 14. [MEDIUM] No recovery capability — `customer-db`

- **Evidence:** backups disabled
- **Well-Architected pillar:** Reliability
- **CPS 234-aligned area:** Information security capability
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable versioning or backups with tested restores.

The absence of recovery capabilities in the customer-db resource, specifically the disabled backups, poses a significant risk to the bank's ability to recover from data loss or corruption, which could lead to financial losses and damage to customer trust. To address this, enabling versioning or backups with tested restores is recommended to ensure the system's reliability and mitigate the risk of a data breach.

### 15. [MEDIUM] No mutual TLS between services — `inference-api`

- **Evidence:** mTLS not enforced
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Adopt a service mesh with mTLS.

This specific finding about no mutual TLS between services could lead to security vulnerabilities, as it allows for man-in-the-middle attacks where an attacker could intercept and manipulate communications between services. To address this, adopting a service mesh with mutual TLS would be recommended to enhance security and adhere to the zero-trust principle.

### 16. [MEDIUM] Provider lock-in on model access — `llm-endpoint`

- **Evidence:** model access hard-coded to one provider API
- **Well-Architected pillar:** Cost Optimization
- **CPS 234-aligned area:** Information security capability
- **Zero-trust principle:** n/a
- **Remediation:** Add an abstraction layer (OpenAI-compatible gateway) so models are swappable.

This finding indicates that the current architecture locks the bank into using a single provider for its language models, which could lead to vendor lock-in risks and potentially higher costs if the chosen provider were to change its pricing or service terms. To mitigate this, the recommended remediation is to add an abstraction layer that allows the bank to use models from different providers, such as an OpenAI-compatible gateway, ensuring model access is not tied to a single provider.

### 17. [MEDIUM] Unrestricted egress from model workload — `llm-endpoint`

- **Evidence:** unrestricted outbound access
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Apply an egress allowlist.

This specific finding is concerning because it exposes our model workload to unrestricted egress, which could potentially allow unauthorized access to external resources. To address this, we should apply an egress allowlist to ensure only trusted resources can be accessed, aligning with our commitment to the zero-trust principle.
