"""配置文件 - 管理所有API密钥和应用配置
Author: shuhuNB560 / shuhuNB515
"""
import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "data", "app.db"))

    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # 模型选择 (MIMO API)
    VISION_MODEL = os.getenv("VISION_MODEL", "mimo-v2-omni")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "mimo-v2-flash")
    STT_MODEL = os.getenv("STT_MODEL", "mimo-v2.5-asr")
    TTS_MODEL = os.getenv("TTS_MODEL", "mimo-v2.5-tts")
    TTS_VOICE = os.getenv("TTS_VOICE", "alloy")

    # 成本控制参数
    FRAME_SAMPLE_INTERVAL = int(os.getenv("FRAME_SAMPLE_INTERVAL", "5"))
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "512"))
    IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY", "70"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
    VAD_SILENCE_THRESHOLD = float(os.getenv("VAD_SILENCE_THRESHOLD", "0.01"))
    VAD_SILENCE_DURATION = float(os.getenv("VAD_SILENCE_DURATION", "1.5"))

    # 限流
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,https://shuhuNB515.github.io,http://shuhu.me,https://shuhu.me")

    # 截图存储
    SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "data", "screenshots")
