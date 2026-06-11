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

st.set_page_config(
    page_title="AIAI Seedance2 本地前端",
    layout="wide"
)

st.title("AIAI Seedance2 本地前端测试工具")

st.caption("适配参数：model / prompt / image / image_tail / video / audio / duration / resolution / aspect_ratio / fps / watermark / with_audio / async / extra_body")

# -------------------------
# 侧边栏：接口配置
# -------------------------

with st.sidebar:
    st.header("接口配置")

    api_key = st.text_input(
        "AIAI API Key",
        value=os.getenv("AIAI_API_KEY", ""),
        type="password"
    )

    base_url = st.text_input(
        "Base URL",
        value="https://aiai.ac/api/v1"
    )

    create_path = st.text_input(
        "创建任务路径",
        value="/videos/generations",
        help="如果失败，可以尝试 /video/generations 或 /videos"
    )

    query_path_template = st.text_input(
        "查询任务路径模板",
        value="/videos/generations/{id}",
        help="如果失败，可以尝试 /video/generations/{id}、/videos/{id}、/tasks/{id}"
    )

    st.divider()

    st.markdown("### 常用备用路径")

    st.code(
        "/videos/generations\n"
        "/video/generations\n"
        "/videos\n"
        "\n"
        "/videos/generations/{id}\n"
        "/video/generations/{id}\n"
        "/videos/{id}\n"
        "/tasks/{id}",
        language="text"
    )


# -------------------------
# 主区域：参数
# -------------------------

left, right = st.columns([1.05, 0.95])

with left:
    st.subheader("核心参数")

    model = st.selectbox(
        "model",
        [
            "doubao-seedance-2.0",
            "doubao-seedance-2.0-fast",
        ],
        index=0
    )

    prompt = st.text_area(
        "prompt",
        value="东方仙侠奇幻风，白发九尾狐、狐狸、红色华服长袍，云海仙宫背景，梦幻粉紫天空，整体唯美，电影感镜头，细腻光影",
        height=140
    )

    duration = st.slider(
        "duration：时长，4-15 秒",
        min_value=4,
        max_value=15,
        value=5,
        step=1
    )

    resolution = st.selectbox(
        "resolution",
        ["480p", "720p", "1080p"],
        index=1
    )

    aspect_ratio = st.selectbox(
        "aspect_ratio",
        ["16:9", "9:16", "3:4", "4:3", "1:1", "21:9", "adaptive"],
        index=0
    )

    fps = st.selectbox(
        "fps",
        [24, 30],
        index=1
    )

    watermark = st.checkbox(
        "watermark：是否添加 AI 生成水印",
        value=False
    )

    with_audio = st.checkbox(
        "with_audio：是否生成音效",
        value=True,
        help="截图说明：Seedance 默认带音频"
    )

    async_mode = st.checkbox(
        "async：是否异步生成",
        value=True,
        help="截图说明：推荐 true"
    )


with right:
    st.subheader("素材 URL / 本地上传")

    st.info("AIAI 返回的错误显示：素材必须是 http/https 公网 URL。可以先把本地图片上传到公网临时图床，再自动填入 image / image_tail。")
    st.caption("第三方图床会公开托管文件，请不要上传隐私或敏感素材。tmpfiles 链接约 60 分钟后失效。")

    st.session_state.setdefault("image_url_input", "")
    st.session_state.setdefault("image_tail_url_input", "")

    public_upload_provider = st.selectbox(
        "本地图片转公网 URL 服务",
        ["Catbox（长期直链）", "tmpfiles.org（60 分钟）"],
        index=0
    )

    image_file = st.file_uploader(
        "上传首帧图片",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_file"
    )

    if image_file is not None and st.button("上传首帧到公网 URL", key="upload_image_to_public"):
        with st.spinner("正在上传首帧图片..."):
            try:
                public_url = upload_to_public_host(image_file, public_upload_provider)
            except Exception as exc:
                st.error(str(exc))
            else:
                st.session_state["image_url_input"] = public_url
                st.success("首帧图片已上传，URL 已填入 image")
                st.code(public_url, language="text")

    image_url = st.text_input(
        "image：首帧图片 URL",
        placeholder="https://xxx.com/first-frame.png",
        key="image_url_input"
    )

    image_tail_file = st.file_uploader(
        "上传尾帧图片",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_tail_file"
    )

    if image_tail_file is not None and st.button("上传尾帧到公网 URL", key="upload_image_tail_to_public"):
        with st.spinner("正在上传尾帧图片..."):
            try:
                public_url = upload_to_public_host(image_tail_file, public_upload_provider)
            except Exception as exc:
                st.error(str(exc))
            else:
                st.session_state["image_tail_url_input"] = public_url
                st.success("尾帧图片已上传，URL 已填入 image_tail")
                st.code(public_url, language="text")

    image_tail_url = st.text_input(
        "image_tail：尾帧图片 URL",
        placeholder="https://xxx.com/last-frame.png",
        key="image_tail_url_input"
    )

    video_url = st.text_input(
        "video：参考视频 URL，用于视频编辑/延长",
        value="",
        placeholder="https://xxx.com/reference.mp4"
    )

    audio_url = st.text_input(
        "audio：参考音频 URL",
        value="",
        placeholder="https://xxx.com/reference.mp3"
    )


