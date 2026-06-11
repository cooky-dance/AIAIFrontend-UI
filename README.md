# AIAIFrontend UI

AI 短片自动化创作控制台。本项目正在开发中。

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
