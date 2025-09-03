import { getApiUrl, getApiHeaders } from '../config/api';

// Types for cache management
export interface CacheableQuery {
  endpoint: string;
  method: string;
  query_params: Record<string, string>;
  body?: unknown;
  user_context?: string;
}

export interface CachedQueryInfo {
  cache_key: string;
  description: string;
  endpoint: string;
  method: string;
  created_at: string;
  expires_at: string;
  query_params: Record<string, string>;
  user_context?: string;
}

export interface CacheOperationResponse {
  success: boolean;
  message: string;
  cache_key: string;
}

export interface CacheStats {
  total_entries: number;
  active_entries: number;
  expired_entries: number;
}

export class CacheService {
  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = getApiUrl(endpoint);
    
    try {
      const response = await fetch(url, {
        headers: {
          ...getApiHeaders(),
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`Cache API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Cache API request error:', error);
      throw error;
    }
  }

  /**
   * Get all cached queries
   */
  static async listCachedQueries(): Promise<CachedQueryInfo[]> {
    return this.makeRequest<CachedQueryInfo[]>('/cache');
  }

  /**
   * Invalidate a specific cached query
   */
  static async invalidateCache(query: CacheableQuery): Promise<CacheOperationResponse> {
    return this.makeRequest<CacheOperationResponse>('/cache/invalidate', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  /**
   * Refresh (invalidate and recompute) a cached query
   */
  static async refreshCache(query: CacheableQuery): Promise<CacheOperationResponse> {
    return this.makeRequest<CacheOperationResponse>('/cache/refresh', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  /**
   * Get cache statistics
   */
  static async getCacheStats(): Promise<CacheStats> {
    return this.makeRequest<CacheStats>('/cache/stats');
  }

  /**
   * Clean up expired cache entries
   */
  static async cleanupCache(): Promise<{ cleaned_entries: number; message: string }> {
    return this.makeRequest<{ cleaned_entries: number; message: string }>('/cache/cleanup', {
      method: 'POST',
    });
  }

  /**
   * Helper function to create a query for proposal analysis
   */
  static createProposalAnalysisQuery(proposalData: unknown): CacheableQuery {
    return {
      endpoint: '/pre-filter',
      method: 'POST',
      query_params: {},
      body: proposalData,
    };
  }

  /**
   * Helper function to create a query for community analysis
   */
  static createCommunityAnalysisQuery(topic: string, method: 'GET' | 'POST' = 'POST'): CacheableQuery {
    if (method === 'GET') {
      return {
        endpoint: '/community',
        method: 'GET',
        query_params: { topic },
      };
    } else {
      return {
        endpoint: '/community',
        method: 'POST',
        query_params: {},
        body: { topic },
      };
    }
  }

  /**
   * Helper function to create a query for related proposals
   */
  static createRelatedProposalsQuery(query: string, limit?: number): CacheableQuery {
    const queryParams: Record<string, string> = { query };
    if (limit) {
      queryParams.limit = limit.toString();
    }

    return {
      endpoint: '/related-proposals',
      method: 'GET',
      query_params: queryParams,
    };
  }
}
