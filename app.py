from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from online.major import EduQASystem
from pydantic import BaseModel

class Query(BaseModel):
    query: str
    session_id: str

app = FastAPI()
Edu = EduQASystem()
# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

@app.post("/chat")
def stream_text(query: Query):
    # 确保返回的是流式生成器
    return StreamingResponse(
        Edu.get_answer(query.query, query.session_id),
        media_type="text/plain"
    )
@app.get("/new_session")
def new_session():
    return Edu.new_session()

@app.get("/switch_session")
def switch_session(session_id: str):
    return Edu.switch_session(session_id)

@app.post("/clear_session")
def clear_session(session_id: str):
    return Edu.clear_session(session_id)




if __name__ == "__main__":
    import uvicorn
    # /docs打开前端
    uvicorn.run(app, host="0.0.0.0", port=8000)