export interface PromptContext {
  project?: string;
  character?: string;
  scene: string;
  style?: string;
  usage: "image" | "video" | "storyboard";
  aspectRatio?: string;
  emotion?: string;
  action?: string;
  camera?: string;
  lighting?: string;
}

export interface PromptOutput {
  imagePrompt: string;
  videoPrompt: string;
  negativePrompt: string;
  styleTags: string[];
  providerSuggestion: string;
  reusePolicy: PromptReusePolicy;
}

export interface PromptReusePolicy {
  shouldReuse: boolean;
  shouldAvoid: boolean;
  reuseReason: string;
  requiredReviewCount: number;
}

export function createDraftPromptOutput(context: PromptContext): PromptOutput {
  const base = [context.character, context.scene, context.style, context.camera, context.lighting]
    .filter(Boolean)
    .join(", ");

  return {
    imagePrompt: base,
    videoPrompt: [base, context.action, context.emotion].filter(Boolean).join(", "),
    negativePrompt: "text, watermark, logo, distorted face, inconsistent clothing",
    styleTags: context.style ? [context.style] : [],
    providerSuggestion: context.usage === "video" ? "seedance2" : "manual",
    reusePolicy: {
      shouldReuse: false,
      shouldAvoid: false,
      reuseReason: "Prompt reuse requires saved runs and reviews.",
      requiredReviewCount: 3
    }
  };
}

export const promptReuseRules = [
  "Only reuse prompts that are attached to a reviewed GenerationRun.",
  "Prefer prompts with overallScore >= 8 and shouldReuse=true.",
  "Avoid prompts with shouldAvoid=true unless the user explicitly wants to study failure cases.",
  "Keep role identity, visual style, camera, lighting, and negative constraints together when reusing a prompt.",
  "Track the source run_id whenever a prompt is reused."
];
