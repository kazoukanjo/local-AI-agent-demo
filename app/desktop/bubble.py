from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QFont, QRadialGradient
from PySide6.QtWidgets import QWidget

class Bubble(QWidget):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Area đủ rộng để vẽ smooth glow
        self.setFixedSize(110, 110)
        
        self.is_hovered = False
        self._scale_factor = 1.0

        # Animation thu phóng Premium 200ms
        self.anim = QPropertyAnimation(self, b"scale_factor")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.anim.setStartValue(1.05)
            self.anim.setEndValue(0.95)
            self.anim.start()
            self.clicked.emit()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.anim.setStartValue(0.95)
            self.anim.setEndValue(1.05 if self.is_hovered else 1.0)
            self.anim.start()

    def enterEvent(self, event):
        self.is_hovered = True
        self.anim.stop()
        self.anim.setStartValue(self._scale_factor)
        self.anim.setEndValue(1.05)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.anim.stop()
        self.anim.setStartValue(self._scale_factor)
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().leaveEvent(event)
        
    def get_scale_factor(self):
        return self._scale_factor

    def set_scale_factor(self, value):
        self._scale_factor = value
        self.update()
        
    scale_factor = Property(float, get_scale_factor, set_scale_factor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        painter.translate(center)
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-center)

        rect = self.rect().adjusted(25, 25, -25, -25)
        
        # Ambient Sakura Glow
        glow = QRadialGradient(center, 48)
        glow_opacity = 120 if self.is_hovered else 80
        glow.setColorAt(0.0, QColor(233, 160, 184, glow_opacity))
        glow.setColorAt(1.0, QColor(233, 160, 184, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, 45, 45)

        # Base Surface
        bg_color = QColor("#161D29") if self.is_hovered else QColor("#111722")
        painter.setBrush(bg_color)
        
        # Subtle Border
        painter.setPen(QColor(233, 160, 184, 60))
        painter.drawEllipse(rect)

        # AI Avatar
        painter.setFont(QFont("Segoe UI", 20))
        painter.setPen(QColor("#F5C4D3"))
        painter.drawText(rect, Qt.AlignCenter, "🌸")
        painter.end()