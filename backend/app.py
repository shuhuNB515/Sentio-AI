"""Flask主应用 - AI视觉对话助手后端
Author: shuhuNB560 / shuhuNB515
"""
import uuid
import base64
import os
import bcrypt
from dotenv import load_dotenv

# 加载.env文件（override=True确保覆盖系统环境变量）
load_dotenv(override=True)

from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from config import Config
from services import (
    analyze_frame, compress_image,
    describe_scene, read_text, identify_objects, translate_scene, analyze_emotion,
    speech_to_text, text_to_speech,
    chat, update_vision_context, clear_session,
    check_rate_limit, record_usage, get_usage_stats,
    init_db, create_user, get_user_by_username, get_user_by_id,
    update_user_login, update_user_settings,
    create_conversation, get_user_conversations, get_conversation,
    update_conversation_title, delete_conversation, archive_conversation,
    add_message, get_conversation_messages,
    add_screenshot, get_user_screenshots
)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins="*")
jwt = JWTManager(app)

# 初始化数据库
init_db()

# ============ 认证接口 ============

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    if len(username) < 3 or len(username) > 20:
        return jsonify({"error": "用户名长度需在3-20之间"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码长度至少6位"}), 400

    if get_user_by_username(username):
        return jsonify({"error": "用户名已存在"}), 409

    # 随机头像颜色
    colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f43f5e", "#10b981", "#f59e0b", "#06b6d4"]
    import random
    avatar_color = random.choice(colors)

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_id = create_user(username, password_hash, avatar_color)

    token = create_access_token(identity=str(user_id))
    return jsonify({
        "token": token,
        "user": {"id": user_id, "username": username, "avatar_color": avatar_color}
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "")
    password = data.get("password", "")

    user = get_user_by_username(username)
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify({"error": "用户名或密码错误"}), 401

    update_user_login(user["id"])
    token = create_access_token(identity=str(user["id"]))
    return jsonify({
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "avatar_color": user["avatar_color"],
            "settings": user.get("settings", "{}")
        }
    })


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "avatar_color": user["avatar_color"],
        "settings": user.get("settings", "{}"),
        "created_at": user["created_at"],
        "last_login": user.get("last_login")
    })


@app.route("/api/auth/settings", methods=["PUT"])
@jwt_required()
def save_settings():
    user_id = int(get_jwt_identity())
    settings = request.json.get("settings", {})
    update_user_settings(user_id, settings)
    return jsonify({"status": "ok"})

# ============ 会话接口 ============

@app.route("/api/conversations", methods=["POST"])
@jwt_required()
def new_conversation():
    user_id = int(get_jwt_identity())
    conv_id = str(uuid.uuid4())
    title = request.json.get("title", "New Conversation")
    create_conversation(conv_id, user_id, title)
    return jsonify({"id": conv_id, "title": title})


@app.route("/api/conversations", methods=["GET"])
@jwt_required()
def list_conversations():
    user_id = int(get_jwt_identity())
    convs = get_user_conversations(user_id)
    return jsonify(convs)


@app.route("/api/conversations/<conv_id>", methods=["GET"])
@jwt_required()
def get_conv(conv_id):
    conv = get_conversation(conv_id)
    if not conv:
        return jsonify({"error": "会话不存在"}), 404
    messages = get_conversation_messages(conv_id)
    return jsonify({"conversation": conv, "messages": messages})


@app.route("/api/conversations/<conv_id>", methods=["PUT"])
@jwt_required()
def update_conv(conv_id):
    data = request.json
    if "title" in data:
        update_conversation_title(conv_id, data["title"])
    if data.get("archive"):
        archive_conversation(conv_id)
    return jsonify({"status": "ok"})


@app.route("/api/conversations/<conv_id>", methods=["DELETE"])
@jwt_required()
def remove_conv(conv_id):
    delete_conversation(conv_id)
    clear_session(conv_id)
    return jsonify({"status": "ok"})

# ============ 对话接口 ============

