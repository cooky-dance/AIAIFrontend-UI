import os
import json
import time
import base64
import mimetypes
from copy import deepcopy

import requests
import streamlit as st


# =========================
# 基础工具函数
# =========================

def join_url(base_url: str, path: str) -> str:
    base_url = base_url.rstrip("/")
    path = path.strip()
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return base_url + path


def is_http_url(value: str) -> bool:
    value = (value or "").strip()
    return value.startswith(("http://", "https://"))


def describe_url_value(value: str) -> str:
    value = (value or "").strip()
    if value.startswith("data:"):
        return "data URL（通常来自本地上传，AIAI 当前不接受）"
    if len(value) >= 2 and value[1] == ":":
        return "本地文件路径（需要先上传成公网 URL）"
    if value.startswith(("/", "\\")):
        return "本地文件路径（需要先上传成公网 URL）"
    if len(value) > 120:
        return value[:120] + f"... <length={len(value)}>"
    return value


def file_to_data_url(uploaded_file) -> str:
    """把本地上传文件转成 data URL。注意：部分平台可能只接受 http/https URL。"""
    raw = uploaded_file.getvalue()
    mime = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def upload_file_tuple(uploaded_file):
    raw = uploaded_file.getvalue()
    if not raw:
        raise ValueError("上传文件为空")
    mime = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or "application/octet-stream"
    return uploaded_file.name, raw, mime


def upload_to_catbox(uploaded_file) -> str:
    name, raw, mime = upload_file_tuple(uploaded_file)
    res = requests.post(
        "https://catbox.moe/user/api.php",
        data={"reqtype": "fileupload"},
        files={"fileToUpload": (name, raw, mime)},
        timeout=180,
    )
    if not res.ok:
        raise RuntimeError(f"Catbox 上传失败：HTTP {res.status_code} {res.text[:300]}")
    url = res.text.strip()
    if not is_http_url(url):
        raise RuntimeError(f"Catbox 没有返回有效公网 URL：{url[:300]}")
    return url


def upload_to_tmpfiles(uploaded_file) -> str:
    name, raw, mime = upload_file_tuple(uploaded_file)
    res = requests.post(
        "https://tmpfiles.org/api/v1/upload",
        files={"file": (name, raw, mime)},
        timeout=180,
    )
    if not res.ok:
        raise RuntimeError(f"tmpfiles 上传失败：HTTP {res.status_code} {res.text[:300]}")
    try:
        data = res.json()
    except Exception as exc:
        raise RuntimeError(f"tmpfiles 返回的不是 JSON：{res.text[:300]}") from exc

    url = ""
    if isinstance(data, dict):
        nested = data.get("data")
        if isinstance(nested, dict):
            url = nested.get("url") or ""
        url = url or data.get("url") or ""

    if url.startswith("https://tmpfiles.org/") and not url.startswith("https://tmpfiles.org/dl/"):
        url = url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/", 1)

    if not is_http_url(url):
        raise RuntimeError(f"tmpfiles 没有返回有效公网 URL：{str(data)[:300]}")
    return url


def upload_to_public_host(uploaded_file, provider: str) -> str:
    if provider.startswith("Catbox"):
        return upload_to_catbox(uploaded_file)
    return upload_to_tmpfiles(uploaded_file)


