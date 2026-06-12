import { NextResponse } from "next/server";
import { seedance2Provider } from "@aiai/providers";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ taskId: string }> }
) {
  const { taskId } = await params;
  if (!taskId) {
    return NextResponse.json({ error: "taskId 不能为空" }, { status: 400 });
  }

  const result = await seedance2Provider.getTask(taskId);
  return NextResponse.json(result);
}