@app.route("/api/chat", methods=["POST"])
@jwt_required()
def chat_endpoint():
    client_id = request.remote_addr
    if not check_rate_limit(client_id):
        return jsonify({"error": "请求过于频繁，请稍后再试"}), 429

    data = request.json
    session_id = data.get("session_id")
    user_message = data.get("message", "")
    image_b64 = data.get("image")

    if not session_id or not user_message:
        return jsonify({"error": "缺少必要参数"}), 400

    try:
        # 保存用户消息
        add_message(session_id, "user", user_message, has_image=bool(image_b64))

        reply = chat(session_id, user_message, image_b64)
        record_usage("chat")

        # 保存AI回复
        add_message(session_id, "assistant", reply)

        # 自动更新会话标题（首条消息）
        conv = get_conversation(session_id)
        if conv and conv["title"] == "New Conversation":
            title = user_message[:30] + ("..." if len(user_message) > 30 else "")
            update_conversation_title(session_id, title)

        return jsonify({"reply": reply, "session_id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/multimodal", methods=["POST"])
@jwt_required()
def multimodal_endpoint():
    client_id = request.remote_addr
    if not check_rate_limit(client_id):
        return jsonify({"error": "请求过于频繁"}), 429

    data = request.json
    session_id = data.get("session_id")
    user_message = data.get("message", "")
    image_b64 = data.get("image")
    need_tts = data.get("tts", False)

    if not session_id:
        return jsonify({"error": "缺少session_id"}), 400

    try:
        if image_b64:
            description = analyze_frame(image_b64, "请简要描述画面内容。")
            update_vision_context(session_id, description)

        reply = chat(session_id, user_message, image_b64)
        record_usage("chat")

        add_message(session_id, "user", user_message, has_image=bool(image_b64))
        add_message(session_id, "assistant", reply)

        conv = get_conversation(session_id)
        if conv and conv["title"] == "New Conversation":
            title = user_message[:30] + ("..." if len(user_message) > 30 else "")
            update_conversation_title(session_id, title)

        result = {"reply": reply, "session_id": session_id}

        if need_tts and reply:
            try:
                audio_data = text_to_speech(reply)
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")
                result["audio"] = audio_b64
                record_usage("tts")
            except Exception:
                pass

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============ 快捷视觉功能 ============

@app.route("/api/vision/quick", methods=["POST"])
@jwt_required()
def vision_quick():
    """快捷视觉功能：describe/ocr/objects/translate/emotion"""
    client_id = request.remote_addr
    if not check_rate_limit(client_id):
        return jsonify({"error": "请求过于频繁"}), 429

    data = request.json
    image_b64 = data.get("image")
    action = data.get("action", "describe")
    session_id = data.get("session_id")

    if not image_b64:
        return jsonify({"error": "缺少图像数据"}), 400

    action_map = {
        "describe": describe_scene,
        "ocr": read_text,
        "objects": identify_objects,
        "translate": translate_scene,
        "emotion": analyze_emotion,
    }

    if action not in action_map:
        return jsonify({"error": f"不支持的操作: {action}"}), 400

    try:
        result = action_map[action](image_b64)
        record_usage("vision")

        # 保存到消息记录
        if session_id:
            action_names = {
                "describe": "场景描述", "ocr": "文字识别",
                "objects": "物体识别", "translate": "翻译", "emotion": "情绪分析"
            }
            add_message(session_id, "user", f"[{action_names[action]}]", has_image=True)
            add_message(session_id, "assistant", result)

        return jsonify({"result": result, "action": action})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============ 语音接口 ============

@app.route("/api/stt", methods=["POST"])
@jwt_required()
def stt_endpoint():
    if "audio" not in request.files:
        return jsonify({"error": "缺少音频文件"}), 400

    audio_file = request.files["audio"]
    audio_data = audio_file.read()

    try:
        text = speech_to_text(audio_data, audio_file.filename or "audio.webm")
        record_usage("stt")
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tts", methods=["POST"])
@jwt_required()
def tts_endpoint():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "缺少文本"}), 400

    try:
        audio_data = text_to_speech(text)
        record_usage("tts")
        return Response(audio_data, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============ 截图接口 ============

@app.route("/api/screenshots", methods=["POST"])
@jwt_required()
def save_screenshot():
    user_id = int(get_jwt_identity())
    data = request.json
    image_b64 = data.get("image", "")
    description = data.get("description", "")
    conv_id = data.get("conversation_id")

    if not image_b64:
        return jsonify({"error": "缺少图像数据"}), 400

    try:
        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        img_data = base64.b64decode(image_b64)
        with open(filepath, "wb") as f:
            f.write(img_data)

        sid = add_screenshot(user_id, filename, description, conv_id)
        return jsonify({"id": sid, "path": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/screenshots", methods=["GET"])
@jwt_required()
def list_screenshots():
    user_id = int(get_jwt_identity())
    screenshots = get_user_screenshots(user_id)
    return jsonify(screenshots)


@app.route("/api/screenshots/<path:filename>", methods=["GET"])
def get_screenshot(filename):
    filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype="image/jpeg")
    return jsonify({"error": "文件不存在"}), 404

# ============ 统计接口 ============

@app.route("/api/stats", methods=["GET"])
@jwt_required()
def stats_endpoint():
    return jsonify(get_usage_stats())


@app.route("/api/health", methods=["GET"])
def health_endpoint():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
