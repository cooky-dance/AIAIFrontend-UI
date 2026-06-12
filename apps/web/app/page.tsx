import Link from "next/link";

const stageItems = [
  { label: "当前阶段", value: "Phase 1", detail: "前端 MVP 与数据闭环" },
  { label: "工作方式", value: "Semi-auto", detail: "先半自动，后全自动" },
  { label: "Provider", value: "Official / Gateway", detail: "官方 API 与中转 API 共用 adapter" },
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
  },
  {
    title: "Seedance2 视频生成",
    body: "通过统一 Provider 调用 AIAI 中转 API，提交文生视频 / 图生视频任务并轮询状态。",
    status: "可用"
  }
];

const apiPlans = [
  {
    title: "官方 API",
    body: "面向 OpenAI Image API 等官方服务，API Key 只从服务端 .env 读取，前端永不暴露密钥。",
    items: ["标准 baseUrl", "官方模型名", "服务端 API Route", "结果保存为 GenerationRun"]
  },
  {
    title: "中转 API",
    body: "面向 AIAI / Seedance2 等兼容或中转服务，通过 endpointKind、baseUrl、apiKeyEnv 切换。",
    items: ["自定义 baseUrl", "中转模型名", "异步任务轮询", "失败原因写入 metadata"]
  },
  {
    title: "统一 Provider",
    body: "前端只选择 provider，不直接写具体模型请求逻辑，后续替换来源时不改页面流程。",
    items: ["createTask", "getTask", "ProviderConfig", "api / manual / browser"]
  }
];

const uiPrinciples = [
  "首页优先展示当前项目、最近生成、最近评分、可复用提示词、Skill 草稿数量和 Provider 状态。",
  "SaaS 控制台风格：信息密度适中、边框清晰、少装饰、适合反复创作与复盘。",
  "核心流程保持在一个方向上：项目设定 -> 角色设定 -> 提示词 -> 生成结果 -> 评分 -> 经验沉淀。",
  "真实生成接入前，所有 API 区域以清晰的开发中状态和 mock / placeholder 状态呈现。"
];

const promptReuseRules = [
  "只有已经保存为 GenerationRun 并完成评分的提示词，才进入复用候选。",
  "优先复用 overallScore >= 8 且 shouldReuse=true 的提示词。",
  "shouldAvoid=true 的提示词默认只作为避坑案例，不进入常规复用。",
  "复用时必须保留角色核心特征、风格标签、镜头、光线和 negative prompt。",
  "每次复用都记录来源 run_id，方便后续追溯成功经验。"
];

const skillRules = [
  "重复出现 3 次以上的经验才允许生成 Skill 草稿。",
  "正向经验和避坑经验分开沉淀。",
  "每条规则都必须保留来源 run_id。",
  "Skill 草稿先进入 data/skills-drafts/，人工审核后再合并到 .claude/skills/。",
  "系统不能自动覆盖正式 Skill，也不能把一次偶然结果写成长期规则。"
];

const skillFiles = [
  "prompt-director",
  "image2-character-prompt",
  "seedance2-video-prompt",
  "skill-curator"
];

const roadmap = [
  "项目库 / 角色库 / 风格库",
  "提示词生成器",
  "手动上传结果",
  "评分系统",
  "OpenAI Image API",
  "Seedance2 Provider",
  "Provider adapter 抽象",
  "Browser Provider semi-auto",
  "Skill 草稿生成"
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen px-5 py-6 text-ink sm:px-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-7">
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
            <span>开发中，当前提供框架首页和规则骨架</span>
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

        <section>
          <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold">控制台模块</h2>
              <p className="text-sm text-slate-600">首页会逐步接入项目、角色、提示词、结果和评分数据。</p>
            </div>
            <span className="w-fit rounded bg-slate-100 px-3 py-1 text-sm text-slate-700">MVP 骨架</span>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
            {dashboardPanels.map((panel) => (
              <article key={panel.title} className="rounded border border-line bg-panel p-4">
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
        </section>

        <section>
          <h2 className="text-lg font-semibold">官方 / 中转 API 接入</h2>
          <p className="mt-1 text-sm text-slate-600">
            Provider adapter 统一处理官方 API 与中转 API，真实密钥只存在服务端环境变量中。
          </p>
          <div className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-3">
            {apiPlans.map((plan) => (
              <article key={plan.title} className="rounded border border-line bg-panel p-4">
                <h3 className="font-semibold text-ink">{plan.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{plan.body}</p>
                <ul className="mt-3 space-y-2 text-sm text-slate-700">
                  {plan.items.map((item) => (
                    <li key={item} className="flex gap-2">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-600" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1fr]">
          <div>
            <h2 className="text-lg font-semibold">UI 设计原则</h2>
            <ul className="mt-3 space-y-3 rounded border border-line bg-panel p-4 text-sm leading-6 text-slate-700">
              {uiPrinciples.map((rule) => (
                <li key={rule} className="flex gap-3">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-500" />
                  <span>{rule}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h2 className="text-lg font-semibold">开发顺序</h2>
            <ol className="mt-3 space-y-2 rounded border border-line bg-panel p-4">
              {roadmap.map((item, index) => (
                <li key={item} className="flex gap-3 text-sm text-slate-700">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-emerald-50 font-semibold text-emerald-700">
                    {index + 1}
                  </span>
                  <span className="pt-0.5">{item}</span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1fr]">
          <div>
            <h2 className="text-lg font-semibold">提示词复用规则</h2>
            <ul className="mt-3 space-y-3 rounded border border-line bg-panel p-4 text-sm leading-6 text-slate-700">
              {promptReuseRules.map((rule) => (
                <li key={rule} className="flex gap-3">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-600" />
                  <span>{rule}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h2 className="text-lg font-semibold">Skill 沉淀规则</h2>
            <ul className="mt-3 space-y-3 rounded border border-line bg-panel p-4 text-sm leading-6 text-slate-700">
              {skillRules.map((rule) => (
                <li key={rule} className="flex gap-3">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-purple-600" />
                  <span>{rule}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="rounded border border-line bg-panel p-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Skill 文件</h2>
              <p className="mt-1 text-sm text-slate-600">
                当前已填充初始 Skill 要求，后续由 Claude Code 维护规则和经验沉淀。
              </p>
            </div>
            <span className="w-fit rounded bg-violet-50 px-3 py-1 text-sm font-medium text-violet-700">
              .claude/skills
            </span>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {skillFiles.map((name) => (
              <div key={name} className="rounded border border-line p-3 text-sm font-medium text-slate-800">
                {name}
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
