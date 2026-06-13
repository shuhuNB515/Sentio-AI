"""视觉理解服务 - 处理摄像头图像分析 + 快捷视觉功能
Author: shuhuNB560 / shuhuNB515
"""
import base64
import io
import time
import hashlib
from PIL import Image
from openai import OpenAI
from config import Config

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
    return _client

_cache = {}
_cache_ttl = Config.CACHE_TTL  # 默认300秒

def _cache_key(image_b64: str) -> str:
    return hashlib.md5(image_b64[:500].encode()).hexdigest()

def _cache_get(key: str) -> str | None:
    """缓存查询，自动清除过期条目"""
    if key in _cache:
        val, ts = _cache[key]
        if time.time() - ts < _cache_ttl:
            return val
        del _cache[key]
    return None

def _cache_set(key: str, val: str):
    _cache[key] = (val, time.time())

def compress_image(image_b64: str) -> str:
    try:
        image_data = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(image_data))
        max_size = Config.MAX_IMAGE_SIZE
        ratio = min(max_size / max(img.size), 1.0)
        if ratio < 1.0:
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=Config.IMAGE_QUALITY)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception:
        return image_b64

def _vision_call(messages: list, max_tokens: int = 300) -> str:
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=Config.VISION_MODEL,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception:
        # 某些模型只支持流式返回
        stream = client.chat.completions.create(
            model=Config.VISION_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )
        result = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                result += chunk.choices[0].delta.content
        return result

def analyze_frame(image_b64: str, prompt: str = "请描述你看到的画面内容。") -> str:
    key = _cache_key(image_b64)
    cached = _cache_get(key)
    if cached:
        return cached

    compressed = compress_image(image_b64)
    result = _vision_call([{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    }])
    _cache_set(key, result)
    return result

def analyze_frame_for_chat(image_b64: str, user_message: str, history: list) -> str:
    compressed = compress_image(image_b64)
    messages = []
    for msg in history[-Config.MAX_CONVERSATION_HISTORY:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": user_message},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    })
    return _vision_call(messages, 500)

# ============ 快捷视觉功能 ============

def describe_scene(image_b64: str) -> str:
    """场景描述 - 详细描述当前画面"""
    compressed = compress_image(image_b64)
    return _vision_call([{
        "role": "system",
        "content": "你是一个视觉描述专家。请用生动、详细的语言描述你看到的场景，包括环境、人物、物体、光线、氛围等。用中文回答，3-5句话。"
    }, {
        "role": "user",
        "content": [
            {"type": "text", "text": "请详细描述这个场景"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    }], 400)

def read_text(image_b64: str) -> str:
    """文字识别 - 识别画面中的文字"""
    compressed = compress_image(image_b64)
    return _vision_call([{
        "role": "system",
        "content": "你是一个OCR专家。请识别并提取画面中所有可见的文字内容，保持原始格式和排版。如果画面中没有文字，请说明。用中文回答。"
    }, {
        "role": "user",
        "content": [
            {"type": "text", "text": "请识别画面中的所有文字"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    }], 500)

def identify_objects(image_b64: str) -> str:
    """物体识别 - 识别画面中的物体"""
    compressed = compress_image(image_b64)
    return _vision_call([{
        "role": "system",
        "content": "你是一个物体识别专家。请列出画面中所有可识别的物体和人物，对每个物体简要描述其位置、颜色、状态。用中文回答，使用列表格式。"
    }, {
        "role": "user",
        "content": [
            {"type": "text", "text": "请识别画面中的所有物体"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    }], 400)

def translate_scene(image_b64: str) -> str:
    """场景翻译 - 翻译画面中的外文"""
    compressed = compress_image(image_b64)
    return _vision_call([{
        "role": "system",
        "content": "你是一个翻译专家。请识别画面中的所有外文文字，并将其翻译成中文。如果画面中没有外文，请描述画面内容并说明。格式：原文 -> 译文"
    }, {
        "role": "user",
        "content": [
            {"type": "text", "text": "请翻译画面中的文字"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    }], 400)

def analyze_emotion(image_b64: str) -> str:
    """情绪分析 - 分析画面中人物的情绪"""
    compressed = compress_image(image_b64)
    return _vision_call([{
        "role": "system",
        "content": "你是一个情绪分析专家。请分析画面中人物的表情、姿态和情绪状态。如果画面中没有人物，请描述场景的整体氛围。用中文回答。"
    }, {
        "role": "user",
        "content": [
            {"type": "text", "text": "请分析画面中的情绪"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{compressed}", "detail": "low"}}
        ]
    }], 300)
