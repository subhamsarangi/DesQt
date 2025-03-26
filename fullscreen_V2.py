import sys
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, QEvent, QUrl
from PyQt6.QtGui import QGuiApplication

from PyQt6.QtMultimedia import (
    QMediaDevices,
    QCamera,
    QMediaCaptureSession,
    QMediaRecorder,
    QAudioInput,
    QScreenCapture,
)


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

        # Check for camera and microphone availability using QMediaDevices.
        self.camera_device = QMediaDevices.defaultVideoInput()
        self.audio_device = QMediaDevices.defaultAudioInput()

        # Check for screen capture permission.
        self.screen = QGuiApplication.primaryScreen()
        if self.screen is not None:
            test_pixmap = self.screen.grabWindow(0)
            self.screen_ok = not test_pixmap.isNull()
        else:
            self.screen_ok = False

        # Recording-related objects for camera/audio.
        self.camera = None
        self.audio_input = None
        self.camera_capture_session = None
        self.camera_recorder = None

        # Recording-related objects for screen.
        self.screen_capture = None
        self.screen_capture_session = None
        self.screen_recorder = None

        # Output file URLs.
        self.camera_output_file = None
        self.screen_output_file = None

        # Create pages.
        self.home_page = self.create_home_page()
        self.eval_page = self.create_evaluation_page()
        self.summary_page = self.create_summary_page()
        self.disqualified_page = self.create_disqualified_page()

        # Add pages to stack.
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.eval_page)
        self.stack.addWidget(self.summary_page)
        self.stack.addWidget(self.disqualified_page)

        # Timer variables.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = 0

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Status labels for camera, microphone, and screen.
        self.camera_status_label = QLabel()
        self.mic_status_label = QLabel()
        self.screen_status_label = QLabel()
        set_large_font(self.camera_status_label)
        set_large_font(self.mic_status_label)
        set_large_font(self.screen_status_label)
        layout.addWidget(self.camera_status_label)
        layout.addWidget(self.mic_status_label)
        layout.addWidget(self.screen_status_label)

        # Check and update the status.
        cam_ok = self.camera_device is not None
        mic_ok = self.audio_device is not None

        self.camera_status_label.setText(
            "Camera: OK" if cam_ok else "Camera: Not available"
        )
        self.mic_status_label.setText(
            "Microphone: OK" if mic_ok else "Microphone: Not available"
        )
        self.screen_status_label.setText(
            "Screen: OK"
            if self.screen_ok
            else "Screen: Not available or permission denied"
        )

        # Start button.
        self.btn_start = QPushButton("Start")
        set_large_font(self.btn_start)
        self.btn_start.clicked.connect(self.start_evaluation)
        # Disable start if any device is missing.
        self.btn_start.setEnabled(cam_ok and mic_ok and self.screen_ok)
        layout.addWidget(self.btn_start)
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
        try:
            # Ensure recordings are initialized successfully
            if not self.init_recordings():
                return

            # Rest of the start_evaluation method remains the same
            self.stack.setCurrentWidget(self.eval_page)
            self.start_time = time.time()
            self.timer.start(1000)  # update every second
            self.showFullScreen()

            # Explicitly start recordings with additional checks
            if hasattr(self, "camera_recorder"):
                self.camera_recorder.record()
            if hasattr(self, "screen_recorder"):
                self.screen_recorder.record()

            # Debug prints
            print("Camera Recorder State:", self.camera_recorder.recorderState())
            print("Screen Recorder State:", self.screen_recorder.recorderState())

        except Exception as e:
            print(f"Error starting evaluation: {e}")
            self.show_error_message("Evaluation Start Error", str(e))

    def on_camera_active_changed(self, active: bool):
        if active:
            print("Camera is active, starting recording...")
            self.camera_recorder.record()
        else:
            print("Camera is inactive.")

    def init_screen_recording(self):
        try:
            # Explicitly get the primary screen
            screen = QGuiApplication.primaryScreen()
            if not screen:
                raise ValueError("No primary screen found")

            # Create screen capture with more explicit configuration
            self.screen_capture = QScreenCapture()

            # Set the specific screen to capture
            self.screen_capture.setScreen(screen)

            # Create capture session specifically for screen
            self.screen_capture_session = QMediaCaptureSession()
            self.screen_capture_session.setScreenCapture(self.screen_capture)

            # Create media recorder
            self.screen_recorder = QMediaRecorder()
            self.screen_capture_session.setRecorder(self.screen_recorder)

            # Set output file for screen recording with absolute path
            screen_output_path = str(Path("screen_recording.mp4").resolve())
            self.screen_recorder.setOutputLocation(
                QUrl.fromLocalFile(screen_output_path)
            )

            # Detailed error handling
            self.screen_recorder.errorOccurred.connect(
                self.handle_screen_recorder_error
            )

            # Additional configuration to improve recording reliability
            self.screen_capture.setActive(True)

            print("Screen recording initialized successfully")
            return True

        except Exception as e:
            print(f"Screen recording initialization error: {e}")
            self.show_error_message("Screen Recording Setup Error", str(e))
            return False

    def init_recordings(self):
        try:
            # Camera recording setup (previous implementation)
            self.camera = QCamera(self.camera_device)
            self.audio_input = QAudioInput(self.audio_device)

            self.camera_capture_session = QMediaCaptureSession()
            self.camera_capture_session.setCamera(self.camera)
            self.camera_capture_session.setAudioInput(self.audio_input)

            self.camera_recorder = QMediaRecorder()
            self.camera_capture_session.setRecorder(self.camera_recorder)

            camera_output_path = str(Path("camera_recording.mp4").resolve())
            self.camera_recorder.setOutputLocation(
                QUrl.fromLocalFile(camera_output_path)
            )

            self.camera_recorder.errorOccurred.connect(
                self.handle_camera_recorder_error
            )

            # Start camera
            self.camera.start()

            # Separate method for screen recording with additional error checking
            screen_recording_success = self.init_screen_recording()
            if not screen_recording_success:
                raise ValueError("Screen recording setup failed")

        except Exception as e:
            print(f"Error initializing recordings: {e}")
            self.show_error_message("Recording Initialization Error", str(e))
            return False

        return True

    def handle_camera_recorder_error(self, error, error_string):
        """Handle camera recorder errors with detailed logging."""
        print(f"Camera Recorder Error: {error}")
        print(f"Error Details: {error_string}")
        self.show_error_message("Camera Recording Error", error_string)

    def handle_screen_recorder_error(self, error, error_string):
        """Enhanced screen recorder error handling"""
        print(f"Screen Recorder Error: {error}")
        print(f"Error Details: {error_string}")

        # Additional diagnostic information
        screen = QGuiApplication.primaryScreen()
        if screen:
            print("Screen Geometry:", screen.geometry())
            print("Screen Device Pixel Ratio:", screen.devicePixelRatio())

        self.show_error_message(
            "Screen Recording Error",
            f"Error: {error_string}\n\n"
            "Possible causes:\n"
            "- Insufficient permissions\n"
            "- Screen capture not supported\n"
            "- Missing video codec",
        )

    def show_error_message(self, title, message):
        """Display an error message to the user."""
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec()

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.setText(f"Timer: {elapsed} s")

    def stop_evaluation(self):
        # Stop timer and both recordings, show summary.
        self.timer.stop()

        if self.camera_recorder:
            self.camera_recorder.stop()
        if self.screen_recorder:
            self.screen_recorder.stop()

        if self.camera:
            self.camera.stop()

        elapsed = int(time.time() - self.start_time)
        self.summary_label.setText(f"Elapsed Time: {elapsed} s")
        self.showNormal()  # exit full screen
        self.stack.setCurrentWidget(self.summary_page)

        # More robust file location reporting
        try:
            camera_location = self.camera_recorder.actualLocation().toLocalFile()
            screen_location = self.screen_recorder.actualLocation().toLocalFile()

            print("Camera recording saved at:", camera_location)
            print("Screen recording saved at:", screen_location)
        except Exception as e:
            print(f"Error checking recording locations: {e}")

    def go_home(self):
        # Return to home page; also stop any ongoing recording.
        self.timer.stop()
        if self.camera_recorder:
            self.camera_recorder.stop()
        if self.screen_recorder:
            self.screen_recorder.stop()
        if self.camera:
            self.camera.stop()
        self.showNormal()
        self.stack.setCurrentWidget(self.home_page)

    # Override keyPressEvent to block F11 and Esc.
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_F11, Qt.Key.Key_Escape):
            event.ignore()
        else:
            super().keyPressEvent(event)

    # Monitor focus events: if focus is lost during evaluation, disqualify.
    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if (
                not self.isActiveWindow()
                and self.stack.currentWidget() == self.eval_page
            ):
                self.timer.stop()
                if self.camera_recorder:
                    self.camera_recorder.stop()
                if self.screen_recorder:
                    self.screen_recorder.stop()
                if self.camera:
                    self.camera.stop()
                self.showNormal()
                self.stack.setCurrentWidget(self.disqualified_page)
        super().changeEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.stack.currentWidget() == self.eval_page:
                self.timer.stop()
                if self.camera_recorder:
                    self.camera_recorder.stop()
                if self.screen_recorder:
                    self.screen_recorder.stop()
                if self.camera:
                    self.camera.stop()
                self.showNormal()
                self.stack.setCurrentWidget(self.disqualified_page)
        return super().event(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
