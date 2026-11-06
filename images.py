"""Chèn ảnh minh hoạ vào các trang của bot."""

import os
from functools import lru_cache

from telegram import LinkPreviewOptions

from config import BASE_DIR

IMAGES_DIR = os.path.join(BASE_DIR, "images")
# image_links.txt nằm trong images/; vẫn hỗ trợ đặt ở thư mục gốc (cách cũ).
LINKS_FILES = (
    os.path.join(IMAGES_DIR, "image_links.txt"),
    os.path.join(BASE_DIR, "image_links.txt"),
)
EXTENSIONS = ("png", "jpg", "jpeg")

# Nút quay lại / lệnh khác tên nhưng dùng chung ảnh với trang gốc.
ALIASES = {
    "start": "home",
    "menu": "home",
    "help": "huongdan",
    "hdsd": "huongdan",
    "vpn": "sni",
    "sni_khongnen": "sni_khongnen_1",
    "sni_conen": "sni_conen_1",
    "back_gonen": "gonen",
    "package_back": "gonen",
    "back_viettel": "net_viettel",
    "back_vina": "net_vina",
    "back_mobi": "net_mobi",
}

_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def canonical(key):
    """Đổi mã trang/callback thành tên ảnh.

    "step_android_v2rayng_2" -> "android_v2rayng_2"
    "menu"                   -> "home"
    """
    key = ALIASES.get(key, key)
    if key.startswith("step_"):
        key = key[len("step_"):]
    return key


@lru_cache(maxsize=1)
def load_links():
    """Đọc image_links.txt -> {tên_ảnh: url}. Dòng sai/để trống bị bỏ qua."""
    links = {}
    # Duyệt ngược để file đứng trước (images/) ghi đè file đứng sau.
    for path in reversed(LINKS_FILES):
        try:
            with open(path, encoding="utf-8-sig") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    name, _, url = line.partition("=")
                    name, url = name.strip(), url.strip()
                    if name and url.lower().startswith(("http://", "https://")):
                        links[name] = url
        except OSError:
            continue
    return links


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
    """Trả về tên file ảnh của trang `key` trong images/ (nếu có)."""
    name = canonical(key)
    for ext in EXTENSIONS:
        filename = f"{name}.{ext}"
        if os.path.isfile(os.path.join(IMAGES_DIR, filename)):
            return filename
    return None


def image_url(key):
    """URL ảnh của trang `key`, hoặc None nếu chưa có."""
    url = load_links().get(canonical(key))
    if url:
        return url
    base = _base_url()
    filename = find_image(key) if base else None
    return base + filename if filename else None


def preview_options(key):
    """LinkPreviewOptions cho trang `key`.

    Có ảnh -> hiện ảnh lớn phía trên nội dung.
    Không có ảnh -> tắt hẳn link preview (tránh Telegram tự xem trước
    link website trong nội dung).
    """
    url = image_url(key)
    if not url:
        return _NO_PREVIEW
    return LinkPreviewOptions(url=url, show_above_text=True, prefer_large_media=True)
