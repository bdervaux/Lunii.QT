"""
Background fetching of story covers.

Official covers come from the Lunii database (the same source already used by
Story.get_picture(): DB_OFFICIAL -> localized_infos -> image -> image_url, served
from storage.googleapis.com/lunii-data-prod). Third-party covers come from the
local cache, filled when a STUdio pack with a thumbnail is imported.

Every image is cached in CACHE_DIR, so a cover is downloaded only once.
"""
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import QObject, QThread, Signal

MAX_PARALLEL_DOWNLOADS = 6


class CoverFetcher(QThread):
    # (generation, story uuid as upper-case string, image bytes)
    signal_cover = Signal(int, str, bytes)
    # (generation, number of covers found, number of stories)
    signal_done = Signal(int, int, int)

    def __init__(self, stories, generation: int, reload: bool = False, parent: QObject = None):
        super().__init__(parent)
        # snapshot: the device story list can change while we run
        self.stories = list(stories)
        self.generation = generation
        self.reload = reload
        self._abort = threading.Event()

    def abort(self):
        self._abort.set()

    def _fetch_one(self, story):
        if self._abort.is_set():
            return story, None
        try:
            return story, story.get_picture(self.reload, timeout=8)
        except Exception:
            # a broken cover must never break the story list
            return story, None

    def run(self):
        found = 0
        pool = ThreadPoolExecutor(max_workers=MAX_PARALLEL_DOWNLOADS)
        try:
            futures = [pool.submit(self._fetch_one, s) for s in self.stories]
            for fut in as_completed(futures):
                if self._abort.is_set():
                    break
                story, data = fut.result()
                if data:
                    found += 1
                    self.signal_cover.emit(self.generation, story.str_uuid, bytes(data))
        finally:
            # on abort (app closing), don't wait for queued downloads
            pool.shutdown(wait=not self._abort.is_set(), cancel_futures=True)
        if not self._abort.is_set():
            self.signal_done.emit(self.generation, found, len(self.stories))
