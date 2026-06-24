# OHLCV Regression Proof

## Status

Behavior-equivalent regression proof obtained. Byte-identical RP replay was not claimed.

## Byte Replay Availability

Repo discovery found canonical result populations `RP-2592`, `RP-3731`, and `RP-7134`, plus historical runner command examples, but no committed repo-native replay command that deterministically regenerates those exact files byte-identically from the isolated worktree.

## Proof Used

- `tests/test_offline_research_runner.py::test_15m_input_identity_scope_remains_unchanged` confirms the OHLCV-only input identity hash scope remains unchanged.
- Full `tests/test_offline_research_runner.py` passed.
- Full `tests/test_spec_signal_compiler.py` passed.
- Existing result-population validator passed against committed canonical result populations.
- `git diff --check` passed.
- No canonical result-population files were modified.

## Boundary

No byte-identical claim is made.
