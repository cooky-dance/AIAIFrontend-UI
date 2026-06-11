export type ProviderType = "api" | "manual" | "browser";
export type GenerationType = "image" | "video";
export type TaskStatus = "pending" | "running" | "succeeded" | "failed";

export interface CreateTaskInput {
  type: GenerationType;
  prompt: string;
  negativePrompt?: string;
  inputImageUrl?: string;
  aspectRatio?: string;
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

export interface GenerationProvider {
  id: string;
  name: string;
  type: ProviderType;
  createTask(input: CreateTaskInput): Promise<CreateTaskResult>;
  getTask(taskId: string): Promise<GetTaskResult>;
}
