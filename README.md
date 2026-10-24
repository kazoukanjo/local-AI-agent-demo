# AI Agent của Khánh

Desktop AI Assistant chạy native trên Windows. Giao diện chính không mở trình duyệt.

## Điểm chính
- Floating chat bubble ở góc màn hình.
- Chat desktop native bằng PySide6.
- Ctrl+Shift+Space để gọi AI.
- Gemini function calling.
- App discovery: Start Menu/Desktop/Program Files/PATH.
- Web fallback cho YouTube, Facebook, Zalo Web, Discord, Spotify, Google, ChatGPT, GitHub...
- Tìm/đọc TXT, MD, CSV, JSON, LOG, code, PDF, DOCX, XLSX.
- Browser automation bằng Playwright, semantic fill/click.
- SQLite memory.
- Confirmation gate.
- Sakura/Japanese-inspired dark UI.

## Cài đặt

Khuyến nghị Python 3.12+; nếu máy bạn đang dùng Python 3.14 thì thử trực tiếp, nếu package GUI gặp lỗi compatibility hãy dùng Python 3.13.

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
```

Mở `.env`, điền API key mới của bạn:

```env
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-2.5-flash
```

Chạy:

```powershell
python main.py
```

Hoặc double click `run_agent.bat`.

## Cách dùng
- "Mở Opera Air"
- "Mở YouTube"
- "Mở Zalo"
- "Tìm file đề thi vật lý"
- "Đọc file D:\TaiLieu\vatly.pdf và tóm tắt"
- "Mở website này và tìm câu 5"
- "Điền tên vào ô Họ tên"

Browser automation chỉ mở khi bạn yêu cầu thao tác website. Giao diện AI không chạy trên Chrome/Edge.

## Bảo mật
Không commit `.env`. Không lưu API key vào source. Không dùng arbitrary shell execution. Các hành động có hậu quả cần confirmation.
