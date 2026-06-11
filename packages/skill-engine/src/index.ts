export interface SkillDraftSource {
  runId: string;
  lesson: string;
  polarity: "reuse" | "avoid";
}

export function canPromoteToSkill(sources: SkillDraftSource[]): boolean {
  return sources.length >= 3;
}
