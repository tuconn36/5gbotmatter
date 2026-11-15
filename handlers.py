"""Xử lý command, callback query và trả lời tự động của bot 5G MATTER."""

import asyncio
import html
import logging
import os
import random
import time

from telegram import CallbackQuery, LinkPreviewOptions, MessageEntity, Update
from telegram.constants import ChatType, ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import ApplicationHandlerStop, ContextTypes

import admin as admin_module
import icons
from config import is_admin
from images import preview_options
from matching import normalize, pick_page
from keyboards import (
    DONE_CALLBACK,
    back_keyboard,
    device_keyboard,
    goinen_keyboard,
    help_keyboard,
    sni_keyboard,
    sni_step_keyboard,
    step_keyboard,
    main_keyboard,
    mobi_goi_keyboard,
    package_back_keyboard,
    support_keyboard,
    vina_goi_keyboard,
    viettel_goi_keyboard,
)
from texts import (
    DEVICE_TEXTS,
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
    SNI_STEP_TEXTS,
    STEP_TEXTS,
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
    if key == "vpn":  # nút / lệnh cũ trong các tin nhắn đã gửi
        key = "sni"
    if key in ("sni_khongnen", "sni_conen"):  # nút cũ -> bước 1
        key += "_1"
    if key in _HOME_KEYS:
        return MAIN_TEXT, main_keyboard()
    if key in _HELP_KEYS:
        return HELP_TEXT, help_keyboard()
    if key in _GONEN_KEYS:
        return GOI_NEN_TEXT, goinen_keyboard()
    if key in _NETWORK_PAGES:
        text, keyboard = _NETWORK_PAGES[key]
        return text, keyboard()
    if key in DEVICE_TEXTS:
        return DEVICE_TEXTS[key], device_keyboard(key)
    if key in STEP_TEXTS:
        return STEP_TEXTS[key], step_keyboard(key)
    if key in PACKAGE_TEXTS:
        back_to = PACKAGE_NETWORK.get(key, "gonen")
        return PACKAGE_TEXTS[key], package_back_keyboard(back_to)
    if key == "sni":
        return PAGES["sni"], sni_keyboard()
    if key in SNI_STEP_TEXTS:
        return SNI_STEP_TEXTS[key], sni_step_keyboard(key)
    if key == "hotro":
        return PAGES[key], support_keyboard()
    if key in PAGES:
        return PAGES[key], back_keyboard()
    return None


def _is_not_modified(error):
    """Lỗi 'Message is not modified' khi bấm lại cùng một nút."""
    raw = getattr(error, "message", None) or str(error)
    return "message is not modified" in raw.casefold()


async def _with_icon_fallback(make_call):
    """Gọi Telegram; nếu custom emoji bị từ chối thì thử lại bằng emoji thường.

    make_call: hàm không tham số trả về coroutine và TỰ DỰNG bàn phím bên
    trong, để lần thử lại dựng được bàn phím mới bằng emoji thường.

    Chỉ khi lần thử lại thành công mới coi custom emoji là nguyên nhân và tắt
    hẳn (lỗi khác như tin quá cũ sẽ không làm mất icon động).
    """
    try:
        return await make_call()
    except BadRequest as error:
        if _is_not_modified(error) or not icons.custom_in_use():
            raise
        logger.warning("Telegram từ chối, thử lại bằng emoji thường: %s", error)
        with icons.fallback():
            result = await make_call()
        logger.warning(
            "Đã tắt icon động (bot chưa đủ điều kiện dùng custom emoji "
            "trên nút bấm). Xem hướng dẫn trong icons.py."
        )
        icons.disable()
        return result


# ==========================================
# TỰ TAN BIẾN
# ==========================================
# Tin bot gửi (menu, hướng dẫn, /id, /ping...) tự "tan biến" sau 3-4 phút
# KHÔNG có thao tác. Mỗi lần người dùng bấm nút, đồng hồ được tính lại.
# Nếu tin do lệnh (/start, /goi...) sinh ra, tin lệnh của người dùng cũng bị
# xoá cùng lúc (trong nhóm cần quyền xoá tin; không có quyền thì bỏ qua).
# Đặt biến môi trường AUTO_DISSOLVE=0 để tắt.
AUTO_DISSOLVE = os.environ.get("AUTO_DISSOLVE", "1").strip().lower() not in {
    "0", "false", "off", "no",
}
DISSOLVE_IDLE_RANGE = (180, 240)  # giây: ngẫu nhiên 3-4 phút

# Thời gian hiển thị hiệu ứng tan biến trước khi xoá tin nhắn (giây).
DISSOLVE_SECONDS = 1.3

_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

# (chat_id, message_id) của tin bot -> task đang đếm giờ.
_pending = {}
# (chat_id, message_id) của tin bot -> message_id tin lệnh của người dùng.
_user_msgs = {}


async def _delete_quietly(bot, chat_id, message_id):
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except TelegramError as error:
        logger.debug("Không xoá được tin %s: %s", message_id, error)


async def _vanish(bot, chat_id, message_id, plain):
    """Đổi tin sang spoiler (hạt bụi tan biến) rồi xoá, kèm tin lệnh của user."""
    if plain:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"<tg-spoiler>{html.escape(plain)}</tg-spoiler>",
                parse_mode=PARSE_MODE,
                link_preview_options=_NO_PREVIEW,
            )
            await asyncio.sleep(DISSOLVE_SECONDS)
        except TelegramError as error:
            logger.debug("Không đổi được sang spoiler: %s", error)
    await _delete_quietly(bot, chat_id, message_id)
    user_message_id = _user_msgs.pop((chat_id, message_id), None)
    if user_message_id:
        await _delete_quietly(bot, chat_id, user_message_id)


