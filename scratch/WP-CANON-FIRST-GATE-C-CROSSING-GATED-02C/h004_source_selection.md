# H-004 source selection

Karl's statement, `use our best candidate so far. i approve`, is interpreted only as candidate-selection authority.

## Exact sources

- `research/hypotheses/H-004/HYPOTHESIS.md` — `sha256:5e2b385c4e59bcd9f64e0c3df3a94fee47e54484360b9fd913b5ce0d5d8e9b91`
- `research/decisions/DEC-0004.md` — `sha256:1940204f5a59618275b06d1ab64c232b086d28e570ffeb0ed57b501d61a3f836`
- `research/experiments/REP-0005.report.json` — `sha256:15e97eb7f2ec3f747691966fc9404317948b768ed5e897043a7766ca516ce6f2`
- `research/experiments/REP-0011.report.json` — `sha256:32b597e7aa06018bebfc9018167838a42141318a97684ea5eeac0232a2431f97`
- Later comparison evidence: `REP-0014` — `sha256:606ebfd6aeea5474653442fe3907f500d0f0a21b981967cef3703473e402c1af`; `REP-0015` — `sha256:8c884caa9277761022a128c878a9f23b89afef3af4a9ddd91afe4de91467b582`.

## Current metrics and comparison basis

REP-0011 is the clean full-period post-WP-5b reproduction: Sharpe `0.746191460507614`, total PnL `39897.77544811701`, profit factor `1.5037466064620668`, 41 trades, long net PnL `41206.417530000006`, short net PnL `11231.55919600001`, max drawdown `0.697949870640699`, 90-day concentration `0.9901`, and 5/8 gates passed. It failed Sharpe, drawdown, and concentration.

The full committed report scan found later, window-specific H-004 evidence with higher Sharpe. REP-0014 has the highest comparable report Sharpe (`1.739521471772824`) and 6/8 gates, but still fails drawdown (`0.3323145024165733`) and concentration (`0.7148`) and recommends archive. REP-0015 has Sharpe `1.5655754389103171`, 6/8 gates, and also recommends archive. No different candidate exceeds REP-0014's comparable Sharpe; H-003 REP-0029 is next at `1.3018468203713047`.

Therefore H-004 remains the strongest historical diagnostic source family. It remains concluded `NO-GO` and archived. This selection grants no promotion, execution, candidate-registry, Gate-C, queue, runtime, paper, or live authority.

