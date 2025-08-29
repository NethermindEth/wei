import { useState, useEffect, useCallback } from 'react';
import { apolloClient } from '../services/graphql';
import { ProposalsQuery, GetProposalsBySpaceId } from '../queries/proposals.gql';

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
  refetch: () => void;
}

export function useProposals(initialPageSize = 20, spaceId?: string): UseProposalsResult {
  const [pageSize] = useState(initialPageSize);
  const [skip, setSkip] = useState(0);
  const [allProposals, setAllProposals] = useState<Proposal[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchProposals = useCallback(async (resetData = true) => {
    setLoading(true);
    try {
      const currentSkip = resetData ? 0 : skip;
      const query = spaceId ? GetProposalsBySpaceId : ProposalsQuery;
      const variables = spaceId 
        ? { space: spaceId, first: pageSize, skip: currentSkip }
        : { first: pageSize, skip: currentSkip, orderDirection: 'desc' };

      const result = await apolloClient.query<ProposalsData>({
        query,
        variables,
        fetchPolicy: 'network-only'
      });

      if (result.data?.proposals) {
        if (resetData) {
          setAllProposals(result.data.proposals);
          setSkip(0);
        } else {
          setAllProposals(prev => {
            // Create a map for O(1) lookup and ensure uniqueness
            const proposalMap = new Map(prev.map(p => [p.id, p]));
            result.data.proposals.forEach(p => {
              if (!proposalMap.has(p.id)) {
                proposalMap.set(p.id, p);
              }
            });
            return Array.from(proposalMap.values());
          });
        }
        setHasMore(result.data.proposals.length === pageSize);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch proposals'));
    } finally {
      setLoading(false);
    }
  }, [spaceId, pageSize, skip]);

  useEffect(() => {
    fetchProposals(true);
  }, [fetchProposals]);

  const loadMore = async () => {
    if (loading || !hasMore) return;
    
    setSkip(prev => prev + pageSize);
    await fetchProposals(false);
  };

  const refetch = () => {
    fetchProposals(true);
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
