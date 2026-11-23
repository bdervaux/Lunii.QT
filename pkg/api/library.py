"""
Local story library: story packs kept on the computer, usable without any Lunii plugged in.

The library is a plain folder (default: ~/Bibliothèque Lunii). Every supported pack in it
(.zip, .7z, .pk, .plain.pk, .v1.pk, .v2.pk) is one entry. Titles, descriptions and covers are
read from the pack itself (STUdio story.json / thumbnail.png, Lunii.QT export metadata) and,
for official stories, from the Lunii database already used by the app.

Reading packs never needs a device: it only opens the archives.
"""
import binascii
import hashlib
import json
import os
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import py7zr

from pkg.api.constants import CFG_DIR, LUNII_SUPPORTED_EXT
from pkg.api.stories import (Story, FILE_UUID, FILE_THUMB, FILE_META, FILE_STUDIO_JSON, FILE_STUDIO_THUMB)

DEFAULT_LIBRARY_DIR = os.path.join(str(Path.home()), "Bibliothèque Lunii")
FILE_LIBRARY_CACHE = os.path.join(CFG_DIR, "library-cache.json")
LIBRARY_THUMBS_DIR = os.path.join(CFG_DIR, "library-thumbs")

MAX_COVER_BYTES = 5 * 1024 * 1024


@dataclass
class LibraryEntry:
    path: str
    title: str
    description: str = ""
    uuid: Optional[str] = None          # upper-case string, as Story.str_uuid
    night_mode: bool = False
    official: bool = False
    size: int = 0
    mtime: float = 0.0
    cover_file: Optional[str] = None    # cached cover on disk (may be None)
    on_device: bool = False             # filled by the UI

    # same small interface as Story, so the cover wall can show both
    @property
    def key(self):
        return "LIB:" + self.path

    @property
    def str_uuid(self):
        return self.key

    @property
    def name(self):
        return self.title

    @property
    def hidden(self):
        return False

    def night_mode_available(self):
        return self.night_mode

    def is_official(self):
        return self.official

    def cover_bytes(self) -> Optional[bytes]:
        if self.cover_file and os.path.isfile(self.cover_file):
            try:
                with open(self.cover_file, "rb") as fp:
                    return fp.read()
            except OSError:
                return None
        return None


def is_supported(path: str) -> bool:
    low = path.lower()
    return any(low.endswith(ext) for ext in LUNII_SUPPORTED_EXT) and not os.path.basename(low).startswith(".")


def _uuid_from_name(name: str) -> Optional[UUID]:
    """Lunii archives keep the story in a folder named after its UUID (hex or dashed)."""
    parts = [p for p in Path(name).parts if p not in (".", "..")]
    for part in parts:
        candidate = part.strip()
        try:
            if len(candidate) == 32 and "-" not in candidate:
                return UUID(bytes=binascii.unhexlify(candidate))
            if len(candidate) == 36 and candidate.count("-") == 4:
                return UUID(candidate)
        except (ValueError, binascii.Error):
            continue
    return None


def _studio_info(story_json: dict):
    title = story_json.get("title") or ""
    desc = story_json.get("description") or ""
    nm = bool(story_json.get("nightModeAvailable", False))
    uuid = None
    for snode in story_json.get("stageNodes") or []:
        try:
            uuid = UUID(snode.get("uuid"))
            break
        except (TypeError, ValueError):
            continue
    return title, desc, nm, uuid


def _read_zip(path: str):
    title, desc, nm, uuid, cover = "", "", False, None, None
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        lower = {n.lower(): n for n in names}

        def find(suffix):
            for low, real in lower.items():
                if low.endswith(suffix.lower()):
                    return real
            return None

        def small(name):
            if name and zf.getinfo(name).file_size <= MAX_COVER_BYTES:
                return zf.read(name)
            return None

        uuid_file = find(FILE_UUID)
        studio_json = find(FILE_STUDIO_JSON)
        if uuid_file:                                   # Lunii.QT export (.plain.pk / .pk)
            try:
                uuid = UUID(bytes=zf.read(uuid_file)[:16])
            except ValueError:
                uuid = None
            meta_file = find(FILE_META)
            if meta_file:
                try:
                    meta = json.loads(zf.read(meta_file))
                    title = meta.get("title") or ""
                    desc = meta.get("description") or ""
                except (ValueError, KeyError):
                    pass
            cover = small(find(FILE_THUMB))
        elif studio_json:                               # STUdio pack
            try:
                title, desc, nm, uuid = _studio_info(json.loads(zf.read(studio_json)))
            except ValueError:
                pass
            cover = small(find(FILE_STUDIO_THUMB))
        else:                                           # raw Lunii v2/v3/Flam archive
            for name in names:
                uuid = _uuid_from_name(name)
                if uuid:
                    break
            cover = small(find(FILE_THUMB))
    return title, desc, nm, uuid, cover


def _read_7z(path: str):
    title, desc, nm, uuid, cover = "", "", False, None, None
    with py7zr.SevenZipFile(path, mode="r") as archive:
        names = archive.getnames()
    studio_json = next((n for n in names if n.lower().endswith(FILE_STUDIO_JSON)), None)
    thumb = next((n for n in names if n.lower().endswith(FILE_STUDIO_THUMB) or n.lower().endswith(FILE_THUMB)), None)
    wanted = [n for n in (studio_json, thumb) if n]
    contents = {}
    if wanted:
        with py7zr.SevenZipFile(path, mode="r") as archive:
            contents = archive.read(wanted) or {}
    if studio_json and studio_json in contents:
        try:
            title, desc, nm, uuid = _studio_info(json.loads(contents[studio_json].read()))
        except ValueError:
            pass
    else:
        for name in names:
            uuid = _uuid_from_name(name)
            if uuid:
                break
    if thumb and thumb in contents:
        data = contents[thumb].read()
        cover = data if len(data) <= MAX_COVER_BYTES else None
    return title, desc, nm, uuid, cover


