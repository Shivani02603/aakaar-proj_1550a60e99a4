import axios, { AxiosInstance } from 'axios';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

// Request interceptor to add Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// TypeScript interfaces for request and response types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
}

export interface RegisterResponse {
  message: string;
}

export interface DocumentUploadResponse {
  documentId: string;
}

export interface ProcessDocumentResponse {
  status: string;
}

export interface ListDocumentsResponse {
  documents: Array<{
    id: string;
    name: string;
    status: string;
  }>;
}

export interface AIQueryRequest {
  query: string;
}

export interface AIQueryResponse {
  answer: string;
}

export interface IngestDocumentsRequest {
  documentIds: string[];
}

export interface IngestDocumentsResponse {
  status: string;
}

export interface ListChatSessionsResponse {
  sessions: Array<{
    id: string;
    name: string;
    createdAt: string;
  }>;
}

export interface GetChatMessagesResponse {
  messages: Array<{
    id: string;
    sender: string;
    content: string;
    timestamp: string;
  }>;
}

export interface CreateChatSessionRequest {
  name: string;
}

export interface CreateChatSessionResponse {
  sessionId: string;
}

export interface StreamQueryResponse {
  data: string;
}

// API route functions
export const login = (data: LoginRequest) => api.post<LoginResponse>('/api/auth/login', data);

export const register = (data: RegisterRequest) => api.post<RegisterResponse>('/api/auth/register', data);

export const uploadDocument = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<DocumentUploadResponse>('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const processDocument = (documentId: string) =>
  api.post<ProcessDocumentResponse>(`/api/documents/${documentId}/process`);

export const listDocuments = () => api.get<ListDocumentsResponse>('/api/documents');

export const aiQuery = (data: AIQueryRequest) => api.post<AIQueryResponse>('/api/ai/query', data);

export const ingestDocuments = (data: IngestDocumentsRequest) =>
  api.post<IngestDocumentsResponse>('/api/ai/ingest', data);

export const listChatSessions = () => api.get<ListChatSessionsResponse>('/api/chat/sessions');

export const getChatMessages = (sessionId: string) =>
  api.get<GetChatMessagesResponse>(`/api/chat/sessions/${sessionId}/messages`);

export const createChatSession = (data: CreateChatSessionRequest) =>
  api.post<CreateChatSessionResponse>('/api/chat/sessions', data);

export const streamQueryResponse = (queryId: string) =>
  api.get<StreamQueryResponse>(`/api/stream/query/${queryId}`);

export default api;