"""Nội dung hiển thị của bot 5G MATTER."""

# ==========================================
# CÔNG CỤ ĐỊNH DẠNG
# ==========================================

# Đường kẻ mảnh ngăn cách phần tiêu đề với phần nội dung.
# Gạch đơn nhẹ hơn gạch đôi khi render trong Telegram.
SEP = "────────────────────"

# Ký hiệu mở đầu nhãn mục (tab nhỏ).
TAB = "▌"


def section(title):
    """Nhãn mục dạng tab cho một khối nội dung.

    title: chữ tiêu đề, đã escape sẵn nếu chứa ký tự đặc biệt.
    """
    return f"{TAB} <b>{title}</b>"


def card(lines):
    """Bọc một danh sách dòng thành thẻ (blockquote native của Telegram).

    Telegram tự vẽ gạch dọc cho mọi dòng nằm trong <blockquote>,
    nên cạnh trái luôn thẳng hàng ở mọi client, kể cả khi client
    dùng font tỉ lệ. Không thêm tiền tố "> " vì Telegram sẽ hiểu
    đó là blockquote lồng nhau (không được phép).
    """
    body = "\n".join(lines)
    return f"<blockquote>{body}</blockquote>"


def escape(text):
    """Escape ký tự đặc biệt cho HTML parse mode của Telegram.

    Dùng cho dữ liệu do người dùng nhập (tên, username...)
    để không làm vỡ HTML khi render.
    """
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ==========================================
# HẰNG SỐ CHUNG
# ==========================================

# Website và tài khoản quản trị viên lấy từ config.py (một nguồn duy nhất).
from config import ADMIN_URL, ADMIN_USERNAME, WEBSITE  # noqa: E402,F401

# Cảnh báo dùng chung cho mọi trang gói nền của nhà mạng.
REGISTER_WARNING = (
    "⚠️ <b>Đăng ký gói nền là bắt buộc</b> — "
    "không đăng ký sẽ không dùng được 4G/5G."
)

# Dòng website dùng trong thẻ.
WEBSITE_LINE = f'🌐 <a href="{WEBSITE}">5gmatter.site</a>'


# ==========================================
# TRANG CHÍNH
# ==========================================
MAIN_TEXT = "\n\n".join([
    "✨ <b>5G MATTER</b>\n<i>⚡ Tự động · Nhanh chóng · Bảo mật</i>",
    card([
        "📱 Chọn thiết bị bên dưới để xem cách cài đặt",
        "📶 <b>Gói nền 4G/5G</b> — giá theo nhà mạng",
        "🔁 <b>Đổi SNI</b> — có nền / không nền",
        "🔐 <b>Thuê ID Shadowrocket</b>",
    ]),
    "💬 Cần hỗ trợ? Bấm <b>Liên hệ hỗ trợ</b>.",
])


# ==========================================
# HƯỚNG DẪN SỬ DỤNG
# ==========================================
HELP_TEXT = "\n\n".join([
    "❓ <b>HƯỚNG DẪN SỬ DỤNG</b>\n<i>Bấm nút hoặc gõ từ khóa, không cần nhớ lệnh</i>",
    card([
        "👆 <b>Bấm nút</b> trên menu để chọn thiết bị hoặc gói cước",
        "⌨️ <b>Gõ từ khóa</b>: <code>iphone</code>, <code>android</code>, "
        "<code>windows</code>, <code>gói nền</code>, <code>sni</code>, <code>hỗ trợ</code>",
    ]),
    section("LỆNH NHANH") + "\n" + card([
        "<code>/start</code> · <code>/goi</code> · <code>/sni</code> · "
        "<code>/thueid</code> · <code>/hotro</code>",
        "<code>/huongdan</code> · <code>/id</code> · <code>/ping</code>",
    ]),
])


