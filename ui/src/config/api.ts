export const API_CONFIG = {
  // Backend API base URL - adjust this based on your development setup
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    ANALYZE: '/analyze',
  },
} as const;

export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
