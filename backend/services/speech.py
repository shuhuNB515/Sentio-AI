"""语音服务 - 语音识别(STT)和语音合成(TTS)
Author: shuhuNB560 / shuhuNB515
"""
import base64
import io
import os
import tempfile
import requests
from openai import OpenAI
from config import Config

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL, organization='')
    return _client

def speech_to_text(audio_data: bytes, filename: str = "audio.webm") -> str:
    """语音转文字 - 使用mimo-v2.5-asr模型"""
    client = _get_client()

    # 自动检测音频格式（通过magic bytes，不依赖文件名）
    ext = _detect_audio_format(audio_data)
    mime_type = f"audio/{ext}" if ext != "webm" else "audio/webm"
    audio_b64 = base64.b64encode(audio_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{audio_b64}"

    print(f"[STT] 检测格式: {ext}, 大小: {len(audio_data)} bytes")

    try:
        # mimo ASR使用chat/completions接口
        response = client.chat.completions.create(
            model=Config.STT_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "input_audio", "input_audio": {"data": data_url, "format": ext}}
                ]
            }],
            max_tokens=500,
        )
        result = response.choices[0].message.content or ""
        print(f"[STT] 识别结果: {result}")
        return result.strip()
    except Exception as e:
        print(f"[STT] 识别失败: {e}")
        return ""


def _detect_audio_format(data: bytes) -> str:
    """通过文件头magic bytes检测音频格式"""
    if len(data) < 4:
        return "webm"
    if data[:4] == b'RIFF':
        return "wav"
    if data[:4] == b'\x1a\x45\xdf\xa3':
        return "webm"
    if data[:3] == b'ID3' or data[:2] == b'\xff\xfb' or data[:2] == b'\xff\xf3':
        return "mp3"
    if data[:4] == b'fLaC':
        return "flac"
    if data[:4] == b'OggS':
        return "ogg"
    return "wav"

def text_to_speech(text: str) -> bytes:
    """文字转语音 - 使用mimo-v2.5-tts模型"""
    client = _get_client()

    # 尝试标准OpenAI audio/speech接口
    try:
        response = client.audio.speech.create(
            model=Config.TTS_MODEL,
            voice=Config.TTS_VOICE,
            input=text,
        )
        return response.content
    except Exception:
        pass

    # 使用mimo chat/completions接口实现TTS
    try:
        response = client.chat.completions.create(
            model=Config.TTS_MODEL,
            messages=[
                {"role": "assistant", "content": text}
            ],
            audio={
                "format": "mp3",
                "voice": "mimo_default"
            }
        )
        audio_data = response.choices[0].message.audio.data
        return base64.b64decode(audio_data)
    except Exception:
        pass

    # 最后尝试直接HTTP请求
    try:
        resp = requests.post(
            f"{Config.OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": Config.TTS_MODEL,
                "messages": [
                    {"role": "assistant", "content": text}
                ],
                "audio": {
                    "format": "mp3",
                    "voice": "mimo_default"
                }
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            audio_data = data["choices"][0]["message"]["audio"]["data"]
            return base64.b64decode(audio_data)
    except Exception:
        pass

    # 所有方法都失败，返回空音频
    return b""

def detect_silence(audio_data: bytes, threshold: float = None) -> bool:
    """简单的VAD（语音活动检测）- 检测音频是否为静音"""
    import struct
    try:
        threshold = threshold or Config.VAD_SILENCE_THRESHOLD
        # 简单RMS能量检测
        if len(audio_data) < 2:
            return True
        # 尝试解析为16bit PCM
        samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data[:len(audio_data)//2*2])
        if not samples:
            return True
        rms = (sum(s*s for s in samples) / len(samples)) ** 0.5 / 32768.0
        return rms < threshold
    except Exception:
        return False
