export const API_CONFIG = {
  // Backend API base URL - adjust this based on your development setup
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // API key for authentication
  API_KEY: process.env.NEXT_PUBLIC_API_KEY || 'key1222',
  
  // API endpoints
  ENDPOINTS: {
    ANALYZE: '/analyze',
  },
} as const;

/**
 * Get the full API URL for a given endpoint
 */
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

/**
 * Get headers for API requests including authentication
 */
export const getApiHeaders = (): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add API key if available
  if (API_CONFIG.API_KEY) {
    headers['x-api-key'] = API_CONFIG.API_KEY;
  }
  return headers;
};
