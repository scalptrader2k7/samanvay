# Samanvay judge demo script

Target length: 6â€“8 minutes. Use workspace `public-demo` or the isolated Phase 13 workspace. Use the local owner token only when recording decisions.

## 1 Problem and boundary

Open Quality dashboard. Explain that organizations use inconsistent procurement and material descriptions. Samanvay preserves each original record and proposes traceable harmonization for review. State immediately that the data is public surrogate text, IDs are prototype Samanvay IDs, human accuracy validation is pending, and there is no live ERP writeback.

## 2 Trace a real candidate

Open Materials and search `M000753`. Open candidates and select `M000925`.

Show:

- both NTPC source IDs and original pipe descriptions;
- bounded lexical retrieval rank and score;
- the separate `near duplicate` rule proposal;
- supported ASTM A312 and dimension evidence;
- unknown values, which are not treated as agreement.

Say: â€œRetrieval proposes this pair. The pair rules explain it. A reviewer still decides.â€

## 3 Show the safety boundary

Use the prepared evidence file `reports/phase13/critical_conflict.json` for `M000830` and `M000834`. Show the 150 mmÂ² versus 240 mmÂ² cable conflict and the identity-merge block. This proves wording similarity cannot override a supported critical conflict.

## 4 Record and trace a decision

Return to the pipe pair, enter a concrete reason, and approve identity. Open Registry. Show the `SMV-P-*` prototype ID, readable description, technical evidence and mappings to M000753 and M000925. State that it is workspace-scoped and proposed, not an official national code.

Open Review, reconsider to defer, then approve again. Open Governance. Show three linked decisions, server-derived actor, reasons, before/after mapping state and audit history. Explain that source records are immutable.

## 5 Reconcile quality and export

Open Quality dashboard. Point to loaded records, two active mappings, unresolved records, completeness and review state. Explain that these are persisted counts and rule outputs. Download the quality workbook and note that financial metrics are unavailable because transaction and price data are absent.

## 6 Show the integration boundary

Open Integration and choose CPSE/SAP-shaped. Validate the two real records. Show the explicit source-to-canonical mapping, retained unmapped column, blank material code, preview digest, `matching core changed: false`, and `ERP writes: false`.

## 7 Close with evidence

Open `docs/phase13_claim_evidence.md` or the Phase 13 evidence folder. State that 128 tests, Python compilation, JavaScript syntax, OpenAPI generation, raw hashes, clean-copy installation and the full local browser replay passed in the final run. Managed Neon/OIDC/Vercel validation remains pending external account setup.

Fresh-checkout note: the seeding utility rebuilds the absent ignored Phase 3 pack from committed candidates and mappings.
