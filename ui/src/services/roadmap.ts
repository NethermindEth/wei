import { getApiUrl, getApiHeaders } from '@/config/api';
import { RoadmapRequest, RoadmapResponse } from '@/types/roadmap';
import { CacheService } from './cache';

/**
 * Generate a roadmap for a given subject/protocol
 */
export async function generateRoadmap(request: RoadmapRequest): Promise<RoadmapResponse> {
  const response = await fetch(getApiUrl('/roadmap'), {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Roadmap generation failed: ${response.status} ${response.statusText}`);
  }

  const apiResponse = await response.json();
  // Extract the roadmap response from the API wrapper
  return apiResponse.result.response;
}

/**
 * Get cached roadmap results (deprecated - use getRoadmap instead)
 * The POST endpoint handles caching automatically
 */
export async function getCachedRoadmap(request: RoadmapRequest): Promise<RoadmapResponse | null> {
  // This function is deprecated - the POST endpoint handles caching automatically
  // Just call getRoadmap instead
  try {
    return await getRoadmap(request);
  } catch (error) {
    console.warn('Failed to get roadmap:', error);
    return null;
  }
}

/**
 * Refresh the cache for roadmap generation and get fresh results
 */
export async function refreshRoadmap(request: RoadmapRequest): Promise<RoadmapResponse> {
  const query = CacheService.createRoadmapQuery(request);
  
  // Refresh the cache first
  await CacheService.refreshCache(query);
  
  // Then get the fresh result
  return generateRoadmap(request);
}

/**
 * Get roadmap with caching - the POST endpoint handles caching automatically
 */
export async function getRoadmap(request: RoadmapRequest): Promise<RoadmapResponse> {
  // The POST endpoint already handles caching, so we just call it directly
  return generateRoadmap(request);
}
