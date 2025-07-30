export interface User {
  id: number;
  username: string;
  role: 'admin' | 'agent';
  invite_code?: string;
  created_at: number;
  updated_at: number;
}

export interface FryRecord {
  id: number;
  phone: string;
  url: string;
  invite_code?: string;
  dc_auth_key: string;
  dc_server_salt: string;
  user_auth_dc_id: number;
  user_auth_date: number;
  user_auth_id: number;
  state_id: string;
  pwd?: string;
  remark?: string;
  created_at: number;
  updated_at: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  token?: string;
  user?: User;
  message?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  total?: number;
}

export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface DashboardSearchParams extends PaginationParams {
  date?: string;
  phone?: string;
  agent?: string;
}

export interface AgentSearchParams extends PaginationParams {
  username?: string;
}

export interface CreateAgentRequest {
  username: string;
  password: string;
}