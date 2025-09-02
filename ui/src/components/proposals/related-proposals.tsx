"use client";

import * as React from "react";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";

interface RelatedProposal {
  url: string;
  title: string;
  summary?: string;
  published_date?: string;
  relevance_score?: number;
  source: string;
}

interface RelatedProposalsResponse {
  related_proposals: RelatedProposal[];
  query: string;
}

interface RelatedProposalsProps {
  proposalText: string;
  proposalTitle: string;
}

export function RelatedProposals({ proposalText, proposalTitle }: RelatedProposalsProps) {
  const [relatedProposals, setRelatedProposals] = React.useState<RelatedProposal[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // Extract key phrases from proposal text for better search
  const extractKeyPhrases = React.useCallback((text: string): string => {
    // Simple extraction of meaningful words (can be improved with NLP)
    const words = text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => 
        word.length > 4 && 
        !['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were', 'said', 'what', 'when', 'where', 'would', 'could', 'should'].includes(word)
      );
    
    // Take the first 10 most relevant words
    return words.slice(0, 10).join(' ');
  }, []);

  const searchRelatedProposals = React.useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Create a search query from the proposal title and key phrases from the text
      const query = `${proposalTitle} ${extractKeyPhrases(proposalText)}`.trim();
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      
      if (!apiKey) {
        throw new Error('API key not configured');
      }

      const response = await fetch(
        `${apiUrl}/related-proposals?query=${encodeURIComponent(query)}&limit=5`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: RelatedProposalsResponse = await response.json();
      setRelatedProposals(data.related_proposals);
    } catch (err) {
      console.error('Failed to fetch related proposals:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch related proposals');
    } finally {
      setLoading(false);
    }
  }, [proposalText, proposalTitle, extractKeyPhrases]);

  React.useEffect(() => {
    if (proposalText && proposalTitle) {
      searchRelatedProposals();
    }
  }, [proposalText, proposalTitle, searchRelatedProposals]);

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getDomainDisplayName = (source: string): string => {
    const domainMap: Record<string, string> = {
      'snapshot.org': 'Snapshot',
      'forum.arbitrum.foundation': 'Arbitrum Forum',
      'governance.aave.com': 'Aave Governance',
      'compound.finance': 'Compound',
      'gov.uniswap.org': 'Uniswap Governance',
      'forum.makerdao.com': 'MakerDAO Forum',
      'research.tally.xyz': 'Tally Research',
      'commonwealth.im': 'Commonwealth',
    };
    return domainMap[source] || source;
  };

  if (loading) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-6">
        <h2 className="text-lg font-semibold mb-4 text-white/90">Related Proposals</h2>
        <div className="flex items-center">
          <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mr-2"></div>
          <p className="text-white/70 text-sm">Searching for related proposals...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-6">
        <h2 className="text-lg font-semibold mb-4 text-white/90">Related Proposals</h2>
        <div className="text-red-400 text-sm">{error}</div>
      </div>
    );
  }

  if (relatedProposals.length === 0) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-6">
        <h2 className="text-lg font-semibold mb-4 text-white/90">Related Proposals</h2>
        <p className="text-white/60 text-sm">No related proposals found.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6">
      <h2 className="text-lg font-semibold mb-4 text-white/90">Related Proposals</h2>
      
      <div className="space-y-4">
        {relatedProposals.map((proposal, index) => (
          <div
            key={index}
            className="border border-white/10 rounded-lg p-4 bg-white/5 hover:bg-white/10 transition-colors"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-white/90 mb-2 line-clamp-2">
                  <a
                    href={proposal.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-[--color-accent] transition-colors"
                  >
                    {proposal.title}
                  </a>
                </h3>
                
                {proposal.summary && (
                  <p className="text-sm text-white/70 mb-2 line-clamp-3">
                    {proposal.summary}
                  </p>
                )}
                
                <div className="flex items-center gap-3 text-xs text-white/60">
                  <span className="font-medium">
                    {getDomainDisplayName(proposal.source)}
                  </span>
                  {proposal.published_date && (
                    <>
                      <span>•</span>
                      <span>{formatDate(proposal.published_date)}</span>
                    </>
                  )}
                  {proposal.relevance_score && (
                    <>
                      <span>•</span>
                      <span>Score: {proposal.relevance_score.toFixed(2)}</span>
                    </>
                  )}
                </div>
              </div>
              
              <a
                href={proposal.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-shrink-0 p-1 text-white/40 hover:text-white/80 transition-colors"
                title="Open in new tab"
              >
                <ArrowTopRightOnSquareIcon className="w-4 h-4" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
