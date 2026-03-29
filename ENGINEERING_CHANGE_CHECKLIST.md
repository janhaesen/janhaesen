# Engineering Change Checklist

Use this checklist for every change (feature, bugfix, refactor, infra, docs). Mark each item as:

- `[x]` done
- `[ ]` not done
- `[N/A]` not applicable

---

## 0) Change Summary

- **Title**:
- **Type**: Feature / Bugfix / Refactor / Chore / Security / Performance / Docs
- **Risk level**: Low / Medium / High
- **Problem statement**:
- **What changed**:
- **User impact**:
- **Rollback plan**:

## 1) Requirements and Scope

- [ ] Acceptance criteria are clear and testable
- [ ] Scope is minimal and excludes unrelated changes
- [ ] Edge cases and failure modes are identified
- [ ] Assumptions/dependencies are listed
- [ ] Non-goals are documented

## 2) Design and Architecture

- [ ] Approach and tradeoffs are documented in PR/ADR notes
- [ ] Solution fits existing architecture and conventions
- [ ] Complexity is justified (no premature abstraction)
- [ ] Public interfaces are intentional and stable

## 3) Correctness and Code Quality

- [ ] Code is readable and maintainable
- [ ] Error handling is explicit
- [ ] Logging is useful and not noisy
- [ ] No dead code, debug prints, or untracked TODOs
- [ ] Format/lint/static checks pass

## 4) Testing

### Automated
- [ ] Unit tests cover happy path and edge/error paths
- [ ] Integration tests updated when boundaries are crossed
- [ ] E2E tests updated if user journeys changed
- [ ] Regression test added for bugfixes
- [ ] CI test suite passes

### Manual (if needed)
- [ ] Manual verification steps are documented
- [ ] Cross-platform/environment sanity checks completed

## 5) Backward Compatibility and Versioning

- [ ] Public API compatibility reviewed (source/binary/protocol)
- [ ] Config/env var compatibility reviewed
- [ ] Data/schema/event contract compatibility reviewed
- [ ] Breaking changes and migration path documented
- [ ] Deprecations include timeline and alternatives
- [ ] Version bump follows release/versioning policy

## 6) Data and Migration Safety

- [ ] Data/storage migrations are safe and idempotent
- [ ] Rollback or recovery path exists
- [ ] Large migrations are chunked and monitored
- [ ] Data retention and privacy constraints are respected

## 7) Security and Privacy

- [ ] Threats considered (authz/authn/injection/SSRF/etc.)
- [ ] Inputs validated and outputs encoded where needed
- [ ] No secrets in code, logs, or test artifacts
- [ ] Dependencies checked for known vulnerabilities
- [ ] Least-privilege access maintained

## 8) Performance and Reliability

- [ ] Performance impact is acceptable for expected load
- [ ] Timeouts/retries/backoff behavior is correct
- [ ] Concurrency/idempotency concerns addressed
- [ ] Memory/CPU/network overhead reviewed
- [ ] SLO/SLA impact evaluated

## 9) Observability and Operations

- [ ] Metrics/logs/traces added or updated
- [ ] Alerts/dashboards/runbooks updated when needed
- [ ] Feature flag/kill switch used for risky changes
- [ ] On-call/support notes updated for new failure modes

## 10) Dependencies, Build, and Release

- [ ] New dependencies are necessary and acceptable (license/maintenance)
- [ ] Build and packaging steps pass in CI
- [ ] Changelog/release notes updated
- [ ] Artifacts/provenance/signing requirements met (if applicable)

## 11) Documentation and DX

- [ ] README/docs/examples are updated
- [ ] Upgrade/migration docs are added when needed
- [ ] Internal handoff notes are added for non-trivial changes

## 12) PR Hygiene

- [ ] PR links issue/ticket and explains why/how/risk
- [ ] PR is reasonably scoped and reviewable
- [ ] Screenshots/logs/traces included when useful
- [ ] Self-review completed before requesting review
- [ ] Required reviewers/owners are assigned
- [ ] All required CI checks pass

## 13) Final Merge Gate

- [ ] Tests pass locally and in CI
- [ ] Backward compatibility checks completed
- [ ] Rollout plan confirmed (canary/staged when needed)
- [ ] Rollback path is validated
- [ ] Stakeholders notified for user-visible/high-risk changes

## 14) Post-Merge / Post-Release

- [ ] Deployment verified in target environment(s)
- [ ] Metrics/logs/traces checked after release
- [ ] Error rates and latency are normal
- [ ] Follow-up tasks are filed for deferred work
- [ ] Incidents or surprises are captured in notes

## Optional: Quick Risk Matrix

- **Blast radius**: Low / Medium / High
- **Detectability**: Easy / Moderate / Hard
- **Recovery time**: Fast / Moderate / Slow
- **Mitigation**: Feature flag / Canary / Shadow / Rollback tested / Other

## Optional: Project Commands

Fill these with repo-standard commands:

- Test: `...`
- Lint/format: `...`
- Static analysis/type checks: `...`
- Compatibility checks: `...`
- Security/dependency scan: `...`
- Build/package: `...`
- Smoke tests: `...`

