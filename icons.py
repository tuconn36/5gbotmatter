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
    "huongdan": "❓", "chat": "💬", "app": "📲","download": "📥",
    "home": "🏠", "back": "🔙", "prev": "◀", "next": "▶", "done": "✅",
    "viettel": "🔴", "vina": "🔵", "mobi": "🟢",
    "t15kn": "📆", "tiktok": "🎵", "mxh100": "💪",
    "vina0": "💎", "tk30": "🚀",
    "khongnen": "🚫", "conen": "✅",
    "spark": "✨", "bolt": "⚡", "phone": "📱",
}

_enabled = os.environ.get("CUSTOM_ICONS", "1").strip().lower() not in {"0", "false", "off", "no"}
_force_fallback = contextvars.ContextVar("icons_force_fallback", default=False)

# ID gán nhanh lúc bot đang chạy (khi admin gửi emoji động cho bot).
# Mất khi bot khởi động lại; muốn giữ lâu dài thì dán vào icons.txt.
_overrides = {}


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


def _ids():
    """ID từ icons.txt, được ghi đè bởi ID gán nhanh lúc chạy."""
    return {**load_ids(), **_overrides}


def _custom_id(name):
    if not _enabled or _force_fallback.get():
        return None
    return _ids().get(name)


def custom_in_use():
    return _enabled and not _force_fallback.get() and bool(_ids())


def apply(ids):
    """Gán nhanh {tên_icon: custom_emoji_id} cho các nút (không cần khởi động lại)."""
    global _enabled
    _overrides.update({n: i for n, i in ids.items() if n in FALLBACKS})
    _enabled = True


def normalize_emoji(text):
    """Bỏ ký tự chọn kiểu hiển thị (U+FE0F/FE0E) để so khớp emoji."""
    return (text or "").replace("\ufe0f", "").replace("\ufe0e", "").strip()


def names_by_emoji():
    """{emoji đã chuẩn hoá: [tên icon]} - để ghép emoji động vào đúng icon."""
    result = {}
    for name, char in FALLBACKS.items():
        result.setdefault(normalize_emoji(char), []).append(name)
    return result


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
    emoji_id = _ids().get(name) if _enabled else None
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fb}</tg-emoji>'
    return fb


def plain_button(icon, label, **kwargs):
    """Nút KHÔNG có emoji thường.

    Icon đã có ID trong icons.txt -> hiện icon động trước chữ.
    Chưa có ID (hoặc Telegram từ chối) -> chỉ có chữ, không icon.
    """
    emoji_id = _custom_id(icon)
    if emoji_id:
        return InlineKeyboardButton(label, icon_custom_emoji_id=emoji_id, **kwargs)
    return InlineKeyboardButton(label, **kwargs)


def lead_icon(name):
    """Icon động đứng đầu dòng chữ (kèm 1 dấu cách); chưa có ID thì trả về chuỗi rỗng."""
    emoji_id = _ids().get(name) if _enabled else None
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{FALLBACKS[name]}</tg-emoji> '
    return ""
