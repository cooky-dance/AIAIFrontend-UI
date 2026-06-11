export type ProviderType = "api" | "manual" | "browser";
export type ApiEndpointKind = "official" | "gateway";
export type GenerationType = "image" | "video";
export type TaskStatus = "pending" | "running" | "succeeded" | "failed";

export interface CreateTaskInput {
  type: GenerationType;
  prompt: string;
  negativePrompt?: string;
  inputImageUrl?: string;
  aspectRatio?: string;
  duration?: number;
  model?: string;
  metadata?: Record<string, unknown>;
}

export interface CreateTaskResult {
  taskId?: string;
  status: TaskStatus;
  outputUrl?: string;
  metadata?: Record<string, unknown>;
}

export interface GetTaskResult extends CreateTaskResult {
  error?: string;
}

export interface ApiEndpointConfig {
  kind: ApiEndpointKind;
  baseUrl: string;
  apiKeyEnv: string;
  defaultModel?: string;
  headers?: Record<string, string>;
}

export interface ProviderConfig {
  id: string;
  name: string;
  providerKey: string;
  type: ProviderType;
  enabled: boolean;
  api?: ApiEndpointConfig;
  mode?: "manual" | "semi-auto" | "full-auto";
  profileDir?: string;
  downloadDir?: string;
}

export interface GenerationProvider {
  id: string;
  name: string;
  type: ProviderType;
  config?: ProviderConfig;
  createTask(input: CreateTaskInput): Promise<CreateTaskResult>;
  getTask(taskId: string): Promise<GetTaskResult>;
}
