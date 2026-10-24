"""Legacy API kept for compatibility. V4 does not open this server automatically."""
from fastapi import FastAPI
app=FastAPI(title='AI Agent của Khánh V4 Internal API')
@app.get('/health')
def health(): return {'ok':True,'service':'ai-agent-cua-khanh-v4'}
