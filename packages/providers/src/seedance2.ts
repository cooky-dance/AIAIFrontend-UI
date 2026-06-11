import { aiaiGatewayEndpoint, joinEndpoint, resolveApiKey } from "./api-endpoints";
import type { CreateTaskInput, CreateTaskResult, GenerationProvider, GetTaskResult } from "./provider-types";

export const seedance2Provider: GenerationProvider = {
  id: "seedance2",
  name: "Seedance2 Gateway API",
  type: "api",
  config: {
    id: "seedance2",
    name: "Seedance2 Gateway API",
    providerKey: "seedance2",
    type: "api",
    enabled: false,
    api: aiaiGatewayEndpoint
  },
  async createTask(input: CreateTaskInput): Promise<CreateTaskResult> {
    resolveApiKey(aiaiGatewayEndpoint);

    return {
      status: "pending",
      metadata: {
        endpointKind: aiaiGatewayEndpoint.kind,
        endpoint: joinEndpoint(aiaiGatewayEndpoint.baseUrl, "/videos/generations"),
        model: input.model ?? aiaiGatewayEndpoint.defaultModel,
        supports: ["text-to-video", "image-to-video", "async-status"],
        implementationStatus: "placeholder"
      }
    };
  },
  async getTask(taskId: string): Promise<GetTaskResult> {
    return {
      taskId,
      status: "pending",
      metadata: {
        endpoint: joinEndpoint(aiaiGatewayEndpoint.baseUrl, `/videos/generations/${taskId}`),
        implementationStatus: "Seedance2 task polling is reserved for a later phase."
      }
    };
  }
};
