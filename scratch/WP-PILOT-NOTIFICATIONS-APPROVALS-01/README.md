# WP-PILOT-NOTIFICATIONS-APPROVALS-01

Scratch-only Apprise plus IssueOps approval-queue pilot.

Run:

```powershell
python -m tools.notifications_poc.run_notifications_approvals_poc --output-dir scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01 --dry-run
python -m tools.notifications_poc.run_notifications_approvals_poc --output-dir scratch/WP-PILOT-NOTIFICATIONS-APPROVALS-01 --dry-run --exercise-apprise
```

All outputs are local dry-run artifacts. The pilot does not send real notifications, create GitHub issues, use credentials, write canonical state, approve candidates, or touch paper/live/runtime paths.
