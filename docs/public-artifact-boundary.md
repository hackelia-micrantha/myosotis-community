# Public artifact and specification boundary

Status: accepted public-repository policy

This repository owns public packaging and community collaboration. It does not own normative Myosotis protocol or SDK truth.

## Current authority

The canonical private Myosotis repository remains authoritative for:

- normative RFCs and protocol requirements;
- normative protocol schemas;
- SDK and reference-runtime implementation;
- detailed security analysis;
- healthcare validation plans;
- internal conformance evidence and source claims data.

This public repository is authoritative only for its own public website, public publication contracts, public claims/provenance projection, contribution process, and public community material.

A merged public issue, pull request, example, diagram, JSON file, or design note does not create a normative protocol requirement.

## Publication stages

### Stage 1 — current public surface

Allowed through normal review:

- website and documentation;
- public threat/design summaries;
- synthetic diagrams/examples;
- public claims/provenance metadata;
- community/governance/validation tooling.

### Stage 2 — separate decision required

The following may become public later, but **must not be introduced without a dedicated boundary decision**:

- sanitized protocol schemas;
- protocol fixtures;
- conformance bundles/results;
- reference clients;
- SDK components;
- richer implementation evidence.

A Stage 2 decision must specify:

- exact artifact and owning canonical source;
- whether the artifact is generated, derived, or independently maintained;
- normative versus non-normative status;
- compatibility/versioning rules;
- synchronization and stale-artifact behavior;
- public test/evidence requirements;
- sanitization review;
- licensing and third-party notices;
- security and healthcare-data constraints.

CI currently reserves top-level implementation/specification surfaces so adding them requires an explicit policy/validator change rather than accidental drift.

### Stage 3 — normative authority transfer

Moving normative protocol/specification authority to a public repository requires a separate organization/repository-governance decision. It is not implied by publishing Stage 2 artifacts.

Such a decision must identify ownership, migration, versioning, compatibility, security review, release authority, and the disposition of the existing canonical private source.

## Sanitization review

Before publishing material derived from private or sensitive sources:

1. identify the canonical source revision and intended public evidence/confidence level;
2. copy only the minimum information required for the public purpose;
3. remove private repository paths, issue/PR metadata, credentials, infrastructure identifiers, operational logs, and exploit-sensitive details;
4. replace healthcare/personal/production data with synthetic data;
5. confirm redistribution rights for third-party, employer, customer, generated, dataset, model, and media material;
6. ensure the result cannot imply stronger production, security, regulatory, or clinical evidence than is actually governed;
7. update the public provenance/claims projection where substantive claims change;
8. run the repository validation and review the final diff as public content.

Do not preserve private Git history when a clean reviewed public artifact is sufficient.

## Proposal/import flow

Public proposals that affect canonical design remain advisory here. An authorized maintainer may distill the safe proposal into the canonical RFC/decision process. Acceptance happens only in the owning canonical process; the public projection is updated afterward from the accepted source revision.

This one-way decision boundary prevents external contributions from accidentally creating a second specification authority.
