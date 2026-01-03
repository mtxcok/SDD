from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


class RuntimeState:
    """Persist agent_id / agent_token between restarts (JSON file)."""

    def __init__(self, path: Path):
        self.path = path
        self.agent_id: Optional[str] = None
        self.agent_token: Optional[str] = None
        self._load()

    # ---------------------------------------------------------------------
    # public helpers
    # ---------------------------------------------------------------------
    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "agent_id": self.agent_id,
            "agent_token": self.agent_token,
            "ts": int(time.time()),
        }
        self.path.write_text(json.dumps(data, indent=2))

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text())
            self.agent_id = data.get("agent_id")
            self.agent_token = data.get("agent_token")
        except Exception:
            # ignore corrupt file; start fresh
            self.agent_id = None
            self.agent_token = None

