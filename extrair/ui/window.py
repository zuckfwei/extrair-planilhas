"""Janela principal e eventos da interface."""
from pathlib import Path
from threading import Event

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import VERSION
from ..backend import Cancelled, Spreadsheet, export_text_file, extract_sheet
from .table_model import SpreadsheetPreviewModel
from .worker import BackgroundJob


COPY_LIMIT = 10 * 1024 * 1024
DEFAULT_ROW_HEIGHT = 30
MAX_EXPANDED_ROW_HEIGHT = 240


class FirstItemComboBox(QComboBox):
    """Abre a lista posicionada no primeiro item."""

    def showPopup(self):
        super().showPopup()
        self.view().scrollToTop()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.spreadsheet = None
        self.extraction = None
        self.background_job = None
        self.cancel_event = None
        self.close_after_job = False

        self._configure_window()
        self._build_interface()
        self._clear_extraction()

    def _configure_window(self):
        self.setWindowTitle(f'Extrair — {VERSION}')
        self.resize(980, 620)
        self.setMinimumSize(700, 460)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setAcceptDrops(True)

        icon = self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView)
        self.setWindowIcon(icon)

    def _build_interface(self):
        workspace = QWidget(objectName='workspace')
        main_layout = QVBoxLayout(workspace)
        main_layout.setContentsMargins(20, 16, 20, 14)
        main_layout.setSpacing(12)
        self.setCentralWidget(workspace)

        title = self._label('Extrair planilha', 'title')
        main_layout.addWidget(title)
        main_layout.addWidget(self._build_source_card())
        main_layout.addWidget(self._build_preview_card(), 1)
        self._add_status_area(main_layout)
        self._add_shortcuts()

    def _build_source_card(self):
        card = QFrame(objectName='card')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 14)
        card_layout.setSpacing(10)

        file_row = QHBoxLayout()
        self.open_button = QPushButton('Abrir planilha')
        self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_button.clicked.connect(self.browse_for_file)
        file_row.addWidget(self.open_button)

        self.file_description = self._label('Nenhum arquivo selecionado', 'muted')
        self.file_description.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )
        file_row.addWidget(self.file_description, 1)
        card_layout.addLayout(file_row)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(10)

        sheet_field = QVBoxLayout()
        sheet_field.setSpacing(4)
        sheet_field.addWidget(self._label('Aba', 'fieldLabel'))
        self.sheet_selector = FirstItemComboBox()
        self.sheet_selector.setPlaceholderText('Selecione um arquivo')
        self.sheet_selector.setEnabled(False)
        self.sheet_selector.currentIndexChanged.connect(self._clear_extraction)
        sheet_field.addWidget(self.sheet_selector)
        fields_row.addLayout(sheet_field, 1)

        content_field = QVBoxLayout()
        content_field.setSpacing(4)
        content_field.addWidget(self._label('Conteúdo', 'fieldLabel'))
        self.content_selector = FirstItemComboBox()
        self.content_selector.addItems(['Preservar fórmulas', 'Valores salvos na planilha'])
        self.content_selector.setToolTip(
            'XLS oferece somente valores. Os demais formatos usam o valor salvo '
            'quando a opção de fórmulas está desativada.'
        )
        self.content_selector.currentIndexChanged.connect(self._clear_extraction)
        content_field.addWidget(self.content_selector)
        fields_row.addLayout(content_field, 1)

        self.extract_button = QPushButton('Extrair', objectName='primary')
        self.extract_button.setEnabled(False)
        self.extract_button.clicked.connect(self.extract_selected_sheet)
        fields_row.addWidget(self.extract_button, 0, Qt.AlignmentFlag.AlignBottom)

        card_layout.addLayout(fields_row)
        return card

    def _build_preview_card(self):
        card = QFrame(objectName='card')
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(9)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self._label('Prévia', 'section'))
        self.summary = self._label('', 'muted')
        toolbar.addWidget(self.summary)
        toolbar.addStretch()

        self.copy_button = QPushButton('Copiar')
        self.copy_button.clicked.connect(self.copy_result)
        toolbar.addWidget(self.copy_button)

        self.save_button = QPushButton('Salvar TXT')
        self.save_button.clicked.connect(self.save_result)
        toolbar.addWidget(self.save_button)
        card_layout.addLayout(toolbar)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Pesquisar conteúdo')
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_preview)
        card_layout.addWidget(self.search_input)

        self.preview_pages = QStackedWidget()
        self.preview_pages.addWidget(self._build_empty_preview())
        self.preview_table = self._build_preview_table()
        self.preview_pages.addWidget(self.preview_table)
        card_layout.addWidget(self.preview_pages, 1)
        return card

    def _build_empty_preview(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.addStretch()
        message = self._label('Abra uma planilha para começar.', 'muted')
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_layout.addWidget(message)
        page_layout.addStretch()
        return page

    def _build_preview_table(self):
        table = QTableView()
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setWordWrap(True)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        table.setCornerButtonEnabled(False)

        self.table_model = SpreadsheetPreviewModel()
        table.setModel(self.table_model)

        horizontal_header = table.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        horizontal_header.setDefaultSectionSize(150)
        horizontal_header.setMinimumSectionSize(70)
        horizontal_header.setStretchLastSection(False)

        vertical_header = table.verticalHeader()
        vertical_header.setDefaultSectionSize(DEFAULT_ROW_HEIGHT)
        vertical_header.setMinimumSectionSize(24)

        table.doubleClicked.connect(self.toggle_cell)
        return table

    def _add_status_area(self, main_layout):
        status_row = QHBoxLayout()
        self.status_label = self._label('Pronto para abrir uma planilha.', 'muted')
        self.status_label.setWordWrap(True)
        status_row.addWidget(self.status_label, 1)

        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.clicked.connect(self.cancel_current_job)
        self.cancel_button.hide()
        status_row.addWidget(self.cancel_button)
        main_layout.addLayout(status_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

    def _add_shortcuts(self):
        QShortcut(QKeySequence.StandardKey.Open, self, activated=self.browse_for_file)
        QShortcut(QKeySequence.StandardKey.Save, self, activated=self.save_result)

    @staticmethod
    def _label(text, object_name):
        label = QLabel(text)
        label.setObjectName(object_name)
        return label

    def filter_preview(self, text):
        self.table_model.set_filter(text)
        vertical_header = self.preview_table.verticalHeader()
        vertical_header.resizeSections(QHeaderView.ResizeMode.Fixed)

    def toggle_cell(self, index):
        if not index.isValid():
            return
        if not self.table_model.data(index):
            return

        row = index.row()
        current_height = self.preview_table.rowHeight(row)
        if current_height > DEFAULT_ROW_HEIGHT:
            self.preview_table.setRowHeight(row, DEFAULT_ROW_HEIGHT)
            return

        required_height = self.preview_table.sizeHintForRow(row)
        expanded_height = min(required_height, MAX_EXPANDED_ROW_HEIGHT)
        expanded_height = max(expanded_height, DEFAULT_ROW_HEIGHT)
        self.preview_table.setRowHeight(row, expanded_height)

    def _clear_extraction(self, _selected_index=None):
        if self.extraction is not None:
            self.extraction.remove_temporary_file()
            self.extraction = None

        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.search_input.clear()
        self.search_input.setEnabled(False)
        self.preview_pages.setCurrentIndex(0)
        self.table_model.set_cells([])
        self.summary.clear()

        if self.spreadsheet is not None:
            self.status_label.setText('Pronto para extrair.')

    def browse_for_file(self):
        if self.background_job is not None:
            return

        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            'Abrir planilha',
            '',
            'Planilhas (*.xlsx *.xlsm *.xls *.ods)',
        )
        if not path:
            return
        self.open_file(path)

    def _start_background_job(self, task, on_success):
        self.cancel_event = Event()
        self.background_job = BackgroundJob(task)
        self.background_job.succeeded.connect(on_success)
        self.background_job.failed.connect(self._show_job_error)
        self.background_job.progress.connect(self._show_extraction_progress)
        self.background_job.finished.connect(self._finish_background_job)

        controls = (
            self.open_button,
            self.sheet_selector,
            self.content_selector,
            self.extract_button,
            self.copy_button,
            self.save_button,
        )
        for control in controls:
            control.setEnabled(False)

        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.cancel_button.show()
        self.background_job.start()

    def _show_job_error(self, message):
        self.status_label.setText(message)

    def _show_extraction_progress(self, cell_count):
        formatted_count = f'{cell_count:,}'.replace(',', '.')
        self.status_label.setText(f'Extraindo… {formatted_count} células processadas.')

    def _finish_background_job(self):
        self.background_job.deleteLater()
        self.background_job = None
        self.cancel_event = None

        self.open_button.setEnabled(True)
        has_spreadsheet = self.spreadsheet is not None
        self.sheet_selector.setEnabled(has_spreadsheet)
        self.extract_button.setEnabled(has_spreadsheet)

        is_legacy_excel = False
        if has_spreadsheet:
            is_legacy_excel = self.spreadsheet.extension == '.xls'
        self.content_selector.setEnabled(not is_legacy_excel)

        has_result = False
        if self.extraction is not None:
            has_result = self.extraction.cell_count > 0
        self.copy_button.setEnabled(has_result)
        self.save_button.setEnabled(has_result)

        self.cancel_button.hide()
        self.progress_bar.hide()

        if self.close_after_job:
            self.close()

    def cancel_current_job(self):
        if self.background_job is None:
            return
        self.cancel_event.set()
        self.status_label.setText('Cancelando…')

    def open_file(self, path):
        if self.background_job is not None:
            return

        self.status_label.setText('Lendo as abas da planilha…')

        def load_spreadsheet(_progress_callback):
            spreadsheet = Spreadsheet(path)
            if self.cancel_event.is_set():
                spreadsheet.close()
                raise Cancelled()
            return spreadsheet

        self._start_background_job(load_spreadsheet, self._spreadsheet_loaded)

    def _spreadsheet_loaded(self, spreadsheet):
        self._clear_extraction()
        if self.spreadsheet is not None:
            self.spreadsheet.close()
        self.spreadsheet = spreadsheet

        self.sheet_selector.blockSignals(True)
        self.sheet_selector.clear()
        self.sheet_selector.addItems(spreadsheet.sheet_names)
        self.sheet_selector.setCurrentIndex(0)
        self.sheet_selector.blockSignals(False)

        if spreadsheet.extension == '.xls':
            self.content_selector.setCurrentIndex(1)

        self.open_button.setText('Trocar planilha')
        self.open_button.setToolTip(str(spreadsheet.path))

        file_size_kb = spreadsheet.path.stat().st_size / 1024
        sheet_count = len(spreadsheet.sheet_names)
        description = (
            f'{spreadsheet.path.name}  —  '
            f'{file_size_kb:,.1f} KB  —  '
            f'{sheet_count} aba(s)'
        )
        self.file_description.setText(description)
        self.file_description.setToolTip(str(spreadsheet.path))
        self.status_label.setText('Arquivo aberto. Escolha uma aba e clique em Extrair.')

    def extract_selected_sheet(self):
        if self.background_job is not None:
            return
        if self.spreadsheet is None:
            return

        self._clear_extraction()
        sheet_name = self.sheet_selector.currentText()
        include_formulas = self.content_selector.currentIndex() == 0
        self.status_label.setText(f'Extraindo a aba {sheet_name}…')

        def run_extraction(progress_callback):
            return extract_sheet(
                spreadsheet=self.spreadsheet,
                sheet_name=sheet_name,
                include_formulas=include_formulas,
                cancel_event=self.cancel_event,
                progress_callback=progress_callback,
            )

        self._start_background_job(run_extraction, self._extraction_finished)

    def _extraction_finished(self, result):
        self.extraction = result
        self.table_model.set_cells(result.preview_cells)
        self.preview_pages.setCurrentIndex(1)
        self.search_input.setEnabled(True)

        cell_count = f'{result.cell_count:,}'.replace(',', '.')
        formula_count = f'{result.formula_count:,}'.replace(',', '.')
        self.summary.setText(
            f'{cell_count} células  •  '
            f'{formula_count} fórmulas  •  '
            f'{result.elapsed_seconds:.2f} s'
        )

        if result.cell_count > 0:
            self.status_label.setText('Extração concluída.')
        else:
            self.status_label.setText('Nenhuma célula preenchida foi encontrada.')

    def copy_result(self):
        if self.extraction is None:
            return
        if self.background_job is not None:
            return
        if self.extraction.file_size > COPY_LIMIT:
            QMessageBox.information(
                self,
                'Resultado grande',
                'Resultados acima de 10 MB devem ser salvos em TXT.',
            )
            return

        text = self.extraction.temporary_path.read_text(encoding='utf-8')
        QApplication.clipboard().setText(text)
        self.status_label.setText('Texto copiado.')

    def save_result(self):
        if self.extraction is None:
            return
        if self.background_job is not None:
            return

        suggested_name = self._suggested_output_name()
        selected_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            'Salvar texto',
            suggested_name,
            'Texto UTF-8 (*.txt)',
        )
        if not selected_path:
            return

        destination = Path(selected_path)
        if not destination.suffix:
            destination = destination.with_suffix('.txt')
        destination = destination.resolve()

        same_as_source = destination == self.spreadsheet.path.resolve()
        wrong_extension = destination.suffix.lower() != '.txt'
        if same_as_source or wrong_extension:
            QMessageBox.warning(
                self,
                'Escolha um arquivo TXT',
                'Salve em um arquivo .txt diferente da planilha original.',
            )
            return

        source = self.extraction.temporary_path
        self.status_label.setText('Salvando…')

        def export_result(_progress_callback):
            return export_text_file(source, destination, self.cancel_event)

        self._start_background_job(export_result, self._text_file_saved)

    def _suggested_output_name(self):
        sheet_name = self.sheet_selector.currentText()
        safe_characters = []
        for character in sheet_name:
            if character.isalnum() or character in '-_':
                safe_characters.append(character)
            else:
                safe_characters.append('_')
        safe_sheet_name = ''.join(safe_characters)
        return f'{self.spreadsheet.path.stem}-{safe_sheet_name}.txt'

    def _text_file_saved(self, destination):
        self.status_label.setText(f'Arquivo salvo em {destination}')

    def dragEnterEvent(self, event):
        if self.background_job is not None:
            return

        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return

        urls = mime_data.urls()
        if len(urls) != 1:
            return
        if not urls[0].isLocalFile():
            return
        event.acceptProposedAction()

    def dropEvent(self, event):
        if self.background_job is not None:
            return
        path = event.mimeData().urls()[0].toLocalFile()
        self.open_file(path)

    def closeEvent(self, event):
        if self.background_job is not None:
            self.close_after_job = True
            self.cancel_current_job()
            event.ignore()
            return

        if self.spreadsheet is not None:
            self.spreadsheet.close()
        if self.extraction is not None:
            self.extraction.remove_temporary_file()
        event.accept()
