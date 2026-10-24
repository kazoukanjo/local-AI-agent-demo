from PySide6.QtCore import QThread,Signal
class AgentWorker(QThread):
    finished=Signal(dict); failed=Signal(str)
    def __init__(self,agent,text,parent=None): super().__init__(parent); self.agent=agent; self.text=text
    def run(self):
        try:self.finished.emit(self.agent.run(self.text))
        except Exception as e:self.failed.emit(str(e))
