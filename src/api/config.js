// 后端 API 基础地址
// 开发环境下可直接指向本地 FastAPI 服务
// 如需通过反向代理，也可以把它改成 '/api'

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

