"""Chức năng quản trị: khởi động lại bot."""

import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)

API_URL = "https://api.github.com"
API_VERSION = "2022-11-28"
WORKFLOW_FILE = os.environ.get("WORKFLOW_FILE", "bot.yml")


class RestartError(Exception):
    """Không khởi động lại được bot (lý do nằm trong message)."""


def _settings():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        raise RestartError(
            "Thiếu GITHUB_TOKEN hoặc GITHUB_REPOSITORY "
            "(lệnh này chỉ chạy khi bot đang chạy trên GitHub Actions)."
        )
    return {
        "token": token,
        "repo": repo,
        "ref": os.environ.get("GITHUB_REF_NAME") or "main",
        "run_id": os.environ.get("GITHUB_RUN_ID"),
    }


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }


def _reason(response):
    """Lấy thông điệp lỗi ngắn từ phản hồi GitHub (không lộ token)."""
    try:
        detail = response.json().get("message", "")
    except ValueError:
        detail = ""
    return f"GitHub trả về {response.status_code}: {detail or 'không rõ lý do'}"


async def restart_bot():
    """Dispatch run mới rồi huỷ run hiện tại."""
    cfg = _settings()
    headers = _headers(cfg["token"])
    repo = cfg["repo"]

    async with httpx.AsyncClient(timeout=15, headers=headers) as client:
        try:
            response = await client.post(
                f"{API_URL}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/dispatches",
                json={"ref": cfg["ref"]},
            )
        except httpx.HTTPError as error:
            raise RestartError(f"Không gọi được GitHub API: {type(error).__name__}") from error
        if response.status_code != 204:
            raise RestartError(_reason(response))

        run_id = cfg["run_id"]
        if not run_id:
            # Chạy local: không có run hiện tại để huỷ.
            logger.info("Không có GITHUB_RUN_ID, bỏ qua bước huỷ run hiện tại.")
            return

        # Chờ một chút để run mới kịp vào hàng đợi rồi mới huỷ run cũ.
        await asyncio.sleep(3)
        try:
            response = await client.post(
                f"{API_URL}/repos/{repo}/actions/runs/{run_id}/cancel"
            )
        except httpx.HTTPError as error:
            raise RestartError(f"Đã tạo run mới nhưng không huỷ được run cũ: {type(error).__name__}") from error
        if response.status_code not in (202, 204):
            raise RestartError("Đã tạo run mới nhưng không huỷ được run cũ. " + _reason(response))
