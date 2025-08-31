"use client";

import React, { useEffect, useRef, useState } from 'react';
import { useProposals } from '../../hooks/useProposals';
import { Proposal } from '../../types/graphql';
import { useSpaces } from '../../hooks/useSpaces';
import { Space } from '../../types/graphql';
import { ProposalCard } from './proposal-card';
import { SpaceDropdown } from '../ui/space-dropdown';

interface ProposalListProps {
  onSelectProposal: (proposal: Proposal) => void;
  selectedProposalId?: string;
}

export function ProposalList({ onSelectProposal, selectedProposalId }: ProposalListProps) {
  const [selectedSpace, setSelectedSpace] = useState<Space | null>(null);
  const [isChangingSpace, setIsChangingSpace] = useState(false);
  const { spaces, loading: spacesLoading } = useSpaces();
  const { proposals, loading, error, loadMore, hasMore } = useProposals(20, selectedSpace?.id);
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

  // Reset changing state when loading completes
  useEffect(() => {
    if (!loading && isChangingSpace) {
      setIsChangingSpace(false);
    }
  }, [loading, isChangingSpace]);

  const handleSpaceSelect = (space: Space | null) => {
    setIsChangingSpace(true);
    setSelectedSpace(space);
  };

  if (error) {
    return (
      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <p className="text-red-400">Error loading proposals: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="grid gap-3 h-full overflow-hidden grid-rows-[auto_auto_1fr] w-[500px] min-w-[500px] max-w-[500px]">
      <h2 className="text-lg font-medium text-white/90 break-words">Select a Proposal</h2>
      
      {/* Space/Project Filter */}
      <div className="w-[500px] min-w-[500px] max-w-[500px]">
        <SpaceDropdown
          spaces={spaces}
          selectedSpace={selectedSpace}
          onSpaceSelect={handleSpaceSelect}
          loading={spacesLoading}
          placeholder="All Projects"
        />
      </div>
      
      {/* Fixed height container to prevent layout shifts */}
      <div 
        className="flex-1 overflow-hidden w-full min-w-full max-w-full box-border min-h-0 h-full"
      >
        {proposals.length === 0 && (loading || isChangingSpace) ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-[#9fb5cc]">
              {isChangingSpace ? 'Filtering proposals...' : 'Loading proposals...'}
            </p>
          </div>
        ) : proposals.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-[#9fb5cc]">
              {selectedSpace ? `No proposals found in ${selectedSpace.name}.` : 'No proposals found.'}
            </p>
          </div>
        ) : (
          <div 
            className="h-full overflow-y-auto overflow-x-hidden pr-2 w-[500px] min-w-[500px] max-w-[500px]"
          >
            <div 
              className="grid gap-4 grid-cols-1 auto-rows-[140px] w-[480px] min-w-[480px] max-w-[480px] box-border table-fixed flex-shrink-0"
            >
              {proposals.map(proposal => (
                <ProposalCard
                  key={proposal.id}
                  proposal={proposal}
                  onClick={onSelectProposal}
                  isSelected={proposal.id === selectedProposalId}
                />
              ))}
            </div>
            
            <div ref={loadMoreRef} className="py-2 text-center">
              {loading && hasMore && (
                <p className="text-sm text-[#9fb5cc]">Loading more proposals...</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
