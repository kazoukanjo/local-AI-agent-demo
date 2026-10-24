from __future__ import annotations
import json, os, re, subprocess, threading, webbrowser
from pathlib import Path
from rapidfuzz import process, fuzz
from ..config import APP_CACHE_PATH

WEB_ALIASES = {
    "youtube": "https://www.youtube.com",
    "yt": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "fb": "https://www.facebook.com",
    "messenger": "https://www.messenger.com",
    "instagram": "https://www.instagram.com",
    "tiktok": "https://www.tiktok.com",
    "zalo web": "https://chat.zalo.me",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "google drive": "https://drive.google.com",
    "google docs": "https://docs.google.com",
    "google sheets": "https://sheets.google.com",
    "google ai studio": "https://aistudio.google.com",
    "chatgpt": "https://chatgpt.com",
    "github": "https://github.com",
    "discord": "https://discord.com/app",
    "spotify": "https://open.spotify.com",
    "google maps": "https://maps.google.com",
    "canva": "https://www.canva.com",
    "figma": "https://www.figma.com",
    "notion": "https://www.notion.so",
    "wikipedia": "https://www.wikipedia.org",
}

class AppLauncher:
    def __init__(self):
        self._lock=threading.Lock(); self.apps=[]; self.loaded=False

    def _roots(self):
        roots=[]
        for key in ("APPDATA","PROGRAMDATA","USERPROFILE"):
            v=os.environ.get(key)
            if v: roots.append(Path(v))
        for env in ("ProgramFiles","ProgramFiles(x86)","LOCALAPPDATA"):
            v=os.environ.get(env)
            if v: roots.append(Path(v))
        return roots

    def scan(self, force=False):
        with self._lock:
            if self.loaded and not force: return self.apps
            found=[]; seen=set()
            start_roots=[
                Path(os.environ.get("APPDATA", ""))/"Microsoft/Windows/Start Menu/Programs",
                Path(os.environ.get("PROGRAMDATA", ""))/"Microsoft/Windows/Start Menu/Programs",
                Path(os.environ.get("USERPROFILE", ""))/"Desktop",
            ]
            for root in start_roots:
                if not root.exists(): continue
                try:
                    for p in root.rglob('*'):
                        if p.suffix.lower() in {'.lnk','.url','.exe'} and str(p).lower() not in seen:
                            found.append({'name':p.stem,'path':str(p),'kind':p.suffix.lower()}); seen.add(str(p).lower())
                except (OSError, PermissionError): pass
            # Search common app directories without walking the entire disk.
            for root in self._roots():
                if not root.exists() or root.name.upper() in {'APPDATA','PROGRAMDATA'}: continue
                try:
                    for p in root.rglob('*.exe'):
                        s=str(p).lower()
                        if s in seen: continue
                        if any(part.lower() in {'node_modules','.git','windowsapps'} for part in p.parts): continue
                        found.append({'name':p.stem,'path':str(p),'kind':'.exe'}); seen.add(s)
                        if len(found)>18000: break
                except (OSError, PermissionError): pass
                if len(found)>18000: break
            self.apps=found; self.loaded=True
            try: APP_CACHE_PATH.write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf-8')
            except Exception: pass
            return found

    def _open(self, path):
        try:
            if path.lower().endswith(('.lnk','.url')): os.startfile(path)
            else: subprocess.Popen([path], shell=False)
            return True
        except Exception:
            return False

    def open(self, keyword: str):
        key=keyword.strip().lower()
        if not key: return {'ok':False,'message':'Tên ứng dụng trống.'}
        apps=self.scan()
        exact=[a for a in apps if a['name'].lower()==key]
        if exact:
            if self._open(exact[0]['path']): return {'ok':True,'message':f'Đã mở {keyword}.','path':exact[0]['path']}
        names=[a['name'] for a in apps]
        match=process.extractOne(key,names,scorer=fuzz.WRatio) if names else None
        if match and match[1]>=78:
            cand=next(a for a in apps if a['name']==match[0])
            if self._open(cand['path']): return {'ok':True,'message':f'Đã mở {cand["name"]}.','path':cand['path'],'score':match[1]}
        # PATH executable fallback
        for candidate in {key, key.replace(' ','')+'.exe', key+'.exe'}:
            try:
                subprocess.Popen([candidate], shell=False); return {'ok':True,'message':f'Đã mở {keyword}.'}
            except Exception: pass
        if key in WEB_ALIASES:
            return {'ok':False,'web_fallback':WEB_ALIASES[key],'message':f'Không tìm thấy app {keyword} trên máy. Có thể mở phiên bản web.'}
        return {'ok':False,'message':f'Không tìm thấy ứng dụng phù hợp: {keyword}'}

    def open_path(self,path:str):
        p=Path(os.path.expandvars(os.path.expanduser(path))).resolve()
        if not p.exists(): return {'ok':False,'message':'Đường dẫn không tồn tại.','path':str(p)}
        os.startfile(str(p)); return {'ok':True,'message':f'Đã mở {p}','path':str(p)}

    def open_url(self,url:str):
        if not re.match(r'^https?://',url,re.I): url='https://'+url
        webbrowser.open(url); return {'ok':True,'message':f'Đã mở {url}','url':url}

launcher=AppLauncher()

def open_app(keyword:str): return launcher.open(keyword)
def open_path(path:str): return launcher.open_path(path)
def open_url(url:str): return launcher.open_url(url)
def list_installed_apps(query:str='',limit:int=20):
    apps=launcher.scan(); q=query.strip().lower()
    if q: apps=sorted(apps,key=lambda a: fuzz.WRatio(q,a['name'].lower()),reverse=True)
    return {'ok':True,'apps':apps[:limit]}
