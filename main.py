import sys
from PySide6.QtWidgets import QApplication,QMessageBox
from app.config import ENABLE_HOTKEY,HOTKEY
from app.core.agent import GeminiAgent
from app.desktop.app import DesktopApp
from app.hotkey import HotkeyController
from app.logging_config import setup_logging

def main():
    setup_logging()
    qt=QApplication.instance() or QApplication(sys.argv)
    try: agent=GeminiAgent()
    except Exception as e:
        QMessageBox.critical(None,'AI Agent của Khánh',str(e)); return 1
    desktop=DesktopApp(agent)
    if ENABLE_HOTKEY:
        hotkey=HotkeyController(HOTKEY); hotkey.activated.connect(desktop.toggle); hotkey.start(); desktop.hotkey=hotkey
    return desktop.run()
if __name__=='__main__': raise SystemExit(main())
