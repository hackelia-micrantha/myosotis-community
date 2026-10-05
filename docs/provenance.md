# Public provenance and claims

Myosotis publishes a deliberately small, machine-readable projection of canonical design provenance.

The public files are:

- `web/provenance.json` — reviewed source revision, RFC IDs/statuses, page review dates, page claim IDs, and bounded public evidence records;
- `web/claims.json` — approved public claim groups, claim type, evidence confidence, source IDs, limitations, and public surfaces;
- `web/provenance.schema.json` and `web/claims.schema.json` — JSON Schema contracts for those files.

These artifacts are **non-normative**. They do not copy private RFC text, requirement bodies, private issue/PR content, internal repository paths, healthcare data, or exploit-sensitive implementation detail.

## Claim binding

Every public `<section>` carries:

- `data-claim-id` — a stable public ledger identifier;
- `data-claim-confidence` — the evidence confidence asserted by that section.

CI requires every section claim to exist in the ledger and requires the page confidence to match the ledger. It also requires every ledger claim to be referenced by its declared public surface.

The ledger separates:

- claim `type`: `design`, `constraint`, `risk-bounding`, `conformance`, `deployment`, or `clinical`;
- evidence `confidence`: `design`, `conformance`, `deployment`, or `clinical`.

A conformance/deployment/clinical claim requires explicit evidence metadata. Evidence references must resolve to the public evidence registry, carry a level at least as strong as the claim confidence, match the reviewed source revision, and be reviewed no later than the claim. Clinical confidence additionally requires a governed clinical-evidence record; no current public claim has clinical confidence.

## Source synchronization

Public CI deliberately has **no private-core credentials**.

After a canonical review, an authorized reviewer supplies only approved metadata:

```sh
nix develop --command python3 scripts/update_provenance.py \
  --source-revision <40-char-sha> \
  --reviewed-at YYYY-MM-DD \
  --source-status RFC-003=Draft \
  --page-reviewed index.html \
  --page-reviewed whitepaper.html
```

The updater:

1. accepts only a commit SHA, review date, and statuses for RFC IDs already approved in the public source set;
2. updates the site-wide source revision and only the pages explicitly named with `--page-reviewed`;
3. updates a claim review date only when all of that claim's public surfaces were explicitly reviewed;
4. never reads the private repository;
5. refuses to introduce a new RFC ID implicitly.

Adding/removing claims, adding a new RFC source, changing evidence strength, or publishing clinical/deployment evidence remains a reviewed source change, not a synchronization operation.

## Drift behavior

Each page embeds the reviewed source SHA and review date. CI requires those values to match its entry in `provenance.json`.

Therefore, updating the approved source revision without explicitly passing each affected page via `--page-reviewed` makes the site fail validation until that page is reviewed intentionally. Claim IDs and confidence are checked in the same gate.

The deployment smoke also verifies that the provenance and claims JSON are actually published with the site.
