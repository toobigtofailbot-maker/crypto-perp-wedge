# Validation Matrix

Use the package class to decide the minimum validation evidence.

| Package class | Minimum validation |
|---|---|
| Docs/config-only package | Check changed-file scope, forbidden-path preservation, artifact preservation, dependency-file preservation, and internal consistency of guidance. |
| Research artifact package | Validate artifact family shape, required companion docs, and any package-specific evidence outputs; do not infer execution authority from artifacts. |
| Schema package | Run schema validation plus paired validator/tests and confirm downstream artifact compatibility. |
| Validator package | Run targeted validator tests against current schemas and representative artifacts; confirm no unintended query-layer drift. |
| Query-layer package | Run targeted query checks against current schemas/artifacts and confirm no schema or validator contract drift. |
| Helper/tool package | Run targeted tool tests or dry runs and confirm no protected runtime influence. |
| Shadow/evidence package | Validate committed evidence integrity, zero-override expectations, and advisory-only semantics. |
| PR review package | Inspect changed files directly, confirm objective-to-diff fit, check validation evidence, and scan for forbidden-scope drift. |

If the package needs stronger validation than the table minimum, follow the stricter package brief.
