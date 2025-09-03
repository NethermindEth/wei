import { getApiUrl, getApiHeaders } from '../config/api';

export interface User {
  id: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

export interface RegisterResponse {
  user: User;
  message: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export class AuthService {
  private static readonly TOKEN_KEY = 'wei_access_token';
  private static readonly REFRESH_TOKEN_KEY = 'wei_refresh_token';
  private static readonly USER_KEY = 'wei_user';

  /**
   * Make authenticated API request
   */
  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = getApiUrl(endpoint);
    const token = this.getAccessToken();
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(getApiHeaders() as Record<string, string>),
    };

    // Add JWT token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        headers: {
          ...headers,
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Auth API request error:', error);
      throw error;
    }
  }

  /**
   * Register a new user
   */
  static async register(data: RegisterRequest): Promise<RegisterResponse> {
    return this.makeRequest<RegisterResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * Login user
   */
  static async login(data: LoginRequest): Promise<LoginResponse & { user: User }> {
    const response = await this.makeRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Store tokens
    this.setTokens(response.access_token, response.refresh_token);

    // Fetch user profile
    const user = await this.getCurrentUserProfile();
    this.setUser(user);

    return { ...response, user };
  }

  /**
   * Get current user profile
   */
  static async getCurrentUserProfile(): Promise<User> {
    return this.makeRequest<User>('/auth/me', {
      method: 'GET',
    });
  }

  /**
   * Refresh access token
   */
  static async refreshToken(): Promise<RefreshTokenResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.makeRequest<RefreshTokenResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    // Update stored tokens
    this.setTokens(response.access_token, response.refresh_token);

    return response;
  }

  /**
   * Logout user
   */
  static logout(): void {
    this.clearTokens();
    this.clearUser();
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    const token = this.getAccessToken();
    
    if (!token) return false;

    // Check if token is expired
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch {
      return false;
    }
  }

  /**
   * Get current user
   */
  static getCurrentUser(): User | null {
    try {
      const userStr = localStorage.getItem(this.USER_KEY);
      if (!userStr || userStr === 'undefined' || userStr === 'null') {
        return null;
      }
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Get access token
   */
  static getAccessToken(): string | null {
    const token = localStorage.getItem(this.TOKEN_KEY);
    return token && token !== 'undefined' && token !== 'null' ? token : null;
  }

  /**
   * Get refresh token
   */
  static getRefreshToken(): string | null {
    const token = localStorage.getItem(this.REFRESH_TOKEN_KEY);
    return token && token !== 'undefined' && token !== 'null' ? token : null;
  }

  /**
   * Set tokens in localStorage
   */
  private static setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  /**
   * Set user data in localStorage
   */
  private static setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  /**
   * Clear tokens from localStorage
   */
  private static clearTokens(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * Clear user data from localStorage
   */
  private static clearUser(): void {
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * Clear any invalid data from localStorage
   */
  static clearInvalidData(): void {
    try {
      const userStr = localStorage.getItem(this.USER_KEY);
      if (userStr === 'undefined' || userStr === 'null') {
        localStorage.removeItem(this.USER_KEY);
      }
      
      const accessToken = localStorage.getItem(this.TOKEN_KEY);
      if (accessToken === 'undefined' || accessToken === 'null') {
        localStorage.removeItem(this.TOKEN_KEY);
      }
      
      const refreshToken = localStorage.getItem(this.REFRESH_TOKEN_KEY);
      if (refreshToken === 'undefined' || refreshToken === 'null') {
        localStorage.removeItem(this.REFRESH_TOKEN_KEY);
      }
    } catch (error) {
      console.warn('Error clearing invalid data:', error);
    }
  }
}
