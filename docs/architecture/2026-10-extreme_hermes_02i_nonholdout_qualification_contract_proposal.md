# Extreme Hermes 02I: independent non-holdout qualification contract

**PROPOSAL / NOT LOCKED / NO IMPLEMENTATION AUTHORITY**

WP-EXTREME-HERMES-02I-NONHOLDOUT-QUALIFICATION-CONTRACT-DESIGN-01.
Source-audit base: `b4ff62b99ffcf93a896de85f796d2bf88b87b52b` (2026-10-25).

## 1. Owner decision card

| Class | Decision-relevant statement |
| --- | --- |
| LOCKED FACT | D2-020 retains scientific protocol and Stage 5B gates; D2-021 defines canonical base/feature parent identity; D2-026 assigns durable envelope, holdout and contamination authority to CPW. None makes a source hash a non-holdout permission. [S1–S3] |
| PROPOSED CHOICE | Extend the existing CPW scientific-authority boundary with a narrowly scoped, human-designated partition attestation and deterministic verifier. Require an immutable, physically bounded non-holdout object before any candidate data open. Reuse existing identity and Governor semantics; create no second authority store. |
| NEEDS KARL DECISION | Accept, alter or reject that authority/custody model: Karl alone designates, revokes or replaces partitions; a specifically designated CPW custodian attests physical provenance independently of the requesting agent/operator; CPW verifies exact bindings and current durable state. This proposal appoints nobody and designates no interval. |
| LATER ONLY | Approve actual partitions, custodian identity and evidence, scientific protocol and access scope in a separate bounded WP; explicitly authorize protected implementation and physical proof. Real envelopes, searches and Stage 5B activation retain their separate gates. Merging this proposal grants none of these permissions. |

**Recommendation:** one CPW verifier using a Karl-controlled partition designation
and independently attested physical subset, with authority status in the existing
D2-026 store. Its output is evidence for a future native admission check, never a
SearchContract, scientific approval or pipeline dispatch. This is a proposed
contract, not a new D2 decision, operational certificate or current authority.

The tradeoff is deliberate: physically separating the allowed subset and retaining
custody evidence costs preparation and storage, but permits refusal before reading
a mixed history file. An envelope-only check is smaller but lacks physical
partition provenance. A signed external attestation alone proves an issuer's
claim, not current CPW revocation or contamination state. A general certificate
service or shadow database would duplicate existing ownership. Neither Hermes,
Research Memory, Prefect, operator prose, an 02H proposal nor an 02G packet may
designate a partition or become an independent authority.

## 2. Inspected facts and reuse assessment

All source references below bind to the audit base above. Repository files and
declarations were inspected; no raw data, real envelope or database was opened.

