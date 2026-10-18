"""Inicialização da aplicação desktop."""
import sys

from PySide6.QtWidgets import QApplication, QProxyStyle, QStyle

from . import VERSION
from .ui.style import STYLE
from .ui.window import MainWindow


class ComboBoxDropDownStyle(QProxyStyle):
    """Usa listas comuns nos seletores, sempre iniciadas pelo primeiro item."""

    def styleHint(self, hint, option=None, widget=None, return_data=None):
        if hint == QStyle.StyleHint.SH_ComboBox_Popup:
            return 0
        return super().styleHint(hint, option, widget, return_data)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Extrair')
    app.setApplicationVersion(VERSION)
    app.setStyle(ComboBoxDropDownStyle(app.style()))
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    if len(sys.argv) > 1:
        window.open_file(sys.argv[1])
    sys.exit(app.exec())
