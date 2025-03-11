import sys
import urllib.request
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QToolBar,
    QStatusBar,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction


class WebBrowser(QMainWindow):
    def __init__(self, online_url, offline_path):
        super().__init__()

        # Store URLs
        self.online_url = online_url
        self.offline_path = offline_path

        # Set application name
        self.setWindowTitle("Python Desktop App")

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
        self.setWindowTitle(f"Python Desktop App - {title}")

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


def create_offline_content():
    """Create basic offline content if it doesn't exist"""
    offline_dir = Path("offline_content")
    offline_dir.mkdir(exist_ok=True)

    offline_file = offline_dir / "index.html"

    if not offline_file.exists():
        offline_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Desktop App - Offline Mode</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .message {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin-bottom: 20px;
        }
        .docs-section {
            margin-top: 30px;
        }
        code {
            background-color: #f7f7f7;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #f7f7f7;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Python Desktop App - Offline Mode</h1>
        
        <div class="message">
            <p><strong>You are currently viewing cached offline content.</strong></p>
            <p>The application cannot connect to <code>https://www.linux.org/</code> at this time. Use the "Check Connection" button in the toolbar to try reconnecting.</p>
        </div>
        
        <div class="docs-section">
            <h2>Cached Documentation</h2>
            <p>This is a placeholder for offline documentation. In a complete implementation, you would:</p>
            <ul>
                <li>Create a script to download and save the content from your website for offline use</li>
                <li>Structure the offline content to mirror the online site navigation</li>
                <li>Update the offline content periodically when connected</li>
            </ul>
            
            <h3>Example Code</h3>
            <pre><code>def hello_world():
    print("Welcome to Python Desktop!")
    
hello_world()</code></pre>
        </div>
    </div>
</body>
</html>
"""
        offline_file.write_text(offline_html)

    return str(offline_file.absolute())


def main():
    # Create application
    app = QApplication(sys.argv)

    # Set application name
    app.setApplicationName("Python Desktop App")

    # Website URL
    online_url = "https://www.linux.org/"

    # Create offline content
    offline_path = create_offline_content()

    # Create browser instance
    browser = WebBrowser(online_url, offline_path)
    browser.show()

    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
