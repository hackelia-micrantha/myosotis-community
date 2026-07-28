# Public Publication Policy

Myosotis Community publishes conservative summaries of private canonical design work. Public content is informative and reviewable, but it is not itself the normative protocol or SDK specification.

## Scope

This policy applies to:

- website pages;
- design and whitepaper summaries;
- threat-model summaries;
- diagrams;
- sanitized examples;
- release notes and public project-status statements.

## Required provenance

Every substantive public artifact should record:

```yaml
project: Myosotis
source_repository: hackelia-micrantha/myosotis
source_revision: commit-sha
source_rfcs:
  - number: RFC-NNN
    status: Draft | Proposed | Accepted | Implemented
publication_status: provisional | reviewed | evidence-backed
reviewed_at: YYYY-MM-DD
```

A site-wide provenance manifest may cover multiple pages when they are reviewed from the same source revision. Page-specific overrides should be used when sources differ.

## Draft-derived publication

Public content may derive from Draft or Proposed RFCs to support early review. Such content must:

- identify itself as provisional design material;
- state that requirements may change;
- avoid production, performance, regulatory, or clinical efficacy claims;
- distinguish normative design language from exploratory examples;
- be reviewed when source RFCs change materially.

## Claim confidence

Public claims must not imply a stronger evidence level than is available.

| Confidence | Meaning |
|---|---|
| `design` | Specified or intended, but not demonstrated by an implementation. |
| `conformance` | Demonstrated by deterministic protocol or SDK tests. |
| `deployment` | Observed in a defined non-clinical deployment. |
| `clinical` | Supported by an appropriately governed clinical evidence process. |

Most current Myosotis public material is `design` confidence.

## Healthcare claim discipline

Healthcare is the primary use case, but current public material must not claim:

- diagnostic or treatment capability;
- replacement of clinical judgment;
- safety or efficacy outcomes;
- HIPAA, PIPEDA, medical-device, or other regulatory compliance as a completed fact;
- production handling of patient data;
- approval by a healthcare organization or regulator.

Allowed language describes design constraints, intended workflows, threat boundaries, and validation plans.

## Public/private boundary

The private `hackelia-micrantha/myosotis` repository is canonical for:

- RFCs and normative schemas;
- protocol and SDK implementation;
- internal threat analysis;
- healthcare validation plans;
- conformance evidence and claims-ledger source data.

This public repository is canonical only for the public website and community-facing publication artifacts.

## Review checklist

Before publication or material revision:

- [ ] Project naming is consistently `Myosotis`.
- [ ] Source revision and RFC statuses are recorded.
- [ ] Claims do not exceed their evidence level.
- [ ] Healthcare examples use synthetic or non-production framing.
- [ ] No private repository paths, secrets, patient data, or exploit-sensitive detail are exposed.
- [ ] Security invariants match the source RFCs.
- [ ] Links, HTML, accessibility, and deployment checks pass.
- [ ] Security and privacy contacts are current.
