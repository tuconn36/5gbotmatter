"""Chèn ảnh minh hoạ vào các trang của bot.

Cách hoạt động: đặt ảnh vào thư mục images/ với tên trùng mã trang
(vd images/android_v2rayng_1.png = ảnh bước 1 của v2rayNG). Bot sẽ gắn ảnh đó lên ĐẦU tin nhắn
dưới dạng link preview của Telegram, nên vẫn dùng được với nút bấm
(không phải gửi lại tin mới). Trang nào chưa có ảnh thì hiện như cũ.

Điều kiện: ảnh phải tải được qua một URL công khai.
  - Chạy trên GitHub Actions (repo PUBLIC): tự dùng raw.githubusercontent.com.
  - Chạy nơi khác: đặt biến IMAGE_BASE_URL, vd https://domain.com/images/
"""

import os

from telegram import LinkPreviewOptions

from config import BASE_DIR

IMAGES_DIR = os.path.join(BASE_DIR, "images")
EXTENSIONS = ("png", "jpg", "jpeg")

# Nút quay lại / lệnh khác tên nhưng dùng chung ảnh với trang gốc.
ALIASES = {
    "start": "home",
    "menu": "home",
    "help": "huongdan",
    "hdsd": "huongdan",
    "back_gonen": "gonen",
    "package_back": "gonen",
    "back_viettel": "net_viettel",
    "back_vina": "net_vina",
    "back_mobi": "net_mobi",
}

_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def _base_url():
    """URL thư mục chứa ảnh (kết thúc bằng '/'), hoặc '' nếu không xác định."""
    url = os.environ.get("IMAGE_BASE_URL", "").strip()
    if url:
        return url.rstrip("/") + "/"
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        branch = os.environ.get("GITHUB_REF_NAME") or "main"
        return f"https://raw.githubusercontent.com/{repo}/{branch}/images/"
    return ""


def find_image(key):
    """Trả về tên file ảnh của trang `key` (nếu có trong images/)."""
    key = ALIASES.get(key, key)
    if key.startswith("step_"):
        key = key[len("step_"):]  # ảnh của bước: <mã app>_<số bước>.png
    for ext in EXTENSIONS:
        name = f"{key}.{ext}"
        if os.path.isfile(os.path.join(IMAGES_DIR, name)):
            return name
    return None


def preview_options(key):
    """LinkPreviewOptions cho trang `key`.

    Có ảnh -> hiện ảnh lớn phía trên nội dung.
    Không có ảnh -> tắt hẳn link preview (tránh Telegram tự xem trước
    link website trong nội dung).
    """
    base = _base_url()
    name = find_image(key) if base else None
    if not name:
        return _NO_PREVIEW
    return LinkPreviewOptions(
        url=base + name,
        show_above_text=True,
        prefer_large_media=True,
    )
