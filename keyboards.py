"""Bàn phím inline của bot 5G MATTER.

Bố cục gọn gàng, nút quay lại ở mọi cấp.
Nhãn nút dùng emoji + chữ viết tắt để nhìn gọn trên màn hình hẹp.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_URL, WEBSITE
from texts import APP_DEVICE, APP_GUIDES, DEVICE_APPS


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
            InlineKeyboardButton("🛡️ Dịch vụ VPN", callback_data="vpn"),
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
            InlineKeyboardButton("🎵 TikTok 50K", callback_data="pkg_viettel_tiktok"),
            InlineKeyboardButton("📆 Tuần T15KN", callback_data="pkg_viettel_t15kn"),
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
            InlineKeyboardButton("🌐 Mở website 5G MATTER", url=WEBSITE),
        ],
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
            InlineKeyboardButton("🌐 Mở website 5G MATTER", url=WEBSITE),
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
            callback_data=f"app_{app_id}",
        )]
        for app_id in DEVICE_APPS[device]["apps"]
    ]
    rows.append([InlineKeyboardButton("🏠 Menu chính", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def app_keyboard(app_key):
    """Nút dưới trang hướng dẫn một app."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Chọn app khác", callback_data=APP_DEVICE[app_key]),
        ],
        [
            InlineKeyboardButton("💬 Chat quản trị viên", url=ADMIN_URL),
        ],
        [
            InlineKeyboardButton("🏠 Menu chính", callback_data="home"),
        ],
    ])
