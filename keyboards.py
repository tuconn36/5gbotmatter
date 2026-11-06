"""Bàn phím inline của bot 5G MATTER."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_URL, WEBSITE
from texts import APP_GUIDES, DEVICE_APPS, SNI_STEP_INFO, STEP_INFO


def main_keyboard():
    """Menu chính."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤖 Android", callback_data="android"),
            InlineKeyboardButton("🍎 iOS", callback_data="ios"),
            InlineKeyboardButton("🖥️ Windows", callback_data="windows"),
        ],
        [
            InlineKeyboardButton("📶 Gói nền 4G/5G", callback_data="gonen"),
        ],
        [
            InlineKeyboardButton("🔁 Đổi SNI", callback_data="sni"),
            InlineKeyboardButton("🔐 Thuê ID Shadowrocket", callback_data="thueid"),
        ],
        [
            InlineKeyboardButton("🎧 Liên hệ hỗ trợ", callback_data="hotro"),
            InlineKeyboardButton("❓ Hướng dẫn", callback_data="huongdan"),
        ],
    ])


def back_keyboard():
    """Nút quay lại menu chính."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Menu chính", callback_data="home"),
        ],
    ])


def goinen_keyboard():
    """Danh sách nhà mạng."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔴 Viettel", callback_data="net_viettel"),
            InlineKeyboardButton("🔵 VinaPhone", callback_data="net_vina"),
            InlineKeyboardButton("🟢 MobiFone", callback_data="net_mobi"),
        ],
        [
            InlineKeyboardButton("🏠 Menu chính", callback_data="home"),
        ],
    ])


def viettel_goi_keyboard():
    """Các gói Viettel."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📆 Tuần T15KN", callback_data="pkg_viettel_t15kn"),
            InlineKeyboardButton("🎵 TikTok 50K", callback_data="pkg_viettel_tiktok"),
            InlineKeyboardButton("💪 Gói MXH100", callback_data="pkg_viettel_mxh100"),
        ],
        [
            InlineKeyboardButton("🔙 Quay lại", callback_data="gonen"),
        ],
    ])


def vina_goi_keyboard():
    """Các gói VinaPhone."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💎 Gói 0 NỀN", callback_data="pkg_vina_0"),
            InlineKeyboardButton("🚀 Gói TK30", callback_data="pkg_vina_30"),
        ],
        [
            InlineKeyboardButton("🔙 Quay lại", callback_data="gonen"),
        ],
    ])


def mobi_goi_keyboard():
    """Các gói MobiFone."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Gói DK TIK30", callback_data="pkg_mobi_tiktok"),
        ],
        [
            InlineKeyboardButton("🔙 Quay lại", callback_data="gonen"),
        ],
    ])


def package_back_keyboard(back_to="gonen"):
    """Nút sau khi mở chi tiết gói.

    back_to: callback_data của trang cần quay lại
    (mặc định về danh sách nhà mạng)."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Quay lại", callback_data=back_to),
        ],
        [
            InlineKeyboardButton("🏠 Menu chính", callback_data="home"),
        ],
    ])


def help_keyboard():
    """Bàn phím cho trang hướng dẫn."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Menu chính", callback_data="home"),
        ],
    ])


def support_keyboard():
    """Bàn phím liên hệ hỗ trợ."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Chat quản trị viên", url=ADMIN_URL),
        ],
        [
            InlineKeyboardButton("🏠 Menu chính", callback_data="home"),
        ],
    ])


def device_keyboard(device):
    """Danh sách app của một thiết bị (mỗi app một nút)."""
    rows = [
        [InlineKeyboardButton(
            f"📲 {APP_GUIDES[app_id]['name']}",
            callback_data=f"step_{app_id}_1",
        )]
        for app_id in DEVICE_APPS[device]["apps"]
    ]
    rows.append([InlineKeyboardButton("🏠 Menu chính", callback_data="home")])
    return InlineKeyboardMarkup(rows)


# Nút kết thúc hướng dẫn: bot sẽ làm tin nhắn "tan biến" (xem handlers.py).
DONE_CALLBACK = "done"


def _done_button():
    return InlineKeyboardButton("✅ Xong", callback_data=DONE_CALLBACK)


def step_keyboard(key):
    """Nút điều hướng cho một bước: ◀ Bước trước / Bước tiếp ▶."""
    app_id, number, total, device = STEP_INFO[key]
    if number > 1:
        back = InlineKeyboardButton(
            "◀ Bước trước", callback_data=f"step_{app_id}_{number - 1}"
        )
    else:
        back = InlineKeyboardButton("🔙 Chọn app khác", callback_data=device)
    home = InlineKeyboardButton("🏠 Menu chính", callback_data="home")

    if number < total:
        nxt = InlineKeyboardButton(
            "Bước tiếp ▶", callback_data=f"step_{app_id}_{number + 1}"
        )
        return InlineKeyboardMarkup([[back, nxt], [home]])

    # Bước cuối: nút Xong
    return InlineKeyboardMarkup([[_done_button()], [back, home]])


def sni_keyboard():
    """Chọn loại SIM cho Đổi SNI."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Không nền (Vina 0đ)", callback_data="sni_khongnen_1")],
        [InlineKeyboardButton("✅ Có nền (các SIM còn lại)", callback_data="sni_conen_1")],
        [InlineKeyboardButton("🏠 Menu chính", callback_data="home")],
    ])


def sni_step_keyboard(key):
    """Nút điều hướng cho một bước Đổi SNI: ◀ Bước trước / Bước tiếp ▶."""
    option, number, total = SNI_STEP_INFO[key]
    if number > 1:
        back = InlineKeyboardButton(
            "◀ Bước trước", callback_data=f"{option}_{number - 1}"
        )
    else:
        back = InlineKeyboardButton("🔙 Chọn loại SIM", callback_data="sni")
    home = InlineKeyboardButton("🏠 Menu chính", callback_data="home")

    if number < total:
        nxt = InlineKeyboardButton(
            "Bước tiếp ▶", callback_data=f"{option}_{number + 1}"
        )
        return InlineKeyboardMarkup([[back, nxt], [home]])

    # Bước cuối: nút Xong
    return InlineKeyboardMarkup([[_done_button()], [back, home]])
