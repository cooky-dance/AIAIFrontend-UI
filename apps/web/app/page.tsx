const stageItems = [
  { label: "当前阶段", value: "Phase 1", detail: "前端 MVP 与数据闭环" },
  { label: "工作方式", value: "Semi-auto", detail: "先半自动，后全自动" },
  { label: "Provider", value: "Planned", detail: "Manual / Image API / Seedance2 / Browser" },
  { label: "状态", value: "In development", detail: "项目正在开发中" }
];

const dashboardPanels = [
  {
    title: "项目库",
    body: "管理项目、世界观、短片目标、常用比例和视觉风格。",
    status: "待实现"
  },
  {
    title: "角色库",
    body: "沉淀角色外貌、服装、性格、关键词、禁止项和参考图。",
    status: "待实现"
  },
  {
    title: "提示词生成器",
    body: "按项目、角色、场景、镜头、动作和风格生成 Image / Video Prompt。",
    status: "待实现"
  },
  {
    title: "结果与评分",
    body: "保存 GenerationRun，记录评分、问题、复用规则和 Skill 草稿入口。",
    status: "待实现"
  }
];

const roadmap = [
  "项目库 / 角色库 / 风格库",
  "提示词生成器",
  "手动上传结果",
  "评分系统",
  "OpenAI Image API",
  "Seedance2 Provider",
  "Browser Provider semi-auto",
  "Skill 草稿生成"
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen px-5 py-6 text-ink sm:px-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-4 border-b border-line pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
              AI short-film creative console
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-ink sm:text-4xl">
              AIAIFrontend UI
            </h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
              本项目正在开发中，目标是搭建一个本地可用的 AI 短片创作控制台：管理项目、角色和风格，生成图片与视频提示词，保存结果评分，并沉淀可复用经验。
            </p>
          </div>
          <div className="flex items-center gap-3 rounded border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
            <span>开发中，当前仅提供框架首页</span>
          </div>
        </header>

        <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {stageItems.map((item) => (
            <div key={item.label} className="rounded border border-line bg-panel p-4">
              <div className="text-sm text-slate-500">{item.label}</div>
              <div className="mt-2 text-xl font-semibold text-ink">{item.value}</div>
              <div className="mt-1 text-sm leading-6 text-slate-600">{item.detail}</div>
            </div>
          ))}
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded border border-line bg-panel p-5">
            <div className="flex flex-col gap-2 border-b border-line pb-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold">控制台模块</h2>
                <p className="mt-1 text-sm text-slate-600">首页会逐步接入项目、角色、提示词、结果和评分数据。</p>
              </div>
              <span className="w-fit rounded bg-slate-100 px-3 py-1 text-sm text-slate-700">MVP 骨架</span>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              {dashboardPanels.map((panel) => (
                <article key={panel.title} className="rounded border border-line p-4">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-ink">{panel.title}</h3>
                    <span className="rounded bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                      {panel.status}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{panel.body}</p>
                </article>
              ))}
            </div>
          </div>

          <aside className="rounded border border-line bg-panel p-5">
            <h2 className="text-lg font-semibold">开发顺序</h2>
            <ol className="mt-4 space-y-3">
              {roadmap.map((item, index) => (
                <li key={item} className="flex gap-3 text-sm text-slate-700">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-emerald-50 font-semibold text-emerald-700">
                    {index + 1}
                  </span>
                  <span className="pt-0.5">{item}</span>
                </li>
              ))}
            </ol>
          </aside>
        </section>
      </div>
    </main>
  );
}