def mask_large_values(obj):
    """预览请求体时隐藏超长 data URL，避免页面卡顿。"""
    if isinstance(obj, dict):
        return {k: mask_large_values(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [mask_large_values(v) for v in obj]
    if isinstance(obj, str):
        if obj.startswith("data:"):
            return f"{obj[:40]}... <data_url length={len(obj)}>"
        if len(obj) > 500:
            return obj[:500] + f"... <length={len(obj)}>"
    return obj


def extract_task_id(data):
    """从不同中转商可能的返回结构里提取任务 ID。"""
    if not isinstance(data, dict):
        return None

    direct_keys = ["id", "task_id", "taskId", "job_id", "generation_id"]
    for key in direct_keys:
        if key in data and isinstance(data[key], str):
            return data[key]

    # 常见嵌套结构
    for container_key in ["data", "result", "output"]:
        sub = data.get(container_key)
        if isinstance(sub, dict):
            for key in direct_keys:
                if key in sub and isinstance(sub[key], str):
                    return sub[key]

    return None


def deep_find_urls(obj):
    urls = []

    if isinstance(obj, dict):
        for v in obj.values():
            urls.extend(deep_find_urls(v))

    elif isinstance(obj, list):
        for item in obj:
            urls.extend(deep_find_urls(item))

    elif isinstance(obj, str):
        if obj.startswith("http://") or obj.startswith("https://"):
            urls.append(obj)

    return urls


def pick_video_url(data):
    """优先从常见字段找视频 URL。"""
    if not isinstance(data, dict):
        return None

    candidate_paths = [
        ["url"],
        ["video_url"],
        ["data", "url"],
        ["data", "video_url"],
        ["metadata", "url"],
        ["output", "url"],
        ["output", "video_url"],
        ["result", "url"],
        ["result", "video_url"],
        ["content", "video_url"],
    ]

    for path in candidate_paths:
        cur = data
        ok = True
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                ok = False
                break
        if ok and isinstance(cur, str) and cur.startswith(("http://", "https://")):
            return cur

    urls = deep_find_urls(data)
    video_like = [u for u in urls if any(ext in u.lower() for ext in [".mp4", ".mov", ".webm", ".m3u8"])]
    if video_like:
        return video_like[0]

    return urls[0] if urls else None


def post_json(url, api_key, payload):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    res = requests.post(url, headers=headers, json=payload, timeout=180)

    try:
        data = res.json()
    except Exception:
        data = {"raw_text": res.text}

    return res.status_code, data


def get_json(url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    res = requests.get(url, headers=headers, timeout=120)

    try:
        data = res.json()
    except Exception:
        data = {"raw_text": res.text}

    return res.status_code, data


# =========================
# Streamlit 页面
# =========================

FEATURE_MODULES = [
    ("项目库", "管理项目、世界观、短片目标、常用比例和视觉风格。", "规划中"),
    ("角色库", "沉淀角色外貌、服装、性格、关键词、禁止项和参考图。", "规划中"),
    ("风格库", "保存风格关键词、色彩、光影、构图、渲染类型和适用范围。", "规划中"),
    ("提示词生成器", "根据项目、角色、场景、用途、镜头和光线生成 Image / Video Prompt。", "规划中"),
    ("出图任务", "后续通过 OpenAI Image API、Manual Provider 或 Browser Provider 进入结果库。", "预留"),
    ("视频任务", "当前可用 AIAI / Seedance2 中转接口测试文生视频与图生视频。", "可测试"),
    ("评分系统", "保存 overall、角色一致性、风格一致性、动作、镜头、可剪辑性等评分。", "规划中"),
    ("Skill 草稿", "从多次评分中总结可复用经验，先进入草稿，再人工合并。", "规划中"),
]

PROVIDER_ROWS = [
    ("API Provider", "OpenAI Image API / Seedance2 API", "官方和中转 API 统一走 Provider adapter。"),
    ("Manual Provider", "复制提示词 / 手动生成 / 手动上传", "MVP 阶段优先跑通创作闭环。"),
    ("Browser Provider", "Playwright / 独立 profile / semi-auto", "只做半自动，不绕过登录、验证码或付费限制。"),
]

PROMPT_REUSE_RULES = [
    "只有保存为 GenerationRun 并完成评分的提示词，才进入复用候选。",
    "优先复用 overallScore >= 8 且 shouldReuse=true 的提示词。",
    "shouldAvoid=true 的提示词默认只作为避坑案例。",
    "复用时保留角色核心特征、风格标签、镜头、光线和 negative prompt。",
    "每次复用记录来源 run_id，方便追溯成功经验。",
]

SKILL_RULES = [
    "重复出现 3 次以上的经验才生成 Skill 草稿。",
    "正向经验和避坑经验分开沉淀。",
    "每条规则保留来源 run_id。",
    "草稿输出到 data/skills-drafts/。",
    "人工审核后才能合并到 .claude/skills/。",
    "系统不能自动覆盖正式 Skill。",
]


def inject_page_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f6f8fb;
            color: #0f172a;
        }
        .block-container {
            max-width: 1280px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            color: #0f172a;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dbe2ec;
            border-radius: 6px;
            padding: 14px 16px;
        }
        div[data-testid="stMetric"] * {
            color: #0f172a !important;
        }
        div[data-testid="stMetricDelta"] * {
            color: #16a34a !important;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #dbe2ec;
            border-radius: 6px;
            background: #ffffff;
        }
        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] p {
            color: #0f172a;
        }
        .app-card {
            border: 1px solid #dbe2ec;
            border-radius: 6px;
            padding: 16px;
            background: #ffffff;
            min-height: 138px;
        }
        .app-card h3 {
            font-size: 1rem;
            margin: 0 0 0.55rem;
            color: #0f172a;
        }
        .app-card p {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.6;
            margin: 0;
        }
        .status-pill {
            display: inline-block;
            margin-top: 0.8rem;
            padding: 0.18rem 0.55rem;
            border-radius: 4px;
            background: #eef6ff;
            color: #1d4ed8;
            font-size: 0.78rem;
        }
        .quiet-note {
            border-left: 3px solid #0f766e;
            background: #f8fafc;
            padding: 0.8rem 1rem;
            color: #334155;
            line-height: 1.7;
            margin: 0.5rem 0 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_feature_cards():
    for row_start in range(0, len(FEATURE_MODULES), 4):
        cols = st.columns(4)
        for col, (title, body, status) in zip(cols, FEATURE_MODULES[row_start: row_start + 4]):
            with col:
                st.markdown(
                    f"""
                    <div class="app-card">
                        <h3>{title}</h3>
                        <p>{body}</p>
                        <span class="status-pill">{status}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_rule_list(items):
    for item in items:
        st.markdown(f"- {item}")


def add_url_field(payload, invalid_url_fields, field_name: str, field_value: str):
    field_value = (field_value or "").strip()
    if not field_value:
        return
    if is_http_url(field_value):
        payload[field_name] = field_value
    else:
        invalid_url_fields[field_name] = describe_url_value(field_value)


def build_payload(
    model,
    prompt,
    duration,
    resolution,
    aspect_ratio,
    fps,
    watermark,
    with_audio,
    async_mode,
    final_image,
    final_image_tail,
    video_url,
    audio_url,
    real_person_mode,
    draft,
    return_last_frame,
    generation_mode,
    camera_strength,
    movement_amplitude,
    camera_control,
    static_mask,
):
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "fps": fps,
        "watermark": watermark,
        "with_audio": with_audio,
        "async": async_mode,
    }
    invalid_url_fields = {}

    add_url_field(payload, invalid_url_fields, "image", final_image)
    add_url_field(payload, invalid_url_fields, "image_tail", final_image_tail)
    add_url_field(payload, invalid_url_fields, "video", video_url)
    add_url_field(payload, invalid_url_fields, "audio", audio_url)

    extra_body = {}
    if real_person_mode:
        extra_body["real_person_mode"] = True
    if draft:
        extra_body["draft"] = True
    if return_last_frame:
        extra_body["return_last_frame"] = True
    if generation_mode != 0:
        extra_body["generation_mode"] = generation_mode
    if camera_strength.strip():
        extra_body["camera_strength"] = camera_strength.strip()
    if movement_amplitude.strip():
        extra_body["movement_amplitude"] = movement_amplitude.strip()
    if camera_control.strip():
        extra_body["camera_control"] = camera_control.strip()
    if static_mask.strip():
        extra_body["static_mask"] = static_mask.strip()
    if extra_body:
        payload["extra_body"] = extra_body

    return payload, invalid_url_fields


st.set_page_config(
    page_title="AI 短片创作控制台 | AIAI 中转测试",
    layout="wide",
)
inject_page_style()

st.title("AI 短片创作控制台")
st.caption("AIAI / Seedance2 中转 API 测试工具已重构为控制台原型。项目正在开发中。")
st.markdown(
    """
    <div class="quiet-note">
    日常创作尽量在这个前端完成：项目设定、角色设定、风格模板、提示词生成、生成结果、评分复盘和 Skill 草稿沉淀。
    当前页面保留 AIAI 中转 API 测试能力，并展示后续控制台功能结构。
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("当前阶段", "Phase 1", "前端 MVP")
metric_cols[1].metric("Provider", "Seedance2", "AIAI 中转 API")
metric_cols[2].metric("工作模式", "Semi-auto", "先半自动")
metric_cols[3].metric("状态", "开发中", "功能扩展中")

tab_overview, tab_task, tab_reuse, tab_skill = st.tabs(
    ["控制台概览", "AIAI 视频任务", "提示词复用", "Skill 草稿规则"]
)

with tab_overview:
    st.subheader("功能模块")
    render_feature_cards()

    st.subheader("Provider 系统")
    st.dataframe(
        [
            {"类型": provider_type, "范围": scope, "说明": note}
            for provider_type, scope, note in PROVIDER_ROWS
        ],
        width="stretch",
        hide_index=True,
    )

    with st.expander("查看系统分层", expanded=False):
        st.code(
            "前端控制台 -> Provider 系统 -> 数据层 -> Agent 工作流\n"
            "前端是生产车间，Codex 是工程师，Claude Code 是经验管理员，用户是导演和审美决策者。",
            language="text",
        )

    with st.expander("查看开发顺序", expanded=False):
        render_rule_list(
            [
                "项目库 / 角色库 / 风格库",
                "提示词生成器",
                "手动上传结果",
                "评分系统",
                "OpenAI Image API",
                "Seedance2 Provider",
                "Provider adapter 抽象",
                "Browser Provider semi-auto",
                "Skill 草稿生成",
            ]
        )

with tab_task:
    st.subheader("AIAI / Seedance2 视频任务")
    st.caption("所有配置都收进下方控件。主流程只保留：填提示词、准备素材、创建任务、查询结果。")

    with st.expander("接口配置", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            api_key = st.text_input(
                "AIAI API Key",
                value=os.getenv("AIAI_API_KEY", ""),
                type="password",
            )
            base_url = st.text_input("Base URL", value="https://aiai.ac/api/v1")
        with c2:
            create_path = st.text_input(
                "创建任务路径",
                value="/videos/generations",
                help="如果失败，可以尝试 /video/generations 或 /videos",
            )
            query_path_template = st.text_input(
                "查询任务路径模板",
                value="/videos/generations/{id}",
                help="如果失败，可以尝试 /video/generations/{id}、/videos/{id}、/tasks/{id}",
            )
        st.code(
            "/videos/generations\n"
            "/video/generations\n"
            "/videos\n\n"
            "/videos/generations/{id}\n"
            "/video/generations/{id}\n"
            "/videos/{id}\n"
            "/tasks/{id}",
            language="text",
        )

    with st.expander("核心生成参数", expanded=True):
        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            model = st.selectbox(
                "model",
                ["doubao-seedance-2.0", "doubao-seedance-2.0-fast"],
                index=0,
            )
            prompt = st.text_area(
                "prompt",
                value="东方仙侠奇幻风，白发九尾狐、狐狸、红色华服长袍，云海仙宫背景，梦幻粉紫天空，整体唯美，电影感镜头，细腻光影",
                height=150,
            )
        with c2:
            duration = st.slider("duration", min_value=4, max_value=15, value=5, step=1)
            resolution = st.selectbox("resolution", ["480p", "720p", "1080p"], index=1)
            aspect_ratio = st.selectbox(
                "aspect_ratio",
                ["16:9", "9:16", "3:4", "4:3", "1:1", "21:9", "adaptive"],
                index=0,
            )
            fps = st.selectbox("fps", [24, 30], index=1)
            watermark = st.toggle("watermark", value=False)
            with_audio = st.toggle("with_audio", value=True)
            async_mode = st.toggle("async", value=True)

    st.session_state.setdefault("image_url_input", "")
    st.session_state.setdefault("image_tail_url_input", "")

    with st.expander("素材输入与公网 URL", expanded=False):
        st.info("AIAI 的素材字段只接受 http/https URL。本地图片需要先上传到公网临时图床。")
        public_upload_provider = st.selectbox(
            "本地图片转公网 URL 服务",
            ["Catbox（长期直链）", "tmpfiles.org（60 分钟）"],
            index=0,
        )
        col_first, col_tail = st.columns(2)
        with col_first:
            image_file = st.file_uploader(
                "首帧图片",
                type=["png", "jpg", "jpeg", "webp"],
                key="image_file",
            )
            if image_file is not None and st.button("上传首帧", key="upload_image_to_public"):
                with st.spinner("正在上传首帧图片..."):
                    try:
                        public_url = upload_to_public_host(image_file, public_upload_provider)
                    except Exception as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["image_url_input"] = public_url
                        st.success("首帧 URL 已填入")
            image_url = st.text_input(
                "image",
                placeholder="https://xxx.com/first-frame.png",
                key="image_url_input",
            )
        with col_tail:
            image_tail_file = st.file_uploader(
                "尾帧图片",
                type=["png", "jpg", "jpeg", "webp"],
                key="image_tail_file",
            )
            if image_tail_file is not None and st.button("上传尾帧", key="upload_image_tail_to_public"):
                with st.spinner("正在上传尾帧图片..."):
                    try:
                        public_url = upload_to_public_host(image_tail_file, public_upload_provider)
                    except Exception as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["image_tail_url_input"] = public_url
                        st.success("尾帧 URL 已填入")
            image_tail_url = st.text_input(
                "image_tail",
                placeholder="https://xxx.com/last-frame.png",
                key="image_tail_url_input",
            )
        video_url = st.text_input("video", value="", placeholder="https://xxx.com/reference.mp4")
        audio_url = st.text_input("audio", value="", placeholder="https://xxx.com/reference.mp3")

    with st.expander("高级参数 extra_body", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            real_person_mode = st.checkbox("real_person_mode", value=False)
            draft = st.checkbox("draft", value=False)
            return_last_frame = st.checkbox("return_last_frame", value=False)
            generation_mode = st.selectbox(
                "generation_mode",
                [0, 1, 2],
                index=0,
                format_func=lambda x: {0: "0：默认", 1: "1：运镜控制", 2: "2：笔刷"}[x],
            )
        with c2:
            camera_strength = st.text_input("camera_strength", value="")
            movement_amplitude = st.text_input("movement_amplitude", value="")
            camera_control = st.text_area("camera_control", value="", height=80)
            static_mask = st.text_area("static_mask", value="", height=80)

    final_image = image_url.strip()
    if not final_image and image_file is not None:
        final_image = f"本地上传文件：{image_file.name}"

    final_image_tail = image_tail_url.strip()
    if not final_image_tail and image_tail_file is not None:
        final_image_tail = f"本地上传文件：{image_tail_file.name}"

    payload, invalid_url_fields = build_payload(
        model,
        prompt,
        duration,
        resolution,
        aspect_ratio,
        fps,
        watermark,
        with_audio,
        async_mode,
        final_image,
        final_image_tail,
        video_url,
        audio_url,
        real_person_mode,
        draft,
        return_last_frame,
        generation_mode,
        camera_strength,
        movement_amplitude,
        camera_control,
        static_mask,
    )

    create_url = join_url(base_url, create_path)

    st.subheader("提交与查询")
    if invalid_url_fields:
        st.error("素材字段必须填写 http:// 或 https:// 开头的公网 URL。")
        st.json(invalid_url_fields)

    action_cols = st.columns([1, 1, 2])
    with action_cols[0]:
        create_clicked = st.button("创建任务", type="primary", width="stretch")
    with action_cols[1]:
        preview_open = st.toggle("请求体预览", value=False)
    with action_cols[2]:
        st.code(create_url, language="text")

    if preview_open:
        st.code(json.dumps(mask_large_values(payload), ensure_ascii=False, indent=2), language="json")

    if create_clicked:
        if not api_key:
            st.error("请先填写 AIAI API Key")
        elif not prompt.strip():
            st.error("请填写 prompt")
        elif invalid_url_fields:
            st.error("请先修正素材 URL。AIAI 不接受本地路径或 data URL。")
        else:
            with st.spinner("正在提交任务..."):
                status_code, data = post_json(create_url, api_key, payload)

            st.write(f"HTTP 状态码：`{status_code}`")
            st.json(data)

            task_id = extract_task_id(data)
            video_found = pick_video_url(data)

            if task_id:
                st.session_state["task_id"] = task_id
                st.success(f"任务 ID：{task_id}")
            if video_found:
                st.success("响应中已找到视频 URL")
                st.video(video_found)
                st.code(video_found, language="text")
            if not task_id and not video_found:
                st.warning("没有找到任务 ID，也没有找到视频 URL。可能是接口路径或请求体格式不匹配。")

    with st.expander("查询任务状态", expanded=False):
        task_id_input = st.text_input("任务 ID", value=st.session_state.get("task_id", ""))
        query_url = join_url(
            base_url,
            query_path_template.replace("{id}", task_id_input.strip() if task_id_input else "{id}"),
        )
        st.code(query_url, language="text")
        q1, q2, q3 = st.columns([1, 1, 1])
        with q1:
            query_once = st.button("查询一次", width="stretch")
        with q2:
            poll_times = st.number_input("轮询次数", min_value=1, max_value=60, value=20, step=1)
        with q3:
            poll_interval = st.number_input("间隔秒数", min_value=3, max_value=60, value=10, step=1)

        if query_once:
            if not api_key:
                st.error("请先填写 AIAI API Key")
            elif not task_id_input.strip():
                st.error("请填写任务 ID")
            else:
                with st.spinner("正在查询任务..."):
                    status_code, data = get_json(query_url, api_key)
                st.write(f"HTTP 状态码：`{status_code}`")
                st.json(data)
                video_found = pick_video_url(data)
                if video_found:
                    st.success("找到视频 URL")
                    st.video(video_found)
                    st.code(video_found, language="text")
                else:
                    st.info("暂未找到视频 URL，可能还在生成中，或者查询路径不对。")

        if st.button("自动轮询", width="stretch"):
            if not api_key:
                st.error("请先填写 AIAI API Key")
            elif not task_id_input.strip():
                st.error("请填写任务 ID")
            else:
                placeholder = st.empty()
                for i in range(int(poll_times)):
                    with st.spinner(f"第 {i + 1}/{poll_times} 次查询..."):
                        status_code, data = get_json(query_url, api_key)
                    placeholder.write(f"HTTP 状态码：`{status_code}`")
                    placeholder.json(data)
                    video_found = pick_video_url(data)
                    if video_found:
                        st.success("视频生成完成")
                        st.video(video_found)
                        st.code(video_found, language="text")
                        break
                    time.sleep(int(poll_interval))
                else:
                    st.warning("轮询结束，仍未找到视频 URL。请检查任务状态或查询路径。")

with tab_reuse:
    st.subheader("提示词复用与评分闭环")
    st.write("后续所有生成结果都会进入 GenerationRun，再进入 Review，最后决定是否复用或沉淀为避坑规则。")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 复用规则")
        render_rule_list(PROMPT_REUSE_RULES)
    with c2:
        st.markdown("#### 评分字段")
        st.dataframe(
            [
                {"类型": "图片", "字段": "overall / character / style / composition / lighting / detail"},
                {"类型": "视频", "字段": "overall / stability / motion / camera / continuity / editability"},
                {"类型": "反馈", "字段": "liked / problems / nextRule / shouldReuse / shouldAvoid / shouldMakeSkill"},
            ],
            width="stretch",
            hide_index=True,
        )

    with st.expander("复用候选记录结构", expanded=False):
        st.code(
            json.dumps(
                {
                    "run_id": "run_xxx",
                    "prompt": "reviewed prompt text",
                    "overallScore": 9,
                    "shouldReuse": True,
                    "shouldAvoid": False,
                    "nextRule": "下次保持角色核心特征和镜头语言",
                },
                ensure_ascii=False,
                indent=2,
            ),
            language="json",
        )

with tab_skill:
    st.subheader("Skill 草稿沉淀")
    st.write("Skill 不直接自动覆盖正式文件。重复出现的经验先生成草稿，人工审核后再进入正式 Skill。")
    render_rule_list(SKILL_RULES)

    st.subheader("当前 Skill 文件")
    st.dataframe(
        [
            {"Skill": "prompt-director", "用途": "根据项目、角色、场景和风格生成稳定提示词。"},
            {"Skill": "image2-character-prompt", "用途": "生成角色人设图提示词，保持身份一致性。"},
            {"Skill": "seedance2-video-prompt", "用途": "将首帧或图片提示词转换成视频提示词。"},
            {"Skill": "skill-curator", "用途": "从评分记录总结 Skill 草稿。"},
        ],
        width="stretch",
        hide_index=True,
    )

    with st.expander("Skill 草稿输出结构", expanded=False):
        st.code(
            "Skill 名称\n"
            "适用场景\n"
            "正向规则\n"
            "避坑规则\n"
            "Prompt 模板\n"
            "来源 run_id\n"
            "待人工确认事项",
            language="text",
        )
