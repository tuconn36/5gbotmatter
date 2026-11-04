"""Nội dung hiển thị của bot 5G MATTER.

Tất cả nội dung dùng HTML parse mode của Telegram.
Ký tự đặc biệt phải escape: & -> &amp; , < -> &lt; , > -> &gt;

NGUYÊN TẮC THIẾT KẾ GIAO DIỆN
------------------------------
1. Mọi khối "thẻ" dùng <blockquote>. Đây là khung gạch dọc native của
   Telegram: cạnh trái luôn thẳng hàng ở mọi client (kể cả khi client
   dùng font tỉ lệ), khác với khung kín ╭─╮ bị lệch cạnh phải.
2. Tiêu đề dùng <b>, mô tả phụ dùng <i>, giá / mã đăng ký dùng <code>
   để nổi bật như một "chip" nhỏ.
3. Nhãn mục dùng "▌ <b>TIÊU ĐỀ</b>" tạo cảm giác tab mở đầu khối.
4. Không dùng quá nhiều ký tự trang trí: khoảng cách trắng + nhãn mục
   đã đủ để tách khối, giữ tin nhắn gọn và dễ đọc trên màn hình nhỏ.
"""

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
    SEP,
    section("THEO THIẾT BỊ") + "\n" + card([
        "Chọn thiết bị của bạn để xem hướng dẫn cài đặt",
        "và cách dùng đầy đủ.",
    ]),
    section("GÓI CƯỚC &amp; DỊCH VỤ") + "\n" + card([
        "📶 <b>Gói nền 4G/5G</b> — bảng giá theo Viettel, VinaPhone, MobiFone",
        "🔐 <b>Thuê ID Shadowrocket</b> — hỗ trợ tải ứng dụng",
    ]),
    "💬 Cần hỗ trợ? Bấm nút <b>Liên hệ hỗ trợ</b> bên dưới.",
])


# ==========================================
# HƯỚNG DẪN SỬ DỤNG
# ==========================================
HELP_TEXT = "\n\n".join([
    "❓ <b>HƯỚNG DẪN SỬ DỤNG</b>\n<i>Bot tự hiểu từ khóa, không cần nhớ lệnh</i>",
    section("CÁCH 1 — DÙNG NÚT") + "\n" + card([
        "Chọn thiết bị hoặc gói cước ngay trên menu,",
        "bot sẽ mở đúng trang hướng dẫn.",
    ]),
    section("CÁCH 2 — GÕ TỪ KHÓA") + "\n" + card([
        "Gõ <code>iphone</code>, <code>android</code>, <code>windows</code>,",
        "<code>gói nền</code>, <code>thuê id</code>, <code>hỗ trợ</code>…",
        "Bot sẽ tự động trả lời đúng trang.",
    ]),
    section("LỆNH NHANH") + "\n" + card([
        "<code>/start</code> · <code>/menu</code> · <code>/huongdan</code> · "
        "<code>/id</code> · <code>/ping</code>",
    ]),
    "💬 Cần trợ giúp? Bấm nút <b>Liên hệ hỗ trợ</b>.",
])


# ==========================================
# CÁC TRANG NỘI DUNG
# ==========================================
def _device_page(icon, name, steps):
    """Dựng trang hướng dẫn cho một thiết bị.

    steps: danh sách các bước (mỗi bước một dòng) đã escape sẵn.
    """
    return "\n\n".join([
        f"{icon} <b>{name.upper()}</b>\n"
        f"<i>Hướng dẫn cài đặt &amp; sử dụng trên {name}</i>",
        section("TRƯỚC KHI BẮT ĐẦU") + "\n" + card([
            "① Mở <b>Telegram</b> và nhắn tin cho bot",
            "② Chọn <b>Gói nền 4G/5G</b> đúng nhà mạng của bạn",
            "③ Nhận file cấu hình và làm theo hướng dẫn",
        ]),
        section("DỊCH VỤ PHÙ HỢP") + "\n" + card([
            "📶 <b>Gói nền 4G/5G</b> — data nền ưu tiên cho mọi app",
            "🛡️ <b>Dịch vụ VPN</b> — ẩn IP, mở khóa nội dung",
        ]),
        section("HƯỚNG DẪN CÀI ĐẶT") + "\n" + card(steps),
        section("CẦN HỖ TRỢ") + "\n" + card([
            "💬 Bấm nút <b>Liên hệ hỗ trợ</b> để được admin hỗ trợ trực tiếp.",
            f"📝 Hoặc đăng ký tại {WEBSITE_LINE}",
        ]),
    ])


