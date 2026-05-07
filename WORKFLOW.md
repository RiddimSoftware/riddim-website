---
tracker:
  kind: linear
  endpoint: https://api.linear.app/graphql
  api_key: $LINEAR_API_KEY
  api_key_aws_secret:
    secret_id: linear/api-key
    profile: riddim-agent
    region: us-east-1
  project_slug: WEB
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Done
    - Canceled
    - Cancelled
    - Duplicate
polling:
  interval_ms: 30000
reviewer:
  enrolled_repos:
    - RiddimSoftware/riddim-website
  opener_allowlist:
    - riddim-developer-bot
    - app/riddim-developer-bot
workspace:
  root: ./.symphony/workspaces
  repository_root: .
  base_branch: main
  branch_prefix_template: claude
  use_git_worktree: true
  require_clean_root: true
hooks:
  timeout_ms: 60000
agent:
  providers:
    - name: codex
      weight: 1
    - name: claude
      weight: 1
  max_concurrent_agents: 1
  max_turns: 20
  max_retry_backoff_ms: 300000
  max_resume_attempts: 5
  max_fix_attempts: 3
  max_concurrent_agents_by_state:
    In Progress: 1
    Todo: 1
  github_bot:
    enabled: true
    path_prefix: /Users/sunny/code/agent-config/bin
    aws_profile: riddim-agent
    expected_login: riddim-developer-bot[bot]
    git_author_name: riddim-developer-bot
    git_author_email: developer-bot@riddimsoftware.com
  reviewer_bot:
    enabled: false
    path_prefix: /Users/sunny/code/agent-config/bin
    aws_profile: riddim-agent
    expected_login: riddim-reviewer-bot[bot]
    git_author_name: riddim-reviewer-bot
    git_author_email: reviewer-bot@riddimsoftware.com
codex:
  command: codex app-server
  approval_policy:
    mode: never
  thread_sandbox:
    mode: danger-full-access
  turn_sandbox_policy:
    mode: danger-full-access
  turn_timeout_ms: 3600000
  read_timeout_ms: 5000
  stall_timeout_ms: 300000
claude:
  command: claude --dangerously-skip-permissions -p
  turn_timeout_ms: 3600000
server:
  port: 4778
---
# Riddim Website Symphony Workflow

Implement Linear issue {{ issue.identifier }} for riddimsoftware.com: {{ issue.title }}.

State: {{ issue.state }}
Estimate: {{ issue.estimate }}
Attempt: {{ attempt }}

Labels:
{% for label in issue.labels %}
- {{ label }}
{% endfor %}

Description:
{{ issue.description }}

Follow the repository instructions in AGENTS.md and CLAUDE.md when present.
Read the Symphony Handoff Context at the top of this prompt before acting. Its
mode tells you whether this is fresh work, resumed worktree work, or an
existing PR fix.

Before editing files:
- Confirm {{ issue.identifier }} is In Progress in Linear.
- Add a Linear comment with the selected provider, workspace path, and start time.
- If the issue is not In Progress, stop and report the blocker.

Repository rules:
- This repo builds the static public site for `riddimsoftware.com`.
- Symphony starts you in an issue-specific git worktree. Do not edit the root
  checkout or create another worktree unless the issue explicitly requires it.
- Keep the root checkout on main if you inspect it.
- Keep each change scoped to one Linear issue and one pull request.
- Treat the handoff context's routing decision as binding when present.
- Use the current branch from the handoff context.
- If the routing decision points at another repository, or if you can prove the
  routing evidence is wrong, stop and leave a blocking Linear comment instead of
  switching repos or opening a PR elsewhere.
- If the handoff mode is `fix_existing_pr` or `resumed`, push fixes to the
  existing PR branch. Do not open a new PR under any circumstances.
- If the issue estimate is missing in this prompt, treat it as the standard 8
  complexity tier and mention the missing estimate in the PR body and a Linear
  comment.
- Preserve brand guidance in `docs/brand.md` and release guidance in `docs/release-process.md`.

PR ownership lifecycle:
Your responsibility is to own the PR from creation until one of these terminal
conditions:
- GitHub automerge completes the merge — stop and leave a summary comment in
  Linear.
- A reviewer blocks the PR with requested changes — push fixes and update your
  Linear blocker comment.
- A human-gated check requires manual intervention — leave a detailed Linear
  comment with the exact action needed and stop.

Do not manually merge the PR. GitHub automerge owns all merges. Your role is to
push a shippable branch and keep the PR unblocked.

PR handoff contract:
- Create at least one commit for the issue before handoff.
- Confirm the branch is clean with `git status --porcelain`.
- Refresh the repo root with `git fetch origin main` and rebase the worktree
  branch onto `origin/main`.
- Push the branch to origin before opening the PR.
- Use plain `gh`; Symphony has already set `RIDDIM_DEV_BOT_GH=1` and verified
  the `gh agent-bot status` preflight so `gh pr create` opens as
  `riddim-developer-bot[bot]`.
- Fresh run: open exactly one PR with `gh pr create --label autonomous`.
- Fresh run: include `Reviewer-Boundary: review-only` in the PR body so the
  legacy developer-fix workflow skips this PR and Symphony's
  WakeDeveloperForPRAction owns fix cycles.
- Resumed or fix_existing_pr run: push to the existing branch. Do not create a
  new PR.
- Use the PR title format `[{{ issue.identifier }}]: <short description>`.
- Include verification evidence and any skipped checks with reasons in the PR body.

Durable state for resume:
After opening or updating the PR, leave a Linear comment with:
- Implementation notes and key decisions made.
- Verification evidence (commands run and pass/fail results).
- Tradeoffs or known limitations.
- Any blockers or follow-up work required.

This comment is the resume packet. A fresh agent session rebuilds context from
it, so write it as a self-contained handoff, not a conversation summary.

After posting the resume comment, stop. Do not wait for review, CI, automerge,
or human confirmation.

Verification expectations:
- Install dependencies with `npm install --package-lock=false` when dependencies are missing.
- Run `npm run validate` for site changes.
- For visual changes, inspect the generated `_site` output and capture screenshots when the issue asks for visual evidence.
- Report any verification that could not run with the exact command and reason.
