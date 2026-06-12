import { aiaiGatewayEndpoint, joinEndpoint } from "./api-endpoints";
import type {
  CreateTaskInput,
  CreateTaskResult,
  GenerationProvider,
  GetTaskResult,
  TaskStatus
} from "./provider-types";

const CREATE_PATH = "/videos/generations";

function readApiKey(): string | undefined {
  const value = process.env[aiaiGatewayEndpoint.apiKeyEnv];
  return value && value.length > 0 ? value : undefined;
}

export function isSeedance2Enabled(): boolean {
  return Boolean(readApiKey());
}

function buildHeaders(apiKey: string): Record<string, string> {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
    ...aiaiGatewayEndpoint.headers
  };
}

function mapStatus(raw: unknown): TaskStatus {
  const value = String(raw ?? "").toLowerCase();
  if (["succeeded", "success", "completed", "done"].includes(value)) {
    return "succeeded";
  }
  if (["failed", "error", "canceled", "cancelled", "expired"].includes(value)) {
    return "failed";
  }
  if (["running", "processing", "in_progress", "generating"].includes(value)) {
    return "running";
  }
  return "pending";
}

function extractTaskId(payload: Record<string, any>): string | undefined {
  return payload.task_id ?? payload.id ?? payload.data?.task_id ?? payload.data?.id;
}

function extractOutputUrl(payload: Record<string, any>): string | undefined {
  return (
    payload.video_url ??
    payload.output?.video_url ??
    payload.data?.video_url ??
    (Array.isArray(payload.data) ? payload.data[0]?.url : undefined) ??
    payload.content?.video_url
  );
}

function placeholderResult(input: CreateTaskInput): CreateTaskResult {
  return {
    status: "pending",
    metadata: {
      endpointKind: aiaiGatewayEndpoint.kind,
      endpoint: joinEndpoint(aiaiGatewayEndpoint.baseUrl, CREATE_PATH),
      model: input.model ?? aiaiGatewayEndpoint.defaultModel,
      supports: ["text-to-video", "image-to-video", "async-status"],
      implementationStatus: "placeholder",
      reason: `Missing API key environment variable: ${aiaiGatewayEndpoint.apiKeyEnv}`
    }
  };
}

export const seedance2Provider: GenerationProvider = {
  id: "seedance2",
  name: "Seedance2 Gateway API",
  type: "api",
  config: {
    id: "seedance2",
    name: "Seedance2 Gateway API",
    providerKey: "seedance2",
    type: "api",
    enabled: isSeedance2Enabled(),
    api: aiaiGatewayEndpoint
  },
  async createTask(input: CreateTaskInput): Promise<CreateTaskResult> {
    const apiKey = readApiKey();
    if (!apiKey) {
      return placeholderResult(input);
    }

    const model = input.model ?? aiaiGatewayEndpoint.defaultModel;
    const endpoint = joinEndpoint(aiaiGatewayEndpoint.baseUrl, CREATE_PATH);
    const body: Record<string, unknown> = {
      model,
      prompt: input.prompt
    };
    if (input.negativePrompt) {
      body.negative_prompt = input.negativePrompt;
    }
    if (input.inputImageUrl) {
      body.image_url = input.inputImageUrl;
    }
    if (input.aspectRatio) {
      body.aspect_ratio = input.aspectRatio;
    }
    if (input.duration) {
      body.duration = input.duration;
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: buildHeaders(apiKey),
        body: JSON.stringify(body)
      });
      const payload = (await response.json().catch(() => ({}))) as Record<string, any>;

      if (!response.ok) {
        return {
          status: "failed",
          metadata: {
            endpoint,
            model,
            httpStatus: response.status,
            error: payload.error?.message ?? payload.message ?? "Seedance2 createTask request failed"
          }
        };
      }

      return {
        taskId: extractTaskId(payload),
        status: mapStatus(payload.status),
        outputUrl: extractOutputUrl(payload),
        metadata: { endpoint, model, raw: payload }
      };
    } catch (error) {
      return {
        status: "failed",
        metadata: {
          endpoint,
          model,
          error: error instanceof Error ? error.message : "Unknown network error"
        }
      };
    }
  },
  async getTask(taskId: string): Promise<GetTaskResult> {
    const apiKey = readApiKey();
    const endpoint = joinEndpoint(aiaiGatewayEndpoint.baseUrl, `${CREATE_PATH}/${taskId}`);

    if (!apiKey) {
      return {
        taskId,
        status: "pending",
        metadata: {
          endpoint,
          implementationStatus: "placeholder",
          reason: `Missing API key environment variable: ${aiaiGatewayEndpoint.apiKeyEnv}`
        }
      };
    }

    try {
      const response = await fetch(endpoint, {
        method: "GET",
        headers: buildHeaders(apiKey)
      });
      const payload = (await response.json().catch(() => ({}))) as Record<string, any>;

      if (!response.ok) {
        return {
          taskId,
          status: "failed",
          error: payload.error?.message ?? payload.message ?? "Seedance2 getTask request failed",
          metadata: { endpoint, httpStatus: response.status }
        };
      }

      const status = mapStatus(payload.status);
      return {
        taskId,
        status,
        outputUrl: extractOutputUrl(payload),
        error: status === "failed" ? payload.error?.message ?? payload.fail_reason : undefined,
        metadata: { endpoint, raw: payload }
      };
    } catch (error) {
      return {
        taskId,
        status: "failed",
        error: error instanceof Error ? error.message : "Unknown network error",
        metadata: { endpoint }
      };
    }
  }
};
