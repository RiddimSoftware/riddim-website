---
tracker:
  kind: linear
  endpoint: https://api.linear.app/graphql
  api_key: $LINEAR_API_KEY
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
workspace:
  root: ./.symphony/workspaces
hooks:
  timeout_ms: 60000
agent:
  providers:
    - name: codex
      weight: 1
    - name: claude
      weight: 1
  max_concurrent_agents: 3
  max_turns: 20
  max_retry_backoff_ms: 300000
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
Attempt: {{ attempt }}

Labels:
{% for label in issue.labels %}
- {{ label }}
{% endfor %}

Description:
{{ issue.description }}

Follow the repository instructions in CLAUDE.md.

Repository rules:
- This repo builds the static public site for `riddimsoftware.com`.
- Keep the root checkout on main. Use a feature worktree for branch work.
- Keep each change scoped to one Linear issue and one pull request.
- Use branch names that include the issue identifier, such as `claude/web-123-short-slug`.
- Link the issue in the PR title or body so Linear can auto-link and transition it.
- Preserve brand guidance in `docs/brand.md` and release guidance in `docs/release-process.md`.

Verification expectations:
- Install dependencies with `npm install --package-lock=false` when dependencies are missing.
- Run `npm run validate` for site changes.
- For visual changes, inspect the generated `_site` output and capture screenshots when the issue asks for visual evidence.
- Report any verification that could not run with the exact command and reason.