# -------------------------
# 高级参数 extra_body
# -------------------------

st.subheader("额外参数 extra_body")

with st.expander("展开高级控制参数", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        real_person_mode = st.checkbox(
            "extra_body.real_person_mode：真人模式",
            value=False,
            help="开启真人模式，无需手动调用素材接口对含真人的图片/视频/音频进行转白"
        )

        draft = st.checkbox(
            "extra_body.draft：是否生成样片",
            value=False
        )

        return_last_frame = st.checkbox(
            "extra_body.return_last_frame：是否返回最后一帧图片",
            value=False
        )

        generation_mode = st.selectbox(
            "extra_body.generation_mode",
            [0, 1, 2],
            index=0,
            format_func=lambda x: {
                0: "0：默认模式",
                1: "1：运镜控制模式",
                2: "2：笔刷模式"
            }[x]
        )

    with col2:
        camera_strength = st.text_input(
            "extra_body.camera_strength：镜头运动强度",
            value="",
            placeholder="例如：low / medium / high，具体以 AIAI 支持值为准"
        )

        movement_amplitude = st.text_input(
            "extra_body.movement_amplitude：运动幅度",
            value="",
            placeholder="例如：small / medium / large，具体以 AIAI 支持值为准"
        )

        camera_control = st.text_area(
            "extra_body.camera_control：镜头控制描述",
            value="",
            placeholder="例如：镜头缓慢推进，轻微环绕，低角度仰拍",
            height=80
        )

        static_mask = st.text_area(
            "extra_body.static_mask：静态笔刷",
            value="",
            placeholder="如果接口要求 mask URL / base64 / 特定格式，在这里填写",
            height=80
        )


# -------------------------
# 构造请求体
# -------------------------

final_image = image_url.strip()
if not final_image and image_file is not None:
    final_image = f"本地上传文件：{image_file.name}"

final_image_tail = image_tail_url.strip()
if not final_image_tail and image_tail_file is not None:
    final_image_tail = f"本地上传文件：{image_tail_file.name}"

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

def add_url_field(field_name: str, field_value: str):
    field_value = (field_value or "").strip()
    if not field_value:
        return
    if is_http_url(field_value):
        payload[field_name] = field_value
    else:
        invalid_url_fields[field_name] = describe_url_value(field_value)


add_url_field("image", final_image)
add_url_field("image_tail", final_image_tail)
add_url_field("video", video_url)
add_url_field("audio", audio_url)

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


# -------------------------
# 请求体预览
# -------------------------

st.subheader("请求体预览")

if invalid_url_fields:
    st.error("素材字段必须填写 http:// 或 https:// 开头的公网 URL。请修正下面这些字段后再提交。")
    st.json(invalid_url_fields)

st.code(
    json.dumps(mask_large_values(payload), ensure_ascii=False, indent=2),
    language="json"
)


# -------------------------
# 创建任务
# -------------------------

create_url = join_url(base_url, create_path)

st.subheader("创建视频任务")

st.write("创建任务 URL：")
st.code(create_url, language="text")

if st.button("创建任务", type="primary"):
    if not api_key:
        st.error("请先填写 AIAI API Key")
    elif not prompt.strip():
        st.error("请填写 prompt")
    elif invalid_url_fields:
        st.error("请先修正素材 URL。AIAI 不接受本地路径或 data URL，只接受 http/https 公网链接。")
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


# -------------------------
# 查询任务
# -------------------------

st.subheader("查询任务")

task_id_input = st.text_input(
    "任务 ID",
    value=st.session_state.get("task_id", "")
)

query_url = join_url(base_url, query_path_template.replace("{id}", task_id_input.strip() if task_id_input else "{id}"))

st.write("查询任务 URL：")
st.code(query_url, language="text")

col_query, col_poll = st.columns([1, 1])

with col_query:
    if st.button("查询一次"):
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


with col_poll:
    poll_times = st.number_input(
        "自动轮询次数",
        min_value=1,
        max_value=60,
        value=20,
        step=1
    )

    poll_interval = st.number_input(
        "轮询间隔秒数",
        min_value=3,
        max_value=60,
        value=10,
        step=1
    )

    if st.button("自动轮询"):
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
