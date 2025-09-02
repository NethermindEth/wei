// Deep research types matching the backend models

export interface DeepResearchRequest {
  topic: string;
}

export interface DiscussionResource {
  name: string;
  link: string;
  type: string;
  description: string;
  quality_of_discourse: string;
}

export interface DeepResearchResponse {
  topic: string;
  resources: DiscussionResource[];
}

export interface DeepResearchApiResponse {
  topic: string;
  resources: DiscussionResource[];
  from_cache: boolean;
  created_at: string;
  expires_at: string;
}

// Grouped resources by type for better organization
export interface GroupedResources {
  [resourceType: string]: DiscussionResource[];
}

// Resource type categories for grouping
export const RESOURCE_TYPE_CATEGORIES = [
  'Documentation',
  'Forum',
  'Discord',
  'Telegram',
  'GitHub',
  'Newsletter',
  'Conference',
  'Meetup',
  'Reddit',
  'Blog',
  'Podcast',
  'YouTube',
  'Twitter',
  'Academic',
  'Other'
] as const;

export type ResourceTypeCategory = typeof RESOURCE_TYPE_CATEGORIES[number];
