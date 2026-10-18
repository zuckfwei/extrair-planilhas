"""Execução de tarefas fora da interface."""
from PySide6.QtCore import QThread, Signal

from .extractor import Cancelled


class Job(QThread):
    done = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, task, cancel):
        super().__init__()
        self.task, self.cancel = task, cancel

    def run(self):
        try:
            self.done.emit(self.task())
        except Cancelled:
            self.failed.emit('Operação cancelada.')
        except Exception as error:
            self.failed.emit(f'Não foi possível concluir. {error}')
