import type { CreateTaskInput, CreateTaskResult, GenerationProvider, GetTaskResult } from "./provider-types";

export abstract class BrowserProviderBase implements GenerationProvider {
  readonly type = "browser";

  constructor(
    readonly id: string,
    readonly name: string,
    readonly targetUrl: string
  ) {}

  async createTask(input: CreateTaskInput): Promise<CreateTaskResult> {
    return {
      status: "pending",
      metadata: {
        mode: "semi-auto",
        targetUrl: this.targetUrl,
        prompt: input.prompt,
        nextAction: "Open isolated Playwright profile, fill prompt, and wait for user action."
      }
    };
  }

  async getTask(taskId: string): Promise<GetTaskResult> {
    return {
      taskId,
      status: "pending",
      metadata: {
        mode: "semi-auto",
        nextAction: "Waiting for manual download or upload."
      }
    };
  }
}
