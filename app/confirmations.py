import threading
import uuid

class ConfirmationManager:
    def __init__(self):
        self.pending = {}
        self.lock = threading.Lock()

    def create(self, action, details):
        token = uuid.uuid4().hex
        with self.lock:
            self.pending[token] = {"action": action, "details": details}
        return token

    def pop(self, token):
        with self.lock:
            return self.pending.pop(token, None)

manager = ConfirmationManager()

DANGEROUS_TOOL_NAMES = {
    "browser_submit",
    "browser_delete",
    "delete_file",
    "send_message",
    "purchase",
}

def requires_confirmation(tool_name, args):
    if tool_name in DANGEROUS_TOOL_NAMES:
        return True
    if tool_name == "browser_click":
        combined = (
            str(args.get("selector", "")) + " " +
            str(args.get("description", ""))
        ).lower()
        risky = [
            "submit", "send", "delete", "remove", "buy",
            "purchase", "pay", "checkout", "confirm",
            "đăng", "gửi", "xóa", "mua"
        ]
        return any(x in combined for x in risky)
    return False
