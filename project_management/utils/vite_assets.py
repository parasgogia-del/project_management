import json
import os

import frappe

APP_NAME = "project_management"
FRONTEND_DIR = "frontend"

manifest_cache = {}


def load_manifest():
	global manifest_cache
	# Re-read on every request in developer mode; cache only a non-empty manifest.
	if manifest_cache and not frappe.conf.developer_mode:
		return manifest_cache

	manifest_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)),
		"public",
		FRONTEND_DIR,
		".vite",
		"manifest.json",
	)

	if not os.path.exists(manifest_path):
		return {}

	with open(manifest_path) as f:
		manifest_cache = json.load(f)
	return manifest_cache


def resolve_entry(entry_key=None):
	manifest = load_manifest()
	if entry_key and entry_key in manifest:
		return manifest[entry_key]
	for value in manifest.values():
		if value.get("isEntry"):
			return value
	return {}


def get_chunk(chunk_key):
	manifest = load_manifest()
	if chunk_key in manifest:
		return manifest[chunk_key]
	for key, value in manifest.items():
		if value.get("file") == chunk_key or key == chunk_key:
			return value
	return None


def asset_url(file_path):
	return f"/assets/{APP_NAME}/{FRONTEND_DIR}/{file_path}"


def collect_css(chunk, visited=None):
	"""CSS of a chunk plus the CSS of every chunk it statically imports."""
	visited = visited if visited is not None else set()
	files = []
	for css in chunk.get("css", []):
		if css not in files:
			files.append(css)
	for imp in chunk.get("imports", []):
		if imp in visited:
			continue
		visited.add(imp)
		imported = get_chunk(imp)
		if imported:
			for css in collect_css(imported, visited):
				if css not in files:
					files.append(css)
	return files


def get_vite_js(entry_key=None):
	entry = resolve_entry(entry_key)
	if not entry:
		return []

	files = [asset_url(entry["file"])]
	for imp in entry.get("imports", []):
		chunk = get_chunk(imp)
		if chunk:
			files.append(asset_url(chunk["file"]))
	return files


def get_vite_css(entry_key=None):
	entry = resolve_entry(entry_key)
	if not entry:
		return []
	return [asset_url(css) for css in collect_css(entry)]