PAGES = {
    "android": _device_page(
        "🤖",
        "Android",
        [
            "① Mở <b>Telegram</b> → chọn <b>Gói nền</b> → đúng nhà mạng",
            "② Đăng ký gói (hoặc soạn mã đăng ký gửi đầu số)",
            "③ Tải file cấu hình mà bot gửi cho bạn",
            "④ Mở <b>Shadowrocket</b> → <b>＋</b> → <b>Import from File</b>",
            "⑤ Chọn file vừa tải → bật công tắc kết nối",
        ],
    ),
    "ios": _device_page(
        "🍎",
        "iOS",
        [
            "① Mở <b>Telegram</b> → chọn <b>Gói nền</b> → đúng nhà mạng",
            "② Đăng ký gói (hoặc soạn mã đăng ký gửi đầu số)",
            "③ Tải file cấu hình mà bot gửi cho bạn",
            "④ Tải <b>Shadowrocket</b> từ <b>App Store</b> (bản trả phí)",
            "⑤ Mở app → <b>＋</b> → <b>Import from File</b> → chọn file",
            "⑥ Bật công tắc kết nối → cho phép thêm cấu hình VPN proxy",
        ],
    ),
    "windows": _device_page(
        "🖥️",
        "Windows",
        [
            "① Mở <b>Telegram</b> → chọn <b>Gói nền</b> → đúng nhà mạng",
            "② Đăng ký gói (hoặc soạn mã đăng ký gửi đầu số)",
            "③ Tải file cấu hình mà bot gửi cho bạn",
            "④ Cài <b>v2rayN</b> (Windows) rồi mở lên",
            "⑤ Menu <b>Servers</b> → <b>Import server from file</b> → chọn file",
            "⑥ Bấm <b>Enter</b> để chọn server, rồi <b>Set as system proxy</b>",
            "⑦ Tắt kết nối: bỏ chọn <b>System proxy</b> trong v2rayN",
        ],
    ),
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
        section("LIÊN HỆ NHANH NHẤT") + "\n" + card([
            f"💬 Quản trị viên: <b>@{ADMIN_USERNAME}</b>",
            WEBSITE_LINE,
        ]),
        section("MẸO NHANH") + "\n" + card([
            "🆔 Nhấn <code>/id</code> để lấy ID Telegram của bạn,",
            "gửi kèm ID khi cần hỗ trợ để được phản hồi nhanh hơn.",
        ]),
    ]),
    "vpn": "\n\n".join([
        "🛡️ <b>DỊCH VỤ VPN</b>\n"
        "<i>Kết nối an toàn · Ẩn IP · Mở khóa nội dung</i>",
        section("TÍNH NĂNG") + "\n" + card([
            "🌍 <b>Đa quốc gia</b> — nhiều vị trí máy chủ",
            "⚡ <b>Tốc độ cao</b> — ổn định, không giật lag",
            "🎬 <b>Mở khóa nội dung</b> — xem nội dung bị chặn theo vùng",
        ]),
        section("HƯỚNG DẪN CÀI ĐẶT") + "\n" + card([
            "① Cài <b>Shadowrocket</b> (iOS/macOS) hoặc <b>v2rayN</b> (Windows)",
            "② Nhập file cấu hình mà bot gửi cho bạn qua <b>Import</b>",
            "③ Bật công tắc kết nối và chọn server phù hợp",
        ]),
        section("GÓI DỊCH VỤ") + "\n" + card([
            "⏳ Thời hạn: <b>1 tháng</b> · <b>3 tháng</b> · <b>12 tháng</b>",
            "📱 Hỗ trợ: <b>Android</b> · <b>iOS</b> · <b>Windows</b>",
        ]),
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
            "tagline": "Rẻ nhất — không giới hạn dung lượng",
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
    "vina": ("🔵", "Gói nền Vinaphone"),
    "viettel": ("🔴", "Gói nền Viettel"),
    "mobi": ("🟢", "Gói nền Mobifone"),
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
        section("⚠️ LƯU Ý BẮT BUỘC") + "\n" + card([REGISTER_WARNING]),
        section("CÁC GÓI HIỆN CÓ"),
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
        "<i>Lệnh đã được gửi tới máy chủ</i>",
        section("TRẠNG THÁI") + "\n" + card([
            "⏳ Đang tạo phiên chạy mới trên GitHub Actions…",
            "⏱️ Bot sẽ trở lại sau vài chục giây.",
        ]),
        section("LƯU Ý") + "\n" + card([
            "🔕 Bot sẽ ngừng phản hồi trong lúc khởi động lại.",
            "🆔 Nhắn <code>/id</code> nếu cần kiểm tra lại thông tin.",
        ]),
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
            "🌐 Vào GitHub → Actions → chạy workflow <code>bot.yml</code>.",
            "🔁 Hoặc nhấn nút <b>Run workflow</b> trên tab Actions.",
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
    "<code>vpn</code> hoặc bấm /menu để xem danh sách.</i>"
)
