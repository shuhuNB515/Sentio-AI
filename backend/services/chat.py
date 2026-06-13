"""AI对话服务 - 管理对话上下文和模型路由"""
import time
from openai import OpenAI
from config import Config

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
    return _client

# 会话存储（生产环境应使用Redis等）
_sessions = {}

def _get_session(session_id: str) -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "history": [],
            "last_vision_summary": "",
            "last_frame_time": 0,
            "created_at": time.time()
        }
    return _sessions[session_id]

def _trim_history(history: list) -> list:
    """裁剪对话历史，控制token消耗"""
    max_rounds = Config.MAX_CONVERSATION_HISTORY
    if len(history) > max_rounds * 2:
        return history[-(max_rounds * 2):]
    return history

def _select_model(has_image: bool) -> str:
    """模型路由：根据是否包含图像选择模型"""
    if has_image:
        return Config.VISION_MODEL
    return Config.CHAT_MODEL  # 纯文本用更便宜的模型

def chat(session_id: str, user_message: str, image_b64: str = None) -> str:
    """处理对话请求"""
    session = _get_session(session_id)
    has_image = image_b64 is not None

    # 构建消息列表
    from datetime import date
    messages = [
        {
            "role": "system",
            "content": (
                f"You are MiMo, an AI assistant developed by Xiaomi. Today is {date.today()}. "
                "You can see the user's camera view and hear what they say. "
                "Please give natural, accurate and helpful replies based on visual content and conversation context. "
                "Keep replies concise, usually no more than 3 sentences. Reply in Chinese."
            )
        }
    ]

    # 添加视觉上下文摘要
    if session["last_vision_summary"]:
        messages.append({
            "role": "system",
            "content": f"[当前画面描述] {session['last_vision_summary']}"
        })

    # 添加对话历史
    for msg in session["history"]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 当前用户消息
    if has_image:
        from services.vision import compress_image
        compressed = compress_image(image_b64)
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{compressed}",
                        "detail": "low"
                    }
                }
            ]
        })
    else:
        messages.append({"role": "user", "content": user_message})

    # 选择模型
    model = _select_model(has_image)

    client = _get_client()

    # 尝试非流式，失败则用流式
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e1:
        print(f"[chat] 非流式调用失败: {e1}, 尝试流式...")
        # 某些模型只支持流式返回
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                stream=True,
            )
            reply = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    reply += chunk.choices[0].delta.content
        except Exception as e2:
            print(f"[chat] 流式调用也失败: {e2}")
            raise e1

    if not reply or not reply.strip():
        reply = "抱歉，我暂时无法回答，请重试。"

    # 更新会话历史
    if has_image:
        session["history"].append({"role": "user", "content": f"[附带图片] {user_message}"})
    else:
        session["history"].append({"role": "user", "content": user_message})
    session["history"].append({"role": "assistant", "content": reply})
    session["history"] = _trim_history(session["history"])

    return reply

def update_vision_context(session_id: str, summary: str):
    """更新视觉上下文摘要"""
    session = _get_session(session_id)
    session["last_vision_summary"] = summary
    session["last_frame_time"] = time.time()

def clear_session(session_id: str):
    """清除会话"""
    if session_id in _sessions:
        del _sessions[session_id]

def get_session_info(session_id: str) -> dict:
    """获取会话信息"""
    session = _get_session(session_id)
    return {
        "history_length": len(session["history"]),
        "last_frame_time": session["last_frame_time"],
    }
