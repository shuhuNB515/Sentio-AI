# Sentio-AI services package
# Author: shuhuNB560 / shuhuNB515
from services.vision import (
    analyze_frame, analyze_frame_for_chat, compress_image,
    describe_scene, read_text, identify_objects, translate_scene, analyze_emotion
)
from services.speech import speech_to_text, text_to_speech, detect_silence
from services.chat import chat, update_vision_context, clear_session, get_session_info
from services.cost_control import (
    check_rate_limit, record_usage, get_usage_stats,
    should_send_frame, estimate_cost
)
from services.database import (
    init_db, create_user, get_user_by_username, get_user_by_id,
    update_user_login, update_user_settings,
    create_conversation, get_user_conversations, get_conversation,
    update_conversation_title, delete_conversation, archive_conversation,
    add_message, get_conversation_messages,
    add_screenshot, get_user_screenshots
)
