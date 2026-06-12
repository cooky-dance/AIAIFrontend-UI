# AIAIFrontend UI

AI short-film creative console. This project is under active development.

The long-term workflow is:

Project setup -> character setup -> style templates -> prompt generation -> image generation -> video generation -> review -> Skill draft -> future reuse.

## Current Status

The repository is being upgraded from a single Streamlit Seedance2 testing tool into a local creative console based on the project document.

Current foundation:

- `apps/web`: Next.js App Router, TypeScript, and Tailwind CSS frontend.
- `packages/providers`: Provider adapter contracts for API, Manual, and Browser providers.
- `packages/prompt-engine`: Prompt generation and reuse rules.
- `packages/skill-engine`: Skill draft curation rules.
- `prisma/schema.prisma`: SQLite data model foundation.
- `data/*`: local folders for runs, feedback, downloads, browser profiles, and Skill drafts.
- `.claude/skills/*`: initial Skill requirement files.

## System Layers

```text
AI Short-Film Creative Console
├─ Frontend Console
│  ├─ Projects
│  ├─ Characters
│  ├─ Styles
│  ├─ Prompt Generator
│  ├─ Image Tasks
│  ├─ Video Tasks
│  ├─ Review System
│  └─ Skill Draft Management
│
├─ Provider System
│  ├─ API Provider
│  │  ├─ OpenAI Image API
│  │  └─ Seedance2 API
│  │
│  ├─ Manual Provider
│  │  ├─ Copy Prompt
│  │  ├─ Generate Manually
│  │  └─ Upload Result Manually
│  │
│  └─ Browser Provider
│     ├─ Playwright Chromium
│     ├─ Isolated Login Profile
│     ├─ Semi-auto Mode
│     └─ Full-auto Reserved
│
├─ Data Layer
│  ├─ SQLite
│  ├─ Prisma
│  ├─ GenerationRun
│  ├─ Review
│  ├─ ProviderConfig
│  └─ SkillDraft
│
└─ Agent Workflow
   ├─ Codex: engineering and implementation
   └─ Claude Code: rules, prompts, and Skills
```

## Future Official / Gateway API Integration

The system will support both official APIs and gateway APIs through one Provider adapter contract.

Official APIs:

- Use standard service endpoints such as OpenAI Image API.
- Read API keys only from server-side `.env` variables.
- Never expose API keys to the frontend.
- Save successful outputs as `GenerationRun` records.

Gateway APIs:

- Support services such as AIAI / Seedance2.
- Configure endpoint kind, base URL, API key environment variable, and default model.
- Support async video tasks with `createTask`, `getTask`, polling, and error metadata.
- Keep provider-specific request logic inside `packages/providers`.

## UI Design

The UI should feel like a working local SaaS console, not a landing page.

- Prioritize project status, recent results, reviews, reusable prompts, Skill drafts, and Provider status.
- Keep the interface dense but readable, with clear borders and predictable layout.
- Preserve the main workflow: project -> character -> style -> prompt -> result -> review -> Skill draft.
- Mark incomplete API flows as development, mock, or placeholder states.
- Start with semi-auto Browser Provider workflows before attempting full automation.

## Prompt Reuse Rules

1. Only reviewed `GenerationRun` prompts can become reuse candidates.
2. Prefer prompts with `overallScore >= 8` and `shouldReuse=true`.
3. Treat `shouldAvoid=true` prompts as avoidance examples by default.
4. Preserve character identity, style tags, camera, lighting, and negative prompt when reusing.
5. Track source `run_id` for every reuse.
6. Do not promote unreviewed outputs into formal Skills.

## Skill Sedimentation Rules

1. Only summarize lessons that repeat at least 3 times.
2. Separate positive reusable rules from avoidance rules.
3. Keep source `run_id` references for every rule.
4. Write drafts to `data/skills-drafts/`.
5. Require human review before merging into `.claude/skills/`.
6. Never overwrite formal Skills automatically.
7. Do not turn one-off results into long-term rules.

## Run Next.js App

Install dependencies:

```bash
npm install
```

Start the web app:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

On Windows, you can also double-click `双击启动_AI短片创作控制台.bat`.
The launcher includes a small menu for:

- Next.js main console: `http://127.0.0.1:3000`
- Streamlit AIAI gateway test tool: `http://127.0.0.1:8501`
- Dependency check / install

`双击启动_aiai_seedance2_frontend.bat` is kept only as a compatibility entry and now forwards to the new launcher.

## Environment

Copy `.env.example` to `.env` and fill values locally.

```bash
cp .env.example .env
```

API keys must stay in `.env` and must not be committed.

## Legacy Streamlit Tool

The previous local Seedance2 Streamlit test tool is still kept:

```bash
pip install -r requirements.txt
streamlit run aiai_seedance2_frontend.py
```