# ==========================================
# CÁC TRANG NỘI DUNG
# ==========================================
# Thiết bị -> danh sách app. Thêm/bớt app chỉ cần sửa APP_GUIDES và DEVICE_APPS.
DEVICE_APPS = {
    "android": {
        "icon": "🤖", "name": "Android",
        "apps": ["android_v2rayng", "android_happ"],
    },
    "ios": {
        "icon": "🍎", "name": "iOS",
        "apps": ["ios_shadowrocket", "ios_v2box", "ios_happ"],
    },
    "windows": {
        "icon": "🖥️", "name": "Windows",
        "apps": ["windows_v2rayn", "windows_happ"],
    },
}

_IMPORT = "Bấm <b>＋</b> → nhập cấu hình bot gửi (dán link hoặc chọn file)."

# Mỗi app gồm nhiều BƯỚC; mỗi bước = (tiêu đề, nội dung) và là một trang riêng
# có nút "Bước tiếp ▶". Ảnh của bước: images/<mã app>_<số bước>.png
APP_GUIDES = {
    "android_v2rayng": {
        "device": "android",
        "name": "v2rayNG",
        "source": "tải trên CH Play",
        "steps": [
            ("Tải ứng dụng", "Tải <b>v2rayNG</b> trên CH Play rồi mở app."),
            ("Nhập cấu hình", _IMPORT),
            ("Kết nối", "Chọn cấu hình vừa nhập → bấm nút <b>▶</b> để kết nối."),
        ],
    },
    "android_happ": {
        "device": "android",
        "name": "Happ",
        "source": "tải trên CH Play",
        "steps": [
            ("Tải ứng dụng", "Tải <b>Happ</b> trên CH Play rồi mở app."),
            ("Nhập cấu hình", _IMPORT),
            ("Kết nối", "Bấm nút kết nối là dùng được."),
        ],
    },
    "ios_shadowrocket": {
        "device": "ios",
        "name": "Shadowrocket",
        "source": "tải trên App Store (trả phí)",
        "steps": [
            ("Tải ứng dụng", "Tải <b>Shadowrocket</b> trên App Store rồi mở app."),
            ("Nhập cấu hình", "Bấm <b>＋</b> → <b>Import from File</b> → chọn file cấu hình."),
            ("Kết nối", "Bật công tắc kết nối."),
            ("Cho phép VPN", "Bấm <b>Allow</b> khi iPhone hỏi thêm cấu hình VPN."),
        ],
    },
    "ios_v2box": {
        "device": "ios",
        "name": "V2Box",
        "source": "tải trên App Store",
        "steps": [
            ("Tải ứng dụng", "Tải <b>V2Box</b> trên App Store rồi mở app."),
            ("Nhập cấu hình", _IMPORT),
            ("Kết nối", "Chọn máy chủ → bấm kết nối → bấm <b>Allow</b> khi iPhone hỏi thêm VPN."),
        ],
    },
    "ios_happ": {
        "device": "ios",
        "name": "Happ",
        "source": "miễn phí trên App Store",
        "steps": [
            ("Tải ứng dụng", "Tải <b>Happ</b> trên App Store rồi mở app."),
            ("Nhập cấu hình", _IMPORT),
            ("Kết nối", "Bấm nút kết nối → bấm <b>Allow</b> khi iPhone hỏi thêm VPN."),
        ],
    },
    "windows_v2rayn": {
        "device": "windows",
        "name": "v2rayN",
        "source": "tải miễn phí trên GitHub (2dust/v2rayN)",
        "steps": [
            ("Tải ứng dụng", "Tải <b>v2rayN</b>, giải nén rồi mở lên."),
            ("Nhập cấu hình", "Menu <b>Servers</b> → <b>Import server from file</b> → chọn file."),
            ("Kết nối", "Chọn server → <b>Enter</b> → <b>Set as system proxy</b>."),
        ],
        "tip": "Muốn tắt: bỏ chọn <b>System proxy</b> trong v2rayN.",
    },
    "windows_happ": {
        "device": "windows",
        "name": "Happ",
        "source": "tải bản Windows trên trang chủ Happ",
        "steps": [
            ("Tải ứng dụng", "Tải <b>Happ</b> bản Windows rồi mở lên."),
            ("Nhập cấu hình", _IMPORT),
            ("Kết nối", "Bấm nút kết nối là dùng được."),
        ],
    },
}


