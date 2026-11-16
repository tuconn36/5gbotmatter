"""Bàn phím inline của bot 5G MATTER"""

from telegram import InlineKeyboardMarkup

from config import ADMIN_URL, WEBSITE
from icons import plain_button as button
from texts import APP_GUIDES, DEVICE_APPS, SNI_STEP_INFO, STEP_INFO


def _home_button():
    return button("home", "Menu chính", callback_data="home")


def main_keyboard():
    """Menu chính."""
    return InlineKeyboardMarkup([
        [
            button("android", "Android", callback_data="android"),
            button("ios", "iOS", callback_data="ios"),
            button("windows", "Windows", callback_data="windows"),
        ],
        [
            button("gonen", "Gói nền 4G/5G", callback_data="gonen"),
        ],
        [
            button("sni", "Đổi SNI", callback_data="sni"),
            button("thueid", "Thuê ID Shadowrocket", callback_data="thueid"),
        ],
        [
            button("hotro", "Liên hệ hỗ trợ", callback_data="hotro"),
            button("huongdan", "Hướng dẫn", callback_data="huongdan"),
        ],
    ])


def back_keyboard():
    """Nút quay lại menu chính."""
    return InlineKeyboardMarkup([[_home_button()]])


def goinen_keyboard():
    """Danh sách nhà mạng."""
    return InlineKeyboardMarkup([
        [
            button("viettel", "Viettel", callback_data="net_viettel"),
            button("vina", "VinaPhone", callback_data="net_vina"),
            button("mobi", "MobiFone", callback_data="net_mobi"),
        ],
        [_home_button()],
    ])


def viettel_goi_keyboard():
    """Các gói Viettel."""
    return InlineKeyboardMarkup([
        [
            button("t15kn", "Tuần T15KN", callback_data="pkg_viettel_t15kn"),
            button("tiktok", "TikTok 50K", callback_data="pkg_viettel_tiktok"),
            button("mxh100", "Gói MXH100", callback_data="pkg_viettel_mxh100"),
        ],
        [button("back", "Quay lại", callback_data="gonen")],
    ])


def vina_goi_keyboard():
    """Các gói VinaPhone."""
    return InlineKeyboardMarkup([
        [
            button("vina0", "Gói 0 NỀN", callback_data="pkg_vina_0"),
            button("tk30", "Gói TK30", callback_data="pkg_vina_30"),
        ],
        [button("back", "Quay lại", callback_data="gonen")],
    ])


def mobi_goi_keyboard():
    """Các gói MobiFone."""
    return InlineKeyboardMarkup([
        [button("tiktok", "Gói DK TIK30", callback_data="pkg_mobi_tiktok")],
        [button("back", "Quay lại", callback_data="gonen")],
    ])


def package_back_keyboard(back_to="gonen"):
    """Nút sau khi mở chi tiết gói.

    back_to: callback_data của trang cần quay lại
    (mặc định về danh sách nhà mạng)."""
    return InlineKeyboardMarkup([
        [button("back", "Quay lại", callback_data=back_to)],
        [_home_button()],
    ])


def help_keyboard():
    """Bàn phím cho trang hướng dẫn."""
    return InlineKeyboardMarkup([[_home_button()]])


def support_keyboard():
    """Bàn phím liên hệ hỗ trợ."""
    return InlineKeyboardMarkup([
        [button("chat", "Chat quản trị viên", url=ADMIN_URL)],
        [_home_button()],
    ])


def device_keyboard(device):
    """Danh sách app của một thiết bị (mỗi app một nút)."""
    rows = [
        [button(
            "app",
            APP_GUIDES[app_id]["name"],
            callback_data=f"step_{app_id}_1",
        )]
        for app_id in DEVICE_APPS[device]["apps"]
    ]
    rows.append([_home_button()])
    return InlineKeyboardMarkup(rows)


# Nút kết thúc hướng dẫn: bot sẽ làm tin nhắn "tan biến" (xem handlers.py).
DONE_CALLBACK = "done"


def _done_button():
    return button("done", "Xong", callback_data=DONE_CALLBACK)


def _step_nav(back_label_cb, prev_cb, next_cb, number, total):
    """Hàng điều hướng chung: Bước trước / Bước tiếp, hoặc nút Xong ở bước cuối."""
    if number > 1:
        back = button("prev", "Bước trước", callback_data=prev_cb)
    else:
        back = button("back", back_label_cb[0], callback_data=back_label_cb[1])
    home = _home_button()

    if number < total:
        nxt = button("next", "Bước tiếp", callback_data=next_cb)
        return InlineKeyboardMarkup([[back, nxt], [home]])

    # Bước cuối: nút Xong
    return InlineKeyboardMarkup([[_done_button()], [back, home]])


def step_keyboard(key):
    """Nút điều hướng cho một bước: Bước trước / Bước tiếp."""
    app_id, number, total, device = STEP_INFO[key]
    return _step_nav(
        ("Chọn app khác", device),
        f"step_{app_id}_{number - 1}",
        f"step_{app_id}_{number + 1}",
        number,
        total,
    )


def sni_keyboard():
    """Chọn loại SIM cho Đổi SNI."""
    return InlineKeyboardMarkup([
        [button("khongnen", "Không nền (Vina 0đ)", callback_data="sni_khongnen_1")],
        [button("conen", "Có nền (các SIM còn lại)", callback_data="sni_conen_1")],
        [_home_button()],
    ])


def sni_step_keyboard(key):
    """Nút điều hướng cho một bước Đổi SNI."""
    option, number, total = SNI_STEP_INFO[key]
    return _step_nav(
        ("Chọn loại SIM", "sni"),
        f"{option}_{number - 1}",
        f"{option}_{number + 1}",
        number,
        total,
    )
