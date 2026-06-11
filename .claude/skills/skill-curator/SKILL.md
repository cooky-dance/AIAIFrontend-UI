---
name: skill-curator
description: Summarize repeated prompt and generation-review lessons into human-reviewable Skill drafts without overwriting formal skills.
---

# Skill Curator

Use this Skill when reviewing multiple `GenerationRun` and `Review` records to extract durable creative rules.

## Goal

Create Skill drafts from repeated evidence, not from one-off impressions.

## Inputs

- Reviewed `GenerationRun` records.
- `Review` records with scores, liked notes, problems, nextRule, shouldReuse, shouldAvoid, and shouldMakeSkill flags.
- Source `run_id` values.

## Rules

1. Only summarize lessons that repeat at least 3 times.
2. Separate positive reusable rules from avoidance rules.
3. Every rule must preserve source `run_id` references.
4. Do not turn one lucky result into a permanent rule.
5. Do not overwrite `.claude/skills/` automatically.
6. Write drafts to `data/skills-drafts/`.
7. Require human review before merging a draft into a formal Skill.
8. If evidence is weak, write "待人工确认" instead of making a definitive claim.

## Output Structure

```text
Skill Name:

Applies When:

Positive Rules:
- Rule
  Source run_id:

Avoidance Rules:
- Rule
  Source run_id:

Prompt Template:

Evidence Summary:

Pending Human Review:
```

## Merge Policy

A draft can become a formal Skill only after the user approves it. The formal Skill must cite the relevant source `run_id` values or summarize where they can be found.
