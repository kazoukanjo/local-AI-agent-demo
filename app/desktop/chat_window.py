import os
from datetime import datetime
from html import escape
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import (
    QColor, QPainter, QLinearGradient, QPainterPath, 
    QKeySequence, QShortcut, QRadialGradient
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextBrowser, QTextEdit, QFrame, 
    QMessageBox, QGraphicsDropShadowEffect, QDialog, 
    QLineEdit, QListWidget, QListWidgetItem, QApplication
)
from .theme import apply_theme
from ..core.worker import AgentWorker

class CommandPaletteDialog(QDialog):
    """Command Palette (Ctrl + K) - Minimal & Premium."""
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setWindowTitle("Command Palette")
        self.setFixedWidth(420)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setStyleSheet("background: #0D1118; border: 1px solid rgba(37,44,56,1); border-radius: 16px;")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)
        
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(12, 12, 12, 12)
        c_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("CommandInput")
        self.search_input.setPlaceholderText("🔍 Tìm lệnh thao tác nhanh (App, Website, File)...")
        self.search_input.textChanged.connect(self.filter_items)
        c_layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background: transparent; border: none; outline: none; }
            QListWidget::item { padding: 12px; border-radius: 10px; color: #A7AFBC; font-size: 14px; }
            QListWidget::item:hover, QListWidget::item:selected { 
                background: rgba(233, 160, 184, 0.1); color: #F5C4D3; 
            }
        """)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        c_layout.addWidget(self.list_widget)
        layout.addWidget(container)

        self.commands = [
            ("🚀 Mở ứng dụng (VD: Mở Opera Air)", "Mở ứng dụng "),
            ("📁 Tìm file trong máy", "Tìm file "),
            ("🌐 Mở Website (VD: Mở YouTube)", "Mở website "),
            ("📄 Đọc file & Phân tích", "Đọc file và tóm tắt "),
            ("📝 Tóm tắt nội dung", "Tóm tắt nội dung "),
            ("📋 Xử lý Clipboard", "Đọc thông tin trong clipboard"),
            ("🛑 Thoát hoàn toàn ứng dụng", "QUIT_APP")
        ]
        self.populate_list()

    def populate_list(self):
        self.list_widget.clear()
        for label, cmd in self.commands:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, cmd)
            self.list_widget.addItem(item)

    def filter_items(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def on_item_clicked(self, item):
        cmd = item.data(Qt.UserRole)
        if self.callback:
            self.callback(cmd)
        self.accept()


class ChatWindow(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.worker = None
        self.pending_token = None
        
        self.setWindowTitle('AI Agent của Khánh')
        self.resize(500, 780)
        self.setMinimumSize(420, 650)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAcceptDrops(True)

        self.root = QFrame(self)
        self.setCentralWidget(self.root)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.root.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.root)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        
        # === HEADER ===
        self.header = QFrame()
        self.header.setFixedHeight(64)
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(20, 0, 16, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title_box.setAlignment(Qt.AlignVCenter)
        
        title_lbl = QLabel('🌸 AI Agent của Khánh')
        title_lbl.setStyleSheet("font-weight: 700; font-size: 15px; color: #F5F5F7; letter-spacing: 0.5px;")
        
        status_lbl = QLabel('● Local AI Assistant Ready')
        status_lbl.setStyleSheet("font-size: 11px; color: #8FD1A5; font-weight: 500;")
        
        title_box.addWidget(title_lbl)
        title_box.addWidget(status_lbl)
        
        hl.addLayout(title_box)
        hl.addStretch()
        
        # --- Nút Tắt Hoàn Toàn ---
        quit_btn = QPushButton('⏻')
        quit_btn.setFixedSize(32, 32)
        quit_btn.setToolTip("Thoát hoàn toàn ứng dụng")
        quit_btn.setStyleSheet("""
            QPushButton { border-radius: 16px; background: transparent; color: #E68E8E; font-size: 16px; font-weight: bold;}
            QPushButton:hover { background: #E68E8E; color: #080A0F; border: none; }
        """)
        quit_btn.clicked.connect(QApplication.instance().quit)
        hl.addWidget(quit_btn)

        # --- Nút Ẩn ---
        close_btn = QPushButton('✕')
        close_btn.setFixedSize(32, 32)
        close_btn.setToolTip("Ẩn ứng dụng (Vẫn chạy ngầm)")
        close_btn.setStyleSheet("""
            QPushButton { border-radius: 16px; background: transparent; color: #6F7785; font-size: 14px;}
            QPushButton:hover { background: rgba(255,255,255,0.1); color: #F5F5F7; border: none; }
        """)
        close_btn.clicked.connect(self.hide)
        hl.addWidget(close_btn)
        
        layout.addWidget(self.header)

        # === CHAT AREA ===
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(20, 10, 20, 10)
        
        self.chat = QTextBrowser()
        self.chat.setOpenExternalLinks(True)
        chat_layout.addWidget(self.chat, 1)
        layout.addWidget(chat_container, 1)

        # === QUICK ACTIONS ===
        quick_frame = QFrame()
        quick_layout = QHBoxLayout(quick_frame)
        quick_layout.setContentsMargins(20, 0, 20, 10)
        quick_layout.setSpacing(8)
        quick_layout.setAlignment(Qt.AlignLeft)
        
        for text, icon in [('App', '🚀'), ('File', '📁'), ('Web', '🌐'), ('Tóm tắt', '📝')]:
            b = QPushButton(f"{icon} {text}")
            b.setCursor(Qt.PointingHandCursor)
            prompt = {'App': 'Mở ứng dụng ', 'File': 'Tìm file ', 'Web': 'Mở website ', 'Tóm tắt': 'Đọc file và tóm tắt '}
            b.clicked.connect(lambda _, p=prompt[text]: self.quick(p))
            quick_layout.addWidget(b)
        layout.addWidget(quick_frame)

        # === INPUT AREA ===
        input_wrap = QFrame()
        input_wrap_layout = QVBoxLayout(input_wrap)
        input_wrap_layout.setContentsMargins(20, 0, 20, 24)
        
        input_card = QFrame()
        input_card.setStyleSheet("""
            QFrame {
                background: #131923;
                border: 1px solid #252C38;
                border-radius: 24px;
            }
        """)
        
        row = QHBoxLayout(input_card)
        row.setContentsMargins(12, 6, 8, 6)
        row.setSpacing(6)
        
        attach_btn = QPushButton('📎')
        attach_btn.setObjectName("BtnTool")
        attach_btn.setFixedSize(36, 36)
        attach_btn.setToolTip("Kéo thả file vào khung chat để phân tích")
        
        self.input = QTextEdit()
        self.input.setObjectName("ChatInput")
        self.input.setPlaceholderText('Giao việc cho AI... (Ctrl+K mở lệnh)')
        self.input.setFixedHeight(40)
        self.input.installEventFilter(self)
        
        mic = QPushButton('🎙')
        mic.setObjectName("BtnTool")
        mic.setFixedSize(36, 36)
        mic.clicked.connect(lambda: self.show_toast("🎙 Míc đang sẵn sàng"))
        
        self.send_btn = QPushButton('➤')
        self.send_btn.setObjectName("BtnSend")
        self.send_btn.setFixedSize(36, 36)
        self.send_btn.clicked.connect(self.send)
        self.send_btn.setEnabled(False)
        self.input.textChanged.connect(self.check_input)
        
        row.addWidget(attach_btn)
        row.addWidget(self.input, 1)
        row.addWidget(mic)
        row.addWidget(self.send_btn)
        
        input_wrap_layout.addWidget(input_card)
        layout.addWidget(input_wrap)

        self.shortcut_palette = QShortcut(QKeySequence("Ctrl+K"), self)
        self.shortcut_palette.activated.connect(self.open_command_palette)

        self._append('🌸 AI Agent', 'bot', '<b>Konnichiwa Khánh!</b> ✨<br>Tôi là trợ lý AI nội bộ trên laptop của bạn.<br>Hãy yêu cầu tôi mở app, lướt web, hay phân tích tài liệu nhé.', is_raw=True)

    def check_input(self):
        self.send_btn.setEnabled(bool(self.input.toPlainText().strip()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.show_toast("📎 Thả file vào đây")

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            file_name = os.path.basename(file_path)
            self.input.setPlainText(f"Đọc nội dung file này: {file_path}")
            self.show_toast(f"✓ Sẵn sàng xử lý: {file_name}")
            self.input.setFocus()

    def open_command_palette(self):
        palette = CommandPaletteDialog(self, callback=self.quick)
        palette.exec()

    def show_toast(self, message):
        toast = QLabel(message, self)
        toast.setStyleSheet("""
            background-color: #111722; color: #E9A0B8; 
            border: 1px solid #252C38; border-radius: 16px; 
            padding: 10px 18px; font-size: 13px; font-weight: 500;
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0,0,0,120))
        shadow.setOffset(0,4)
        toast.setGraphicsEffect(shadow)
        
        toast.adjustSize()
        toast.move((self.width() - toast.width()) // 2, 70)
        toast.show()
        QTimer.singleShot(2500, toast.deleteLater)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() < 64:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0.0, QColor("#080A0F"))
            grad.setColorAt(1.0, QColor("#0D1118"))
            
            rect = self.rect().adjusted(4, 4, -4, -4)
            path = QPainterPath()
            path.addRoundedRect(rect, 20, 20)
            painter.fillPath(path, grad)
            
            mountain = QPainterPath()
            mountain.moveTo(4, self.height() - 4)
            mountain.lineTo(4, self.height() * 0.75)
            mountain.quadTo(self.width() * 0.3, self.height() * 0.6, self.width() * 0.6, self.height() * 0.8)
            mountain.quadTo(self.width() * 0.8, self.height() * 0.9, self.width() - 4, self.height() * 0.65)
            mountain.lineTo(self.width() - 4, self.height() - 4)
            
            mountain_grad = QLinearGradient(0, self.height()*0.6, 0, self.height())
            mountain_grad.setColorAt(0, QColor(17, 23, 34, 100))
            mountain_grad.setColorAt(1, QColor(17, 23, 34, 180))
            painter.fillPath(mountain, mountain_grad)
            
            painter.setPen(QColor(37, 44, 56, 150))
            painter.drawPath(path)
            painter.end()
        except Exception:
            pass

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self.send()
                return True
        return super().eventFilter(obj, event)

    def quick(self, p):
        # Nếu là lệnh thoát thì đóng luôn ứng dụng
        if p == "QUIT_APP":
            QApplication.instance().quit()
            return
            
        self.input.setPlainText(p)
        self.input.setFocus()

    def _append(self, name, role, text, is_raw=False):
        bg = '#111722' if role == 'bot' else '#1D1418'
        border = '#252C38' if role == 'bot' else '#3D2630'
        text_color = '#F5F5F7'
        align_attr = 'align="left"' if role == 'bot' else 'align="right"'
        time_str = datetime.now().strftime("%H:%M")
        
        if is_raw:
            html_text = text
        else:
            html_text = escape(text).replace('\n', '<br>')
        
        html = f"""
        <div {align_attr} style="margin-bottom: 8px;">
            <span style="color: #6F7785; font-size: 11px; margin: 0 4px;">{escape(name)} • {time_str}</span>
            <table {align_attr} width="85%" cellpadding="14" cellspacing="0" style="margin-top: 4px;">
                <tr>
                    <td bgcolor="{bg}" style="color: {text_color}; font-size: 14px; border: 1px solid {border}; border-radius: 16px; line-height: 1.6;">
                        {html_text}
                    </td>
                </tr>
            </table>
        </div><br>
        """
        self.chat.append(html)
        self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())

    def send(self):
        text = self.input.toPlainText().strip()
        if not text or (self.worker and self.worker.isRunning()):
            return
        self.input.clear()
        self._append('Khánh', 'user', text)
        
        self._append('🌸 AI Agent', 'bot', '● ● ● Đang xử lý...')
        
        self.worker = AgentWorker(self.agent, text)
        self.worker.finished.connect(self.on_result)
        self.worker.failed.connect(self.on_error)
        self.worker.start()

    def on_result(self, res):
        self._remove_last()
        ans = res.get('answer', '')
        if not ans and res.get('status'):
            ans = f"✅ {res['status']}"
        self._append('🌸 AI Agent', 'bot', ans)
        
        if res.get('confirmation_token'):
            self.pending_token = res['confirmation_token']
            self._show_confirm()

    def on_error(self, error):
        self._remove_last()
        self._append('🌸 AI Agent', 'bot', f'⚠️ Lỗi hệ thống: {error}')

    def _remove_last(self):
        cur = self.chat.toHtml()
        if '● ● ● Đang xử lý...' in cur:
            body = cur.replace('● ● ● Đang xử lý...', '')
            self.chat.setHtml(body)

    def _show_confirm(self):
        box = QMessageBox(self)
        box.setWindowTitle('AI Agent Xác nhận')
        box.setText('Hành động này có thể thay đổi dữ liệu của bạn. Tiếp tục?')
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if box.exec() == QMessageBox.Yes:
            self.confirm()
        else:
            self.pending_token = None

    def confirm(self):
        if not self.pending_token:
            return
        try:
            res = self.agent.execute_confirmation(self.pending_token)
            self._append('🌸 AI Agent', 'bot', str(res.get('result') or res.get('message') or '✅ Đã xác nhận.'))
        except Exception:
            self._append('🌸 AI Agent', 'bot', '⚠️ Lỗi xác nhận. Vui lòng thử lại.')
        self.pending_token = None

    def showEvent(self, e):
        self.activateWindow()
        self.raise_()
        self.input.setFocus()
        super().showEvent(e)