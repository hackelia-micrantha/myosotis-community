# Myosotis Community

> Public design material for healthcare-first, governed mobile capabilities for agentic systems.

Myosotis develops specifications, protocols, and mobile SDKs for exposing narrow device capabilities to agentic systems while preserving device-local policy enforcement, explicit operator consent, attributable execution, and deterministic failure behavior.

Healthcare is the primary use case, especially bedside and clinical field workflows. Public material may discuss other regulated field environments, but healthcare-derived security, privacy, human-factors, and reliability constraints remain the baseline.

## Repository purpose

This public repository contains:

- the Myosotis public website;
- conservative design summaries;
- a public threat-model summary;
- sanitized diagrams and examples;
- community, contribution, and publication-governance material.

It is **not** the canonical source for normative specifications or the SDK implementation. Public artifacts explain the design but do not create new protocol requirements.

## Current maturity

Myosotis is currently a draft specification and early implementation effort. The published site describes design intent and constraints. It does not claim:

- production validation;
- clinical efficacy;
- regulatory approval;
- runtime performance guarantees;
- a complete or released SDK.

## Website

The static website lives in [`web/`](web/) and is deployed as a build-free Cloudflare Worker asset site.

Deployment configuration is defined by the repository-root [`wrangler.jsonc`](wrangler.jsonc), with `./web` as the asset directory.

## Publication provenance

Public summaries must identify:

- the source revision used;
- the RFC numbers and statuses represented;
- whether a statement is design intent, conformance evidence, deployment evidence, or clinical evidence;
- known omissions or unresolved decisions.

See [`docs/publication-policy.md`](docs/publication-policy.md) and [`docs/provenance.md`](docs/provenance.md). The deployed site publishes [`web/provenance.json`](web/provenance.json) and [`web/claims.json`](web/claims.json) as the machine-readable public projection.

## Security

See [`SECURITY.md`](SECURITY.md) or report privately to `security.myosotis@micrantha.com`.

The deployed site publishes `/.well-known/security.txt` from [`web/.well-known/security.txt`](web/.well-known/security.txt).

## Contributing and licensing

Public contributions are welcome within the documented public/private boundary. See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/public-artifact-boundary.md`](docs/public-artifact-boundary.md), and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

First-party material in this public repository is licensed under Apache-2.0 unless explicitly marked otherwise; see [`LICENSING.md`](LICENSING.md). No CLA is required. External contributions use DCO-style commit sign-off.

Publishing protocol schemas, conformance artifacts, SDK/reference code, or transferring normative specification authority requires a separate explicit boundary decision; ordinary public issues/PRs cannot create normative Myosotis requirements.

## Contact

- General: `myosotis@micrantha.com`
- Security: `security.myosotis@micrantha.com`


## Contributing and licensing

Public contributions are welcome within the repository's deliberately non-normative boundary. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/public-artifact-boundary.md`](docs/public-artifact-boundary.md).

Current first-party public material is Apache-2.0. Future SDK/reference implementation source is not currently published; if that boundary is explicitly enabled, its default is MPL-2.0 unless an existing reviewed source license applies. See [`LICENSING.md`](LICENSING.md).
