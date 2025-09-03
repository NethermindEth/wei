import { getApiUrl, getApiHeaders } from '@/config/api';
import { CacheService } from './cache';

// Types for related proposals
export interface RelatedProposal {
  url: string;
  title: string;
  summary?: string;
  published_date?: string;
  relevance_score?: number;
  source: string;
}

export interface RelatedProposalsResponse {
  related_proposals: RelatedProposal[];
  query: string;
  from_cache: boolean;
  cache_key: string;
}

/**
 * Search for related proposals using Exa service
 */
export async function searchRelatedProposals(
  query: string, 
  limit: number = 5
): Promise<RelatedProposalsResponse> {
  const url = getApiUrl(`/related-proposals?query=${encodeURIComponent(query)}&limit=${limit}`);
  
  const response = await fetch(url, {
    method: 'GET',
    headers: getApiHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.message || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get cached related proposals results
 */
export async function getCachedRelatedProposals(
  query: string, 
  limit: number = 5
): Promise<RelatedProposalsResponse | null> {
  try {
    const cachedQueries = await CacheService.listCachedQueries();
    
    // Look for matching query in cache
    const matchingQuery = cachedQueries.find(cached => 
      cached.endpoint === 'related-proposals' && 
      cached.query_params.query === query &&
      cached.query_params.limit === limit.toString()
    );
    
    if (matchingQuery) {
      // Found in cache, fetch directly using the same parameters
      return await searchRelatedProposals(query, limit);
    }
    
    return null;
  } catch (error) {
    console.warn('Failed to check cache for related proposals:', error);
    return null;
  }
}

/**
 * Refresh (invalidate and recompute) related proposals search
 */
export async function refreshRelatedProposals(
  query: string, 
  limit: number = 5
): Promise<RelatedProposalsResponse> {
  const cacheQuery = {
    endpoint: 'related-proposals',
    method: 'GET',
    query_params: {
      query: query,
      limit: limit.toString(),
    },
  };
  
  // Refresh the cache first
  await CacheService.refreshCache(cacheQuery);
  
  // Then get the fresh result
  return searchRelatedProposals(query, limit);
}
