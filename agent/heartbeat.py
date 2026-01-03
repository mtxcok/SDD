from __future__ import annotations

import threading
from typing import Optional, Callable
import psutil


class Heartbeater:
    """
    小闹钟：每 interval 秒记录 CPU / 内存，并触发可选回调 (on_beat)
    """

    def __init__(self, interval_sec: int, logger, *, on_beat: Optional[Callable[[float, float], None]] = None):
        self.interval = max(1, int(interval_sec))
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self.log = logger
        self.on_beat = on_beat

    # ------------------------------ public ---------------------------------
    def start_background(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.log.info("Heartbeater started (interval=%ss)", self.interval)

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        self.log.info("Heartbeater stopped")

    # ------------------------------ internal -------------------------------
    def _run(self):
        while not self._stop.is_set():
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            self.log.info("heartbeat | cpu=%.1f%% mem=%.1f%%", cpu, mem.percent)

            if self.on_beat:
                try:
                    self.on_beat(cpu, mem.percent)
                except Exception as e:
                    self.log.warning("heartbeat callback error: %s", e)

            self._stop.wait(self.interval)
