"use client";

import React, { useEffect, useRef } from 'react';
import { useProposals, Proposal } from '../../hooks/useProposals';
import { ProposalCard } from './proposal-card';

interface ProposalListProps {
  onSelectProposal: (proposal: Proposal) => void;
  selectedProposalId?: string;
  spaceId?: string | null;
}

export function ProposalList({ onSelectProposal, selectedProposalId, spaceId }: ProposalListProps) {
  const { proposals, loading, error, loadMore, hasMore } = useProposals(20, spaceId);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (loading) return;
    
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        loadMore();
      }
    }, { threshold: 0.5 });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loading, hasMore, loadMore]);

  if (error) {
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <p className="text-red-400">Error loading proposals: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="grid gap-3 overflow-hidden">
      <h2 className="text-lg font-medium text-white/90 break-words">Select a Proposal</h2>
      
      {proposals.length === 0 && loading ? (
        <div className="p-4 text-center">
          <p className="text-[#9fb5cc]">Loading proposals...</p>
        </div>
      ) : proposals.length === 0 ? (
        <div className="p-4 text-center">
          <p className="text-[#9fb5cc]">No proposals found.</p>
        </div>
      ) : (
        <div className="grid gap-4 h-[400px] overflow-y-auto overflow-x-hidden pr-2" style={{ width: '100%', boxSizing: 'border-box' }}>
          {proposals.map(proposal => (
            <ProposalCard
              key={proposal.id}
              proposal={proposal}
              onClick={onSelectProposal}
              isSelected={proposal.id === selectedProposalId}
            />
          ))}
          
          <div ref={loadMoreRef} className="py-2 text-center">
            {loading && hasMore && (
              <p className="text-sm text-[#9fb5cc]">Loading more proposals...</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
