# theme.py

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

is_dark_mode = False  # Tracks the current theme state

def apply_dark_theme(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    app.setStyle("Fusion")

def apply_light_theme(app):
    app.setPalette(app.style().standardPalette())
    app.setStyle("Fusion")

def toggle_theme(app):
    global is_dark_mode
    if is_dark_mode:
        apply_light_theme(app)
    else:
        apply_dark_theme(app)
    is_dark_mode = not is_dark_mode
