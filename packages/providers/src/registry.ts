import type { GenerationProvider } from "./provider-types";
import { manualProvider } from "./manual-provider";
import { openAIImageProvider } from "./openai-image";
import { seedance2Provider } from "./seedance2";
import { ExampleBrowserProvider } from "./example-browser-provider";

export const providerRegistry: GenerationProvider[] = [
  manualProvider,
  openAIImageProvider,
  seedance2Provider,
  new ExampleBrowserProvider()
];

export function getProvider(providerId: string): GenerationProvider | undefined {
  return providerRegistry.find((provider) => provider.id === providerId);
}
