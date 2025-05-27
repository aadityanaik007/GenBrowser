# main.py
import sys
from PySide6.QtWidgets import QApplication
from browser_ui import MainWindow
from theme import toggle_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    toggle_theme(app)  # ✅ Apply dark mode
    app.setApplicationName("GenBrowser")
    app.setOrganizationName("GenBrowser")
    app.setOrganizationDomain("GenBrowser.org")

    window = MainWindow()
    app.exec()
