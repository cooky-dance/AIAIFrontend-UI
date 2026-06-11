# Agent Notes

This repository is the shared root for Codex and Claude Code.

- Codex owns engineering code, frontend pages, API routes, Prisma schema, provider adapters, Playwright automation, uploads, downloads, README updates, and bug fixes.
- Claude Code owns project rules, prompt conventions, Skill drafts, workflow notes, and experience summaries.
- API keys must stay in `.env` files and must never be committed.
- Official and gateway API integrations must go through `packages/providers`; frontend pages should not contain provider-specific request logic.
- Provider config may store `baseUrl`, `endpointKind`, `apiKeyEnv`, and model defaults, but never the actual secret value.
- Browser Provider work should use separate Playwright profiles under `data/browser-profiles/`.
- Skill drafts are written to `data/skills-drafts/` and require human review before becoming formal skills.
- Prompt reuse requires reviewed `GenerationRun` evidence and source `run_id` tracking.
