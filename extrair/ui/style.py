"""Estilo visual da aplicação."""

STYLE = '''
QWidget {
    color: #263b34;
    font-size: 13px;
}
QMainWindow, QWidget#workspace {
    background: #f4f6f3;
}
QFrame#card {
    background: white;
    border: 1px solid #d9e0da;
    border-radius: 8px;
}
QLabel#title {
    font-size: 22px;
    font-weight: 700;
}
QLabel#section {
    font-size: 15px;
    font-weight: 600;
}
QLabel#fieldLabel {
    color: #53685f;
    font-size: 12px;
}
QLabel#muted {
    color: #687a72;
}
QPushButton {
    background: white;
    border: 1px solid #ccd6ce;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: #eef3e9;
    border-color: #8da68b;
}
QPushButton:pressed {
    background: #dfe9d8;
}
QPushButton#primary {
    background: #226348;
    color: white;
    border: 1px solid #226348;
}
QPushButton#primary:hover {
    background: #184c36;
}
QPushButton:disabled {
    background: #edf0eb;
    color: #9aa59d;
    border-color: #e0e5dc;
}
QComboBox, QLineEdit {
    background: white;
    border: 1px solid #d2dad3;
    border-radius: 6px;
    padding: 7px 9px;
    selection-background-color: #226348;
}
QComboBox:focus, QLineEdit:focus {
    border: 1px solid #226348;
}
QComboBox:hover {
    color: #263b34;
    background: white;
    border-color: #d2dad3;
}
QComboBox::drop-down {
    border: none;
    width: 25px;
}
QComboBox QAbstractItemView {
    color: #263b34;
    background: white;
    selection-background-color: white;
    selection-color: #263b34;
    outline: none;
}
QComboBox QAbstractItemView::item:hover {
    color: #263b34;
    background: #f4f6f3;
}
QTableView {
    border: none;
    background: white;
    alternate-background-color: #fafbf8;
    gridline-color: #dfe5df;
    selection-background-color: #e5efdf;
    selection-color: #173b2a;
}
QHeaderView::section {
    background: #f4f6f0;
    color: #5f7168;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #dfe5d9;
    font-size: 11px;
    font-weight: 600;
}
QProgressBar {
    border: none;
    background: #e5ebdf;
    border-radius: 3px;
    max-height: 5px;
}
QProgressBar::chunk {
    background: #4e865c;
    border-radius: 3px;
}
QScrollBar:vertical {
    background: #f4f6f0;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #b7c4b2;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
'''