def cancel_dissolve(key):
    """Huỷ đồng hồ tan biến của một tin (nếu có)."""
    task = _pending.pop(key, None)
    if task:
        task.cancel()


def schedule_dissolve(bot, chat_id, message_id, plain, user_message_id=None):
    """Hẹn giờ cho tin; gọi lại cho cùng một tin sẽ đặt lại đồng hồ."""
    if not AUTO_DISSOLVE or not chat_id or not message_id:
        return
    key = (chat_id, message_id)
    if user_message_id:
        _user_msgs[key] = user_message_id
    cancel_dissolve(key)

    async def runner():
        await asyncio.sleep(random.uniform(*DISSOLVE_IDLE_RANGE))
        await _vanish(bot, chat_id, message_id, plain)

    task = asyncio.create_task(runner())
    _pending[key] = task
    task.add_done_callback(
        lambda t, k=key: _pending.pop(k, None) if _pending.get(k) is t else None
    )


def _track(sent, command_message=None):
    """Hẹn giờ tan biến cho tin bot vừa gửi.

    command_message: tin của người dùng đã sinh ra tin này; chỉ bị xoá khi
    nó là một lệnh (bắt đầu bằng "/").
    """
    if sent is None or not hasattr(sent, "message_id"):
        return
    user_message_id = None
    if command_message is not None:
        text = getattr(command_message, "text", None) or ""
        if text.startswith("/"):
            user_message_id = command_message.message_id
    schedule_dissolve(
        sent.get_bot(), sent.chat_id, sent.message_id, sent.text, user_message_id
    )


def _retrack(query, edited=None):
    """Người dùng vừa bấm nút trên tin này -> tính lại 3-4 phút."""
    message = query.message
    if message is None:
        return
    source = edited if hasattr(edited, "text") else message
    schedule_dissolve(
        query.get_bot(),
        message.chat.id,
        message.message_id,
        getattr(source, "text", None),
    )


async def _reply_view(update: Update, key: str):
    """Gửi một trang dưới dạng tin nhắn mới."""
    message = update.effective_message
    if not message or not resolve_view(key):
        return

    async def call():
        text, keyboard = resolve_view(key)
        return await message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode=PARSE_MODE,
            link_preview_options=preview_options(key),
        )

    sent = await _with_icon_fallback(call)
    _track(sent, message)


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


