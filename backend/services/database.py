"""数据库模块 - SQLite + 用户/会话/消息持久化
Author: shuhuNB560 / shuhuNB515
"""
import sqlite3
import os
import json
from datetime import datetime
from config import Config

def _ensure_dirs():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)

def get_db():
    _ensure_dirs()
    conn = sqlite3.connect(Config.DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_color TEXT DEFAULT '#6366f1',
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT,
            settings TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT DEFAULT 'New Conversation',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            is_archived INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            has_image INTEGER DEFAULT 0,
            image_path TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS screenshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            conversation_id TEXT,
            image_path TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
        CREATE INDEX IF NOT EXISTS idx_screenshots_user ON screenshots(user_id);
    """)
    conn.commit()
    conn.close()

# ============ 用户操作 ============

def create_user(username: str, password_hash: str, avatar_color: str = "#6366f1") -> int:
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, avatar_color) VALUES (?, ?, ?)",
        (username, password_hash, avatar_color)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def get_user_by_username(username: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_login(user_id: int):
    conn = get_db()
    conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def update_user_settings(user_id: int, settings: dict):
    conn = get_db()
    conn.execute("UPDATE users SET settings = ? WHERE id = ?", (json.dumps(settings), user_id))
    conn.commit()
    conn.close()

# ============ 会话操作 ============

def create_conversation(conv_id: str, user_id: int, title: str = "New Conversation"):
    conn = get_db()
    conn.execute(
        "INSERT INTO conversations (id, user_id, title) VALUES (?, ?, ?)",
        (conv_id, user_id, title)
    )
    conn.commit()
    conn.close()

def get_user_conversations(user_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM conversations WHERE user_id = ? AND is_archived = 0 ORDER BY updated_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_conversation(conv_id: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_conversation_title(conv_id: str, title: str):
    conn = get_db()
    conn.execute(
        "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
        (title, datetime.now().isoformat(), conv_id)
    )
    conn.commit()
    conn.close()

def delete_conversation(conv_id: str):
    conn = get_db()
    conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()

def archive_conversation(conv_id: str):
    conn = get_db()
    conn.execute("UPDATE conversations SET is_archived = 1 WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()

# ============ 消息操作 ============

def add_message(conv_id: str, role: str, content: str, has_image: bool = False, image_path: str = None) -> int:
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO messages (conversation_id, role, content, has_image, image_path) VALUES (?, ?, ?, ?, ?)",
        (conv_id, role, content, int(has_image), image_path)
    )
    conn.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), conv_id)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def get_conversation_messages(conv_id: str, limit: int = 50) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT ?",
        (conv_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ============ 截图操作 ============

def add_screenshot(user_id: int, image_path: str, description: str = "", conv_id: str = None) -> int:
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO screenshots (user_id, conversation_id, image_path, description) VALUES (?, ?, ?, ?)",
        (user_id, conv_id, image_path, description)
    )
    conn.commit()
    sid = cursor.lastrowid
    conn.close()
    return sid

def get_user_screenshots(user_id: int, limit: int = 20) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM screenshots WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
