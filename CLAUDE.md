# LinkedIn Posting Agent — Lock Mechanism

This file supplements the agent system prompt. Follow these steps **before** anything else in every run.

---

## Step 0 — Pull and pre-flight checks (MUST be first)

1. `git fetch origin main && git checkout main && git pull --rebase origin main`
2. If `pending-post.json` exists in the repo root: **skip this run** (the previous post has not been consumed by Zapier yet). Append to `skipped.log` and commit with message `Scheduler: skipped - pending post not yet consumed`, then push and exit.
3. Read `scheduler.lock` if it exists:
   - Parse `expires_at` (ISO 8601 UTC).
   - If `expires_at` is in the future: **skip this run** — reason `"lock held by another agent"`.
   - If `expires_at` is in the past: the lock is stale; proceed and overwrite it.

## Step 1 — Acquire lock

Write `scheduler.lock` to the repo root:

```json
{
  "acquired_at": "<now ISO 8601 UTC>",
  "expires_at": "<now + 10 minutes ISO 8601 UTC>"
}
```

Then:

```
git add scheduler.lock
git commit -m "Scheduler: acquire lock"
git push -u origin main
```

- If the push **succeeds**: you hold the lock. Continue to Step 2.
- If the push **fails** (rejected because another agent pushed first): **skip this run** — reason `"lock contention, another agent is running"`. Do NOT append to skipped.log (you never held the lock). Exit.

## Step 2 — Read state and select post

*Only after the lock push succeeds:*

- Read `posted.json` from the local filesystem (it is now current, since you just pulled and no one else can push until you release the lock).
- Apply variety rules and select a candidate as described in the system prompt.

## Step 3 — Publish or skip

Follow the system prompt PUBLISHING and LOGGING steps normally.

## Step 4 — Release lock (final commit)

When making the final commit (posted.json + skipped.log + pending-post.json), also delete the lock:

```
git rm scheduler.lock
```

Include this deletion in the **same** commit as the state files. This atomically releases the lock at the moment the post is recorded.

Commit message formats remain:
- `Scheduler: posted <cert>/<type>/<filename>`
- `Scheduler: skipped - <reason>`

---

## Why this works

Git push is atomic at the remote. Only one agent can successfully push the lock commit; any concurrent agent gets a rejection and skips. The 10-minute TTL ensures a crashed agent never blocks future runs indefinitely.
