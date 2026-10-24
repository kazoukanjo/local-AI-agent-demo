from dotenv import load_dotenv
load_dotenv()  # Nạp .env ngay đầu tiên

import sys
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QMessageBox

from app.config import GEMINI_API_KEY, ALWAYS_ON_TOP
from app.desktop.bubble import Bubble
from app.desktop.chat_window import ChatWindow
from app.desktop.tray import Tray
from app.desktop.theme import apply_theme

class DesktopApp(QObject):
    def __init__(self, agent):
        super().__init__()
        self.qt = QApplication.instance() or QApplication([])
        self.qt.setApplicationName('AI Agent của Khánh')
        apply_theme(self.qt)
        
        self.window = ChatWindow(agent)
        self.bubble = Bubble()
        self.bubble.clicked.connect(self.toggle)
        self.tray = Tray(self.window)
        
        screen = self.qt.primaryScreen().availableGeometry()
        self.bubble.move(screen.right() - 90, screen.bottom() - 90)
        self.bubble.show()
        self.window.hide()

    def toggle(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()
            self.window.raise_()
            self.window.activateWindow()

    def run(self):
        return self.qt.exec()