import sys
import os
import urllib.request
import tempfile
from pathlib import Path
from PyQt6.QtCore import QUrl, QCoreApplication
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QToolBar,
    QPushButton,
    QStatusBar,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QIcon, QAction


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def extract_offline_content():
    """Extract offline content from the bundled resources or use existing files"""
    # Check if we're running from a bundled executable
    if getattr(sys, "frozen", False):
        # When bundled with PyInstaller, extract the offline content to a temp dir
        temp_dir = os.path.join(tempfile.gettempdir(), "desqt_app")
        os.makedirs(temp_dir, exist_ok=True)

        # Create the index.html file
        index_path = os.path.join(temp_dir, "index.html")

        # Try to access the bundled offline content
        try:
            bundled_path = os.path.join(sys._MEIPASS, "offline_content/index.html")
            if os.path.exists(bundled_path):
                # Copy the bundled content to the temp directory
                with open(bundled_path, "r") as src, open(index_path, "w") as dst:
                    dst.write(src.read())
            else:
                # Fall back to creating a basic offline page
                create_basic_offline_page(index_path)
        except Exception:
            # If anything goes wrong, create a basic page
            create_basic_offline_page(index_path)

        return index_path
    else:
        # In development mode, create or use the offline content directory
        offline_dir = Path("offline_content")
        offline_dir.mkdir(exist_ok=True)

        offline_file = offline_dir / "index.html"
        if not offline_file.exists():
            create_basic_offline_page(str(offline_file))

        return str(offline_file.absolute())


def create_basic_offline_page(file_path):
    """Create a basic offline HTML page"""
    offline_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DesQt - Offline</title>
    <style>
        body {
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 0;
        }
        .offline-message {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="offline-message">OFFLINE</div>
</body>
</html>
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(offline_html)


class WebBrowser(QMainWindow):
    def __init__(self, online_url, offline_path):
        super().__init__()

        # Store URLs
        self.online_url = online_url
        self.offline_path = offline_path

        # Set application name
        self.setWindowTitle("DesQt")

        # Set window size
        self.setMinimumSize(1024, 768)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add navigation buttons
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.go_back)
        toolbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.go_forward)
        toolbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        toolbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)

        check_connection_btn = QAction("Check Connection", self)
        check_connection_btn.triggered.connect(self.check_connection)
        toolbar.addAction(check_connection_btn)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Create WebView
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Connect error handler
        self.browser.page().loadFinished.connect(self.handle_load_finished)

        # Initialize - Check connection and load appropriate URL
        self.online_mode = self.is_online()
        self.load_appropriate_content()

        # Connect page title to window title
        self.browser.titleChanged.connect(self.update_title)

    def update_title(self, title):
        self.setWindowTitle(f"DesQt - {title}")

    def is_online(self):
        """Check if we can connect to the internet"""
        try:
            # Try to connect to a reliable server (Google's DNS)
            urllib.request.urlopen("https://8.8.8.8", timeout=1)
            return True
        except:
            return False

    def load_appropriate_content(self):
        """Load either online or offline content based on connectivity"""
        if self.is_online():
            self.browser.load(QUrl(self.online_url))
            self.status_bar.showMessage("Online mode")
            self.online_mode = True
        else:
            offline_url = QUrl.fromLocalFile(self.offline_path)
            self.browser.load(offline_url)
            self.status_bar.showMessage("Offline mode - Using local content")
            self.online_mode = False

    def handle_load_finished(self, success):
        """Handle page load completion"""
        if not success and self.online_mode:
            # If online load failed, switch to offline mode
            self.status_bar.showMessage("Connection failed - Using local content")
            offline_url = QUrl.fromLocalFile(self.offline_path)
            self.browser.load(offline_url)
            self.online_mode = False

    def check_connection(self):
        """Manually check connection and switch modes if needed"""
        current_mode = self.online_mode
        self.load_appropriate_content()
        if current_mode != self.online_mode:
            self.status_bar.showMessage(
                f"Switched to {'online' if self.online_mode else 'offline'} mode"
            )

    def go_back(self):
        self.browser.back()

    def go_forward(self):
        self.browser.forward()

    def reload_page(self):
        current_url = self.browser.url()
        # If we're in online mode but trying to reload an offline page, check connection first
        if self.online_mode and current_url.isLocalFile():
            self.check_connection()
        else:
            self.browser.reload()

    def go_home(self):
        # Go to either online or offline home depending on connectivity
        self.load_appropriate_content()


def main():
    # Create application
    app = QApplication(sys.argv)

    # Set application name
    app.setApplicationName("DesQt")

    # Website URL
    online_url = "https://www.linux.org/"

    # Get/create offline content
    offline_path = extract_offline_content()

    # Create browser instance
    browser = WebBrowser(online_url, offline_path)
    browser.show()

    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
