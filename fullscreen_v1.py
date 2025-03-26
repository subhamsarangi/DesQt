import sys
import time
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt, QTimer, QEvent


# Helper function to set a larger font on widgets
def set_large_font(widget, point_size=18):
    font = widget.font()
    font.setPointSize(point_size)
    widget.setFont(font)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Full Screen Evaluation App")
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.home_page = self.create_home_page()
        self.eval_page = self.create_evaluation_page()
        self.summary_page = self.create_summary_page()
        self.disqualified_page = self.create_disqualified_page()

        # Add pages to stack
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.eval_page)
        self.stack.addWidget(self.summary_page)
        self.stack.addWidget(self.disqualified_page)

        # Timer variables
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = 0

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        btn_start = QPushButton("Start")
        set_large_font(btn_start)
        btn_start.clicked.connect(self.start_evaluation)
        layout.addWidget(btn_start)
        return page

    def create_evaluation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.timer_label = QLabel("Timer: 0 s")
        set_large_font(self.timer_label)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_stop = QPushButton("Stop")
        set_large_font(btn_stop)
        btn_stop.clicked.connect(self.stop_evaluation)
        layout.addWidget(self.timer_label)
        layout.addWidget(btn_stop)
        return page

    def create_summary_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.summary_label = QLabel("Summary")
        set_large_font(self.summary_label)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_back = QPushButton("Back to Home")
        set_large_font(btn_back)
        btn_back.clicked.connect(self.go_home)
        layout.addWidget(self.summary_label)
        layout.addWidget(btn_back)
        return page

    def create_disqualified_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Disqualified due to misuse")
        set_large_font(label)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_back = QPushButton("Back to Home")
        set_large_font(btn_back)
        btn_back.clicked.connect(self.go_home)
        layout.addWidget(label)
        layout.addWidget(btn_back)
        return page

    def start_evaluation(self):
        # Go to evaluation page, start timer, and enter full screen.
        self.stack.setCurrentWidget(self.eval_page)
        self.start_time = time.time()
        self.timer.start(1000)  # update every second
        self.showFullScreen()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.setText(f"Timer: {elapsed} s")

    def stop_evaluation(self):
        self.timer.stop()
        elapsed = int(time.time() - self.start_time)
        self.summary_label.setText(f"Elapsed Time: {elapsed} s")
        self.showNormal()  # exit full screen
        self.stack.setCurrentWidget(self.summary_page)

    def go_home(self):
        # Return to home and ensure normal window state.
        self.timer.stop()
        self.showNormal()
        self.stack.setCurrentWidget(self.home_page)

    # Override keyPressEvent to block F11 and Esc
    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_F11,
            Qt.Key.Key_Escape,
        ):
            # Ignore F11 and Escape to prevent manual full-screen toggle.
            event.ignore()
        else:
            super().keyPressEvent(event)

    # Monitor focus events. If the window loses focus while in evaluation, disqualify.
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            # When the window state changes, check if it lost focus.
            if (
                not self.isActiveWindow()
                and self.stack.currentWidget() == self.eval_page
            ):
                self.timer.stop()
                self.showNormal()
                self.stack.setCurrentWidget(self.disqualified_page)
        super().changeEvent(event)

    def event(self, event):
        # Also monitor focus out events.
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.stack.currentWidget() == self.eval_page:
                self.timer.stop()
                self.showNormal()
                self.stack.setCurrentWidget(self.disqualified_page)
        return super().event(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
