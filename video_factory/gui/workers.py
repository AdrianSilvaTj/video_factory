"""Run a function in a background thread and report back on the GUI thread."""
from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, QThread, Signal


_ALIVE: set = set()


class _Task(QObject):
    done = Signal(object)
    fail = Signal(str)
    progress = Signal(object)

    def __init__(self, fn, with_progress: bool):
        super().__init__()
        self.fn = fn
        self.with_progress = with_progress

    def run(self):
        try:
            self.done.emit(self.fn(self.progress.emit) if self.with_progress else self.fn())
        except Exception as exc:
            self.fail.emit(str(exc) or traceback.format_exc())


def run_task(owner: QObject, fn, on_done, on_fail, on_progress=None) -> None:
    """Start fn in a thread owned by `owner`. Callbacks must be bound methods of QObjects so they run on the GUI thread."""
    thread = QThread(owner)
    task = _Task(fn, on_progress is not None)
    _ALIVE.add(task)
    task.moveToThread(thread)
    thread.started.connect(task.run)
    task.done.connect(on_done)
    task.fail.connect(on_fail)
    if on_progress is not None:
        task.progress.connect(on_progress)
    task.done.connect(thread.quit)
    task.fail.connect(thread.quit)
    thread.finished.connect(lambda: _ALIVE.discard(task))
    thread.finished.connect(task.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.start()