def _pretty_filename(path: str) -> str:
    base = os.path.basename(path)
    for ext in sorted(LUNII_SUPPORTED_EXT, key=len, reverse=True):
        if base.lower().endswith(ext):
            base = base[: -len(ext)]
            break
    return base.replace("_", " ").strip() or os.path.basename(path)


def read_pack(path: str) -> LibraryEntry:
    """Reads title / uuid / cover of a story pack. Never raises: unknown packs get their file name."""
    stat = os.stat(path)
    title, desc, nm, uuid, cover = "", "", False, None, None
    try:
        if path.lower().endswith(".7z"):
            title, desc, nm, uuid, cover = _read_7z(path)
        else:
            title, desc, nm, uuid, cover = _read_zip(path)
    except Exception:
        pass

    official = False
    if uuid:
        story = Story(uuid)
        official = bool(story.is_official())
        known = story.name
        # the Lunii / third-party databases know better than an empty or missing title
        if not title and known and not known.startswith("Unknown story"):
            title = known
        if not desc:
            desc = story.desc if hasattr(story, "desc") else ""
        if not cover:
            try:
                cover = story.get_picture(timeout=5)
            except Exception:
                cover = None

    cover_file = None
    if cover:
        os.makedirs(LIBRARY_THUMBS_DIR, exist_ok=True)
        cover_file = os.path.join(LIBRARY_THUMBS_DIR, hashlib.sha1(path.encode("utf-8")).hexdigest())
        try:
            with open(cover_file, "wb") as fp:
                fp.write(cover)
        except OSError:
            cover_file = None

    return LibraryEntry(path=path, title=title or _pretty_filename(path), description=desc or "",
                        uuid=str(uuid).upper() if uuid else None, night_mode=nm, official=official,
                        size=stat.st_size, mtime=stat.st_mtime, cover_file=cover_file)


class Library:
    def __init__(self, folder: str = DEFAULT_LIBRARY_DIR):
        self.folder = folder
        self.entries: List[LibraryEntry] = []
        self._cache = self._load_cache()

    # ---------------- cache (avoid re-reading big archives at every start)
    @staticmethod
    def _load_cache() -> dict:
        try:
            with open(FILE_LIBRARY_CACHE, encoding="utf-8") as fp:
                return json.load(fp)
        except (OSError, ValueError):
            return {}

    def _save_cache(self):
        try:
            os.makedirs(CFG_DIR, exist_ok=True)
            with open(FILE_LIBRARY_CACHE, "w", encoding="utf-8") as fp:
                json.dump(self._cache, fp, ensure_ascii=False)
        except OSError:
            pass

    def ensure_folder(self):
        os.makedirs(self.folder, exist_ok=True)

    def files(self) -> List[str]:
        if not os.path.isdir(self.folder):
            return []
        found = []
        for root, dirs, names in os.walk(self.folder):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in names:
                full = os.path.join(root, name)
                if is_supported(full):
                    found.append(full)
        return sorted(found, key=lambda p: os.path.basename(p).lower())

    def scan(self) -> List[LibraryEntry]:
        """Slow on first run (opens every archive), then served from the cache."""
        entries = []
        new_cache = {}
        for path in self.files():
            try:
                stat = os.stat(path)
            except OSError:
                continue
            cached = self._cache.get(path)
            if cached and cached.get("size") == stat.st_size and cached.get("mtime") == stat.st_mtime:
                entry = LibraryEntry(**{k: v for k, v in cached.items() if k in LibraryEntry.__dataclass_fields__})
                if entry.cover_file and not os.path.isfile(entry.cover_file):
                    entry = read_pack(path)
            else:
                entry = read_pack(path)
            entry.on_device = False
            entries.append(entry)
            data = dict(entry.__dict__)
            data.pop("on_device", None)
            new_cache[path] = data
        self._cache = new_cache
        self._save_cache()
        entries.sort(key=lambda e: e.title.lower())
        self.entries = entries
        return entries

    def add_files(self, paths: List[str]) -> List[str]:
        """Copies packs into the library. Returns the new paths (files already there are skipped)."""
        self.ensure_folder()
        added = []
        for src in paths:
            if not is_supported(src) or not os.path.isfile(src):
                continue
            if os.path.abspath(os.path.dirname(src)).startswith(os.path.abspath(self.folder)):
                continue                        # already inside the library
            dest = os.path.join(self.folder, os.path.basename(src))
            if os.path.exists(dest):
                if os.path.getsize(dest) == os.path.getsize(src):
                    continue                    # same file already kept
                stem, ext = os.path.splitext(os.path.basename(src))
                n = 2
                while os.path.exists(dest):
                    dest = os.path.join(self.folder, f"{stem} ({n}){ext}")
                    n += 1
            shutil.copy2(src, dest)
            added.append(dest)
        return added

    def entry(self, key: str) -> Optional[LibraryEntry]:
        return next((e for e in self.entries if e.key == key), None)
