"""
Vite manifest reader for Frappe integration.

Reads the Vite-generated .vite/manifest.json to resolve hashed asset filenames
and provides Jinja helpers for injecting them into templates.
"""
import json
import os

_manifest_cache = None

APP_NAME = "project_management"
FRONTEND_DIR = "frontend"


def _get_manifest():
    global _manifest_cache
    if _manifest_cache is not None:
        return _manifest_cache

    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "public",
        FRONTEND_DIR,
        ".vite",
        "manifest.json",
    )

    if not os.path.exists(manifest_path):
        _manifest_cache = {}
        return _manifest_cache

    with open(manifest_path, "r") as f:
        _manifest_cache = json.load(f)
    return _manifest_cache


def _resolve_entry(entry_key=None):
    manifest = _get_manifest()
    if entry_key and entry_key in manifest:
        return manifest[entry_key]
    for key, value in manifest.items():
        if value.get("isEntry"):
            return value
    return {}


def _get_chunk(chunk_key):
    manifest = _get_manifest()
    if chunk_key in manifest:
        return manifest[chunk_key]
    for key, value in manifest.items():
        if value.get("file") == chunk_key or key == chunk_key:
            return value
    return None


def _asset_url(file_path):
    return f"/assets/{APP_NAME}/{FRONTEND_DIR}/{file_path}"


def get_vite_js(entry_key=None):
    entry = _resolve_entry(entry_key)
    if not entry:
        return []

    files = [_asset_url(entry["file"])]
    for imp in entry.get("imports", []):
        chunk = _get_chunk(imp)
        if chunk:
            files.append(_asset_url(chunk["file"]))
    return files


def get_vite_css(entry_key=None):
    entry = _resolve_entry(entry_key)
    if not entry:
        return []
    return [_asset_url(css) for css in entry.get("css", [])]