def _capitalize(text):
    return text[:1].upper() + text[1:]


def render_device(device):
    """Trang chọn app cho một thiết bị."""
    info = DEVICE_APPS[device]
    lines = [
        f"• <b>{APP_GUIDES[app_id]['name']}</b> — {APP_GUIDES[app_id]['source']}"
        for app_id in info["apps"]
    ]
    return "\n\n".join([
        f"{info['icon']} <b>{info['name'].upper()}</b>\n"
        "<i>Chọn một ứng dụng để xem hướng dẫn</i>",
        card(lines),
        "💡 Cần có cấu hình mà bot gửi sau khi đăng ký gói nền.",
    ])


def render_step(app_id, number):
    """Một bước trong hướng dẫn của app (có thanh tiến độ)."""
    app = APP_GUIDES[app_id]
    info = DEVICE_APPS[app["device"]]
    total = len(app["steps"])
    title, detail = app["steps"][number - 1]
    progress = "▰" * number + "▱" * (total - number)
    blocks = [
        f"{info['icon']} <b>{app['name']}</b> · <i>{info['name']}</i>",
        f"<b>Bước {number}/{total}</b> · {title}\n{progress}",
        card([detail]),
    ]
    if number == total:
        if app.get("tip"):
            blocks.append(f"💡 {app['tip']}")
        blocks.append("🎉 Xong rồi, chúc bạn dùng vui vẻ!")
    return "\n\n".join(blocks)


# Trang chọn app theo thiết bị: callback_data = "android" / "ios" / "windows".
DEVICE_TEXTS = {device: render_device(device) for device in DEVICE_APPS}

# Trang từng bước: callback_data = "step_<mã app>_<số bước>".
STEP_TEXTS = {}
# "step_..." -> (mã app, số bước, tổng số bước, thiết bị) để dựng nút điều hướng.
STEP_INFO = {}
for _app_id, _app in APP_GUIDES.items():
    _total = len(_app["steps"])
    for _number in range(1, _total + 1):
        _key = f"step_{_app_id}_{_number}"
        STEP_TEXTS[_key] = render_step(_app_id, _number)
        STEP_INFO[_key] = (_app_id, _number, _total, _app["device"])


PAGES = {
    "gonen": "\n\n".join([
        "📶 <b>GÓI NỀN 4G/5G</b>\n"
        "<i>Đăng ký gói nền để có data ưu tiên trên mọi ứng dụng</i>",
        section("CHỌN NHÀ MẠNG") + "\n" + card([
            "🔴 <b>Viettel</b> — TikTok 50K, gói tuần T15KN, MXH100",
            "🔵 <b>VinaPhone</b> — gói 0 NỀN miễn phí, TK30",
            "🟢 <b>MobiFone</b> — gói DK TIK30 30 ngày",
        ]),
        section("LƯU Ý") + "\n" + card([REGISTER_WARNING]),
    ]),
    "thueid": "\n\n".join([
        "🔐 <b>THUÊ ID SHADOWROCKET</b>\n"
        "<i>Thông tin thuê Apple ID hỗ trợ tải ứng dụng</i>",
        section("BẠN SẼ NHẬN ĐƯỢC") + "\n" + card([
            "🍎 <b>Apple ID</b> dùng riêng cho việc tải ứng dụng",
            "🔑 Thông tin đăng nhập kèm hướng dẫn sử dụng",
        ]),
        section("LIÊN HỆ") + "\n" + card([
            f"💬 Quản trị viên: <b>@{ADMIN_USERNAME}</b>",
            WEBSITE_LINE,
        ]),
    ]),
    "hotro": "\n\n".join([
        "🎧 <b>LIÊN HỆ HỖ TRỢ</b>\n"
        "<i>Đội ngũ 5G MATTER sẵn sàng hỗ trợ bạn</i>",
        card([
            f"💬 Quản trị viên: <b>@{ADMIN_USERNAME}</b>",
            WEBSITE_LINE,
            "🆔 Gửi kèm ID của bạn (lệnh <code>/id</code>) để được xử lý nhanh hơn",
        ]),
    ]),
    "sni": "\n\n".join([
        "🔁 <b>ĐỔI SNI</b>\n"
        "<i>Chọn loại SIM của bạn để xem hướng dẫn</i>",
        card([
            "🚫 <b>Không nền</b> — SIM VinaPhone 0đ",
            "✅ <b>Có nền</b> — tất cả các SIM còn lại",
        ]),
    ]),
    "sni_khongnen": "\n\n".join([
        "🚫 <b>ĐỔI SNI · KHÔNG NỀN</b>\n"
        "<i>Dành cho SIM VinaPhone 0đ</i>",
        card(["📸 Làm theo ảnh hướng dẫn."]),
    ]),
    "sni_conen": "\n\n".join([
        "✅ <b>ĐỔI SNI · CÓ NỀN</b>\n"
        "<i>Dành cho tất cả các SIM còn lại (có gói nền)</i>",
        card(["📸 Làm theo ảnh hướng dẫn."]),
    ]),
    "huongdan": HELP_TEXT,
}

