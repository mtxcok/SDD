from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path


def build_logger(name: str, level: str, work_dir: Path) -> logging.Logger:
    """
    扩音器制造机：
    - name: 扩音器名字（频道名）
    - level: 嗓门大小(INFO/DEBUG/ERROR...)
    - work_dir: 日志本放哪(会写到 work_dir/logs/agent.log)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    # 避免重复装喇叭（多次调用不再重复加 handler）
    if logger.handlers:
      return logger

    fmt = logging.Formatter(
      "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
      datefmt="%H:%M:%S",
    )

    # 屏幕喇叭
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level.upper())
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 日志本
    log_file = work_dir / "logs" / "agent.log"
    fh = RotatingFileHandler(
      log_file,
      maxBytes=5 * 1024 * 1024,   # 5 MB
      backupCount=5,              # 最多保留 5 个 *.log.N
      encoding="utf-8",
    )
    fh.setLevel(level.upper())
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
