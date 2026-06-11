export interface SkillDraftSource {
  runId: string;
  lesson: string;
  polarity: "reuse" | "avoid";
}

export const skillSedimentationRules = [
  "Only summarize lessons that repeat at least 3 times.",
  "Separate reusable positive rules from avoidance rules.",
  "Every rule must preserve source run_id references.",
  "Generate drafts under data/skills-drafts/ first.",
  "Never overwrite formal .claude/skills/ files automatically.",
  "Human review is required before a draft becomes a formal Skill.",
  "Do not turn one-off lucky results into long-term rules."
];

export function canPromoteToSkill(sources: SkillDraftSource[]): boolean {
  return sources.length >= 3;
}

export function groupSkillDraftSources(sources: SkillDraftSource[]) {
  return {
    reusable: sources.filter((source) => source.polarity === "reuse"),
    avoid: sources.filter((source) => source.polarity === "avoid")
  };
}