GOI_NEN_TEXT = PAGES["gonen"]


# ==========================================
# GÓI NỀN THEO NHÀ MẠNG
# ==========================================
# Mỗi gói: tên, giá, mô tả ngắn, các ý chính và cách đăng ký.
# "key" chính là callback_data của nút tương ứng trong keyboards.py.
NETWORK_PACKAGES = {
    "vina": [
        {
            "key": "pkg_vina_0",
            "icon": "💎",
            "title": "0 NỀN",
            "price": "0đ/Tháng",
            "tagline": "Miễn phí — dùng ngay, không tốn phí",
            "bullets": [
                "Đăng ký gói VINA trên web là dùng được ngay",
                "Không cần thẻ cào, không tốn phí đăng ký",
            ],
            "note": "Hợp làm nền mở app, xem video, học tập",
            "action": f'<a href="{WEBSITE}">Đăng ký trên web</a>',
        },
        {
            "key": "pkg_vina_30",
            "icon": "🚀",
            "title": "TK30",
            "price": "30.000đ/tháng",
            "tagline": "Giá mềm — không giới hạn dung lượng",
            "bullets": [
                "Truy cập không giới hạn, không lo cháy data",
                "Tốc độ ổn định, được ưu tiên mạng",
            ],
            "note": "Hợp dùng thường xuyên — video, game, livestream",
            "action": "Soạn <code>TK30</code> gửi <code>888</code>",
        },
    ],
    "viettel": [
        {
            "key": "pkg_viettel_tiktok",
            "icon": "🎵",
            "title": "TikTok 50K",
            "price": "50.000đ/tháng",
            "tagline": "Tiết kiệm — 50K là đủ dùng cả tháng",
            "bullets": [
                "50GB data dành riêng cho TikTok",
                "Nạp đủ 50K là tự gia hạn, không cần thao tác mỗi tháng",
            ],
            "note": "Hợp người xem TikTok nhiều, muốn tiết kiệm",
            "action": "Soạn <code>T50k</code> gửi <code>191</code>",
        },
        {
            "key": "pkg_viettel_t15kn",
            "icon": "📆",
            "title": "Gói tuần T15KN",
            "price": "15.000đ/tuần",
            "tagline": "Khuyến dùng — rẻ nhất, tổng 100GB/tháng",
            "bullets": [
                "25GB data tốc độ cao dùng trong 7 ngày",
                "Nạp đủ 60K — mỗi tuần tự gia hạn, không cần thao tác",
                "Cả tháng tính ra khoảng 100GB",
            ],
            "note": "Hợp dùng vừa phải, muốn linh hoạt theo tuần",
            "action": "Soạn <code>T15KN</code> gửi <code>191</code>",
        },
        {
            "key": "pkg_viettel_mxh100",
            "icon": "💪",
            "title": "Gói MXH100",
            "price": "100.000đ/tháng",
            "tagline": "Thoải mái — không lo hết dữ lượng",
            "bullets": [
                "1GB/ngày — cả tháng 30GB",
                "Bật kèm app là không giới hạn GB",
            ],
            "note": "Hợp hay xem video, livestream, chơi game nặng",
            "action": "Soạn <code>MXH100</code> gửi <code>191</code>",
        },
    ],
    "mobi": [
        {
            "key": "pkg_mobi_tiktok",
            "icon": "🎵",
            "title": "DK TIK30",
            "price": "50.000đ/tháng",
            "tagline": "Tiết kiệm — đủ dùng cho nhu cầu cơ bản",
            "bullets": [
                "50GB data tốc độ cao",
                "Hạn 30 ngày, có thể gia hạn tiếp",
            ],
            "note": "Nên để SIM 0đ — tránh bị trừ tiền trong tài khoản",
            "action": "Soạn <code>DK TIK30</code> gửi <code>9199</code>",
        },
    ],
}

