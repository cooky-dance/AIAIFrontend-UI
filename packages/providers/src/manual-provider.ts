import type { CreateTaskInput, CreateTaskResult, GenerationProvider, GetTaskResult } from "./provider-types";

export const manualProvider: GenerationProvider = {
  id: "manual",
  name: "Manual Provider",
  type: "manual",
  async createTask(input: CreateTaskInput): Promise<CreateTaskResult> {
    return {
      status: "pending",
      metadata: {
        mode: "manual",
        prompt: input.prompt,
        nextAction: "Copy prompt, generate externally, then upload the result."
      }
    };
  },
  async getTask(taskId: string): Promise<GetTaskResult> {
    return {
      taskId,
      status: "pending",
      metadata: {
        mode: "manual",
        nextAction: "Waiting for user-uploaded result."
      }
    };
  }
};
