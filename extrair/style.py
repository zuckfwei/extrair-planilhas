"""Estilo visual da aplicação."""

STYLE = '''
QWidget { color: #233d36; font-family: "Inter", "Segoe UI", "DejaVu Sans"; font-size: 13px; }
QMainWindow, QWidget#workspace { background: #f6f7f4; }
QFrame#sidebar { background: #122e27; border: none; }
QFrame#sidebar QLabel { color: #b3c8bf; background: transparent; }
QFrame#sidebar QLabel#brand { color: #f5fff9; font-size: 27px; font-weight: 700; }
QFrame#sidebar QLabel#active { background: #26483d; color: #deefb7; border-radius: 9px; padding: 13px; font-weight: 600; }
QFrame#sidebar QLabel#step { padding: 10px 12px; }
QFrame#card, QFrame#metric { background: white; border: 1px solid #dce3db; border-radius: 12px; }
QLabel#eyebrow { color: #6f8377; font-size: 11px; font-weight: 700; }
QLabel#title { font-size: 29px; font-weight: 700; letter-spacing: -1px; }
QLabel#subtitle, QLabel#muted { color: #748178; }
QLabel#metricValue { font-size: 24px; font-weight: 650; }
QLabel#section { font-size: 16px; font-weight: 650; }
QLabel#badge { color: #32684b; background: #e8f0e3; padding: 7px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; }
QPushButton { background: white; border: 1px solid #d2dcd2; border-radius: 7px; padding: 10px 16px; font-weight: 600; }
QPushButton:hover { background: #eef3e9; border-color: #8da68b; }
QPushButton:pressed { background: #dfe9d8; }
QPushButton#primary { background: #226348; color: white; border: 1px solid #226348; }
QPushButton#primary:hover { background: #184c36; }
QPushButton:disabled { background: #edf0eb; color: #9aa59d; border-color: #e0e5dc; }
QPushButton#drop { text-align: left; background: #fafcf7; border: 1px dashed #9eb59a; padding: 19px; font-weight: 600; }
QPushButton#drop:hover { background: #edf4e6; }
QComboBox, QLineEdit { background: white; border: 1px solid #d6dfd4; border-radius: 7px; padding: 9px 11px; selection-background-color: #226348; }
QComboBox:focus, QLineEdit:focus { border: 1px solid #226348; }
QComboBox::drop-down { border: none; width: 25px; }
QComboBox QAbstractItemView { background: white; selection-background-color: #e3efdb; selection-color: #233d36; }
QTableView { border: none; background: white; alternate-background-color: #fafbf8; gridline-color: #eff2ec; selection-background-color: #e5efdf; selection-color: #173b2a; }
QHeaderView::section { background: #f4f6f0; color: #738171; padding: 10px; border: none; border-bottom: 1px solid #dfe5d9; font-size: 11px; font-weight: 700; }
QProgressBar { border: none; background: #e5ebdf; border-radius: 3px; max-height: 5px; }
QProgressBar::chunk { background: #4e865c; border-radius: 3px; }
QScrollBar:vertical { background: #f4f6f0; width: 10px; }
QScrollBar::handle:vertical { background: #b7c4b2; border-radius: 5px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
'''