NETWORK_HEADERS = {
    "vina": ("🔵", "Gói nền VinaPhone"),
    "viettel": ("🔴", "Gói nền Viettel"),
    "mobi": ("🟢", "Gói nền MobiFone"),
}


def package_card(package):
    """Dựng một thẻ gói cước.

    Dùng <blockquote> (khung gạch dọc native của Telegram) thay vì
    khung kín, vì khung ╭─╮ sẽ bị lệch cạnh phải khi Telegram render
    bằng font tỉ lệ (chỉ <pre> mới giữ được độ rộng cố định, mà <pre>
    lại mất bold/italic/link). Gạch trái luôn căn, nội dung vẫn định
    dạng đầy đủ.
    """
    icon = package.get("icon", "📦")
    lines = [
        f"<b>{icon} {package['title']}</b> · <code>{package['price']}</code>",
    ]
    if package.get("tagline"):
        lines.append(f"<i>{package['tagline']}</i>")
    for bullet in package["bullets"]:
        lines.append(f"• {bullet}")
    if package.get("note"):
        lines.append(f"💡 {package['note']}")
    lines.append(f"👉 {package['action']}")
    return card(lines)


def render_network(network, only_key=None):
    """Dựng nội dung trang nhà mạng.

    - only_key=None: hiện toàn bộ gói của nhà mạng.
    - only_key có giá trị: chỉ hiện gói đó (dùng cho trang chi tiết).

    Mọi "khối" được nối bằng một dòng trống, nên tách theo "\\n\\n"
    cho ra đúng: header, cảnh báo, từng thẻ gói, và footer.
    """
    icon, title = NETWORK_HEADERS[network]
    packages = NETWORK_PACKAGES[network]
    if only_key is not None:
        packages = [
            package for package in packages
            if package["key"] == only_key
        ]
        subtitle = "<i>Chi tiết gói — đăng ký theo hướng dẫn bên dưới</i>"
    else:
        subtitle = (
            f"<i>{len(packages)} gói nền — ưu tiên data cho mọi ứng dụng</i>"
        )

    blocks = [
        f"{icon} <b>{title}</b>\n{subtitle}",
        REGISTER_WARNING,
    ]
    for package in packages:
        blocks.append(package_card(package))
    return "\n\n".join(blocks)


VIETTEL_TEXT = render_network("viettel")
VINA_TEXT = render_network("vina")
MOBI_TEXT = render_network("mobi")

# Trang chi tiết từng gói: cùng định dạng, chỉ hiện đúng một gói.
PACKAGE_TEXTS = {
    package["key"]: render_network(network, only_key=package["key"])
    for network, packages in NETWORK_PACKAGES.items()
    for package in packages
}

