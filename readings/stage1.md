stage1: 最小化可执行system
![lc_003](E:\xun\Project\ai\项目\RAG\代码\rag_myself\readings\pic\lc_03.png)

# 服务请求处理流程

## 1. 请求接收

- 前端通过 **HTTP** 或 **WebSocket** 发送请求|参数：`query`, `source_filter`, `session_id`

- 接收 `QueryRequest` 

- 接收 JSON 格式数据

### HTTP和WebSocket接口



## 2. 问候检查

- 首先检查用户输入是否为日常问候
- 如果是问候语，直接返回模板化问候回复

## 3. 搜索处理

- 执行 **BM25 搜索**（相似度阈值=0.85）
- 判断是否找到答案

## 4. 答案可靠性判断

- 如果找到答案，检查答案是否可靠
- 答案可靠：直接返回 MySQL 中的答案
- 答案不可靠或未找到答案：进入 RAG 处理

## 5. RAG 系统调用

- 需要 RAG 时调用 RAG 系统
- **WebSocket**: 流式输出
- **HTTP**: 提示使用 WebSocket

## 6. 响应返回

- **HTTP**: 一次性 JSON 返回
- **WebSocket**: 流式 JSON 返回

## 7. 会话管理

- 更新会话历史到 MySQL 数据库

## 关键特性

- **双协议支持**: HTTP 和 WebSocket
- **智能路由**: 根据查询类型选择最佳处理路径
- **流式输出**: WebSocket 支持实时流式响应
- **会话持久化**: 所有对话历史保存到 MySQL

这个架构结合了传统检索（BM25）和现代 RAG 技术，提供了灵活的前后端交互方式。

