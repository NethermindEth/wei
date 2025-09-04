import { useState, useEffect } from 'react';
import { apolloClient } from '../services/graphql';
import { ProposalsQuery, AllProposalsQuery } from '../queries/proposals.gql';

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

export function useProposals(initialPageSize = 20, spaceId: string | null = null): UseProposalsResult {
  const [pageSize] = useState(initialPageSize);
  const [skip, setSkip] = useState(0);
  const [allProposals, setAllProposals] = useState<Proposal[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchProposals = async () => {
      setLoading(true);
      try {
        const query = spaceId ? ProposalsQuery : AllProposalsQuery;
        const variables = spaceId 
          ? { first: pageSize, skip: 0, space: spaceId }
          : { first: pageSize, skip: 0 };
          
        const result = await apolloClient.query<ProposalsData>({
          query,
          variables
        });

        if (result.data?.proposals) {
          setAllProposals(result.data.proposals);
          setHasMore(result.data.proposals.length === pageSize);
        }
        setError(null);
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
        
        setAllProposals(prev => [...prev, ...newProposals]);
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