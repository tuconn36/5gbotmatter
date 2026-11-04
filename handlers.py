"""Xử lý command, callback query và trả lời tự động của bot 5G MATTER."""

import logging
import time

from telegram import CallbackQuery, InlineKeyboardMarkup, Update
from telegram.constants import ChatType, ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import admin as admin_module
from config import is_admin
from matching import normalize, pick_page
from keyboards import (
    back_keyboard,
    goinen_keyboard,
    help_keyboard,
    main_keyboard,
    mobi_goi_keyboard,
    package_back_keyboard,
    support_keyboard,
    vina_goi_keyboard,
    viettel_goi_keyboard,
)
from texts import (
    FALLBACK_TEXT,
    GOI_NEN_TEXT,
    HELP_TEXT,
    MAIN_TEXT,
    MOBI_TEXT,
    PACKAGE_NETWORK,
    PACKAGE_TEXTS,
    PAGES,
    VIETTEL_TEXT,
    VINA_TEXT,
    ping_text,
    restart_failed_text,
    restart_not_allowed_text,
    restart_requested_text,
    user_info_text,
)

logger = logging.getLogger(__name__)

# Thời điểm bot khởi động (dùng cho /ping). bot.py đặt lại khi chạy.
START_TIME = time.time()

PARSE_MODE = ParseMode.HTML


# ==========================================
# BẢNG TRANG: callback_data / từ khóa -> (nội dung, bàn phím)
# ==========================================
_HOME_KEYS = {"home", "start", "menu"}
_HELP_KEYS = {"huongdan", "help", "hdsd"}
_GONEN_KEYS = {"gonen", "back_gonen", "package_back"}

_NETWORK_PAGES = {
    "net_viettel": (VIETTEL_TEXT, viettel_goi_keyboard),
    "net_vina": (VINA_TEXT, vina_goi_keyboard),
    "net_mobi": (MOBI_TEXT, mobi_goi_keyboard),
    "back_viettel": (VIETTEL_TEXT, viettel_goi_keyboard),
    "back_vina": (VINA_TEXT, vina_goi_keyboard),
    "back_mobi": (MOBI_TEXT, mobi_goi_keyboard),
}


def resolve_view(key):
    """Trả về (nội dung, bàn phím) cho một trang, hoặc None nếu không có.

    Dùng chung cho nút bấm, lệnh và tự động trả lời từ khóa để mọi nơi
    hiển thị giống hệt nhau.
    """
    if key in _HOME_KEYS:
        return MAIN_TEXT, main_keyboard()
    if key in _HELP_KEYS:
        return HELP_TEXT, help_keyboard()
    if key in _GONEN_KEYS:
        return GOI_NEN_TEXT, goinen_keyboard()
    if key in _NETWORK_PAGES:
        text, keyboard = _NETWORK_PAGES[key]
        return text, keyboard()
    if key in PACKAGE_TEXTS:
        back_to = PACKAGE_NETWORK.get(key, "gonen")
        return PACKAGE_TEXTS[key], package_back_keyboard(back_to)
    if key in ("hotro", "vpn"):
        return PAGES[key], support_keyboard()
    if key in PAGES:
        return PAGES[key], back_keyboard()
    return None


async def _reply_view(update: Update, key: str):
    """Gửi một trang dưới dạng tin nhắn mới."""
    message = update.effective_message
    view = resolve_view(key)
    if not message or not view:
        return
    text, keyboard = view
    await message.reply_text(text, reply_markup=keyboard, parse_mode=PARSE_MODE)


# ==========================================
# LỆNH
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị menu chính (/start, /menu)."""
    await _reply_view(update, "home")


async def hdsd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị trang hướng dẫn sử dụng."""
    await _reply_view(update, "huongdan")


async def goi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lối tắt tới trang gói nền 4G/5G."""
    await _reply_view(update, "gonen")


async def vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lối tắt tới trang VPN."""
    await _reply_view(update, "vpn")


async def thueid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lối tắt tới trang thuê ID Shadowrocket."""
    await _reply_view(update, "thueid")


async def hotro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lối tắt tới trang liên hệ hỗ trợ."""
    await _reply_view(update, "hotro")


