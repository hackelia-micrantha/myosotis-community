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

See [`docs/publication-policy.md`](docs/publication-policy.md).

## Security

See [`SECURITY.md`](SECURITY.md) or report privately to `security.myosotis@micrantha.com`.

The deployed site publishes `/.well-known/security.txt` from [`web/.well-known/security.txt`](web/.well-known/security.txt).

## Contact

- General: `myosotis@micrantha.com`
- Security: `security.myosotis@micrantha.com`
