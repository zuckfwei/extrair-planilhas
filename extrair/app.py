"""Inicialização da aplicação desktop."""
import sys

from PySide6.QtWidgets import QApplication

from . import VERSION
from .style import STYLE
from .window import Window


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Extrair')
    app.setApplicationVersion(VERSION)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    window = Window()
    window.show()
    if len(sys.argv) > 1:
        window.open_file(sys.argv[1])
    sys.exit(app.exec())
