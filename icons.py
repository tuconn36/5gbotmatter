"""Icon của bot: emoji động (custom emoji) có dự phòng emoji thường."""

import contextlib
import contextvars
import logging
import os
from functools import lru_cache

from telegram import InlineKeyboardButton

from config import BASE_DIR

logger = logging.getLogger(__name__)

ICON_FILE = os.path.join(BASE_DIR, "icons.txt")

FALLBACKS = {
    "android": "🤖", "ios": "🍎", "windows": "🖥️",
    "gonen": "📶", "sni": "🔁", "thueid": "🔐", "hotro": "🎧",
    "huongdan": "❓", "chat": "💬", "app": "📲",
    "home": "🏠", "back": "🔙", "prev": "◀", "next": "▶", "done": "✅",
    "viettel": "🔴", "vina": "🔵", "mobi": "🟢",
    "t15kn": "📆", "tiktok": "🎵", "mxh100": "💪",
    "vina0": "💎", "tk30": "🚀",
    "khongnen": "🚫", "conen": "✅",
    "spark": "✨", "bolt": "⚡", "phone": "📱",
}

_enabled = os.environ.get("CUSTOM_ICONS", "1").strip().lower() not in {"0", "false", "off", "no"}
_force_fallback = contextvars.ContextVar("icons_force_fallback", default=False)


@lru_cache(maxsize=1)
def load_ids():
    """Đọc icons.txt -> {tên_icon: custom_emoji_id}."""
    ids = {}
    try:
        with open(ICON_FILE, encoding="utf-8-sig") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, _, value = line.partition("=")
                name, value = name.strip(), value.strip()
                if not value:
                    continue
                if name not in FALLBACKS:
                    logger.warning("icons.txt: bỏ qua tên icon lạ %r", name)
                    continue
                if not value.isdigit():
                    logger.warning("icons.txt: ID của %r phải là số", name)
                    continue
                ids[name] = value
    except OSError:
        pass
    return ids


def _custom_id(name):
    if not _enabled or _force_fallback.get():
        return None
    return load_ids().get(name)


def custom_in_use():
    return _enabled and not _force_fallback.get() and bool(load_ids())


def disable():
    global _enabled
    _enabled = False


@contextlib.contextmanager
def fallback():
    token = _force_fallback.set(True)
    try:
        yield
    finally:
        _force_fallback.reset(token)


def button(icon, label, **kwargs):
    """Nút có icon: custom emoji nếu có, không thì emoji thường."""
    emoji_id = _custom_id(icon)
    if emoji_id:
        return InlineKeyboardButton(label, icon_custom_emoji_id=emoji_id, **kwargs)
    return InlineKeyboardButton(f"{FALLBACKS[icon]} {label}", **kwargs)


def tg_emoji(name):
    """Icon trong nội dung tin nhắn (HTML)."""
    fb = FALLBACKS[name]
    emoji_id = load_ids().get(name) if _enabled else None
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fb}</tg-emoji>'
    return fb
