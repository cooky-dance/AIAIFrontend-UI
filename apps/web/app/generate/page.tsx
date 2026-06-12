"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { StatusBadge } from "../components/StatusBadge";

type Mode = "text-to-video" | "image-to-video";

interface TaskResult {
  taskId?: string;
  status: "pending" | "running" | "succeeded" | "failed";
  outputUrl?: string;
  error?: string;
  metadata?: Record<string, unknown>;
}

const aspectRatios = ["16:9", "9:16", "1:1", "4:3", "3:4"];
const durations = [4, 5, 8, 10];

export default function GeneratePage() {
  const [mode, setMode] = useState<Mode>("text-to-video");
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [model, setModel] = useState("");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [duration, setDuration] = useState(5);
  const [submitting, setSubmitting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [formError, setFormError] = useState("");
  const [task, setTask] = useState<TaskResult | null>(null);

  const isPlaceholder = task?.metadata?.implementationStatus === "placeholder";
  const isPolling =
    Boolean(task?.taskId) && (task?.status === "pending" || task?.status === "running") && !isPlaceholder;

  const refreshTask = useCallback(async () => {
    if (!task?.taskId) {
      return;
    }
    setRefreshing(true);
    try {
      const response = await fetch(`/api/generations/${task.taskId}`);
      const data = (await response.json()) as TaskResult;
      setTask((prev) => ({ ...prev, ...data }));
    } catch {
      // 保留旧状态，允许手动重试
    } finally {
      setRefreshing(false);
    }
  }, [task?.taskId]);

  useEffect(() => {
    if (!isPolling) {
      return;
    }
    const timer = setInterval(() => {
      void refreshTask();
    }, 5000);
    return () => clearInterval(timer);
  }, [isPolling, refreshTask]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");

    if (!prompt.trim()) {
      setFormError("请填写 prompt。");
      return;
    }
    if (mode === "image-to-video" && !imageUrl.trim()) {
      setFormError("图生视频模式需要提供参考图 URL。");
      return;
    }

    setSubmitting(true);
    setTask(null);
    try {
      const response = await fetch("/api/generations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          negativePrompt: negativePrompt.trim() || undefined,
          inputImageUrl: mode === "image-to-video" ? imageUrl.trim() : undefined,
          aspectRatio,
          duration,
          model: model.trim() || undefined
        })
      });
      const data = (await response.json()) as TaskResult & { error?: string };
      if (!response.ok) {
        setFormError(data.error ?? "提交失败，请稍后重试。");
        return;
      }
      setTask(data);
    } catch {
      setFormError("网络错误，提交失败。");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen px-5 py-6 text-ink sm:px-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        <header className="flex flex-col gap-2 border-b border-line pb-5">
          <Link href="/" className="text-sm text-teal-700 hover:underline">
            ← 返回控制台
          </Link>
          <h1 className="text-2xl font-semibold text-ink sm:text-3xl">Seedance2 视频生成</h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-600">
            通过统一 Provider 调用 AIAI 中转 API（/videos/generations），支持文生视频与图生视频。密钥只存在服务端
            .env 中，前端不接触任何 API Key。
          </p>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[3fr_2fr]">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4 rounded border border-line bg-panel p-5">
            <div className="flex gap-2">
              {(["text-to-video", "image-to-video"] as Mode[]).map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setMode(item)}
                  className={`rounded border px-3 py-2 text-sm font-medium ${
                    mode === item
                      ? "border-teal-700 bg-teal-700 text-white"
                      : "border-line bg-white text-slate-700 hover:border-teal-600"
                  }`}
                >
                  {item === "text-to-video" ? "文生视频" : "图生视频"}
                </button>
              ))}
            </div>

            <label className="flex flex-col gap-1.5 text-sm font-medium text-slate-700">
              Prompt
              <textarea
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                rows={5}
                placeholder="描述镜头、角色、动作、光线和风格……"
                className="rounded border border-line bg-white p-3 text-sm font-normal text-ink focus:border-teal-600 focus:outline-none"
              />
            </label>

            <label className="flex flex-col gap-1.5 text-sm font-medium text-slate-700">
              Negative Prompt（可选）
              <input
                value={negativePrompt}
                onChange={(event) => setNegativePrompt(event.target.value)}
                placeholder="不希望出现的元素"
                className="rounded border border-line bg-white p-3 text-sm font-normal text-ink focus:border-teal-600 focus:outline-none"
              />
            </label>

            {mode === "image-to-video" && (
              <label className="flex flex-col gap-1.5 text-sm font-medium text-slate-700">
                参考图 URL
                <input
                  value={imageUrl}
                  onChange={(event) => setImageUrl(event.target.value)}
                  placeholder="https://..."
                  className="rounded border border-line bg-white p-3 text-sm font-normal text-ink focus:border-teal-600 focus:outline-none"
                />
              </label>
            )}

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <label className="flex flex-col gap-1.5 text-sm font-medium text-slate-700">
                比例
                <select
                  value={aspectRatio}
                  onChange={(event) => setAspectRatio(event.target.value)}
                  className="rounded border border-line bg-white p-2.5 text-sm font-normal text-ink focus:border-teal-600 focus:outline-none"
                >
                  {aspectRatios.map((ratio) => (
                    <option key={ratio} value={ratio}>
                      {ratio}
                    </option>
                  ))}
                </select>
              </label>

              <label className="flex flex-col gap-1.5 text-sm font-medium text-slate-700">
                时长（秒）
                <select
                  value={duration}
                  onChange={(event) => setDuration(Number(event.target.value))}
                  className="rounded border border-line bg-white p-2.5 text-sm font-normal text-ink focus:border-teal-600 focus:outline-none"
                >
                  {durations.map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>

              <label className="flex flex-col gap-1.5 text-sm font-medium text-slate-700">
                模型（可选）
                <input
                  value={model}
                  onChange={(event) => setModel(event.target.value)}
                  placeholder="默认 doubao-seedance-2.0"
                  className="rounded border border-line bg-white p-2.5 text-sm font-normal text-ink focus:border-teal-600 focus:outline-none"
                />
              </label>
            </div>

            {formError && (
              <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{formError}</div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="rounded bg-teal-700 px-4 py-2.5 text-sm font-medium text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "提交中……" : "提交生成任务"}
            </button>
          </form>

          <aside className="flex flex-col gap-4 rounded border border-line bg-panel p-5">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold">任务状态</h2>
              {task && <StatusBadge status={task.status} />}
            </div>

            {!task && (
              <p className="text-sm leading-6 text-slate-600">
                提交任务后在这里展示任务 ID、状态与结果。排队 / 生成中的任务每 5 秒自动刷新一次。
              </p>
            )}

            {task && (
              <div className="flex flex-col gap-3 text-sm">
                {isPlaceholder && (
                  <div className="rounded border border-amber-300 bg-amber-50 px-3 py-2 leading-6 text-amber-900">
                    开发中状态：服务端未配置 AIAI_API_KEY，本次为 mock / placeholder 响应，未发起真实生成。
                  </div>
                )}

                {task.taskId && (
                  <div>
                    <div className="text-slate-500">任务 ID</div>
                    <div className="mt-1 break-all font-mono text-xs text-ink">{task.taskId}</div>
                  </div>
                )}

                {task.outputUrl && (
                  <div>
                    <div className="text-slate-500">输出</div>
                    <a
                      href={task.outputUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-1 block break-all text-teal-700 underline"
                    >
                      {task.outputUrl}
                    </a>
                  </div>
                )}

                {task.error && (
                  <div className="rounded border border-red-200 bg-red-50 px-3 py-2 leading-6 text-red-700">
                    {task.error}
                  </div>
                )}

                {task.taskId && !isPlaceholder && (
                  <button
                    type="button"
                    onClick={() => void refreshTask()}
                    disabled={refreshing}
                    className="w-fit rounded border border-line bg-white px-3 py-1.5 text-sm text-slate-700 hover:border-teal-600 disabled:opacity-60"
                  >
                    {refreshing ? "刷新中……" : "手动刷新"}
                  </button>
                )}

                {task.metadata && (
                  <details className="rounded border border-line bg-white p-3">
                    <summary className="cursor-pointer text-slate-600">metadata</summary>
                    <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-all text-xs text-slate-700">
                      {JSON.stringify(task.metadata, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </aside>
        </div>
      </div>
    </main>
  );
}
