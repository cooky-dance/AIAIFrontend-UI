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
    providerSuggestion: context.usage === "video" ? "seedance2" : "manual"
  };
}
