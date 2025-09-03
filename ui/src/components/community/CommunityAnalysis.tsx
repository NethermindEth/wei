'use client';

import React, { useState, useEffect } from 'react';
import { 
  DeepResearchApiResponse, 
  GroupedResources, 
  DiscussionResource 
} from '@/types/deepresearch';
import { 
  performDeepResearch, 
  getCachedDeepResearch, 
  refreshCommunityAnalysis,
  groupResourcesByType,
  getQualityColor,
  getResourceTypeIcon
} from '@/services/community';
import { ArrowTopRightOnSquareIcon, ClockIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface CommunityAnalysisProps {
  topic: string;
  variant?: 'protocol' | 'proposal';
}

export function CommunityAnalysis({ topic, variant = 'protocol' }: CommunityAnalysisProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DeepResearchApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Automatically trigger analysis when topic changes
  useEffect(() => {
    if (topic && topic.trim()) {
      analyzeCommunity(topic.trim());
    }
  }, [topic]);

  const analyzeCommunity = async (searchTopic: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // First try to get cached results
      const cachedResult = await getCachedDeepResearch(searchTopic);
      if (cachedResult) {
        setResult(cachedResult);
        setIsLoading(false);
        return;
      }

      // If no cache, perform fresh research
      const freshResult = await performDeepResearch(searchTopic);
      setResult(freshResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze community discourse');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!topic.trim()) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const freshResult = await refreshCommunityAnalysis(topic.trim());
      setResult(freshResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const groupedResources: GroupedResources = result ? groupResourcesByType(result.resources) : {};
  const typeCount = Object.keys(groupedResources).length;
  const totalResources = result ? result.resources.length : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h3 className="text-xl font-semibold text-white/90">
            {variant === 'proposal' ? 'Discussion Centers' : 'Community Discourse'}
          </h3>
          <p className="text-white/60">
            {variant === 'proposal' 
              ? 'Major discussion platforms and communities around this proposal topic'
              : 'Key platforms and communities where discourse around this protocol happens'
            }
          </p>
        </div>
        
        {result && !isLoading && (
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white bg-white/5 hover:bg-white/10 rounded-lg transition-colors"
          >
            <ArrowPathIcon className="w-4 h-4" />
            Refresh
          </button>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-8">
          <div className="inline-flex items-center gap-3 text-white/70">
            <div className="w-5 h-5 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
            <span>Analyzing community discourse...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && !isLoading && (
        <div className="space-y-6">
          {/* Results Summary */}
          <div className="flex items-center gap-4 text-sm text-white/60">
            <span>{totalResources} resources found</span>
            <span>•</span>
            <span>{typeCount} categories</span>
            {result.from_cache && (
              <>
                <span>•</span>
                <div className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  <span>Cached result</span>
                </div>
              </>
            )}
          </div>

          {/* Resource Groups */}
          {totalResources > 0 ? (
            <div className="grid gap-4">
              {Object.entries(groupedResources).map(([type, resources]) => (
                <ResourceGroup
                  key={type}
                  type={type}
                  resources={resources}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-white/60">
              <p>No discussion centers found for this topic.</p>
            </div>
          )}

          {/* Footer */}
          <div className="text-center text-xs text-white/40 pt-4 border-t border-white/10">
            <p>
              Last updated: {new Date(result.created_at).toLocaleString()} • 
              Expires: {new Date(result.expires_at).toLocaleString()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

interface ResourceGroupProps {
  type: string;
  resources: DiscussionResource[];
}

function ResourceGroup({ type, resources }: ResourceGroupProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const icon = getResourceTypeIcon(type);

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg overflow-hidden">
      {/* Group Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{icon}</span>
          <h4 className="font-medium text-white/90">{type}</h4>
          <span className="text-xs text-white/50 bg-white/10 px-2 py-1 rounded-full">
            {resources.length}
          </span>
        </div>
        <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
          <svg className="w-4 h-4 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Group Content */}
      {isExpanded && (
        <div className="border-t border-white/10">
          {resources.map((resource, index) => (
            <ResourceCard key={index} resource={resource} />
          ))}
        </div>
      )}
    </div>
  );
}

interface ResourceCardProps {
  resource: DiscussionResource;
}

function ResourceCard({ resource }: ResourceCardProps) {
  const qualityColor = getQualityColor(resource.quality_of_discourse);

  return (
    <div className="p-4 border-b border-white/10 last:border-b-0 hover:bg-white/5 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <h5 className="font-medium text-white/90">{resource.name}</h5>
            <a
              href={resource.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              <ArrowTopRightOnSquareIcon className="w-4 h-4" />
            </a>
          </div>
          
          <p className="text-white/70 text-sm leading-relaxed">
            {resource.description}
          </p>
          
          <div className="flex items-center gap-4 text-xs">
            <span className={`${qualityColor} font-medium`}>
              {resource.quality_of_discourse}
            </span>
            <span className="text-white/40">•</span>
            <span className="text-white/40">{resource.type}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