| Ref | Native source and observed boundary |
| --- | --- |
| S1 | [D2-020](2026-10-bounded_autonomous_research_v2_architecture.md), sections “Bounded research envelope”, “Final holdout and adaptive research”, “Permanent human gates”: construction, WFO/OOS and isolated final holdout remain separate; informative escape consumes holdout across influenced lineage. A new campaign/session cannot reset it. |
| S2 | [D2-021](../decisions.md), “Five-Timeframe Canonical Base and Feature Parent Identity”; [canonical derived lineage](../data/2026-10-binance_usdtm_30m_1h_derived_catalog_and_slice_identity.md); [FT-02](../status_entries/WP-FT-02-FIVE-TIMEFRAME-TAKER-FEATURE-GENERALIZATION-01.md): 15m D4; 30m/1h/4h exact D4-derived bases; direct canonical 1d. Feature parent equals execution base, row-local taker values and exact timestamp joins, available at exclusive completed-bar close. [Catalog](../data_catalog.md) pointers describe identity, not partition permission. |
| S3 | [D2-026](2026-10-v2_autonomy_kernel_durable_authority.md), sections 4–11, 13, 15, 17; current [models](../../tools/research_autonomy/models.py), [envelope](../../tools/research_autonomy/envelope.py), [store](../../tools/research_autonomy/store.py), [builder](../../tools/research_autonomy/contract_builder.py): immutable Karl envelope, controlled revocation/replacement, durable campaign/domain/holdout state and audit lineage. Kernel is implemented; older lock text describing a future implementation is historical sequencing, not evidence of absence. |
| S4 | [02E](../../tools/hermes/data_evidence_resolution.py), `inspect_local`, `_local`; [02F](../../tools/hermes/queue_input_preparation.py), `_evaluate`, `_derived_bytes`: technical hashes, whole-file validation, parent rederivation and external workspace preparation. These may physically read sources; they do not independently certify a partition. |
| S5 | [02G](../../tools/hermes/verified_data_signal_bridge.py), `_fixture_parent`, `_compile`: fixed synthetic corpus recognition is stronger than a label, but historical admission remains `NOT_READY_NON_HOLDOUT_WINDOW_UNVERIFIED`. Compilation follows technical checks and synthetic-only designation; upstream replay can already read files. This is not a safe historical read gate. |
| S6 | [02H](../../tools/hermes/scientific_protocol_preflight.py), `_read_metadata`, `review`; [merged status](../status_entries/WP-EXTREME-HERMES-02H-SCIENTIFIC-PROTOCOL-PREFLIGHT-01.md): metadata-only operator path checks self-declared hashes/proposed structure. Separate controlled fixture replay proves software. Science stays `NOT_READY`, SearchContract `NOT_ISSUABLE`. |
| S7 | [feature resolver](../../tools/data/research_feature_table.py), `resolve_research_feature_table`, `_validate_taker_values`; [native runner inputs](../../tools/research_runner/run_offline_sweep.py), `_load_ohlcv_input`, `_canonical_1d_execution_input`; [compiler](../../tools/research_runner/spec_signal_compiler.py), `compile_signal`: existing identity/feature semantics to retain, not permission to load an unqualified parent or launch a runner. |
| S8 | [Governor](../../tools/research_search/governor.py), `data_reference`: rejects `final_holdout`; [lab readiness](../../tools/lab_readiness/readiness.py), `build_readiness_projection`: read-only display, no acquisition or execution authority. Neither is an independent physical partition certifier. |
| S9 | [02G tests](../../tests/test_hermes_verified_data_signal_bridge.py), `test_designation_refusal_before_compiler`, `test_fixture_label_requires_actual_fixed_values`; [02H tests](../../tests/test_hermes_scientific_protocol_preflight.py), `test_unknown_history_never_opens_sources_or_calls_native`: relevant existing refusal/tripwire patterns, inspected but not executed in this T0 WP. |

**Inference:** these inspected declarations supply reusable identity, metadata,
durable state and refusal primitives, but no equivalent independent positive
non-holdout contract was found. A complete historical hash cannot answer whether
using those bytes is permitted. Physical FT-02 provenance is not a holdout-safety
attestation. No 02B–02H adapter needs duplicating or weakening.

## 3. Minimum proposed binding

One exact candidate object/window per request; no discovery, inferred dates or
unbounded directory inventory. The following are semantic requirements for later
design, not a schema created here. Unknown or conflicting fields fail closed.

| Binding group | Required evidence | Native versus missing |
| --- | --- | --- |
| Request | Request digest; venue, market, instrument; one primary timeframe from `15m`, `30m`, `1h`, `4h`, `1d`; intended consumer and purpose; UTC `[start,end)` bar-open grid, cadence and exclusive completed-bar availability; separate evaluation and warmup dependency intervals. | Native timeframe/timestamp semantics exist. Exact partition request binding is missing. |
| Canonical identity | Data version; exact D4/direct-1d slice identity; immutable catalog, validation and derivation report hashes; full canonical parent identity; bounded subset object digest, byte length, row count, coverage, encoding and column projection; extraction/derivation recipe version and evidence. | Native full-source identities exist [S2/S7]. A subset digest is distinct from its full-parent digest; independently established subset-to-parent proof is missing. |
| Features and dependencies | Feature manifest/table/source-set hashes, exact execution-base parent, full transitive input ancestry; transform code/version; lookback and availability bounds, joins and any fitting/normalization/label horizon. Funding or auxiliary inputs, if requested, require their own bounded bindings. | FT-02 row-local semantics exist. Permission for each physical dependency and leakage proof are missing. No future or undeclared source may be inferred safe. |
| Repository/evidence | Exact verifier/consumer code commit (40 hex Git SHA), repo identity, metadata artifact paths and SHA-256 digests, protocol identity/version/hash and attestation content digest. | Existing evidence bindings check commit and bytes [S3]. Reuse their semantics, not their metadata-only file reader for raw data. Any later HEAD change requires revalidation and explicit rebinding. |
| Independent designation | Immutable designation ID/version/hash, Karl approval reference and control state; custodian identity, designation scope, physical-object attestation ID/version/hash, issuer authentication bound to that content, issuance and validity bounds; classification limited to construction/development or WFO/OOS validation as explicitly permitted. | New proposed evidence. A self-supplied signer/key/hash or role label is insufficient. CPW must resolve the issuer against Karl-controlled trust configuration. Final holdout and unknown classification are refused. |
| Durable context | Envelope ID/version/hash; campaign, search/parent if applicable, contamination-domain and holdout IDs; authority lineage version/hash; partition-control revision and attestation revocation revision; exact requested scope. | Envelope/campaign/holdout snapshots exist [S3]. Partition designation, physical interval mapping and attestation/control revisions do not. An absent search is not permission to create one. |

