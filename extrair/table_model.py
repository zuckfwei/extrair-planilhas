"""Modelo da prévia de células."""
import os

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QFont


class TableModel(QAbstractTableModel):
    def __init__(self, rows=None):
        super().__init__()
        self.rows = rows or []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            return self.rows[index.row()][index.column()]
        if role == Qt.ItemDataRole.FontRole:
            return QFont('Consolas' if os.name == 'nt' else 'DejaVu Sans Mono', 10)
        if role == Qt.ItemDataRole.ForegroundRole and index.column() == 0:
            return QColor('#32724e')

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ('CÉLULA', 'CONTEÚDO')[section]
        return None
