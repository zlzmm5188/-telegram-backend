import axios from 'axios'
import type {
  LoginRequest,
  LoginResponse,
  ApiResponse,
  User,
  FryRecord,
  DashboardSearchParams,
  AgentSearchParams,
  CreateAgentRequest,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器 - 添加认证token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-storage')
  if (token) {
    const authData = JSON.parse(token)
    if (authData.state?.token) {
      config.headers.Authorization = `Bearer ${authData.state.token}`
    }
  }
  return config
})

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除认证信息
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data: LoginRequest): Promise<LoginResponse> =>
    api.post('/auth/login', data).then(res => res.data),
  
  logout: (): Promise<ApiResponse> =>
    api.post('/auth/logout').then(res => res.data),
  
  resetPassword: (data: { username: string; password: string; newPassword: string }): Promise<ApiResponse> =>
    api.post('/auth/reset-password', data).then(res => res.data),
}

export const dashboardAPI = {
  getFryRecords: (params: DashboardSearchParams): Promise<ApiResponse<FryRecord[]>> =>
    api.get('/dashboard/fry-records', { params }).then(res => res.data),
  
  updateRemark: (id: number, remark: string): Promise<ApiResponse> =>
    api.put(`/dashboard/fry-records/${id}/remark`, { remark }).then(res => res.data),
  
  deleteRecord: (id: number): Promise<ApiResponse> =>
    api.delete(`/dashboard/fry-records/${id}`).then(res => res.data),
}

export const agentAPI = {
  getAgents: (params: AgentSearchParams): Promise<ApiResponse<User[]>> =>
    api.get('/agents', { params }).then(res => res.data),
  
  createAgent: (data: CreateAgentRequest): Promise<ApiResponse<User>> =>
    api.post('/agents', data).then(res => res.data),
  
  deleteAgent: (id: number): Promise<ApiResponse> =>
    api.delete(`/agents/${id}`).then(res => res.data),
}

export const telegramAPI = {
  sendCode: (phone: string): Promise<ApiResponse> =>
    api.post('/telegram/send-code', { phone }).then(res => res.data),
  
  verify: (phone: string, code: string): Promise<ApiResponse> =>
    api.post('/telegram/verify', { phone, code }).then(res => res.data),
  
  getMe: (): Promise<ApiResponse> =>
    api.get('/telegram/me').then(res => res.data),
  
  sendMessage: (username: string, message: string): Promise<ApiResponse> =>
    api.post('/telegram/send', { username, message }).then(res => res.data),
}

export default api