The independent custodian must supply provenance establishing both exact canonical
membership and absence of protected bytes/dependencies in the whole physical
object. Merely signing an operator hash does neither. Karl retains material
scientific policy; the custodian attests within that policy and cannot enlarge it.
No numeric purge, embargo, warmup or confidence threshold is invented here.
The attestation must also bind the trusted storage root, immutable snapshot/object
ID and version, and expected filesystem object identity where applicable. An
authenticated storage/custody binding must establish that identity before any
content read; a pathname plus expected digest cannot prevent first-read exposure.

## 4. Proposed safe read sequence

1. **Metadata admission only.** Receive bounded, standalone metadata with no raw
   values. Resolve exact committed metadata and authenticated custodian designation
   through CPW-controlled trust. Do not run 02E/02F/02G replay, hash/stat through an
   untrusted data path, inspect file headers, scan directories, or call a compiler.
   Missing physical custody evidence is a refusal, not a reason to open the file
   to discover whether it is safe. Logs/errors expose only bounded identifiers and
   refusal codes, never source contents, row samples or protected locations.
2. **Authority anchor.** In the CPW-owned boundary, verify active immutable
   envelope/control, exact campaign/domain/holdout identity, audit lineage and
   designation/attestation revisions. Check the exact permitted intervals against
   protected interval mappings and applicable ancestry, including cross-campaign
   reuse in the contamination domain. Current opaque holdout IDs alone do not map
   time intervals [S3]; supplying that independently governed mapping is a later
   prerequisite. No missing mapping or missing contamination edge implies safety.
3. **Prove physical containment before open.** The attestation must bind a sealed
   object whose entire contents and all parser-readable metadata are non-holdout.
   A mixed CSV/Parquet plus row filter is refused, even if the requested rows are
   outside holdout: hashing, headers, read-ahead and decoder metadata may expose
   other rows. Provisioning/extracting such an object is separately authorized
   custodian work, never a fallback in this verifier. If custody cannot establish
   the exact subset without a new protected read, stop for that future authority.
4. **Pin identity and permitted read.** Only after steps 1–3 may a later approved
   implementation resolve/open the attested object. Require an allowlisted local
   storage root and exact ordinary file; deny absolute/drive/UNC/device paths,
   traversal, alternate streams, symlinks, junctions/reparse points, mount redirects
   and hardlinks (`nlink != 1`), including ancestor components. Pin root/directory
   and file identities against the attested storage identity with
   platform-appropriate handles; deny unsupported
   guarantees. Use an immutable storage snapshot or enforced exclusive custody
   through the read, not path checks plus a later reopen. A before/after digest
   cannot undo exposure to substituted bytes. Read-only permissions alone do not
   prove immutability. No network fetch, mmap of a mixed parent, automatic source
   repair or global corpus fallback is allowed.
5. **Validate only the pinned permitted bytes.** Recompute digest/length/grid and
   native semantics on the sealed object; compare to the independently bound
   expected values. Verify derived 30m/1h/4h membership against exact D4 ancestry
   without opening an uncertified full 15m parent. For 1d retain direct canonical
   ancestry. Reject incomplete aggregate bars, gaps, duplicates, unaligned bounds
   and any request that truncates or extends the designated scope. Validate exact
   feature parent/join and exclusive-close availability; never replace native
   canonical identity with a convenient slice hash.
6. **Guard information dependencies.** Warmup, trailing inputs, resampling children,
   confirmation timeframes and auxiliary series must all lie within separately
   designated non-holdout scope. Adjacent `[a,b)`/`[b,c)` windows share no bar open,
   but can still leak through lookback, labels, fitted transforms or future bars.
   Apply the approved protocol to effective dependency intervals, including its
   purge/embargo and label horizons, before open. Reject unknown horizons, global
   fitting and forward/backfill; retain FT-02 row-local/exact-join restrictions.
   A consumed holdout cannot be relabeled development to regain permission.
