# Module: Security

> Information security, technical controls, and vulnerability management.

## How to enable
1. Fill in the sections below
2. Create a skill in `.claude/skills/` for each framework (e.g. `owasp/SKILL.md`)
3. Configure the `@security-auditor` agent

## Adopted frameworks
[SPEC] Check the applicable frameworks:
- [ ] OWASP Top 10
- [ ] NIST Cybersecurity Framework
- [ ] CIS Controls
- [ ] ISO 27001 (Annex A)
- [ ] [Other]

## Required technical controls
[SPEC] Define for the project:

### Authentication
- MFA: [required/optional/not applicable]
- Session: [duration, token type, refresh strategy]
- Passwords: [hash algorithm, complexity requirements]

### Authorization
- Model: [RBAC/ABAC/ACL]
- Principle: least privilege
- Verification: server-side on every route

### Encryption
- In transit: [TLS version]
- At rest: [algorithm, key management]
- Hashing: [algorithm for passwords]
- Key rotation: [frequency]

### Dependencies
- Scan: [tool, frequency]
- SLA for critical CVE: [deadline]
- Automation tool: [Dependabot/Renovate/Snyk]

### Security headers
- [ ] HSTS
- [ ] CSP
- [ ] X-Frame-Options
- [ ] X-Content-Type-Options
- [ ] Referrer-Policy

## Secrets management
- Vault: [SPEC] [HashiCorp Vault/AWS SM/GCP SM/Azure KV]
- Rotation: [SPEC] frequency
- Never in code — enforce via pre-commit hook
