from dotenv import load_dotenv
load_dotenv()
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QObject


class Tray(QObject):
    """
    System Tray controller cho AI Agent của Khánh.
    Giữ tên class là Tray để tương thích với app.py hiện tại.
    """

    def __init__(self, desktop_app):
        super().__init__()

        self.desktop_app = desktop_app

        self.tray = QSystemTrayIcon()

        # Icon mặc định.
        # Sau này có thể thay bằng icon Sakura riêng.
        self.tray.setIcon(QIcon())

        # =========================
        # Context Menu
        # =========================

        self.menu = QMenu()

        # Mở AI Agent
        self.show_action = QAction(
            "Mở AI Agent của Khánh",
            self
        )
        self.show_action.triggered.connect(
            self.show_window
        )
        self.menu.addAction(self.show_action)

        # Ẩn AI Agent
        self.hide_action = QAction(
            "Ẩn AI Agent",
            self
        )
        self.hide_action.triggered.connect(
            self.hide_window
        )
        self.menu.addAction(self.hide_action)

        self.menu.addSeparator()

        # Thoát
        self.exit_action = QAction(
            "Thoát",
            self
        )
        self.exit_action.triggered.connect(
            self.exit_app
        )
        self.menu.addAction(self.exit_action)

        self.tray.setContextMenu(self.menu)

        # Click icon trên System Tray
        self.tray.activated.connect(
            self.on_activated
        )

    # =========================
    # Start Tray
    # =========================

    def start(self):
        self.tray.show()

    # =========================
    # Show Window
    # =========================

    def show_window(self):
        try:
            self.desktop_app.show()
            self.desktop_app.raise_()
            self.desktop_app.activateWindow()

        except Exception as e:
            print(f"Tray show error: {e}")

    # =========================
    # Hide Window
    # =========================

    def hide_window(self):
        try:
            self.desktop_app.hide()

        except Exception as e:
            print(f"Tray hide error: {e}")

    # =========================
    # Toggle Window
    # =========================

    def toggle_window(self):
        try:
            if self.desktop_app.isVisible():
                self.hide_window()
            else:
                self.show_window()

        except Exception as e:
            print(f"Tray toggle error: {e}")

    # =========================
    # Tray Click
    # =========================

    def on_activated(self, reason):

        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window()

    # =========================
    # Exit
    # =========================

    def exit_app(self):
        try:
            self.tray.hide()

            # Lấy QApplication
            app = self.desktop_app.app

            if app is not None:
                app.quit()

        except Exception as e:
            print(f"Tray exit error: {e}")