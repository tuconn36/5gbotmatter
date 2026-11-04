"""Cấu hình bot: đọc biến môi trường, file .env và các hằng số."""

import logging
import os
import re

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOT_NAME = "5G MATTER"

# Website bán gói và tài khoản quản trị viên (dùng cho nút / liên kết).
WEBSITE = "https://5gmatter.site/"
ADMIN_USERNAME = "tune789"
ADMIN_URL = f"https://t.me/{ADMIN_USERNAME}"

MISSING_TOKEN_MESSAGE = (
    "Chưa cấu hình BOT_TOKEN trong biến môi trường!\n"
    "- Local: đặt BOT_TOKEN=... trong file .env hoặc trong terminal\n"
    "- GitHub Actions: thêm secret BOT_TOKEN trong Settings > Secrets"
)

# Token Telegram hợp lệ: <bot_id>:<chuỗi bí mật>
TOKEN_PATTERN = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{30,}$")


def _read_env_file(path):
    """Đọc một file .env và trả về dict các biến trong đó."""
    values = {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].strip()
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                if key:
                    values[key] = value
    except OSError:
        pass
    return values


def _load_dotenv():
    """Nạp biến từ file .env (nếu có), không cần thư viện ngoài.

    Biến đã có trong môi trường (vd GitHub Secrets) luôn được ưu tiên.

    LƯU Ý BẢO MẬT: chỉ đọc .env (đã nằm trong .gitignore). Tuyệt đối
    không đọc .env.example làm nguồn dự phòng, vì file đó được commit
    lên Git - để token thật ở đó là làm lộ token.
    """
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.isfile(env_path):
        return
    for key, value in _read_env_file(env_path).items():
        if key not in os.environ:
            os.environ[key] = value


_load_dotenv()


def get_token():
    """Trả về BOT_TOKEN từ biến môi trường, có kiểm tra định dạng."""
    token = os.environ.get("BOT_TOKEN")
    if not token or not token.strip():
        raise RuntimeError(MISSING_TOKEN_MESSAGE)
    token = token.strip()
    if not TOKEN_PATTERN.match(token):
        raise RuntimeError(
            "BOT_TOKEN không hợp lệ. "
            "Định dạng đúng: <bot_id>:<token> "
            "(ví dụ 123456789:YOUR_TOKEN_HERE)."
        )
    return token


def is_token_configured():
    """Kiểm tra BOT_TOKEN đã được cấu hình chưa (không ném lỗi)."""
    token = os.environ.get("BOT_TOKEN")
    return bool(token and token.strip())


# ==========================================
# QUẢN TRỊ VIÊN
# ==========================================
# Biến môi trường ADMIN_IDS: nhiều Telegram user ID, ngăn cách bằng dấu phẩy.
#   ADMIN_IDS=123456789,987654321
# Để trống -> không ai dùng được lệnh quản trị.
ADMIN_IDS_PATTERN = re.compile(r"^\d+$")


def get_admin_ids():
    """Trả về danh sách Telegram user ID của quản trị viên."""
    raw = os.environ.get("ADMIN_IDS", "")
    ids = []
    for part in raw.split(","):
        value = part.strip()
        if not value:
            continue
        if not ADMIN_IDS_PATTERN.match(value):
            logger.warning("Bỏ qua ADMIN_ID không hợp lệ: %r", value)
            continue
        ids.append(int(value))
    return ids


def is_admin(user_id):
    """Kiểm tra user_id có phải quản trị viên hay không."""
    if user_id is None:
        return False
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False
    return user_id in get_admin_ids()
