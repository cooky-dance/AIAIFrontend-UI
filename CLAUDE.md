# Claude Code Rules

This file defines Claude Code responsibilities for the AI short-film creative console.

Claude Code owns:

- Prompt rules and long-term creative conventions.
- `.claude/skills/` content.
- Skill drafts and workflow documentation.
- Experience summaries derived from reviewed runs.

Claude Code should not:

- Modify frontend business code unless explicitly asked.
- Store API keys in prompts, README files, Skill files, or committed config.
- Promote a one-off result into a durable rule.
- Overwrite formal Skill files automatically from generated drafts.

Skill drafts must be written to `data/skills-drafts/` first and reviewed by the user before being merged into `.claude/skills/`.
