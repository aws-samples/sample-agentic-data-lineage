# Security Setup Guide

This guide helps you set up and configure the security scanning pipeline for this project.

## 🚀 Quick Setup

### 1. GitLab CI/CD Configuration

The `.gitlab-ci.yml` file is already configured with comprehensive security scanning. No additional setup required for basic functionality.

### 2. Enable GitLab Security Features

In your GitLab project settings:

1. **Navigate to**: Settings → Security & Compliance
2. **Enable**:
   - Static Application Security Testing (SAST)
   - Dependency Scanning
   - Secret Detection
   - License Compliance
3. **Configure**: Security Dashboard access for your team

### 3. Local Development Setup

Install pre-commit hooks for local security checking:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run all hooks manually (optional)
pre-commit run --all-files
```

## 🔧 Configuration Details

### Probe Security Scanning

Probe scanning is automatically enabled and runs on every commit. Configuration in `.gitlab-ci.yml`:

```yaml
probe_security_scan:
  stage: security
  image: registry.gitlab.com/gitlab-org/security-products/analyzers/probe:latest
  script:
    - probe scan --format gitlab --output probe-report.json .
  artifacts:
    reports:
      sast: probe-report.json
```

### Security Tool Configuration

| Tool | Purpose | Configuration File | Exclusions |
|------|---------|-------------------|------------|
| **Probe** | Comprehensive vulnerability scanning | `.gitlab-ci.yml` | test/, .venv/, .terraform/ |
| **Bandit** | Python security issues | `.pre-commit-config.yaml` | tests/, B101, B601 |
| **Semgrep** | Multi-language security | `.pre-commit-config.yaml` | test/, .venv/ |
| **Checkov** | Infrastructure security | `.pre-commit-config.yaml` | N/A |
| **detect-secrets** | Secret detection | `.secrets.baseline` | .venv/, .terraform/ |

### Custom Security Rules

Add custom security rules by modifying:

```yaml
# .gitlab-ci.yml - Add custom Semgrep rules
semgrep --config=custom-rules.yml --json --output=custom-report.json .

# .pre-commit-config.yaml - Add custom Bandit rules
- id: bandit
  args: ['-r', '--configfile', '.bandit']
```

## 📊 Monitoring and Alerts

### Security Dashboard Access

1. **Project Level**: Project → Security & Compliance → Security Dashboard
2. **Group Level**: Group → Security → Security Dashboard
3. **Instance Level**: Admin Area → Security & Compliance

### Setting Up Alerts

Configure notifications for security findings:

```yaml
# .gitlab-ci.yml - Add notification stage
security_notification:
  stage: security
  script:
    - |
      if [ -f "probe-report.json" ]; then
        CRITICAL_COUNT=$(jq '[.vulnerabilities[] | select(.severity == "Critical")] | length' probe-report.json)
        if [ "$CRITICAL_COUNT" -gt 0 ]; then
          echo "🚨 Critical vulnerabilities found: $CRITICAL_COUNT"
          # Add your notification logic here (Slack, email, etc.)
        fi
      fi
```

### Integration with External Tools

#### Slack Notifications

```bash
# Add to your CI script
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Security scan completed with findings"}' \
  $SLACK_WEBHOOK_URL
```

#### JIRA Integration

```bash
# Create JIRA ticket for high-severity findings
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"fields":{"project":{"key":"SEC"},"summary":"Security Finding","description":"Details"}}' \
  $JIRA_API_URL
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Probe Scan Fails

```bash
# Check GitLab Runner has access to security analyzers
docker pull registry.gitlab.com/gitlab-org/security-products/analyzers/probe:latest

# Verify project permissions
# Settings → CI/CD → Variables → Add GITLAB_TOKEN if needed
```

#### 2. Pre-commit Hooks Fail

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Skip specific hooks if needed
SKIP=bandit pre-commit run --all-files

# Clear pre-commit cache
pre-commit clean
```

#### 3. False Positives

Add exclusions to configuration files:

```yaml
# .gitlab-ci.yml - Exclude paths from scanning
variables:
  SAST_EXCLUDED_PATHS: "spec, test, tests, tmp, .venv, venv, docs"
```

```yaml
# .pre-commit-config.yaml - Skip specific rules
- id: bandit
  args: ['-r', '--skip', 'B101,B601,B404']
```

### Performance Optimization

#### Reduce Scan Time

```yaml
# .gitlab-ci.yml - Parallel security jobs
security_fast:
  extends: .security_template
  parallel:
    matrix:
      - SCAN_TYPE: [sast, secrets, dependencies]
```

#### Cache Dependencies

```yaml
# .gitlab-ci.yml - Cache security tools
cache:
  key: security-tools-$CI_COMMIT_REF_SLUG
  paths:
    - .cache/
```

## 📋 Security Checklist

### Before Merge Request

- [ ] All security scans pass
- [ ] No critical or high-severity findings
- [ ] Pre-commit hooks executed successfully
- [ ] Security review completed (if required)

### Regular Maintenance

- [ ] Update security tool versions monthly
- [ ] Review and update exclusion lists quarterly
- [ ] Audit security findings and false positives
- [ ] Update security baseline as needed

### Incident Response

1. **Critical Finding Detected**
   - Stop deployment pipeline
   - Create security incident
   - Notify security team
   - Fix before proceeding

2. **False Positive Identified**
   - Document in security baseline
   - Update exclusion rules
   - Notify team of changes

## 🔗 Additional Resources

- [GitLab Security Documentation](https://docs.gitlab.com/ee/user/application_security/)
- [Probe Scanner Documentation](https://docs.gitlab.com/ee/user/application_security/sast/)
- [Security Best Practices](../SECURITY.md)
- [Pre-commit Hooks Documentation](https://pre-commit.com/)

---

**Need Help?** Contact the security team or create an issue in this repository.
