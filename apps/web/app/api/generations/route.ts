import { NextResponse } from "next/server";
import { seedance2Provider } from "@aiai/providers";

export async function POST(request: Request) {
  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "请求体必须是合法 JSON" }, { status: 400 });
  }

  const prompt = typeof body.prompt === "string" ? body.prompt.trim() : "";
  if (!prompt) {
    return NextResponse.json({ error: "prompt 不能为空" }, { status: 400 });
  }

  const result = await seedance2Provider.createTask({
    type: "video",
    prompt,
    negativePrompt: typeof body.negativePrompt === "string" && body.negativePrompt ? body.negativePrompt : undefined,
    inputImageUrl: typeof body.inputImageUrl === "string" && body.inputImageUrl ? body.inputImageUrl : undefined,
    aspectRatio: typeof body.aspectRatio === "string" && body.aspectRatio ? body.aspectRatio : undefined,
    duration: typeof body.duration === "number" && body.duration > 0 ? body.duration : undefined,
    model: typeof body.model === "string" && body.model ? body.model : undefined
  });

  return NextResponse.json(result);
}
