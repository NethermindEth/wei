import { useState, useEffect } from 'react';
import { apolloClient } from '../services/graphql';
import { ProposalsQuery } from '../queries/proposals.gql';

export interface Proposal {
  id: string;
  title: string;
  body: string;
  author: string;
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
}

export function useProposals(initialPageSize = 20): UseProposalsResult {
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
        const result = await apolloClient.query<ProposalsData>({
          query: ProposalsQuery,
          variables: {
            first: pageSize,
            skip: 0,
            orderDirection: 'desc'
          }
        });

        if (result.data?.proposals) {
          setAllProposals(result.data.proposals);
          setHasMore(result.data.proposals.length === pageSize);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch proposals'));
      } finally {
        setLoading(false);
      }
    };

    fetchProposals();
  }, [pageSize]);

  const loadMore = async () => {
    if (loading || !hasMore) return;
    
    const newSkip = skip + pageSize;
    setSkip(newSkip);
    setLoading(true);
    
    try {
      const result = await apolloClient.query<ProposalsData>({
        query: ProposalsQuery,
        variables: {
          first: pageSize,
          skip: newSkip,
          orderDirection: 'desc'
        },
        fetchPolicy: 'network-only' n
      });

      if (result.data?.proposals) {
        const newProposals = result.data.proposals;
        
        if (newProposals.length < pageSize) {
          setHasMore(false);
        }
        
        setAllProposals(prev => [...prev, ...newProposals]);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load more proposals'));
    } finally {
      setLoading(false);
    }
  };

  return {
    proposals: allProposals,
    loading,
    error,
    loadMore,
    hasMore
  };
}
