# Architecture Review: Synthetic AI platform - HALF-FIXED

Reviewed offline, no data leaves this machine. Findings mapped to AWS Well-Architected pillars, zero-trust principles, and control areas aligned to APRA CPS 234 (not a compliance certification).

**Summary:** 13 findings — 2 critical, 6 high, 5 medium.

**Portability note:** 1 finding(s) indicate vendor lock-in risk, not a security risk on their own.

## Findings

### 1. [CRITICAL] Database publicly accessible — `customer-db`

- **Evidence:** reachable from the internet
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Least privilege
- **Remediation:** Move to a private subnet; allow only service identities.

This specific finding is concerning because a publicly accessible database could expose sensitive customer information to unauthorized access from the internet, which could lead to data breaches and loss of customer trust. To address this, we recommend moving the database to a private subnet and allowing access only to service identities, which aligns with the least privilege principle and enhances security.

### 2. [CRITICAL] Model endpoint has no authentication — `llm-endpoint`

- **Evidence:** no authentication
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Require OIDC or token auth with per-caller authorisation.

This specific finding is critical because without authentication on the model endpoint, sensitive data could potentially be accessed by unauthorized users, posing a significant risk to the bank's data security. To address this, we recommend requiring OIDC or token authentication with per-caller authorization to ensure only authorized users can access the endpoint.

### 3. [HIGH] Regulated data outside Australia — `customer-data-bucket`

- **Evidence:** regulated data hosted in us-east-1
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Information asset identification and classification
- **Zero-trust principle:** Assume breach
- **Remediation:** Host regulated data in an Australian region.

This specific finding is concerning because it exposes our customer data to potential risks outside of Australia, which could compromise our compliance with regulatory requirements. To address this, we should host the regulated data in an Australian region to better align with our security and regulatory obligations.

### 4. [HIGH] Database not encrypted at rest — `customer-db`

- **Evidence:** encryption at rest disabled
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable encryption at rest with managed keys.

The database not encrypted at rest poses a significant risk as it exposes customer data to potential unauthorized access, especially in a scenario where the zero-trust principle is assumed breached. To mitigate this risk, enabling encryption at rest with managed keys is recommended to secure the database.

### 5. [HIGH] Regulated data outside Australia — `customer-db`

- **Evidence:** regulated data hosted in us-east-1
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Information asset identification and classification
- **Zero-trust principle:** Assume breach
- **Remediation:** Host regulated data in an Australian region.

This specific finding is concerning because regulated data is currently hosted in a region outside Australia, which could expose the bank to regulatory risks and compliance issues. To address this, we recommend moving the regulated data to an Australian region as per the recommended remediation.

### 6. [HIGH] Open ingress from the internet — `inference-api`

- **Evidence:** open to the internet on port(s) 8080
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Restrict ingress to internal ranges or a gateway on 443.

This specific finding is concerning because it exposes the inference-api service to the internet on port 8080, which could potentially allow unauthorized access and pose a security risk. To address this, we recommend restricting ingress to internal ranges or through a secure gateway on port 443, aligning with the zero-trust principle.

### 7. [HIGH] Shared admin credentials — `inference-api`

- **Evidence:** shared admin credential in use
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Least privilege
- **Remediation:** Use per-workload identities with least-privilege roles.

This specific finding about shared admin credentials in the inference-api service raises a significant concern as it undermines our security posture by potentially exposing sensitive resources to unauthorized access. To address this, we should implement per-workload identities with least-privilege roles to adhere to the least privilege principle and enhance our security architecture.

### 8. [HIGH] Secrets stored in plaintext — `inference-api`

- **Evidence:** plaintext secrets in config
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Move secrets to a secrets manager or sealed secrets.

This specific finding is concerning because storing secrets in plaintext poses a significant risk to our system's security, as it could expose sensitive information if accessed by unauthorized parties. To address this, we should move the secrets to a secrets manager or use sealed secrets to enhance our security posture, aligning with the zero-trust principle of assuming breaches could occur.

### 9. [MEDIUM] No recovery capability — `customer-data-bucket`

- **Evidence:** versioning disabled
- **Well-Architected pillar:** Reliability
- **CPS 234-aligned area:** Information security capability
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable versioning or backups with tested restores.

This specific finding is concerning because without versioning or backups with tested restores enabled, there is no recovery capability in case of data loss or corruption. To address this, enabling versioning or backups with tested restores is recommended.

### 10. [MEDIUM] No recovery capability — `customer-db`

- **Evidence:** backups disabled
- **Well-Architected pillar:** Reliability
- **CPS 234-aligned area:** Information security capability
- **Zero-trust principle:** Assume breach
- **Remediation:** Enable versioning or backups with tested restores.

The absence of recovery capabilities in the customer-db resource, specifically the disabled backups, poses a significant risk to the bank's ability to recover from data loss or corruption, which could lead to financial losses and reputational damage. To address this, enabling versioning or backups with tested restores is recommended to ensure the system's reliability and mitigate the risk of data loss.

### 11. [MEDIUM] No mutual TLS between services — `inference-api`

- **Evidence:** mTLS not enforced
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Verify explicitly
- **Remediation:** Adopt a service mesh with mTLS.

This finding about no mutual TLS between services could lead to security vulnerabilities, as it allows for man-in-the-middle attacks where an attacker could intercept and manipulate communications between services. To address this, adopting a service mesh with mutual TLS would be a recommended remediation to enhance security and protect against such threats.

### 12. [MEDIUM] Provider lock-in on model access — `llm-endpoint`

- **Evidence:** model access hard-coded to one provider API
- **Well-Architected pillar:** Cost Optimization
- **CPS 234-aligned area:** Information security capability
- **Zero-trust principle:** n/a
- **Remediation:** Add an abstraction layer (OpenAI-compatible gateway) so models are swappable.

This finding is concerning because hard-coding model access to a single provider's API could lead to vendor lock-in, potentially increasing costs and reducing flexibility. To address this, adding an abstraction layer like an OpenAI-compatible gateway would allow for model swippability, ensuring the architecture remains cost-effective and adaptable.

### 13. [MEDIUM] Unrestricted egress from model workload — `llm-endpoint`

- **Evidence:** unrestricted outbound access
- **Well-Architected pillar:** Security
- **CPS 234-aligned area:** Implementation of controls
- **Zero-trust principle:** Assume breach
- **Remediation:** Apply an egress allowlist.

This specific finding is concerning because it exposes our model workload to unrestricted egress, which could potentially allow unauthorized access to external resources. To address this, we should apply an egress allowlist to ensure only trusted resources can be accessed, aligning with our commitment to the zero-trust principle.
