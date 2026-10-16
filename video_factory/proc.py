"""Run external programs (FFmpeg, the TTS helper) without a console window on Windows, and allow cancelling them."""
from __future__ import annotations

import subprocess
import sys
import threading
import time

_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
CANCELLED = "Cancelado por el usuario."
_cancel = threading.Event()


class Cancelled(Exception):
    def __init__(self):
        super().__init__(CANCELLED)


def reset() -> None:
    """Call before starting a cancellable operation."""
    _cancel.clear()


def cancel_all() -> None:
    """Ask the running operation to stop: the current program is killed and the next one never starts."""
    _cancel.set()


def _kill_tree(process: subprocess.Popen) -> None:
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True, creationflags=_NO_WINDOW)
    else:
        process.kill()


def run(cmd: list[str], capture_output: bool = False, timeout: float | None = None, **kwargs) -> subprocess.CompletedProcess:
    """Like subprocess.run, but without a console window and interruptible with cancel_all()."""
    if _cancel.is_set():
        raise Cancelled()
    kwargs.setdefault("creationflags", _NO_WINDOW)
    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)
    process = subprocess.Popen(cmd, **kwargs)
    started = time.monotonic()
    while True:
        try:
            stdout, stderr = process.communicate(timeout=0.2)
            return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
        except subprocess.TimeoutExpired:
            if _cancel.is_set():
                _kill_tree(process)
                process.communicate()
                raise Cancelled()
            if timeout is not None and time.monotonic() - started > timeout:
                _kill_tree(process)
                process.communicate()
                raise subprocess.TimeoutExpired(cmd, timeout)
