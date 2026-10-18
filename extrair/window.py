"""Janela principal do extrator."""
from pathlib import Path
from threading import Event

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton,
    QSizePolicy, QStackedWidget, QTableView, QVBoxLayout, QWidget,
)

from . import VERSION
from .extractor import Cancelled, Spreadsheet, extract, export_text
from .table_model import TableModel
from .worker import Job


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.book = self.result = self.job = None
        self.closing = False
        self.setWindowTitle(f'Extrair — {VERSION}')
        self.resize(980, 620)
        self.setMinimumSize(700, 460)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setAcceptDrops(True)
        self.setWindowIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        workspace = QWidget(objectName='workspace')
        body = QVBoxLayout(workspace)
        body.setContentsMargins(20, 16, 20, 14)
        body.setSpacing(12)
        self.setCentralWidget(workspace)
        body.addWidget(self.label('Extrair planilha', 'title'))

        card = QFrame(objectName='card')
        inputs = QVBoxLayout(card)
        inputs.setContentsMargins(14, 12, 14, 14)
        inputs.setSpacing(10)
        file_row = QHBoxLayout()
        self.drop = QPushButton('Abrir planilha')
        self.drop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.drop.clicked.connect(self.browse)
        file_row.addWidget(self.drop)
        self.file_hint = self.label('Nenhum arquivo selecionado', 'muted')
        self.file_hint.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        file_row.addWidget(self.file_hint, 1)
        inputs.addLayout(file_row)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        a = QVBoxLayout()
        a.setSpacing(4)
        a.addWidget(self.label('Aba', 'fieldLabel'))
        self.sheets = QComboBox()
        self.sheets.setPlaceholderText('Selecione um arquivo')
        self.sheets.setEnabled(False)
        self.sheets.currentIndexChanged.connect(self.invalidate)
        a.addWidget(self.sheets)
        controls.addLayout(a, 1)
        b = QVBoxLayout()
        b.setSpacing(4)
        b.addWidget(self.label('Conteúdo', 'fieldLabel'))
        self.mode = QComboBox()
        self.mode.addItems(['Preservar fórmulas', 'Valores salvos na planilha'])
        self.mode.setToolTip('XLS: somente valores. Valores salvos não recalculam fórmulas; sem cache, a célula pode ficar vazia.')
        self.mode.currentIndexChanged.connect(self.invalidate)
        b.addWidget(self.mode)
        controls.addLayout(b, 1)
        self.run_button = QPushButton('Extrair', objectName='primary')
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.process)
        controls.addWidget(self.run_button, 0, Qt.AlignmentFlag.AlignBottom)
        inputs.addLayout(controls)
        body.addWidget(card)

        preview = QFrame(objectName='card')
        pv = QVBoxLayout(preview)
        pv.setContentsMargins(14, 12, 14, 12)
        pv.setSpacing(9)
        toolbar = QHBoxLayout()
        toolbar.addWidget(self.label('Prévia', 'section'))
        self.summary = self.label('', 'muted')
        toolbar.addWidget(self.summary)
        toolbar.addStretch()
        self.copy = QPushButton('Copiar')
        self.save = QPushButton('Salvar TXT')
        self.copy.clicked.connect(self.copy_result)
        self.save.clicked.connect(self.save_result)
        toolbar.addWidget(self.copy)
        toolbar.addWidget(self.save)
        pv.addLayout(toolbar)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Filtrar a prévia por célula, texto ou fórmula…')
        self.search.setClearButtonEnabled(True)
        pv.addWidget(self.search)
        self.stack = QStackedWidget()
        empty = QWidget()
        empty_box = QVBoxLayout(empty)
        empty_box.addStretch()
        message = self.label('Abra uma planilha para começar.', 'muted')
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_box.addWidget(message)
        empty_box.addStretch()
        self.stack.addWidget(empty)
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.model = TableModel()
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(-1)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.table.setModel(self.proxy)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 100)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.stack.addWidget(self.table)
        pv.addWidget(self.stack, 1)
        body.addWidget(preview, 1)
        self.search.textChanged.connect(self.proxy.setFilterFixedString)
        bottom = QHBoxLayout()
        self.status = self.label('Pronto para abrir uma planilha.', 'muted')
        self.status.setWordWrap(True)
        bottom.addWidget(self.status, 1)
        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.hide()
        bottom.addWidget(self.cancel_button)
        body.addLayout(bottom)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        body.addWidget(self.progress_bar)
        self.invalidate()
        QShortcut(QKeySequence.StandardKey.Open, self, activated=self.browse)
        QShortcut(QKeySequence.StandardKey.Save, self, activated=self.save_result)

    @staticmethod
    def label(text, name):
        label = QLabel(text)
        label.setObjectName(name)
        return label

    def invalidate(self, *_):
        if self.result:
            self.result.cleanup()
            self.result = None
        self.copy.setEnabled(False)
        self.save.setEnabled(False)
        self.search.clear()
        self.search.setEnabled(False)
        self.stack.setCurrentIndex(0)
        self.model.beginResetModel()
        self.model.rows = []
        self.model.endResetModel()
        self.summary.clear()
        if self.book:
            self.status.setText('Pronto para extrair.')

    def browse(self):
        if self.job:
            return
        path, _ = QFileDialog.getOpenFileName(self, 'Abrir planilha', '', 'Planilhas (*.xlsx *.xlsm *.xls *.ods)')
        if path:
            self.open_file(path)

    def start_job(self, task, done):
        self.cancel_event = Event()
        self.job = Job(task, self.cancel_event)
        self.job.done.connect(done)
        self.job.failed.connect(self.status.setText)
        self.job.progress.connect(lambda n: self.status.setText(f'Extraindo… {n:,} células processadas.'.replace(',', '.')))
        self.job.finished.connect(self.finished)
        for widget in (self.drop, self.sheets, self.mode, self.run_button, self.copy, self.save):
            widget.setEnabled(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.cancel_button.show()
        self.job.start()

    def finished(self):
        self.job.deleteLater()
        self.job = None
        self.drop.setEnabled(True)
        self.sheets.setEnabled(self.book is not None)
        self.mode.setEnabled(self.book is None or self.book.ext != '.xls')
        self.run_button.setEnabled(self.book is not None)
        self.copy.setEnabled(self.result is not None and self.result.count > 0)
        self.save.setEnabled(self.result is not None and self.result.count > 0)
        self.cancel_button.hide()
        self.progress_bar.hide()
        if self.closing:
            self.close()

    def cancel(self):
        if self.job:
            self.cancel_event.set()
            self.status.setText('Cancelando… aguardando o leitor liberar o arquivo.')

    def open_file(self, path):
        if self.job:
            return
        self.status.setText('Lendo as abas da planilha…')
        def load():
            book = Spreadsheet(path)
            if self.cancel_event.is_set():
                book.close()
                raise Cancelled()
            return book
        self.start_job(load, self.loaded)

    def loaded(self, book):
        self.invalidate()
        if self.book:
            self.book.close()
        self.book = book
        self.sheets.clear()
        self.sheets.addItems(book.sheets)
        self.sheets.setCurrentIndex(0)
        if book.ext == '.xls':
            self.mode.setCurrentIndex(1)
        self.drop.setText('Trocar planilha')
        self.drop.setToolTip(str(book.path))
        size = book.path.stat().st_size / 1024
        hint = f'{book.path.name}  —  {size:,.1f} KB  —  {len(book.sheets)} aba(s)'
        self.file_hint.setText(hint)
        self.file_hint.setToolTip(str(book.path))
        self.status.setText('Arquivo aberto. Escolha uma aba e clique em Extrair conteúdo.')

    def process(self):
        if self.job or not self.book:
            return
        self.invalidate()
        sheet = self.sheets.currentText()
        formulas = self.mode.currentIndex() == 0
        self.status.setText(f'Extraindo a aba {sheet}…')
        self.start_job(lambda: extract(self.book, sheet, formulas, self.cancel_event, self.job.progress.emit), self.extracted)

    def extracted(self, result):
        self.result = result
        self.model.beginResetModel()
        self.model.rows = result.preview
        self.model.endResetModel()
        self.stack.setCurrentIndex(1)
        self.search.setEnabled(True)
        self.summary.setText(
            f'{result.count:,} células  •  {result.formulas:,} fórmulas  •  {result.seconds:.2f} s'.replace(',', '.')
        )
        self.status.setText('Extração concluída. Copie o texto ou exporte o resultado completo.' if result.count else 'Nenhuma célula preenchida nesta aba ou sem valores em cache. Experimente preservar fórmulas.')

    def copy_result(self):
        if not self.result or self.job:
            return
        if self.result.size > 10 * 1024 * 1024:
            QMessageBox.information(self, 'Resultado grande', 'Para manter a interface fluida, exporte este resultado em TXT. A cópia está limitada a 10 MB.')
            return
        QApplication.clipboard().setText(self.result.path.read_text(encoding='utf-8'))
        self.status.setText('Texto completo copiado para a área de transferência.')

    def save_result(self):
        if not self.result or self.job:
            return
        suggested = self.book.path.stem + '-' + ''.join(c if c.isalnum() or c in '-_' else '_' for c in self.sheets.currentText()) + '.txt'
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar texto completo', suggested, 'Texto UTF-8 (*.txt)')
        if not path:
            return
        if not Path(path).suffix:
            path += '.txt'
        destination = Path(path).resolve()
        if destination == self.book.path.resolve() or destination.suffix.lower() != '.txt':
            QMessageBox.warning(self, 'Escolha um arquivo TXT', 'Exporte para um arquivo .txt diferente da planilha original.')
            return
        source = self.result.path
        self.status.setText('Exportando o texto completo…')
        self.start_job(lambda: export_text(source, destination, self.cancel_event), lambda _: self.status.setText(f'Arquivo salvo em {destination}'))

    def dragEnterEvent(self, event):
        if not self.job and event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1 and event.mimeData().urls()[0].isLocalFile():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if not self.job:
            self.open_file(event.mimeData().urls()[0].toLocalFile())

    def closeEvent(self, event):
        if self.job:
            self.closing = True
            self.cancel()
            event.ignore()
            return
        if self.book:
            self.book.close()
        if self.result:
            self.result.cleanup()
        event.accept()
