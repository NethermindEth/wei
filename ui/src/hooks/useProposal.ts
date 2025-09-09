import { useState, useEffect, useCallback } from 'react';
import { apolloClient } from '../services/graphql';
import { GetProposalByIdQuery } from '../queries/proposal.gql';
import { Proposal } from './useProposals';

interface ProposalData {
  proposal: Proposal;
}

interface UseProposalResult {
  proposal: Proposal | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useProposal(proposalId: string): UseProposalResult {
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchProposal = useCallback(async () => {
    if (!proposalId) return;
    
    setLoading(true);
    try {
      const result = await apolloClient.query<ProposalData>({
        query: GetProposalByIdQuery,
        variables: { id: proposalId },
        fetchPolicy: 'network-only' // Always fetch from network to ensure we have the latest data
      });

      if (result.data?.proposal) {
        setProposal(result.data.proposal);
      } else {
        // If the query succeeds but no proposal is found
        setError(new Error(`Proposal with ID "${proposalId}" not found`));
      }
    } catch (err) {
      console.error('Failed to fetch proposal:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch proposal'));
    } finally {
      setLoading(false);
    }
  }, [proposalId]);

  useEffect(() => {
    fetchProposal();
  }, [proposalId, fetchProposal]);

  const refetch = () => {
    fetchProposal();
  };

  return {
    proposal,
    loading,
    error,
    refetch
  };
}
