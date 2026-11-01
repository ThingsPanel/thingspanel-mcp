"""Explicitly confirmed file operations for the Encore metadata candidate.

These routes require Community candidate d4e0540b or a compatible deployed
version. The service remains the authority for tenant and permissions.
"""
import hashlib
import hmac
import ipaddress
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote, urlsplit

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .config import config
from .encore_result import EncoreToolResult

UPLOAD_LIMIT = 10 * 1024 * 1024
DOWNLOAD_LIMIT = 512 * 1024 * 1024
_KEY = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
_HASH = re.compile(r'^"sha256-([a-fA-F0-9]{64})"$')


class _BoundedFile:
    """A file-like upload stream that aborts if its source grows past the cap."""
    def __init__(self, file):
        self.file = file
        self.total = 0

    def read(self, size=-1):
        maximum = UPLOAD_LIMIT - self.total + 1
        if size < 0 or size > maximum:
            size = maximum
        block = self.file.read(size)
        self.total += len(block)
        if self.total > UPLOAD_LIMIT:
            raise ValueError("file exceeds limit")
        return block


class EncoreAssetClient:
    def __init__(self, transport=None, config_obj=None):
        self.transport = transport
        self.config = config_obj or config

    def _identity(self, profile: str):
        credentials = self.config.get_profile(profile)
        token = credentials.get("thingspanel_token")
        base = self.config.encore_base_url
        target = urlsplit(base)
        try:
            local = target.hostname == "localhost" or ipaddress.ip_address(target.hostname or "").is_loopback
        except ValueError:
            local = False
        if not token or not target.hostname or target.username or target.password or target.query or target.fragment:
            raise ValueError("missing identity or invalid Encore endpoint")
        if target.scheme != "https" and not (target.scheme == "http" and local):
            raise ValueError("Encore endpoint requires HTTPS")
        return base.rstrip("/"), token

    async def upload(self, file_path: str, key: str, profile: str) -> Dict[str, Any]:
        if not _KEY.fullmatch(key or ""):
            return {"ok": False, "summary": "需要 8–128 个合法字符的幂等键。", "error": {"type": "invalid_idempotency_key"}}
        started = False
        try:
            base, token = self._identity(profile)
        except (KeyError, ValueError, TypeError):
            return {"ok": False, "summary": "Encore 地址或身份配置无效。", "error": {"type": "configuration"}}
        try:
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(file_path, flags)
            with os.fdopen(fd, "rb") as file:
                info = os.fstat(file.fileno())
                if not stat.S_ISREG(info.st_mode) or not 1 <= info.st_size <= UPLOAD_LIMIT:
                    return {"ok": False, "summary": "图片须为不超过 10 MiB 的非空普通文件。", "error": {"type": "invalid_file"}}
                async with httpx.AsyncClient(transport=self.transport, follow_redirects=False, trust_env=False, timeout=30) as http:
                    started = True
                    async with http.stream("POST", base + "/api/v2/file-assets", headers={"Authorization": "Bearer " + token, "Idempotency-Key": key, "Accept": "application/json"},
                                           data={"purpose": "template-image"}, files={"file": (Path(file_path).name, _BoundedFile(file), "application/octet-stream")}) as response:
                        if response.status_code >= 500 or 300 <= response.status_code < 400:
                            return {"ok": False, "summary": "上传结果未知；先查询，并仅用相同幂等键重试。", "status": response.status_code, "error": {"type": "outcome_unknown"}}
                        if response.status_code != 201:
                            return {"ok": False, "summary": "上传未被服务端接受。", "status": response.status_code, "error": {"type": "http_error"}}
                        chunks = bytearray()
                        async for part in response.aiter_bytes():
                            chunks.extend(part)
                            if len(chunks) > 1024 * 1024:
                                return {"ok": False, "summary": "上传响应过大，请使用相同幂等键查询或重试。", "error": {"type": "outcome_unknown"}}
                        try:
                            result = json.loads(chunks)
                        except (ValueError, UnicodeDecodeError):
                            return {"ok": False, "summary": "上传响应无效，请使用相同幂等键查询或重试。", "error": {"type": "outcome_unknown"}}
                        return {"ok": True, "summary": "文件资产已上传。", "status": 201, "data": result}
        except OSError:
            if not started:
                return {"ok": False, "summary": "无法读取图片文件。", "error": {"type": "invalid_file"}}
            return {"ok": False, "summary": "上传结果未知；先查询，并仅用相同幂等键重试。", "error": {"type": "outcome_unknown"}}
        except (ValueError, httpx.RequestError, httpx.TimeoutException):
            # Once a request starts, even a local read failure could have reached the server.
            return {"ok": False, "summary": "上传结果未知；先查询，并仅用相同幂等键重试。", "error": {"type": "outcome_unknown"}}

    async def download(self, download_id: str, output_path: str, profile: str) -> Dict[str, Any]:
        if not download_id or download_id in (".", "..") or any(c in download_id for c in "/?#%"):
            return {"ok": False, "summary": "下载标识无效。", "error": {"type": "invalid_id"}}
        if not output_path or not Path(output_path).name:
            return {"ok": False, "summary": "需要目标文件路径。", "error": {"type": "invalid_file"}}
        try:
            base, token = self._identity(profile)
        except (KeyError, ValueError, TypeError):
            return {"ok": False, "summary": "Encore 地址或身份配置无效。", "error": {"type": "configuration"}}
        target = Path(output_path)
        temporary = None
        try:
            if os.path.lexists(target):
                return {"ok": False, "summary": "目标文件已存在，不会覆盖。", "error": {"type": "destination_exists"}}
            async with httpx.AsyncClient(transport=self.transport, follow_redirects=False, trust_env=False, timeout=30) as http:
                async with http.stream("GET", base + "/api/v2/metadata-downloads/" + quote(download_id, safe=""), headers={"Authorization": "Bearer " + token}) as response:
                    if response.status_code != 200:
                        return {"ok": False, "summary": "下载服务未返回文件。", "status": response.status_code, "error": {"type": "http_error"}}
                    match = _HASH.fullmatch(response.headers.get("ETag", ""))
                    if not match:
                        return {"ok": False, "summary": "响应缺少有效 SHA-256 ETag。", "error": {"type": "invalid_checksum"}}
                    fd, temporary = tempfile.mkstemp(prefix=".thingspanel-download-", dir=str(target.parent))
                    digest = hashlib.sha256()
                    total = 0
                    with os.fdopen(fd, "wb") as out:
                        async for part in response.aiter_bytes():
                            total += len(part)
                            if total > DOWNLOAD_LIMIT:
                                return {"ok": False, "summary": "下载超过 512 MiB 上限。", "error": {"type": "download_too_large"}}
                            digest.update(part)
                            out.write(part)
                        out.flush()
                        os.fsync(out.fileno())
                    if not hmac.compare_digest(digest.hexdigest(), match.group(1).lower()):
                        return {"ok": False, "summary": "下载文件校验失败。", "error": {"type": "checksum_mismatch"}}
                    os.link(temporary, target)  # atomic and fails if target appears concurrently
                    return {"ok": True, "summary": "文件已下载并校验。", "data": {"output_path": str(target), "bytes": total, "sha256": digest.hexdigest()}}
        except FileExistsError:
            return {"ok": False, "summary": "目标文件已存在，不会覆盖。", "error": {"type": "destination_exists"}}
        except (OSError, ValueError, httpx.RequestError, httpx.TimeoutException):
            return {"ok": False, "summary": "下载失败，未创建目标文件。", "error": {"type": "download_failed"}}
        finally:
            if temporary is not None:
                try: os.unlink(temporary)
                except FileNotFoundError: pass


def register_encore_asset_tools(server: FastMCP, client: Optional[EncoreAssetClient] = None) -> int:
    api = client or EncoreAssetClient()

    async def encore_upload_template_image(file_path: str, idempotency_key: str, confirmed: bool = False,
                                            profile: str = "default") -> Dict[str, Any]:
        """上传模板图片；需要设备元数据候选和明确确认。成功不代表修改了模板。"""
        if not confirmed:
            return {"ok": False, "confirmation_required": True, "summary": "确认上传模板图片后再调用。"}
        return await api.upload(file_path, idempotency_key, profile)

    async def encore_download_metadata_artifact(download_id: str, output_path: str, confirmed: bool = False,
                                                 profile: str = "default") -> Dict[str, Any]:
        """校验并保存原生导出文件；需要设备元数据候选和明确确认。"""
        if not confirmed:
            return {"ok": False, "confirmation_required": True, "summary": "确认写入新文件后再调用。"}
        return await api.download(download_id, output_path, profile)

    for tool in (encore_upload_template_image, encore_download_metadata_artifact):
        tool.__annotations__["return"] = EncoreToolResult
        server.add_tool(tool, structured_output=True,
                        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False))
    return 2
