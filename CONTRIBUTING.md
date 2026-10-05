# Contributing to Myosotis Community

Myosotis Community is the public website, design-summary, community-review, and publication-governance surface for Myosotis. It is **not** the normative protocol repository and is not the canonical SDK implementation.

Contributions are welcome when they improve the public surface without importing private authority, private implementation, sensitive evidence, or healthcare data.

## What can be contributed now

Ordinary contribution flow accepts:

- website defects, accessibility, responsive behavior, and public UX improvements;
- copy and documentation corrections;
- public diagrams and synthetic examples that contain no private design content;
- public threat-summary corrections that do not disclose exploit-sensitive detail;
- community, governance, validation, and publication-process improvements.

Small unambiguous documentation fixes may go directly to a pull request. Material public-claim changes should start with an issue.

## What requires explicit publication review

Do not add these through ordinary contribution flow:

- protocol schemas or fixtures;
- SDK or reference-client code;
- conformance artifacts or implementation evidence;
- detailed threat/security analysis;
- healthcare workflow artifacts beyond already-approved synthetic summaries;
- material derived from private Myosotis repositories;
- generated material whose provenance or redistribution rights are unclear.

A proposal may discuss these categories publicly at a safe level, but publication of an artifact requires the process in `docs/public-artifact-boundary.md`.

## What must never be published here

Do not submit:

- credentials, secrets, private keys, tokens, or production configuration;
- private RFC text, private issue/PR content, private source, private tests, or private repository history;
- patient data, protected health information, production healthcare records, or realistic data copied from a real person;
- vulnerability details before coordinated disclosure;
- internal infrastructure identifiers or operational evidence not approved for publication;
- employer, customer, school, or contract material you do not have the right to redistribute.

Use synthetic examples. If a security report cannot safely be public, follow `SECURITY.md`.

## Public proposal to canonical decision

A public pull request or issue can propose a protocol/design change, but it cannot create a normative Myosotis requirement.

The flow is:

1. the public issue/PR records the externally reviewable problem, constraints, alternatives, and safe evidence;
2. maintainers classify the proposal as public-documentation-only or canonical-design-impacting;
3. when canonical design is affected, an authorized maintainer distills the public proposal into the canonical private RFC/decision process without copying material that lacks redistribution rights;
4. the canonical decision is made by the owning repository/decision authority;
5. only after that decision may the public projection be refreshed through its provenance/claims workflow.

Until step 4 is complete, public proposal text remains non-normative regardless of review or merge status.

## Provenance and rights

Every contribution must identify material that is:

- copied, adapted, translated, or generated from another source;
- derived from private Myosotis work;
- subject to employer, customer, school, or contract ownership;
- materially produced with an AI system;
- governed by a third-party license, dataset, model, or media right.

Do not submit material when ownership or redistribution rights are uncertain.

Changes to substantive public claims must preserve the source-revision, claim-ID, evidence-confidence, and review-date contracts in `docs/provenance.md` and `docs/publication-policy.md`.

## Healthcare and security review

Healthcare-first does not mean clinical validation. Public contributions must not imply diagnostic efficacy, treatment capability, regulatory approval, completed HIPAA/PIPEDA compliance, production patient-data handling, or replacement of clinical judgment without separately governed evidence.

Security-sensitive changes should state trust-boundary effects, failure behavior, and whether the change alters any public security claim. Exploit-sensitive or private-system details belong in the private reporting path, not a public PR.

## Licensing and contributor sign-off

Repository licensing is defined in `LICENSING.md`. Current first-party public material is Apache-2.0 unless explicitly marked otherwise. Future explicitly approved SDK/reference implementation source defaults to MPL-2.0 unless an existing reviewed source license applies.

No CLA or DCO sign-off is currently required. By intentionally submitting a contribution for inclusion, you represent that you have the right to submit the material and agree that accepted material may be distributed under the applicable outbound license for the target artifact class.

## Pull requests

Pull requests should state:

- outcome and linked issue when material;
- whether the change is public-documentation-only or could affect canonical design;
- provenance/source and evidence-confidence impact;
- privacy, healthcare, and security impact;
- compatibility impact;
- third-party/generated-material disclosures;
- validation performed;
- intentionally excluded follow-up.

The pull-request template captures these fields.

## Conduct

Participation is governed by `CODE_OF_CONDUCT.md`.
