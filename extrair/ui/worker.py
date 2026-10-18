"""Execução de tarefas sem bloquear a interface."""
from PySide6.QtCore import QThread, Signal

from ..backend import Cancelled


class BackgroundJob(QThread):
    succeeded = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        try:
            result = self.task(self.progress.emit)
            self.succeeded.emit(result)
        except Cancelled:
            self.failed.emit('Operação cancelada.')
        except Exception as error:
            self.failed.emit(f'Não foi possível concluir. {error}')
