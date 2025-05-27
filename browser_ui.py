import os
from PySide6.QtCore import QSize, Qt, QUrl
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QShortcut
from PySide6.QtPrintSupport import QPrintPreviewDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineDownloadRequest,
    QWebEngineUrlRequestInterceptor,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QMessageBox,
    QTabWidget,
    QWidget,
    QHBoxLayout,
)
from theme import toggle_theme

ICON_PATH = "images"
HOMEPAGE = "https://www.google.com"
AD_HOSTS = {"ads.google.com", "doubleclick.net", "googlesyndication.com", "adnxs.com"}


class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl()
        host = url.host()
        if any(ad_host in host for ad_host in AD_HOSTS):
            print(f"[ADBLOCK] Blocked: {url.toString()}")
            info.block(True)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About GenBrowser")

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        title = QLabel("GenBrowser")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)
        layout.addWidget(title)

        logo = QLabel()
        pixmap = QPixmap(os.path.join(ICON_PATH, "GenLogo.png"))
        scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(scaled_pixmap)
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 23.35.211.233232"))
        layout.addWidget(QLabel("© 2015 GenBrowser Inc."))

        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(os.path.join(ICON_PATH, "GenLogo.png")))
        self.setWindowTitle("GenBrowser")

        profile = QWebEngineProfile.defaultProfile()
        profile.setUrlRequestInterceptor(AdBlocker())
        profile.downloadRequested.connect(self.handle_download)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_current_tab_signals)
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.create_navigation_bar()
        self.create_menu_bar()

        self.add_new_tab(QUrl(HOMEPAGE), "Home")

        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.add_blank_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, activated=self.close_current_tab)

        self.show()

    def create_navigation_bar(self):
        self.navtb = QToolBar("Navigation")
        self.navtb.setIconSize(QSize(16, 16))
        self.addToolBar(self.navtb)

        self.back_btn = QAction(QIcon(os.path.join(ICON_PATH, "arrow-180.png")), "Back", self)
        self.back_btn.triggered.connect(lambda: self.current_browser().back())
        self.navtb.addAction(self.back_btn)

        self.next_btn = QAction(QIcon(os.path.join(ICON_PATH, "arrow-000.png")), "Forward", self)
        self.next_btn.triggered.connect(lambda: self.current_browser().forward())
        self.navtb.addAction(self.next_btn)

        self.reload_btn = QAction(QIcon(os.path.join(ICON_PATH, "arrow-circle-315.png")), "Reload", self)
        self.reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.navtb.addAction(self.reload_btn)

        self.home_btn = QAction(QIcon(os.path.join(ICON_PATH, "home.png")), "Home", self)
        self.home_btn.triggered.connect(lambda: self.current_browser().setUrl(QUrl(HOMEPAGE)))
        self.navtb.addAction(self.home_btn)

        self.navtb.addSeparator()

        self.httpsicon = QLabel()
        self.httpsicon.setPixmap(QPixmap(os.path.join(ICON_PATH, "lock-nossl.png")))
        self.navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon(os.path.join(ICON_PATH, "cross-circle.png")), "Stop", self)
        stop_btn.triggered.connect(lambda: self.current_browser().stop())
        self.navtb.addAction(stop_btn)

        self.find_bar = QLineEdit()
        self.find_bar.setPlaceholderText("Find on page...")
        self.find_bar.returnPressed.connect(lambda: self.current_browser().findText(self.find_bar.text()))
        self.navtb.addWidget(self.find_bar)

    def create_menu_bar(self):
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("Open file...", self.open_file)
        file_menu.addAction("Save Page As...", self.save_file)
        file_menu.addAction("Print...", self.print_page)

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction("Zoom In", lambda: self.current_browser().setZoomFactor(self.current_browser().zoomFactor() + 0.1))
        view_menu.addAction("Zoom Out", lambda: self.current_browser().setZoomFactor(self.current_browser().zoomFactor() - 0.1))

        toggle_dark = QAction("Toggle Dark Mode", self)
        toggle_dark.triggered.connect(lambda: toggle_theme(QApplication.instance()))
        view_menu.addAction(toggle_dark)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction("About GenBrowser", self.about)
        help_menu.addAction("GenBrowser Author", lambda: self.current_browser().setUrl(QUrl("https://aaditya-naik-portfolio.netlify.app/")))

    def current_browser(self):
        return self.tabs.currentWidget().findChild(QWebEngineView)

    def update_current_tab_signals(self, i):
        browser = self.current_browser()
        if browser:
            self.urlbar.setText(browser.url().toString())
            browser.urlChanged.connect(self.update_urlbar)
            browser.loadFinished.connect(self.update_title)

    def add_new_tab(self, qurl=QUrl(""), label="Blank"):
        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(self.update_urlbar)
        browser.loadFinished.connect(self.update_title)

        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(browser)
        container.setLayout(layout)

        i = self.tabs.addTab(container, label)
        self.tabs.setCurrentIndex(i)

    def add_blank_tab(self):
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def update_title(self):
        self.setWindowTitle(f"{self.current_browser().page().title()} - GenBrowser")

    def about(self):
        dlg = AboutDialog()
        dlg.exec()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", "HTML files (*.html *.htm);;All files (*.*)")
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    html = f.read()
                self.current_browser().setHtml(html)
                self.urlbar.setText(filename)
            except Exception as e:
                self.status.showMessage(f"Failed to open file: {e}", 5000)

    def save_html(self, html):
        try:
            with open(self._save_filename, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            self.status.showMessage(f"Failed to save: {e}", 5000)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "", "HTML files (*.html *.htm);;All files (*.*)")
        if filename:
            self._save_filename = filename
            self.current_browser().page().toHtml(self.save_html)

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.current_browser().print_)
        dlg.exec()

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.current_browser().setUrl(q)

    def update_urlbar(self, q):
        icon = "lock-ssl.png" if q.scheme() == "https" else "lock-nossl.png"
        self.httpsicon.setPixmap(QPixmap(os.path.join(ICON_PATH, icon)))
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def handle_download(self, download: QWebEngineDownloadRequest):
        filename = download.suggestedFileName()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setPath(path)
            download.accept()
            self.status.showMessage(f"Downloading {filename}...", 5000)
        else:
            self.status.showMessage("Download canceled", 3000)
