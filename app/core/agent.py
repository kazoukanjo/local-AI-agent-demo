from google import genai
from google.genai import types
from ..config import GEMINI_API_KEY,GEMINI_MODEL
from ..memory import Memory
from ..confirmations import manager,requires_confirmation
from ..tools.registry import FUNCTIONS

SYSTEM=r"""
Bạn là "AI Agent của Khánh", trợ lý AI chạy local trên Windows.

Bạn có thể trò chuyện bình thường và thực hiện tác vụ thật bằng tools được cấp:
- mở ứng dụng Windows bằng từ khóa;
- mở file/thư mục/website;
- tìm và đọc tài liệu;
- đọc website bằng browser automation;
- điền trường và click trên website;
- ghi nhớ điều người dùng yêu cầu;
- liệt kê ứng dụng đã phát hiện.

Nguyên tắc:
1. Nếu yêu cầu là tác vụ, ưu tiên dùng tool thay vì chỉ hướng dẫn.
2. Không nói đã thực hiện nếu tool chưa trả về thành công.
3. "Mở Opera Air", "bật Opera Air", "khởi động Opera Air" đều là open_app("Opera Air").
4. "Mở YouTube/Facebook/Zalo/Discord/Spotify..." dùng open_app trước; nếu không có app và tool trả web_fallback thì có thể mở URL fallback bằng open_url.
5. Tóm tắt/hỏi đáp tài liệu: đọc file trước, rồi dùng nội dung thật để trả lời.
6. Hỏi đáp website: browser_goto -> browser_snapshot -> phân tích nội dung -> nếu được yêu cầu mới browser_fill/browser_click.
7. Không vượt CAPTCHA, đăng nhập thay người dùng, lấy mật khẩu, API key, token, cookie hoặc thông tin xác thực.
8. Các thao tác gửi/xóa/mua/thanh toán/submit/thay đổi tài khoản cần confirmation ở lớp ứng dụng.
9. Không chạy shell/PowerShell/CMD tùy ý. Chỉ dùng tools được cấp.
10. Trả lời tiếng Việt, tự nhiên, ngắn gọn nhưng đủ thông tin.
"""

def declarations():
    return [
      {'name':'open_app','description':'Mở ứng dụng Windows theo tên/từ khóa.','parameters':{'type':'object','properties':{'keyword':{'type':'string'}},'required':['keyword']}},
      {'name':'open_path','description':'Mở file hoặc thư mục bằng ứng dụng mặc định Windows.','parameters':{'type':'object','properties':{'path':{'type':'string'}},'required':['path']}},
      {'name':'open_url','description':'Mở URL bằng trình duyệt mặc định của Windows.','parameters':{'type':'object','properties':{'url':{'type':'string'}},'required':['url']}},
      {'name':'list_installed_apps','description':'Tìm các ứng dụng đã phát hiện trên máy.','parameters':{'type':'object','properties':{'query':{'type':'string'},'limit':{'type':'integer'}},'required':['query']}},
      {'name':'find_files','description':'Tìm file trong các thư mục được cấu hình.','parameters':{'type':'object','properties':{'query':{'type':'string'},'limit':{'type':'integer'}},'required':['query']}},
      {'name':'read_file','description':'Đọc TXT MD CSV JSON LOG PY JS HTML CSS PDF DOCX XLSX.','parameters':{'type':'object','properties':{'path':{'type':'string'}},'required':['path']}},
      {'name':'browser_goto','description':'Mở URL trong browser automation và đọc trang.','parameters':{'type':'object','properties':{'url':{'type':'string'}},'required':['url']}},
      {'name':'browser_snapshot','description':'Đọc trang web hiện tại.','parameters':{'type':'object','properties':{}}},
      {'name':'browser_fill','description':'Điền trường web theo text/label/placeholder hoặc CSS selector.','parameters':{'type':'object','properties':{'target':{'type':'string'},'value':{'type':'string'}},'required':['target','value']}},
      {'name':'browser_click','description':'Click nút/element theo text, role, label, placeholder hoặc CSS selector.','parameters':{'type':'object','properties':{'target':{'type':'string'}},'required':['target']}},
      {'name':'remember','description':'Lưu memory local khi người dùng yêu cầu ghi nhớ.','parameters':{'type':'object','properties':{'key':{'type':'string'},'value':{'type':'string'}},'required':['key','value']}}
    ]

class GeminiAgent:
    def __init__(self):
        if not GEMINI_API_KEY: raise RuntimeError('Thiếu GEMINI_API_KEY trong .env')
        self.client=genai.Client(api_key=GEMINI_API_KEY,http_options={'api_version':'v1'})
        self.memory=Memory()
    def _contents(self,user_text):
        contents=[]
        history=self.memory.recent_messages(14)
        for role,text in history[:-1]: contents.append(types.Content(role=role,parts=[types.Part(text=text)]))
        memories='\n'.join(f'- {k}: {v}' for k,v in self.memory.get_memories(30))
        contents.append(types.Content(role='user',parts=[types.Part(text=f'LOCAL MEMORY:\n{memories or "(trống)"}\n\nCURRENT REQUEST:\n{user_text}')]))
        return contents
    def run(self,user_text):
        self.memory.add_message('user',user_text); contents=self._contents(user_text)
        for _ in range(10):
            response=self.client.models.generate_content(model=GEMINI_MODEL,contents=contents,config=types.GenerateContentConfig(system_instruction=SYSTEM,tools=[types.Tool(function_declarations=declarations())]))
            candidate=response.candidates[0].content; contents.append(candidate)
            calls=[p.function_call for p in candidate.parts if p.function_call]
            if not calls:
                answer=response.text or 'Tôi chưa có câu trả lời.'; self.memory.add_message('model',answer); return {'answer':answer}
            response_parts=[]; pending=None
            for call in calls:
                name=call.name; args=dict(call.args or {})
                if name=='remember': self.memory.set_memory(args['key'],args['value']); result={'ok':True,'message':'Đã lưu memory local.'}
                elif requires_confirmation(name,args):
                    token=manager.create(name,args); result={'ok':False,'needs_confirmation':True,'confirmation_token':token,'message':'Thao tác này cần bạn xác nhận trước khi thực hiện.'}; pending=result
                else:
                    try: result=FUNCTIONS[name](**args)
                    except Exception as exc: result={'ok':False,'error':str(exc)}
                response_parts.append(types.Part.from_function_response(name=name,response={'result':result}))
            contents.append(types.Content(role='user',parts=response_parts))
            if pending: return {'answer':pending['message'],'confirmation_token':pending['confirmation_token']}
        return {'answer':'Agent đã đạt giới hạn số bước tool.'}
    def execute_confirmation(self,token):
        pending=manager.pop(token)
        if not pending:return {'ok':False,'message':'Confirmation token không tồn tại hoặc đã dùng.'}
        try:return {'ok':True,'result':FUNCTIONS[pending['action']](**pending['details'])}
        except Exception as exc:return {'ok':False,'error':str(exc)}
    def clear_memory(self): self.memory.clear_messages()
