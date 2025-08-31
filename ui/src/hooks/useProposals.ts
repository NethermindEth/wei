import { useState, useEffect, useRef } from 'react';
import { apolloClient } from '../services/graphql';
import { ProposalsQuery, GetProposalsBySpaceId } from '../queries/proposals.gql';
import { Proposal, ProposalsQueryResponse } from '../types/graphql';

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

  const fetchProposalsRef = useRef<(resetData?: boolean, customSkip?: number) => Promise<void>>(null!);

  fetchProposalsRef.current = async (resetData = true, customSkip?: number) => {
    setLoading(true);
    try {
      const currentSkip = resetData ? 0 : (customSkip ?? skip);
      const query = spaceId ? GetProposalsBySpaceId : ProposalsQuery;
      const variables = spaceId 
        ? { space: spaceId, first: pageSize, skip: currentSkip }
        : { first: pageSize, skip: currentSkip, orderDirection: 'desc' };

      const result = await apolloClient.query<ProposalsQueryResponse>({
        query,
        variables,
        fetchPolicy: 'network-only'
      });

      if (result.data?.proposals !== undefined) {
        const idCounts: Record<string, number> = {};
        
        const uniqueProposals = result.data.proposals.map(p => {
          if (idCounts[p.id]) {
            idCounts[p.id]++;
            return {
              ...p,
              id: `${p.id}_${idCounts[p.id]}`
            };
          } else {
            idCounts[p.id] = 1;
            return p;
          }
        });
        
        if (resetData) {
          setAllProposals(uniqueProposals);
          setSkip(0);
        } else {
          setAllProposals(prev => {
            const proposalMap = new Map(prev.map(p => [p.id, p]));
            uniqueProposals.forEach(p => {
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
  };

  useEffect(() => {
    fetchProposalsRef.current?.(true);
  }, [spaceId]);

  const loadMore = async () => {
    if (loading || !hasMore) return;
    
    const newSkip = skip + pageSize;
    setSkip(newSkip);
    await fetchProposalsRef.current?.(false, newSkip);
  };

  const refetch = () => {
    fetchProposalsRef.current?.(true);
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
