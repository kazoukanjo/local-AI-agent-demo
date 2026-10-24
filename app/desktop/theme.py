def apply_theme(app):
    qss = """
    /* === DESIGN TOKENS & TYPOGRAPHY === */
    QWidget {
        font-family: "Segoe UI", "Inter", "Noto Sans JP", sans-serif;
        font-size: 14px;
        color: #F5F5F7;
    }

    /* === PREMIUM THIN SCROLLBAR === */
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 6px;
        border-radius: 3px;
        margin: 2px;
    }
    QScrollBar::handle:vertical {
        background: rgba(167, 175, 188, 0.2);
        min-height: 30px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(233, 160, 184, 0.6); /* Sakura Hover */
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        border: none;
        background: none;
        height: 0px;
    }

    /* === CHAT AREA === */
    QTextBrowser {
        background-color: transparent;
        border: none;
        padding: 8px;
    }

    /* === INPUT FIELD (Floating Card Style) === */
    QTextEdit#ChatInput {
        background-color: transparent;
        border: none;
        color: #F5F5F7;
        selection-background-color: #E9A0B8;
        selection-color: #080A0F;
        font-size: 14px;
    }

    /* === QUICK ACTIONS & NORMAL BUTTONS === */
    QPushButton {
        border-radius: 14px;
        background-color: rgba(17, 23, 34, 0.7);
        border: 1px solid rgba(37, 44, 56, 0.8);
        color: #A7AFBC;
        padding: 6px 14px;
        font-weight: 500;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: rgba(233, 160, 184, 0.1);
        color: #F5C4D3;
        border: 1px solid rgba(233, 160, 184, 0.3);
    }
    QPushButton:pressed {
        background-color: rgba(233, 160, 184, 0.2);
        border: 1px solid rgba(233, 160, 184, 0.5);
    }
    QPushButton:disabled {
        opacity: 0.3;
        background-color: transparent;
        border: 1px solid rgba(37, 44, 56, 0.4);
    }

    /* Nút Gửi (Primary Action) */
    QPushButton#BtnSend {
        background-color: #E9A0B8;
        color: #080A0F;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 18px;
    }
    QPushButton#BtnSend:hover {
        background-color: #F1A7C0;
    }
    QPushButton#BtnSend:pressed {
        background-color: #D989A7;
    }
    QPushButton#BtnSend:disabled {
        background-color: #252C38;
        color: #6F7785;
    }

    /* Nút Công cụ Input (Mic, Attach) */
    QPushButton#BtnTool {
        background-color: transparent;
        border: none;
        color: #6F7785;
        font-size: 16px;
        border-radius: 18px;
    }
    QPushButton#BtnTool:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: #E9A0B8;
    }

    /* === COMMAND PALETTE DIALOG === */
    QLineEdit#CommandInput {
        background-color: #0D1118;
        border: 1px solid rgba(233, 160, 184, 0.4);
        border-radius: 12px;
        padding: 10px 14px;
        color: #F5F5F7;
        font-size: 14px;
    }
    """
    app.setStyleSheet(qss)