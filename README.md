# AIAIFrontend UI

AI 短片自动化创作控制台。本项目正在开发中。

[English README](README.en.md)

目标形态：

项目设定 -> 角色设定 -> 风格模板 -> 提示词生成 -> 出图 -> 生视频 -> 评分 -> Skill 沉淀 -> 下次复用。

当前仓库已开始从单一 Streamlit 测试工具升级为文档要求的本地控制台框架：

- `apps/web`: Next.js App Router + TypeScript + Tailwind CSS 前端控制台
- `packages/providers`: Provider adapter 接口，占位支持 API / Manual / Browser Provider
- `packages/prompt-engine`: 提示词生成器规则入口
- `packages/skill-engine`: Skill 草稿沉淀入口
- `prisma/schema.prisma`: SQLite 数据模型起点
- `data/*`: runs、feedback、downloads、browser profiles、Skill drafts 的本地数据目录

## System Layers

```text
AI 短片自动化创作控制台
├─ 前端控制台
│  ├─ 项目库
│  ├─ 角色库
│  ├─ 风格库
│  ├─ 提示词生成器
│  ├─ 出图任务
│  ├─ 视频任务
│  ├─ 评分系统
│  └─ Skill 草稿管理
│
├─ Provider 系统
│  ├─ API Provider
│  │  ├─ OpenAI Image API
│  │  └─ Seedance2 API
│  │
│  ├─ Manual Provider
│  │  ├─ 一键复制提示词
│  │  ├─ 手动生成
│  │  └─ 手动上传结果
│  │
│  └─ Browser Provider
│     ├─ Playwright Chromium
│     ├─ 独立登录 profile
│     ├─ semi-auto 半自动
│     └─ full-auto 预留
│
├─ 数据层
│  ├─ SQLite
│  ├─ Prisma
│  ├─ GenerationRun
│  ├─ Review
│  ├─ ProviderConfig
│  └─ SkillDraft
│
└─ Agent 工作流
   ├─ Codex：开发代码
   └─ Claude Code：维护规则和 Skill
```

核心原则：

前端是生产车间，Codex 是工程师，Claude Code 是经验管理员，用户是导演和审美决策者。

## Project Directory Design

Codex 和 Claude Code 应该引用同一个项目根目录，也就是同一个 Git 仓库。

目标目录结构：

```text
ai-creative-agent/
├─ apps/
│  └─ web/
│     ├─ app/
│     ├─ components/
│     ├─ lib/
│     └─ api/
│
├─ packages/
│  ├─ prompt-engine/
│  ├─ providers/
│  │  ├─ provider-types.ts
│  │  ├─ openai-image.ts
│  │  ├─ seedance2.ts
│  │  ├─ manual-provider.ts
│  │  ├─ browser-provider-base.ts
│  │  └─ example-browser-provider.ts
│  │
│  ├─ browser-automation/
│  │  ├─ launch.ts
│  │  ├─ profile.ts
│  │  ├─ login-check.ts
│  │  └─ download.ts
│  │
│  └─ skill-engine/
│
├─ prisma/
│  └─ schema.prisma
│
├─ data/
│  ├─ runs/
│  ├─ feedback/
│  ├─ downloads/
│  ├─ browser-profiles/
│  └─ skills-drafts/
│
├─ .claude/
│  ├─ skills/
│  │  ├─ prompt-director/
│  │  │  └─ SKILL.md
│  │  ├─ image2-character-prompt/
│  │  │  └─ SKILL.md
│  │  ├─ seedance2-video-prompt/
│  │  │  └─ SKILL.md
│  │  └─ skill-curator/
│  │     └─ SKILL.md
│  │
│  └─ agents/
│
├─ CLAUDE.md
├─ AGENTS.md
├─ README.md
├─ .env
├─ .env.example
├─ package.json
└─ tsconfig.json
```

当前仓库已经创建 `apps/web`、`packages/providers`、`packages/prompt-engine`、`packages/skill-engine`、`prisma` 和 `data` 基础目录。后续会继续补齐 Provider adapter、浏览器半自动模块、Claude Code Skill 初始结构和实际页面功能。

## Future Official / Gateway API Integration

后期会同时支持官方 API 与中转 API。两者必须通过统一 Provider adapter 接入，前端不直接写具体模型请求逻辑。

### Official API

