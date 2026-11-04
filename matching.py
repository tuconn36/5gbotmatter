"""Khớp từ khóa tiếng Việt (không phụ thuộc Telegram, dễ kiểm thử).

Điểm quan trọng: so khớp KHÔNG phân biệt dấu và dạng Unicode.
"gói nền", "goi nen" và "gói nền" (dạng NFD do một số bàn phím gửi)
đều khớp cùng một từ khóa.
"""

import re
import unicodedata


def normalize(text):
    """Chữ thường, bỏ dấu tiếng Việt, gộp khoảng trắng."""
    text = unicodedata.normalize("NFD", text.casefold())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    return re.sub(r"\s+", " ", text).strip()


# Từ khóa viết có dấu cho dễ đọc; sẽ được chuẩn hoá khi nạp.
KEYWORDS = {
    "vpn": [
        "vpn", "vpn free", "vpn premium", "đổi ip", "ẩn ip", "unlock",
        "mở khóa", "bypass", "proxy", "socks5",
    ],
    "ios": ["ios", "iphone", "ipad"],
    "android": ["android", "ard"],
    "windows": ["windows", "win pc", "máy tính", "pc"],
    "gonen": [
        "gói nền 4g", "gói nền 5g", "gói nền", "nền 4g", "nền 5g",
        "gói data",
    ],
    "thueid": ["thuê apple id", "thuê id", "shadowrocket", "apple id"],
    "hotro": ["hỗ trợ", "liên hệ", "admin", "quản trị", "tư vấn"],
    "menu": ["trang chủ", "menu"],
    "huongdan": [
        "hướng dẫn sử dụng", "hướng dẫn", "cách dùng", "help",
    ],
}

# Thứ tự ưu tiên khi nhiều nhóm từ khóa cùng khớp.
# Dịch vụ (gói nền / thuê id / vpn / hỗ trợ) cao hơn thiết bị, vì "gói nền
# cho windows" nghĩa là muốn xem gói nền chứ không phải trang cài đặt.
PAGE_PRIORITY = {
    "menu": 0,
    "huongdan": 1,
    "ios": 2,
    "android": 2,
    "windows": 2,
    "hotro": 3,
    "gonen": 3,
    "thueid": 3,
    "vpn": 3,
}


def _compile(words):
    """Chuẩn hoá và biên dịch sẵn regex nguyên-từ cho từng từ khóa."""
    seen = {}
    for word in words:
        norm = normalize(word)
        if norm and norm not in seen:
            seen[norm] = re.compile(r"(?<!\w)" + re.escape(norm) + r"(?!\w)")
    return list(seen.items())


_COMPILED = {page: _compile(words) for page, words in KEYWORDS.items()}


def contains_keyword(text, word):
    """Tìm từ khóa nguyên từ trong text (cả hai tự chuẩn hoá)."""
    norm = normalize(word)
    pattern = r"(?<!\w)" + re.escape(norm) + r"(?!\w)"
    return re.search(pattern, normalize(text)) is not None


def pick_page(text):
    """Trả về page khớp từ khóa, hoặc None.

    - Ưu tiên page theo PAGE_PRIORITY.
    - Cùng mức ưu tiên thì chọn từ khóa dài nhất
      (ví dụ "gói nền 4g" thắng "gói nền").
    """
    text = normalize(text)
    best_page = None
    best_score = None
    for page, compiled in _COMPILED.items():
        longest = 0
        for norm, pattern in compiled:
            if len(norm) > longest and pattern.search(text):
                longest = len(norm)
        if not longest:
            continue
        score = (PAGE_PRIORITY.get(page, 0), longest)
        if best_score is None or score > best_score:
            best_score = score
            best_page = page
    return best_page