7. **Recheck before release and use.** Bind the result to the same pinned object,
   exact request/code/manifest, and durable revisions. A future CPW native consumer
   must revalidate control/lineage at its admission point; it cannot take an old
   receipt or boolean as permission. No compiler/model/agent receives bytes or
   a reusable path until its separately authorized admission succeeds. No 02I
   implementation may silently route around 02G's current denial.

**Post-anchor races:** a future admission must serialize relevant revocation,
holdout/contamination and partition changes with the permitted read/use, using
the existing CPW authority transaction discipline plus pinned immutable storage.
The later implementation must define and prove the linearization point and
revocation behavior through consumer handoff; an expired snapshot or check then
unlock then read is insufficient. A revision change before admission aborts;
revocation prevents new reads/use, invalidates unreleased evidence and cannot
unread information already exposed. Discovered exposure stops work and follows
existing contamination handling under separate authority, never a freshness reset.
This WP performs no such transaction, lease, exposure record or state change.

## 5. Durable checks, outcomes and non-authority

The later verifier must reject absent/unreachable authority, missing or inactive
envelope/campaign, audit-chain conflict, mismatched domain/holdout, consumed or
contaminated applicable state, expired/revoked/replaced designation or attestation,
stale code/manifest, ambiguous overlaps, insufficient provenance and mutation.
Cached Research Memory, Prefect history, `.cpw/active`, an old receipt or a renamed
campaign cannot substitute for a current check. Conservative domain denial in
`construct_contract` is retained; this proposal creates no isolation exemption.

`ResearchAuthorityStore.load_snapshot` validates lineage but uses a transactional
lock and does not itself verify partition geography, current attestation control
or all envelope checks. It is a reuse seam, not an existing read-only certification
API. `open_search` is a writer and must not be called to obtain qualification.
`verify_evidence` verifies committed metadata, not non-holdout status. [S3]

| Term | Meaning and limit |
| --- | --- |
| `NOT_VERIFIED` | Independent partition/custody proof is absent, stale, ambiguous or refused. No data open, compiler call or admission. A metadata dossier can remain structurally valid. |
| `NOT_READY` | Scientific dependencies are unresolved, irrespective of technical identity or proposed partition evidence. Preserve all original ideas, ordering, critic/memory/queue context and blockers. |
| Proposed qualified evidence | Later-only, scoped evidence that independently designated physical bytes match their permitted binding at an exact authority revision. No public positive status or certificate is introduced here; no automatic pipeline admission follows. |
| Future native acceptance | Separately approved consumer checks exact spec/data/protocol, current partition and durable authority, human gates and all scientific requirements. This proposal cannot supply it. |

“Bytes match” and “permission to use these bytes for non-holdout science” are
separate claims. Even future partition qualification would leave genuine
preregistration, scientific adequacy/leakage review, fixed domains, costs/funding,
WFO/OOS, multiple-testing/DSR, cumulative trial lineage, budgets, valid envelope
and SearchContract unresolved as applicable. Keep 02B–02H blockers; no scientific
promotion, canonical payload write, experiment, scheduler, trading or capital
authority arises from any dossier or from merging this document.

## 6. Threat and acceptance matrix for a later WP

These are required future cases, not executed proofs or certificates in 02I.
Negative read tests must tripwire all data opens, hashing, dataframe readers,
compiler/model/runner calls, logging and exception serialization. Supply protected
sentinel files and prove they are never opened or echoed, including parser error
and recovery paths. Use synthetic values only until physical proof is separately
authorized.

