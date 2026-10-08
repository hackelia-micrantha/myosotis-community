# Public site validation

The Myosotis community site remains a build-free static asset site, but validation is executable and reproducible.

## Toolchain authority

- `flake.nix` / `flake.lock` own the CI and local validation tools.
- `web/` remains the deployment asset directory.
- `web/_headers` owns static response security headers.
- `.github/workflows/site-validation.yml` is the required validation workflow.
- Cloudflare's existing Git integration remains the deployment authority; validation has no deployment credentials.

## Local validation

Run:

```sh
nix flake check
nix develop --command python3 scripts/validate_site.py
nix develop --command python3 scripts/validate_provenance.py
nix develop --command python3 scripts/validate_governance.py
nix develop --command python3 scripts/test_provenance_contract.py
nix develop --command python3 scripts/validate_governance.py
nix develop --command python3 scripts/test_governance.py
nix develop --command sh -ceu 'for file in web/*.html; do tidy -q -errors --show-warnings no "$file" >/dev/null; done'
nix develop --command lychee --no-progress --max-retries 3 --accept 200,204,206,429 'web/**/*.html' 'README.md' 'docs/**/*.md'
```

For browser validation:

```sh
nix develop --command python3 -m http.server 4173 --directory web &
nix develop --command python3 scripts/browser_smoke.py http://127.0.0.1:4173/
```

The browser smoke covers desktop and 320px mobile reflow, the skip-link keyboard path, visible focus, reduced-motion preference exposure, primary landmarks/headings, and browser console errors.

## Security checks

CI also runs Gitleaks against repository history and validates:

- no obsolete Myosotis spellings;
- no private canonical repository URL in deployed web content;
- unexpired `security.txt`;
- local asset/fragment integrity;
- the declared control-site presentation and local-only asset boundary;
- WCAG AA contrast for the control palette's primary text, muted text, and accent tokens;
- parseable HTML/CSS and root Wrangler asset configuration;
- read-only workflow permission and immutable third-party action pins;
- static security-header policy;
- JSON Schema conformance for public provenance and claims;
- exact page-to-manifest source revision/review metadata;
- complete section-to-claim bindings and evidence-confidence agreement;
- public RFC ID/status integrity and evidence-level restrictions;
- evidence-registry referential integrity, evidence/source revision alignment, and review chronology;
- required contribution/licensing/governance artifacts and issue/PR review fields;
- fail-closed reserved top-level protocol/SDK/schema/conformance surfaces unless an explicit boundary decision changes the policy.

The deployed header policy is intentionally strict because the site has no scripts or remote font dependency. HSTS is scoped to the Myosotis host only; it does not set `includeSubDomains` or request preload.

## Production smoke

After a push to `main`, CI separately validates deployment health and public-host routing:

- **Production Worker source:** `https://myosotis-community.ryan78j.workers.dev/` must return the home, design summary, threat model, stylesheet, provenance/claims JSON + schemas, and security.txt over HTTPS. Deployed HTML/CSS must match the checked-out exact `main` source. Expected page markers, CSP, referrer policy, nosniff, permissions policy, and HSTS are checked.
- **Custom hostname probe:** `https://myosotis.micrantha.com/` may return validated site content (`CONTENT_OK`) or a Cloudflare-managed HTTP 403 with `CF-Mitigated: challenge` (`WAF_CHALLENGED`). The latter is recorded explicitly as **not verified for normal visitors**, but does not invalidate the independently verified Worker deployment. Any other HTTP errors or unexpected content fail the job.
- Cloudflare's zone-wide Bot Fight Mode can challenge headless GitHub Actions traffic and cannot be bypassed using a WAF Skip rule. Do not disable protection globally or assert browser accessibility solely because the Worker-native check passes. Human/private-browser review is tracked separately in #18.

This separates deployment validity from zone security handling without adding deployment credentials. Public claim/source binding is defined by `web/provenance.json` and `web/claims.json`; see `docs/provenance.md`. Cloudflare deployment identity remains external to GitHub CI.


## Presentation A/B branches

The production control on `main` intentionally uses the pre-Phyllotaxis presentation while retaining later accessibility, provenance, and security controls.

The Phyllotaxis B treatment is preserved on `ab/phyllotaxis-b`. Preview/deployment systems may use that branch for visual comparison without adding runtime experiment logic to the public site.