- 面向 OpenAI Image API 等官方接口。
- API Key 只从服务端 `.env` 读取，例如 `OPENAI_API_KEY`。
- 前端只选择 provider、模型参数和生成输入，不暴露密钥。
- Provider 负责请求、错误处理、结果保存和 GenerationRun 创建。

### Gateway API

- 面向 AIAI / Seedance2 等中转或兼容接口。
- 使用 `endpointKind=gateway`、`baseUrl`、`apiKeyEnv`、`defaultModel` 描述配置。
- 支持异步视频任务：`createTask`、`getTask`、状态轮询、失败原因记录。
- 中转接口参数不写死在页面里，统一收敛到 `packages/providers`。

### Provider Adapter Contract

```ts
export interface GenerationProvider {
  id: string
  name: string
  type: "api" | "manual" | "browser"
  createTask(input: CreateTaskInput): Promise<CreateTaskResult>
  getTask(taskId: string): Promise<GetTaskResult>
}
```

当前已加入：

- `packages/providers/src/api-endpoints.ts`
- `packages/providers/src/openai-image.ts`
- `packages/providers/src/seedance2.ts`
- `packages/providers/src/manual-provider.ts`
- `packages/providers/src/browser-provider-base.ts`
- `packages/providers/src/registry.ts`

## UI Design

控制台 UI 设计目标是服务日常创作和复盘，而不是营销展示。

- 首页展示当前项目、最近生成结果、最近评分、可复用提示词、Skill 草稿数量、Provider 状态。
- 页面风格保持本地 SaaS 控制台感：清晰边框、稳定信息密度、少装饰、便于长时间使用。
- 核心流程保持单向：项目设定 -> 角色设定 -> 风格模板 -> 提示词生成 -> 生成结果 -> 评分 -> 经验沉淀。
- API 真实接入前，所有生成区显示明确的开发中 / mock / placeholder 状态。
- Browser Provider 默认 semi-auto，不把全自动网页操作作为 MVP 核心。

## Prompt Reuse Rules

提示词复用必须建立在评分和可追溯来源上。

1. 只有保存为 `GenerationRun` 且完成评分的提示词，才进入复用候选。
2. 优先复用 `overallScore >= 8` 且 `shouldReuse=true` 的提示词。
3. `shouldAvoid=true` 的提示词默认只作为避坑案例，不进入常规复用。
4. 复用时必须保留角色核心特征、风格标签、镜头、光线和 negative prompt。
5. 每次复用都记录来源 `run_id`，方便追溯成功经验。
6. 没有评分的数据不进入正式 Skill。

## Skill Sedimentation Rules

Skill 沉淀必须先生成草稿，再人工审核。

1. 重复出现 3 次以上的经验才允许生成 Skill 草稿。
2. 正向经验和避坑经验分开沉淀。
3. 每条规则都必须保留来源 `run_id`。
4. Skill 草稿输出到 `data/skills-drafts/`。
5. 人工审核后才能合并到 `.claude/skills/`。
6. 系统不能自动覆盖正式 Skill。
7. 不要把一次偶然结果写成长期规则。

当前已创建初始 Skill：

- `.claude/skills/prompt-director/SKILL.md`
- `.claude/skills/image2-character-prompt/SKILL.md`
- `.claude/skills/seedance2-video-prompt/SKILL.md`
- `.claude/skills/skill-curator/SKILL.md`

## Development Status

当前阶段：Phase 1，前端 MVP 与数据闭环。

首页已经更新为开发中 Dashboard，后续会按以下顺序推进：

1. 项目库 / 角色库 / 风格库
2. 提示词生成器
3. 手动上传结果
4. 评分系统
5. OpenAI Image API
6. Seedance2 Provider
7. Browser Provider semi-auto
8. Skill 草稿生成

## Run Next.js App

Install dependencies:

```bash
npm install
```

Start the web app:

```bash
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Environment

Copy `.env.example` to `.env` and fill values locally.

```bash
cp .env.example .env
```

API keys must stay in `.env` and must not be committed.

## Legacy Streamlit Tool

The previous local Seedance2 Streamlit test tool is still kept in the repository:

```bash
pip install -r requirements.txt
streamlit run aiai_seedance2_frontend.py
```

On Windows, you can also double-click `双击启动_aiai_seedance2_frontend.bat`.