async def user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị ID người dùng (hỗ trợ quản trị)."""
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    await message.reply_text(user_info_text(user), parse_mode=PARSE_MODE)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kiểm tra độ trễ phản hồi của bot."""
    message = update.effective_message
    if not message:
        return
    start_at = time.perf_counter()
    await message.reply_text("⏱️ Đang kiểm tra...")
    elapsed = (time.perf_counter() - start_at) * 1000
    uptime = int(time.time() - START_TIME)
    await message.reply_text(ping_text(elapsed, uptime), parse_mode=PARSE_MODE)


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Khởi động lại bot (chỉ quản trị viên).

    QUAN TRỌNG: phải reply TRƯỚC khi restart, vì bước huỷ run hiện tại
    sẽ giết tiến trình bot -> không còn gửi được tin nhắn nữa.
    """
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    if not is_admin(user.id):
        logger.warning("Từ chối /restart từ user không phải admin: %s", user.id)
        await message.reply_text(restart_not_allowed_text(), parse_mode=PARSE_MODE)
        return

    await message.reply_text(restart_requested_text(), parse_mode=PARSE_MODE)

    try:
        await admin_module.restart_bot()
    except admin_module.RestartError as error:
        logger.error("Không restart được bot: %s", error)
        await message.reply_text(restart_failed_text(str(error)), parse_mode=PARSE_MODE)
        return
    except Exception as error:  # noqa: BLE001 - không để bot crash
        logger.exception("Lỗi không mong đợi khi restart: %s", error)
        await message.reply_text(restart_failed_text(str(error)), parse_mode=PARSE_MODE)
        return

    logger.info("Đã lệnh restart bot theo yêu cầu của admin %s", user.id)


# ==========================================
# NÚT INLINE
# ==========================================
async def safe_edit(
    query: CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
):
    """Sửa message, bỏ qua lỗi 'Message is not modified' khi bấm lại cùng nút."""
    try:
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=PARSE_MODE,
        )
    except BadRequest as error:
        raw = getattr(error, "message", None) or str(error)
        if raw.strip().casefold().endswith("message is not modified"):
            logger.debug("Bỏ qua lỗi 'message is not modified'")
            return
        logger.warning("Không sửa được message: %s", error)
        raise


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Điều hướng theo callback_data của nút bấm."""
    query = update.callback_query
    if not query:
        return

    view = resolve_view(query.data or "")
    if view is None:
        await query.answer("⚠️ Chức năng này chưa được cấu hình.", show_alert=True)
        return

    await query.answer()
    text, keyboard = view
    await safe_edit(query, text, reply_markup=keyboard)


# ==========================================
# TỪ KHÓA TỰ ĐỘNG
# ==========================================
# Khoảng cách tối thiểu giữa hai lần bot trả lời cùng một user (giây).
REPLY_COOLDOWN = 2.0

# Bỏ qua tin nhắn quá dài (dán văn bản, spam) - không phải câu hỏi từ khóa.
MAX_TEXT_LENGTH = 300


def _allow_reply(context, user) -> bool:
    """Giới hạn tần suất trả lời để tránh spam / flood của Telegram."""
    if not user:
        return True
    user_data = getattr(context, "user_data", None)
    if user_data is None:
        return True
    now = time.monotonic()
    last = user_data.get("_last_reply_at")
    if last is not None and (now - last) < REPLY_COOLDOWN:
        return False
    user_data["_last_reply_at"] = now
    return True


async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tự động trả lời theo từ khóa trong tin nhắn."""
    message = update.effective_message
    if not message or not message.text:
        return
    user = update.effective_user
    if user and user.is_bot:
        return

    if len(message.text) > MAX_TEXT_LENGTH:
        return

    text = normalize(message.text)
    if text.startswith("/"):
        return

    if not _allow_reply(context, user):
        logger.info("Bỏ qua tin nhắn quá nhanh của user %s", getattr(user, "id", "?"))
        return

    page = pick_page(text)
    if page:
        # "menu" trong từ khóa tương ứng trang chủ.
        await _reply_view(update, "home" if page == "menu" else page)
        return

    # Không khớp từ khóa: chỉ gợi ý trong chat riêng, im lặng trong nhóm.
    chat = update.effective_chat
    if chat and chat.type == ChatType.PRIVATE:
        await message.reply_text(
            FALLBACK_TEXT,
            reply_markup=main_keyboard(),
            parse_mode=PARSE_MODE,
        )
