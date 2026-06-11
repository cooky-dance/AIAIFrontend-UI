import { joinEndpoint, officialOpenAIImageEndpoint, resolveApiKey } from "./api-endpoints";
import type { CreateTaskInput, CreateTaskResult, GenerationProvider, GetTaskResult } from "./provider-types";

export const openAIImageProvider: GenerationProvider = {
  id: "openai-image",
  name: "OpenAI Image API",
  type: "api",
  config: {
    id: "openai-image",
    name: "OpenAI Image API",
    providerKey: "openai",
    type: "api",
    enabled: false,
    api: officialOpenAIImageEndpoint
  },
  async createTask(input: CreateTaskInput): Promise<CreateTaskResult> {
    resolveApiKey(officialOpenAIImageEndpoint);

    return {
      status: "pending",
      metadata: {
        endpointKind: officialOpenAIImageEndpoint.kind,
        endpoint: joinEndpoint(officialOpenAIImageEndpoint.baseUrl, "/images/generations"),
        model: input.model ?? officialOpenAIImageEndpoint.defaultModel,
        implementationStatus: "placeholder"
      }
    };
  },
  async getTask(taskId: string): Promise<GetTaskResult> {
    return {
      taskId,
      status: "pending",
      metadata: {
        implementationStatus: "OpenAI Image API polling/download flow is reserved for a later phase."
      }
    };
  }
};
