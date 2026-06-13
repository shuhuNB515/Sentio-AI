"""成本控制服务 - 限流、缓存统计、用量追踪"""
import time
from collections import defaultdict
from config import Config

# 限流记录
_rate_limit_store = defaultdict(list)

# 用量统计
_usage_stats = {
    "vision_calls": 0,
    "chat_calls": 0,
    "stt_calls": 0,
    "tts_calls": 0,
    "cache_hits": 0,
    "total_tokens_saved": 0,
}

def check_rate_limit(client_id: str) -> bool:
    """检查是否超过速率限制"""
    now = time.time()
    window = 60  # 1分钟窗口
    limit = Config.RATE_LIMIT_PER_MINUTE

    # 清理过期记录
    _rate_limit_store[client_id] = [
        t for t in _rate_limit_store[client_id] if now - t < window
    ]

    if len(_rate_limit_store[client_id]) >= limit:
        return False

    _rate_limit_store[client_id].append(now)
    return True

def record_usage(service: str, tokens_saved: int = 0):
    """记录API使用量"""
    key = f"{service}_calls"
    if key in _usage_stats:
        _usage_stats[key] += 1
    _usage_stats["total_tokens_saved"] += tokens_saved

def record_cache_hit():
    """记录缓存命中"""
    _usage_stats["cache_hits"] += 1

def get_usage_stats() -> dict:
    """获取用量统计"""
    return _usage_stats.copy()

def should_send_frame(session_id: str, last_frame_time: float) -> bool:
    """判断是否需要发送新帧（帧采样策略）"""
    now = time.time()
    interval = Config.FRAME_SAMPLE_INTERVAL
    return (now - last_frame_time) >= interval

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """估算API调用成本（美元）"""
    pricing = {
        "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},
        "gpt-4o-mini": {"input": 0.00015 / 1000, "output": 0.0006 / 1000},
        "whisper-1": {"input": 0.006 / 60, "output": 0},  # 按分钟计费
        "tts-1": {"input": 0.015 / 1000, "output": 0},  # 按字符计费
    }
    if model not in pricing:
        return 0.0
    p = pricing[model]
    return input_tokens * p["input"] + output_tokens * p["output"]
