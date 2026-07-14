# State machine

`Gate C -> immutable Spec(review_requested) -> Karl exact planning approval -> protected approval/audit write -> one VM -> VM validation -> Sweep/readiness -> Karl Gate Q -> inert admission -> separate dispatch authority`

- Planning approval does not authorize Gate Q.
- Gate Q does not authorize dispatch.
- Admission does not authorize execution.
- Any missing/hash-mismatched/reused evidence fails closed without transition.
