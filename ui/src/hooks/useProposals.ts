import { useState, useEffect } from 'react';
import { apolloClient } from '../services/graphql';
import { ProposalsQuery, AllProposalsQuery } from '../queries/proposals.gql';
import { ApiService } from '../services/api';
import { ETHEREUM_SPACE_ID } from '../utils/eip-adapters';
import { ProposalSource, toUnifiedProposal } from '../types/proposal-source';

export interface Proposal {
  id: string;
  title: string;
  body: string;
  author: string;
  space?: {
    id: string;
    name: string;
    avatar?: string;
    verified?: boolean;
  };
  // Optional EIP metadata for EIP proposals
  eipData?: {
    eip_number: number;
    status: string;
    eip_type: string;
    category?: string;
    created: string;
    content?: string;
    description?: string;
  };
}

interface ProposalsData {
  proposals: Proposal[];
}

interface UseProposalsResult {
  proposals: Proposal[];
  loading: boolean;
  error: Error | null;
  loadMore: () => void;
  hasMore: boolean;
  refetch: () => void;
}

export function useProposals(initialPageSize = 5, spaceId: string | null = null): UseProposalsResult {
  const [pageSize] = useState(initialPageSize);
  const [skip, setSkip] = useState(0);
  const [allProposals, setAllProposals] = useState<Proposal[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchProposals = async () => {
      setLoading(true);
      // Clear existing proposals when space changes
      setAllProposals([]);
      
      try {
        // Special handling for Ethereum space
        if (spaceId === ETHEREUM_SPACE_ID) {
          // Fetch EIPs instead of proposals
          const eipsResponse = await ApiService.getEips({
            page: 1,
            page_size: pageSize
          });
          
          // Create proposal sources with proper type discrimination
          const eipProposalSources = eipsResponse.eips.map(eip => ({ type: 'eip', eip }) as ProposalSource);
          
          // Convert to unified proposal format
          const eipProposals = eipProposalSources.map(toUnifiedProposal);
          // EIPs loaded successfully
          
          setAllProposals(eipProposals);
          setHasMore(eipsResponse.page < eipsResponse.total_pages);
          setError(null);
        } else {
          // Normal proposal fetching for other spaces
          const query = spaceId ? ProposalsQuery : AllProposalsQuery;
          const variables = spaceId 
            ? { first: pageSize, skip: 0, space: spaceId }
            : { first: pageSize, skip: 0 };
          
          const result = await apolloClient.query<ProposalsData>({
            query,
            variables,
            fetchPolicy: 'network-only' // Force refetch when space changes
          });

          if (result.data?.proposals) {
            // For snapshot proposals, we can use them directly
          // They already match our Proposal interface
          setAllProposals(result.data.proposals);
            setHasMore(result.data.proposals.length === pageSize);
            // Proposals loaded successfully
          }
          setError(null);
        }
      } catch (err) {
        console.error('Failed to fetch proposals:', err);
        setError(err instanceof Error ? err : new Error('Failed to fetch proposals'));
      } finally {
        setLoading(false);
      }
    };

    fetchProposals();
  }, [pageSize, spaceId]);

  const loadMore = async () => {
    if (loading || !hasMore) return;
    
    const newSkip = skip + pageSize;
    setSkip(newSkip);
    setLoading(true);
    
    try {
      // Special handling for Ethereum space
      if (spaceId === ETHEREUM_SPACE_ID) {
        // Calculate page number for EIPs (1-indexed)
        const page = Math.floor(newSkip / pageSize) + 1;
        
        // Fetch next page of EIPs
        const eipsResponse = await ApiService.getEips({
          page,
          page_size: pageSize
        });
        
        // Create proposal sources with proper type discrimination
        const eipProposalSources = eipsResponse.eips.map(eip => ({ type: 'eip', eip }) as ProposalSource);
        
        // Convert to unified proposal format
        const eipProposals = eipProposalSources.map(toUnifiedProposal);
        
        // Check if we've reached the end
        if (eipsResponse.page >= eipsResponse.total_pages) {
          setHasMore(false);
        }
        
        // Append new EIP proposals
        setAllProposals(prev => [...prev, ...eipProposals]);
      } else {
        // Normal proposal loading for other spaces
        const query = spaceId ? ProposalsQuery : AllProposalsQuery;
        const variables = spaceId 
          ? { first: pageSize, skip: newSkip, space: spaceId }
          : { first: pageSize, skip: newSkip };
          
        const result = await apolloClient.query<ProposalsData>({
          query,
          variables,
          fetchPolicy: 'network-only'
        });

        if (result.data?.proposals) {
          const newProposals = result.data.proposals;
          
          if (newProposals.length < pageSize) {
            setHasMore(false);
          }
          
          // For snapshot proposals, we can use them directly
          // They already match our Proposal interface
          setAllProposals(prev => [...prev, ...newProposals]);
        }
      }
    } catch (err) {
      console.error('Failed to load more proposals:', err);
      setError(err instanceof Error ? err : new Error('Failed to load more proposals'));
    } finally {
      setLoading(false);
    }
  };

  const refetch = () => {
    setAllProposals([]);
    setSkip(0);
    setHasMore(true);
    // Trigger refetch by changing the spaceId dependency
  };

  return {
    proposals: allProposals,
    loading,
    error,
    loadMore,
    hasMore,
    refetch
  };
}