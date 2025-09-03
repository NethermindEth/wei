import { API_CONFIG, getApiUrl, getApiHeaders } from '@/config/api';
import { 
  DeepResearchRequest, 
  DeepResearchApiResponse,
  GroupedResources,
  DiscussionResource 
} from '@/types/deepresearch';
import { CacheService } from './cache';

/**
 * Perform deep research on a protocol/community/topic
 */
export async function performDeepResearch(topic: string): Promise<DeepResearchApiResponse> {
  const request: DeepResearchRequest = { topic };
  
  const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.COMMUNITY), {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Deep research failed: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get cached deep research results
 */
export async function getCachedDeepResearch(topic: string): Promise<DeepResearchApiResponse | null> {
  const url = new URL(getApiUrl(API_CONFIG.ENDPOINTS.COMMUNITY));
  url.searchParams.set('topic', topic);
  
  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: getApiHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to get cached research: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  return result || null;
}

/**
 * Group resources by type for better organization
 */
export function groupResourcesByType(resources: DiscussionResource[]): GroupedResources {
  const grouped: GroupedResources = {};
  
  resources.forEach(resource => {
    const normalizedType = normalizeResourceType(resource.type);
    if (!grouped[normalizedType]) {
      grouped[normalizedType] = [];
    }
    grouped[normalizedType].push(resource);
  });
  
  // Sort each group by name
  Object.keys(grouped).forEach(type => {
    grouped[type].sort((a, b) => a.name.localeCompare(b.name));
  });
  
  return grouped;
}

/**
 * Normalize resource type for consistent grouping
 */
function normalizeResourceType(type: string): string {
  const normalized = type.toLowerCase().trim();
  
  // Map various type names to consistent categories
  const typeMapping: { [key: string]: string } = {
    'docs': 'Documentation',
    'documentation': 'Documentation',
    'whitepaper': 'Documentation',
    'spec': 'Documentation',
    'specs': 'Documentation',
    'forum': 'Forum',
    'governance': 'Forum',
    'discord': 'Discord',
    'telegram': 'Telegram',
    'github': 'GitHub',
    'gitlab': 'GitHub',
    'newsletter': 'Newsletter',
    'blog': 'Blog',
    'conference': 'Conference',
    'meetup': 'Meetup',
    'reddit': 'Reddit',
    'podcast': 'Podcast',
    'youtube': 'YouTube',
    'twitter': 'Twitter',
    'academic': 'Academic',
    'paper': 'Academic',
    'research': 'Academic',
  };
  
  return typeMapping[normalized] || capitalizeFirst(type);
}

/**
 * Capitalize first letter of a string
 */
function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Get the quality color based on discourse quality assessment
 */
export function getQualityColor(quality: string): string {
  const lower = quality.toLowerCase();
  
  if (lower.includes('highly technical') || lower.includes('deep') || lower.includes('expert')) {
    return 'text-emerald-400';
  } else if (lower.includes('technical') || lower.includes('developer')) {
    return 'text-blue-400';
  } else if (lower.includes('governance') || lower.includes('proposal')) {
    return 'text-purple-400';
  } else if (lower.includes('casual') || lower.includes('general')) {
    return 'text-yellow-400';
  } else if (lower.includes('announcement') || lower.includes('news')) {
    return 'text-gray-400';
  } else {
    return 'text-white/80';
  }
}

/**
 * Get icon for resource type
 */
export function getResourceTypeIcon(type: string): string {
  const normalized = normalizeResourceType(type).toLowerCase();
  
  const iconMapping: { [key: string]: string } = {
    'documentation': '📚',
    'forum': '💬',
    'discord': '🎮',
    'telegram': '✈️',
    'github': '🐙',
    'newsletter': '📧',
    'blog': '✍️',
    'conference': '🎤',
    'meetup': '🤝',
    'reddit': '🔴',
    'podcast': '🎧',
    'youtube': '📺',
    'twitter': '🐦',
    'academic': '🎓',
  };
  
  return iconMapping[normalized] || '🔗';
}

/**
 * Refresh the cache for community analysis and get fresh results
 */
export async function refreshCommunityAnalysis(topic: string): Promise<DeepResearchApiResponse> {
  const query = CacheService.createCommunityAnalysisQuery(topic, 'POST');
  
  // Refresh the cache first
  await CacheService.refreshCache(query);
  
  // Then get the fresh result
  return performDeepResearch(topic);
}