# callback quay lại của từng gói -> nhà mạng tương ứng,
# để nút "Quay lại" luôn đưa người dùng về đúng trang đang xem.
PACKAGE_NETWORK = {
    "pkg_viettel_tiktok": "net_viettel",
    "pkg_viettel_t15kn": "net_viettel",
    "pkg_viettel_mxh100": "net_viettel",
    "pkg_vina_0": "net_vina",
    "pkg_vina_30": "net_vina",
    "pkg_mobi_tiktok": "net_mobi",
}


# ==========================================
# NỘI DUNG LỆNH /id VÀ /ping
# ==========================================
def user_info_text(user):
    """Dựng nội dung lệnh /id từ thông tin người dùng."""
    return "\n\n".join([
        "🆔 <b>THÔNG TIN CỦA BẠN</b>\n"
        "<i>Gửi thông tin này cho quản trị viên khi cần hỗ trợ</i>",
        section("TÀI KHOẢN") + "\n" + card([
            f"👤 <b>Tên:</b> {escape(user.full_name)}",
            f"🔗 <b>Username:</b> @{escape(user.username)}"
            if user.username else "🔗 <b>Username:</b> <i>chưa đặt</i>",
            f"🆔 <b>ID:</b> <code>{user.id}</code>",
        ]),
        "💡 Nhấn <code>/id</code> bất cứ lúc nào để xem lại thông tin này.",
    ])


def ping_text(elapsed_ms, uptime_seconds):
    """Dựng nội dung lệnh /ping."""
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "\n\n".join([
        "🏓 <b>PONG!</b>\n<i>Phản hồi tức thì</i>",
        section("HIỆU NĂNG") + "\n" + card([
            f"⏱️ <b>Phản hồi:</b> <code>{elapsed_ms:.0f} ms</code>",
            f"🕐 <b>Đã hoạt động:</b> <code>{hours}h {minutes}m {seconds}s</code>",
        ]),
    ])


# ==========================================
# NỘI DUNG LỆNH QUẢN TRỊ
# ==========================================
def restart_requested_text():
    """Nội dung phản hồi khi quản trị viên yêu cầu khởi động lại bot."""
    return "\n\n".join([
        "♻️ <b>ĐANG KHỞI ĐỘNG LẠI BOT</b>\n"
        "<i>Bot sẽ trở lại sau khoảng 1–2 phút</i>",
        "🔕 Trong lúc này bot sẽ tạm ngừng phản hồi.",
    ])


def restart_failed_text(reason):
    """Nội dung phản hồi khi khởi động lại thất bại."""
    return "\n\n".join([
        "❌ <b>KHỞI ĐỘNG LẠI THẤT BẠI</b>\n"
        "<i>Bot vẫn đang chạy bình thường</i>",
        section("LÝ DO") + "\n" + card([
            f"🧾 <code>{escape(reason)}</code>",
        ]),
        section("CÁCH XỬ LÝ") + "\n" + card([
            "🌐 Vào GitHub → tab <b>Actions</b> → <b>5G MATTER Bot</b>.",
            "🔁 Bấm <b>Run workflow</b> để chạy lại bot.",
        ]),
    ])


def restart_not_allowed_text():
    """Nội dung phản hồi khi người dùng không phải quản trị viên."""
    return "\n\n".join([
        "🚫 <b>KHÔNG CÓ QUYỀN</b>\n"
        "<i>Lệnh này chỉ dành cho quản trị viên</i>",
        section("GỢI Ý") + "\n" + card([
            "💬 Cần hỗ trợ? Bấm nút <b>Liên hệ hỗ trợ</b>.",
            WEBSITE_LINE,
        ]),
    ])


# ==========================================
# KHÔNG KHỚP TỪ KHÓA (chỉ hiện trong chat riêng)
# ==========================================
FALLBACK_TEXT = (
    "🤔 <b>Mình chưa hiểu ý bạn</b>\n"
    "<i>Thử gõ từ khóa như <code>iphone</code>, <code>gói nền</code>, "
    "<code>sni</code> hoặc bấm /menu để xem danh sách.</i>"
)
