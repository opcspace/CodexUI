#!/usr/bin/env python3
"""Safely inventory a non-.codexskin source without executing or extracting it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import unicodedata
import zipfile
from pathlib import Path
from typing import Iterable


MAX_FILES = 512
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
IGNORED_DIRECTORIES = {".git", ".build", "node_modules", "__pycache__"}
ACTIVE_EXTENSIONS = {
    ".app",
    ".bash",
    ".bin",
    ".cjs",
    ".command",
    ".dylib",
    ".exe",
    ".fish",
    ".js",
    ".mjs",
    ".pl",
    ".py",
    ".rb",
    ".sh",
    ".so",
    ".zsh",
}
STYLESHEET_EXTENSIONS = {".css", ".less", ".sass", ".scss"}
RASTER_EXTENSIONS = {".jpeg", ".jpg", ".png"}
CONVERT_IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".heic",
    ".ico",
    ".svg",
    ".tif",
    ".tiff",
    ".webp",
}
THEME_DATA_EXTENSIONS = {".json", ".plist", ".toml", ".yaml", ".yml"}
ARCHIVE_EXTENSIONS = {".7z", ".gz", ".rar", ".tar", ".tgz", ".zip"}
FONT_EXTENSIONS = {".eot", ".otf", ".ttf", ".woff", ".woff2"}
DOCUMENT_EXTENSIONS = {".md", ".txt"}
LICENSE_MARKERS = {"attribution", "copyright", "license", "licenses", "notice"}


def json_bytes(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def normalized_path(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def validate_relative_path(value: str) -> str:
    if (
        not value
        or len(value.encode("utf-8")) > 512
        or value.startswith(("/", "~"))
        or "\\" in value
        or "\0" in value
        or "//" in value
    ):
        raise ValueError(f"不安全路径：{value!r}")
    components = value.split("/")
    if any(component in {"", ".", ".."} for component in components):
        raise ValueError(f"不安全路径：{value!r}")
    return value


def category_for(path: str) -> str:
    lowered = path.casefold()
    name = Path(path).name.casefold()
    suffix = Path(name).suffix
    parts = {part.casefold() for part in Path(path).parts}
    if (
        suffix in DOCUMENT_EXTENSIONS
        and (any(marker in name for marker in LICENSE_MARKERS) or "licenses" in parts)
    ):
        return "license"
    if suffix in ACTIVE_EXTENSIONS:
        return "active-content"
    if suffix in STYLESHEET_EXTENSIONS:
        return "stylesheet"
    if suffix in RASTER_EXTENSIONS:
        return "raster-image"
    if suffix in CONVERT_IMAGE_EXTENSIONS:
        return "image-conversion-required"
    if suffix in THEME_DATA_EXTENSIONS:
        return "theme-data"
    if suffix in FONT_EXTENSIONS:
        return "unsupported-binary"
    if suffix in ARCHIVE_EXTENSIONS:
        return "nested-archive"
    if suffix in DOCUMENT_EXTENSIONS:
        return "documentation"
    if lowered.endswith(".codexskin"):
        return "already-codexskin"
    return "other"


def descriptor(path: str, data: bytes) -> dict[str, object]:
    return {
        "byteCount": len(data),
        "category": category_for(path),
        "path": path,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def ensure_limits(file_count: int, total_bytes: int, path: str, byte_count: int) -> None:
    if file_count > MAX_FILES:
        raise ValueError(f"文件数量超过 {MAX_FILES}：{path}")
    if byte_count <= 0 or byte_count > MAX_FILE_BYTES:
        raise ValueError(f"文件大小不安全：{path}")
    if total_bytes > MAX_TOTAL_BYTES:
        raise ValueError("检查内容总大小超过 128 MB")


def inspect_directory(source: Path) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    total_bytes = 0
    seen: set[str] = set()
    for directory, directory_names, file_names in os.walk(source, followlinks=False):
        directory_names[:] = sorted(
            name for name in directory_names if name not in IGNORED_DIRECTORIES
        )
        directory_path = Path(directory)
        for name in directory_names:
            child = directory_path / name
            if child.is_symlink():
                raise ValueError(f"源目录不能包含符号链接：{child.relative_to(source)}")
        for name in sorted(file_names):
            child = directory_path / name
            relative = validate_relative_path(child.relative_to(source).as_posix())
            metadata = child.lstat()
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"源目录不能包含符号链接：{relative}")
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError(f"源目录包含非普通文件：{relative}")
            key = normalized_path(relative)
            if key in seen:
                raise ValueError(f"源目录包含冲突路径：{relative}")
            seen.add(key)
            total_bytes += metadata.st_size
            ensure_limits(len(files) + 1, total_bytes, relative, metadata.st_size)
            data = child.read_bytes()
            if len(data) != metadata.st_size:
                raise ValueError(f"读取时文件大小发生变化：{relative}")
            files.append(descriptor(relative, data))
    return files


def is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0o170000
    return mode == stat.S_IFLNK


def inspect_zip(source: Path) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    total_bytes = 0
    seen: set[str] = set()
    try:
        archive = zipfile.ZipFile(source)
    except zipfile.BadZipFile as error:
        raise ValueError(f"ZIP 无效：{source}") from error
    with archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            path = info.filename.rstrip("/")
            if not path:
                continue
            validate_relative_path(path)
            if info.is_dir():
                continue
            if info.flag_bits & 0x1:
                raise ValueError(f"ZIP 包含加密文件：{path}")
            if is_zip_symlink(info):
                raise ValueError(f"ZIP 包含符号链接：{path}")
            key = normalized_path(path)
            if key in seen:
                raise ValueError(f"ZIP 包含冲突路径：{path}")
            seen.add(key)
            total_bytes += info.file_size
            ensure_limits(len(files) + 1, total_bytes, path, info.file_size)
            if info.compress_size == 0 and info.file_size > 0:
                raise ValueError(f"ZIP 压缩信息异常：{path}")
            if (
                info.compress_size > 0
                and info.file_size > info.compress_size * MAX_COMPRESSION_RATIO
            ):
                raise ValueError(f"ZIP 压缩比异常：{path}")
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ValueError(f"ZIP 文件大小不一致：{path}")
            files.append(descriptor(path, data))
    return files


def inspect_file(source: Path) -> list[dict[str, object]]:
    metadata = source.lstat()
    ensure_limits(1, metadata.st_size, source.name, metadata.st_size)
    data = source.read_bytes()
    if len(data) != metadata.st_size:
        raise ValueError(f"读取时文件大小发生变化：{source.name}")
    return [descriptor(source.name, data)]


def count_categories(files: Iterable[dict[str, object]]) -> dict[str, int]:
    categories = [str(item["category"]) for item in files]
    return {
        "activeContent": categories.count("active-content"),
        "files": len(categories),
        "imageConversionRequired": categories.count("image-conversion-required"),
        "licenses": categories.count("license"),
        "other": sum(
            category
            in {
                "already-codexskin",
                "documentation",
                "nested-archive",
                "other",
                "unsupported-binary",
            }
            for category in categories
        ),
        "rasterImages": categories.count("raster-image"),
        "stylesheets": categories.count("stylesheet"),
        "themeData": categories.count("theme-data"),
    }


def conversion_plan(summary: dict[str, int]) -> dict[str, object]:
    requires_template_review = summary["stylesheets"] > 0
    requires_asset_conversion = summary["imageConversionRequired"] > 0
    requires_rights_confirmation = summary["licenses"] == 0
    if requires_template_review or summary["activeContent"] > 0:
        route = "review-and-map-to-manager-template"
    elif summary["rasterImages"] > 0 or summary["themeData"] > 0:
        route = "build-declarative-source"
    else:
        route = "manual-review"
    return {
        "hasActiveContent": summary["activeContent"] > 0,
        "recommendedRoute": route,
        "requiresAssetConversion": requires_asset_conversion,
        "requiresRightsConfirmation": requires_rights_confirmation,
        "requiresTemplateReview": requires_template_review,
        "steps": [
            "确认素材来源、重新分发和商业使用边界。",
            "把 PNG/JPEG 复制到新 assets 目录；其他图片先转换为 PNG/JPEG。",
            "把旧 CSS 仅作为视觉参考，映射到现有或新增的管理器模板。",
            "创建 skin.json 与 LICENSES；不要复制旧脚本或二进制。",
            "使用 CodexSkinManager/scripts/build_codexskin.py 生成并测试 .codexskin。",
        ],
    }


def inspect_source(source: Path) -> dict[str, object]:
    source = source.expanduser()
    if source.is_symlink():
        raise ValueError(f"源路径不能是符号链接：{source}")
    source = source.resolve(strict=True)
    metadata = source.lstat()
    if stat.S_ISDIR(metadata.st_mode):
        input_kind = "directory"
        files = inspect_directory(source)
    elif stat.S_ISREG(metadata.st_mode):
        if source.suffix.casefold() == ".zip":
            input_kind = "zip"
            files = inspect_zip(source)
        else:
            input_kind = "file"
            files = inspect_file(source)
    else:
        raise ValueError(f"源路径必须是普通文件、目录或 ZIP：{source}")
    if not files:
        raise ValueError("源皮肤中没有可检查文件")
    summary = count_categories(files)
    return {
        "conversionPlan": conversion_plan(summary),
        "files": files,
        "inputKind": input_kind,
        "safety": {
            "activeContentPolicy": "Inventory only; never execute legacy scripts or binaries.",
            "archivePolicy": "Inspect ZIP entries in memory; never extract them to disk.",
        },
        "schemaVersion": 1,
        "source": str(source),
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="只读检查旧 Codex 皮肤，输出安全转换所需的 JSON 清单"
    )
    parser.add_argument("--source", required=True, type=Path, help="旧皮肤文件、目录或 ZIP")
    arguments = parser.parse_args()
    try:
        report = inspect_source(arguments.source)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    print(json_bytes(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