async def sni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lối tắt tới trang Đổi SNI."""
    await _reply_view(update, "sni")


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
    sent = await message.reply_text(user_info_text(user), parse_mode=PARSE_MODE)
    _track(sent, message)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kiểm tra độ trễ phản hồi của bot."""
    message = update.effective_message
    if not message:
        return
    start_at = time.perf_counter()
    checking = await message.reply_text("⏱️ Đang kiểm tra...")
    _track(checking)
    elapsed = (time.perf_counter() - start_at) * 1000
    uptime = int(time.time() - START_TIME)
    sent = await message.reply_text(ping_text(elapsed, uptime), parse_mode=PARSE_MODE)
    _track(sent, message)


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


async def emoji_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin gửi tin có emoji động -> bot trả lại custom_emoji_id để dán vào icons.txt."""
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not is_admin(user.id):
        return  # người thường: để auto_reply xử lý như bình thường

    entities = message.parse_entities([MessageEntity.CUSTOM_EMOJI])
    lines = []
    seen = set()
    for entity, char in entities.items():
        if entity.custom_emoji_id in seen:
            continue
        seen.add(entity.custom_emoji_id)
        lines.append(f"{html.escape(char)} <code>{entity.custom_emoji_id}</code>")
    if lines:
        await message.reply_text(
            "🆔 <b>ID emoji động</b> — dán vào <code>icons.txt</code> "
            "dạng <code>tên_icon = ID</code>:\n\n" + "\n".join(lines),
            parse_mode=PARSE_MODE,
        )
    raise ApplicationHandlerStop  # không để auto_reply trả lời thêm


# ==========================================
# NÚT INLINE
# ==========================================
async def safe_edit(query: CallbackQuery, key: str):
    """Sửa message thành trang `key`, bỏ qua lỗi 'Message is not modified'."""

    async def call():
        text, keyboard = resolve_view(key)
        return await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode=PARSE_MODE,
            link_preview_options=preview_options(key),
        )

    try:
        edited = await _with_icon_fallback(call)
    except BadRequest as error:
        if _is_not_modified(error):
            logger.debug("Bỏ qua lỗi 'message is not modified'")
            _retrack(query)
            return
        logger.warning("Không sửa được message: %s", error)
        raise
    _retrack(query, edited)


async def dissolve_message(query: CallbackQuery):
    """Nút ✅ Xong: làm tin nhắn "tan biến" rồi xoá.

    Telegram không có animation tuỳ ý, nhưng văn bản bọc trong spoiler sẽ
    hiện hiệu ứng hạt bụi tan biến. Bot đổi cả tin nhắn sang dạng spoiler,
    đợi một nhịp rồi xoá hẳn.
    """
    await query.answer("✅ Hoàn tất!")
    message = query.message
    plain = getattr(message, "text", None)
    key = (message.chat.id, message.message_id)
    cancel_dissolve(key)  # đã tan biến thủ công, khỏi hẹn giờ nữa
    user_message_id = _user_msgs.pop(key, None)
    try:
        if plain:
            await query.edit_message_text(
                f"<tg-spoiler>{html.escape(plain)}</tg-spoiler>",
                parse_mode=PARSE_MODE,
                reply_markup=None,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            await asyncio.sleep(DISSOLVE_SECONDS)
        await message.delete()
        if user_message_id:
            await _delete_quietly(query.get_bot(), key[0], user_message_id)
    except BadRequest as error:
        # Không xoá được (tin quá cũ, đã bị xoá, bấm đúp...) -> để lại lời chốt.
        logger.info("Không xoá được tin nhắn sau khi Xong: %s", error)
        try:
            await query.edit_message_text(
                "✅ Hoàn tất!", reply_markup=None, link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        except BadRequest:
            pass


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Điều hướng theo callback_data của nút bấm."""
    query = update.callback_query
    if not query:
        return

    key = query.data or ""
    if key == DONE_CALLBACK:
        await dissolve_message(query)
        return
    view = resolve_view(key)
    if view is None:
        await query.answer("⚠️ Chức năng này chưa được cấu hình.", show_alert=True)
        return

    await query.answer()
    await safe_edit(query, key)


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
        sent = await _with_icon_fallback(
            lambda: message.reply_text(
                FALLBACK_TEXT,
                reply_markup=main_keyboard(),
                parse_mode=PARSE_MODE,
            )
        )
        _track(sent, message)
