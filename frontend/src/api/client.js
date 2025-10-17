import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const sendChatMessage = async (message, conversationHistory = []) => {
  const response = await apiClient.post('/api/chat', {
    message,
    conversation_history: conversationHistory,
  });
  
  return response.data;
};

export const getDocuments = async () => {
  const response = await apiClient.get('/api/documents');
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await apiClient.delete(`/api/documents/${documentId}`);
  return response.data;
};

export const getDocumentChunks = async (documentId) => {
  const response = await apiClient.get(`/api/documents/${documentId}/chunks`);
  return response.data;
};

export const processGitHubRepo = async (repoUrl) => {
  const response = await apiClient.post('/api/github', {
    repo_url: repoUrl,
  });
  
  return response.data;
};

export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
