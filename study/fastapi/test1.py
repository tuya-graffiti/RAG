from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time

# 创建 FastAPI 实例
app = FastAPI()

# 配置跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# 极简示例
# ------------------------------
@app.get("/")
def hello():
    return {"Hello": "World"}

# ------------------------------
# GET 方法接参示例
# ------------------------------
# 方法1：路径参数
@app.get("/api/hello/{name}")
def hello_name(name: str):
    return {"Hello": name}

# 方法2：查询参数
@app.get("/api/hello2")
def hello_query(name: str):
    return {"Hello": name}

# ------------------------------
# POST 方法传参示例（使用 Pydantic）
# ------------------------------
class Query(BaseModel):
    query: str
    session_id: str

@app.post("/chat")
def chat(query: Query):
    return {
        "query": query.query,
        "session_id": query.session_id
    }

# ------------------------------
# 流式输出示例
# ------------------------------
def generate_text():
    for i in range(5):
        time.sleep(1)
        yield f"This is line {i}\n"

@app.get("/stream")
def stream_text():
    return StreamingResponse(
        generate_text(),
        media_type="text/plain"
    )

# ------------------------------
# 启动服务
# ------------------------------
if __name__ == "__main__":
    # """
    # Uvicorn 的核心作用
    # 1. 网络通信
    # 监听端口（如 8000）
    # 接收 HTTP 请求
    # 发送 HTTP 响应
    # 2. 协议处理
    # 解析 HTTP 请求
    # 构建 HTTP 响应
    # 处理 WebSocket 等
    # 3. 进程管理
    # 处理多请求并发
    # 管理 worker 进程
    # 负载均衡
    # """
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
