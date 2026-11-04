"""Điểm khởi chạy bot 5G MATTER."""

import logging
import sys
import time

from telegram import BotCommand
from telegram.error import Conflict, NetworkError, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import handlers
from config import BOT_NAME, get_token

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# URL của Telegram Bot API chứa nguyên token, httpx lại log mỗi request
# ở mức INFO -> token sẽ lọt vào log (kể cả log CI). Tắt đi.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Dấu hiệu bot đã kết nối thành công với Telegram (CI có thể grep chuỗi này).
READY_MARKER = "BOT_DA_SAN_SANG"

# Thử lại khi gặp lỗi mạng tạm thời lúc khởi động.
MAX_NETWORK_RETRIES = 10
NETWORK_RETRY_BASE = 5
MAX_RETRY_DELAY = 60

# Danh sách lệnh hiện trong nút "Menu" của Telegram.
BOT_COMMANDS = [
    BotCommand("start", "Mở menu chính"),
    BotCommand("goi", "Gói nền 4G/5G"),
    BotCommand("vpn", "Dịch vụ VPN"),
    BotCommand("thueid", "Thuê ID Shadowrocket"),
    BotCommand("hotro", "Liên hệ hỗ trợ"),
    BotCommand("huongdan", "Hướng dẫn sử dụng"),
    BotCommand("id", "Xem ID Telegram của bạn"),
    BotCommand("ping", "Kiểm tra bot"),
]


async def post_init(application):
    """Chạy sau khi Application kết nối thành công với Telegram."""
    try:
        await application.bot.set_my_commands(BOT_COMMANDS)
    except TelegramError as error:
        # Không đặt được danh sách lệnh không đáng để dừng bot.
        logger.warning("Không đặt được danh sách lệnh: %s", error)
    logger.info("%s %s", READY_MARKER, BOT_NAME)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Ghi log lỗi thay vì để bot im lặng bỏ qua."""
    logger.error(
        "Lỗi khi xử lý update %s: %s",
        getattr(update, "update_id", "?"),
        context.error,
        exc_info=context.error,
    )


def register_handlers(app):
    """Đăng ký toàn bộ command / callback / auto-reply."""
    app.add_handler(CommandHandler(["start", "menu"], handlers.start))
    app.add_handler(CommandHandler(["hdsd", "huongdan", "help"], handlers.hdsd))
    app.add_handler(CommandHandler("id", handlers.user_id))
    app.add_handler(CommandHandler("ping", handlers.ping))
    # Lối tắt tới từng trang.
    app.add_handler(CommandHandler(["goi", "gonen"], handlers.goi))
    app.add_handler(CommandHandler("vpn", handlers.vpn))
    app.add_handler(CommandHandler("thueid", handlers.thueid))
    app.add_handler(CommandHandler(["hotro", "support"], handlers.hotro))
    # Chỉ quản trị viên (kiểm tra trong handler).
    app.add_handler(CommandHandler("restart", handlers.restart))

    app.add_handler(CallbackQueryHandler(handlers.button_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.auto_reply)
    )
    app.add_error_handler(error_handler)


def build_application():
    """Tạo Application mới từ BOT_TOKEN.

    Mỗi lần thử lại phải dùng Application MỚI: sau khi run_polling()
    thoát, event loop của Application cũ đã bị đóng nên không chạy lại được.
    """
    app = Application.builder().token(get_token()).post_init(post_init).build()
    register_handlers(app)
    return app


def main():
    try:
        app = build_application()
    except RuntimeError as error:
        print(f"❌ Lỗi cấu hình: {error}", file=sys.stderr)
        sys.exit(1)

    logger.info("🚀 %s BOT đang khởi động...", BOT_NAME)

    attempt = 0
    while True:
        handlers.START_TIME = time.time()
        try:
            app.run_polling(
                # Token sai/hết hạn phải fail ngay thay vì retry vô hạn.
                bootstrap_retries=0,
                # Giữ update đang chờ để không mất tin nhắn khi bot restart.
                drop_pending_updates=False,
                allowed_updates=["message", "callback_query"],
            )
            logger.info("Bot đã dừng.")
            break

        except Conflict:
            logger.error(
                "Conflict: bot đang chạy ở nơi khác với cùng token. "
                "Hãy tắt instance cũ rồi thử lại."
            )
            sys.exit(1)

        except NetworkError as error:
            attempt += 1
            if attempt > MAX_NETWORK_RETRIES:
                logger.error("Lỗi mạng %d lần liên tiếp, dừng thử lại: %s", attempt, error)
                sys.exit(1)
            delay = min(MAX_RETRY_DELAY, NETWORK_RETRY_BASE * attempt)
            logger.warning("Lỗi mạng (lần %d): %s - thử lại sau %ds", attempt, error, delay)
            time.sleep(delay)
            # Tạo Application mới cho lần thử tiếp theo.
            app = build_application()

        except TelegramError as error:
            logger.error("Lỗi Telegram: %s", error)
            sys.exit(1)


if __name__ == "__main__":
    main()