| Case | Required result/evidence |
| --- | --- |
| Fixed synthetic positive | Controlled creator, independent test custody/designation fixture, exact sealed object, metadata and authority revisions; deterministic bounded validation. Existing 02G/02H synthetic replay remains software evidence only. No history or science permission. |
| Unknown history, even with convincing 02H proposal | `NOT_VERIFIED`, zero candidate/parent/feature opens and zero compiler calls; retain all ideas and scientific `NOT_READY`. |
| Falsified fixture/non-holdout label; operator hash; catalog-only claim; self-appointed issuer or missing owner | Refuse before data open. Recomputed/signed hash consistency cannot establish authorized issuer or partition provenance. |
| Cross-campaign holdout reuse; consumed domain; absent ancestry edge | Refuse; rename/new campaign cannot restore freshness or demonstrate isolation. |
| Unsupported/out-of-scope timeframe, venue, purpose or version | Refuse; five native timeframes are not blanket permission for each route. |
| Stale HEAD/manifest or changed object after anchor | Refuse on exact binding/revision mismatch. Concurrent replacement/in-place writes must be prevented through use, not merely detected afterward. |
| Wrong canonical parent, diagnostic direct 30m/1h source, wrong feature parent | Refuse, preserving D2-021; no tolerance, source switching or subset hash impersonating a full-parent identity. |
| Partial aggregate, overlapping intervals, hidden warmup outside scope, adjacent-window leakage | Refuse before open from metadata dependency proof; later permitted-byte checks also reject incomplete grids. No automatic narrowing to a surviving window. |
| Future-derived feature, global normalization, forward labels, missing availability horizon | Refuse; require exact transitive dependencies and approved protocol, not feature-name availability. |
| Traversal, ancestor junction/reparse point, hardlink, symlink, redirect or path-swap race | Refuse without protected reads; exercise platform-specific handle and immutable-storage guarantees. |
| Missing/revoked attestation, unavailable store, stale control, concurrent contamination/revocation | Refuse or abort before new reads/use; invalidate result, no offline/cached positive fallback. Crash/retry cannot reset authority. |
| Mixed parent opened to hash/extract; feature parser reloads full corpus; compiler called before admission | Fail the test even if final result says refused. Admission must precede every dependency read and every downstream call. |
| Later physical non-holdout positive | Separate Karl-authorized bounded custody/proof WP only: exact designated subset and ancestry, immutable storage, current DB/control evidence, native byte/grid/feature parity and no holdout reads. Still no science run or Stage 5B activation by implication. |

## 7. Smallest implementation seam, cost and prerequisites

**Future option, not authority:** implement one deterministic CPW-owned verifier
alongside `tools/research_autonomy`, reusing `envelope.py` validation/hashes,
`models.py` exact bindings and `store.py` transaction/audit ownership. Extend that
same logical authority database only if the approved design needs designation,
revocation and physical interval records. Do not repurpose Research Memory or
build a parallel ledger. Reuse Governor final-holdout denial and the native data
semantics after admission, without widening their meaning.

Likely future explicit authorization surfaces are autonomy models/store/builder
and its SQL migrations/write-role grants; applicable envelope/request/evidence
schemas and validators; physical subset custody and trusted issuer provisioning;
Hermes 02E/02F/02G entry/caller paths; native feature/runner input loaders and
their tests if they must consume bounded objects without reloading full parents.
No existing full-file validator may be advertised as subset-safe. If preserving
D2-021 identity requires a new subset-to-parent proof contract, approve it
explicitly before implementing it; do not silently change a native validator to
accept a truncated canonical file. Pure compiler semantics should be reusable.

Start with synthetic authority and storage fixtures proving pre-open denial and
race handling, then the separately approved physical subset proof; integrate a
native consumer only under explicit authorization. Do not migrate 02B–02H packet
formats or relax their current refusals merely to show a positive result.
Operational prerequisites: designated custodian/issuer trust, complete protected
interval and ancestry metadata, bounded immutable objects, supported filesystem
handle guarantees, available separate CPW authority DB and explicit access scope.
Failure to provision them leaves `NOT_VERIFIED`.

Cost is a narrow verifier plus controlled authority-record/consumer changes and
custody evidence, not a framework. The expensive part is proving physical
containment and preventing stale-authority races across reads. Later production
schema/contract changes are at least T2; protected authority writers/crossings
require T3 and its full-release/exact-head requirements. Required tests include
the matrix above, current 02B–02H regressions, affected native data/feature and
autonomy/Governor suites, relevant validators/integrity checks, concurrency and
crash/replay, plus explicitly authorized physical DB/storage proof. This T0
proposal supplies none of that implementation evidence.

## 8. Decision and execution limits

**Only material decision now:** Karl's acceptance, alteration or rejection of the
recommended CPW/Karl/custodian authority model in section 1 after Side 23's
exact-head review. Custodian appointment, actual partition dates, protocol
parameters and physical access are later approval inputs, not Codex discretion
and not permissions hidden in this decision. No real partition can be qualified
until those inputs and separately authorized software/proof exist.

02I changes this document alone. Proportionate verification is source/contradiction
review, path/link existence, exact changed-file/forbidden-scope check, semantic
non-authority audit, `git diff --check` and normal hosted smoke. Full pytest:
**NOT RUN - T0 docs/process policy; not used as merge evidence**. No database,
raw history, holdout, native replay, compiler, model, runner or scientific
experiment was invoked. No protected file, policy, schema or query behavior is
changed. The PR is to remain unmerged for Side 23 and Karl; publication or merge
alone cannot activate a positive certification path, scientific permission or
Stage 5B.
