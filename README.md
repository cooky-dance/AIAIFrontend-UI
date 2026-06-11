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
