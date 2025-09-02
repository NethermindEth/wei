"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Proposal } from '../../hooks/useProposals';
import { Protocol } from './header';

interface SearchResult {
  type: 'proposal' | 'protocol';
  item: Proposal | Protocol;
  score: number;
}

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  proposals: Proposal[];
  protocols: Protocol[];
  onSelectProposal: (proposal: Proposal) => void;
  onSelectProtocol: (protocolId: string) => void;
}

// Simple fuzzy search implementation
function fuzzySearch(query: string, text: string): number {
  const queryLower = query.toLowerCase();
  const textLower = text.toLowerCase();
  
  if (textLower.includes(queryLower)) {
    // Exact substring match gets high score
    return 0.9;
  }
  
  // Character-by-character fuzzy matching
  let queryIndex = 0;
  let textIndex = 0;
  let matches = 0;
  
  while (queryIndex < queryLower.length && textIndex < textLower.length) {
    if (queryLower[queryIndex] === textLower[textIndex]) {
      matches++;
      queryIndex++;
    }
    textIndex++;
  }
  
  // Score based on percentage of query characters found
  const score = matches / queryLower.length;
  return score > 0.5 ? score : 0; // Threshold for relevance
}

function searchItems(
  query: string, 
  proposals: Proposal[], 
  protocols: Protocol[]
): SearchResult[] {
  if (!query.trim()) return [];
  
  const results: SearchResult[] = [];
  
  // Search protocols first (with higher priority)
  protocols.forEach(protocol => {
    const nameScore = fuzzySearch(query, protocol.name);
    if (nameScore > 0) {
      results.push({
        type: 'protocol',
        item: protocol,
        score: nameScore + 0.3 // Boost protocol scores by 0.3 to prioritize them
      });
    }
  });
  
  // Search proposals
  proposals.forEach(proposal => {
    const titleScore = fuzzySearch(query, proposal.title);
    const bodyScore = fuzzySearch(query, proposal.body) * 0.7; // Lower weight for body
    const authorScore = fuzzySearch(query, proposal.author) * 0.8;
    
    const maxScore = Math.max(titleScore, bodyScore, authorScore);
    if (maxScore > 0) {
      results.push({
        type: 'proposal',
        item: proposal,
        score: maxScore
      });
    }
  });
  
  // Sort by type (protocols first) then by score descending
  return results
    .sort((a, b) => {
      // First sort by type: protocols before proposals
      if (a.type !== b.type) {
        return a.type === 'protocol' ? -1 : 1;
      }
      // Then sort by score descending within the same type
      return b.score - a.score;
    })
    .slice(0, 10); // Limit to top 10
}

export function SearchModal({
  isOpen,
  onClose,
  proposals,
  protocols,
  onSelectProposal,
  onSelectProtocol
}: SearchModalProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsContainerRef = useRef<HTMLDivElement>(null);
  const selectedItemRef = useRef<HTMLButtonElement>(null);
  
  const results = searchItems(query, proposals, protocols);
  
  // Reset search when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      // Focus input after modal animation
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);
  
  const handleSelectResult = useCallback((result: SearchResult) => {
    if (result.type === 'proposal') {
      onSelectProposal(result.item as Proposal);
    } else {
      onSelectProtocol((result.item as Protocol).id);
    }
    onClose();
  }, [onSelectProposal, onSelectProtocol, onClose]);

  // Reset selected index when query changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);
  
  // Scroll selected item into view when selectedIndex changes
  useEffect(() => {
    if (selectedItemRef.current && resultsContainerRef.current) {
      // Use requestAnimationFrame to ensure the DOM has updated
      requestAnimationFrame(() => {
        selectedItemRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
        });
      });
    }
  }, [selectedIndex, results.length]);
  
  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      
      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => {
            const newIndex = Math.min(prev + 1, results.length - 1);
            return newIndex;
          });
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => {
            const newIndex = Math.max(prev - 1, 0);
            return newIndex;
          });
          break;
        case 'Enter':
          e.preventDefault();
          if (results[selectedIndex]) {
            handleSelectResult(results[selectedIndex]);
          }
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, onClose, handleSelectResult]);
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-start justify-center p-4 pt-[10vh]">
        <div className="relative w-full max-w-2xl">
          <div className="bg-[#1a1f26] border border-white/10 rounded-lg shadow-2xl overflow-hidden">
            {/* Search Input */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
              <MagnifyingGlassIcon className="w-5 h-5 text-white/40" />
              <input
                ref={inputRef}
                type="text"
                placeholder="Search proposals and protocols..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 bg-transparent text-white placeholder-white/40 focus:outline-none"
              />
              <button
                onClick={onClose}
                className="p-1 text-white/40 hover:text-white/60 transition-colors"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            
            {/* Results */}
            <div ref={resultsContainerRef} className="max-h-96 overflow-y-auto">
              {query.trim() && results.length === 0 && (
                <div className="px-4 py-8 text-center text-white/60">
                  No results found for &ldquo;{query}&rdquo;
                </div>
              )}
              
              {!query.trim() && (
                <div className="px-4 py-8 text-center text-white/60">
                  Start typing to search proposals and protocols...
                </div>
              )}
              
              {results.map((result, index) => (
                <button
                  key={`${result.type}-${(result.item as Proposal | Protocol).id}`}
                  ref={index === selectedIndex ? selectedItemRef : null}
                  onClick={() => handleSelectResult(result)}
                  className={`w-full text-left px-4 py-3 hover:bg-white/5 transition-colors border-l-2 ${
                    index === selectedIndex 
                      ? 'bg-white/10 border-[--color-accent]' 
                      : 'border-transparent'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {result.type === 'proposal' ? (
                        <div className="w-2 h-2 bg-blue-400 rounded-full" />
                      ) : (
                        <div className="w-2 h-2 bg-[--color-accent] rounded-full" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-white/90">
                          {result.type === 'proposal' 
                            ? (result.item as Proposal).title
                            : (result.item as Protocol).name
                          }
                        </span>
                        <span className={`text-xs uppercase font-medium ${
                          result.type === 'protocol' 
                            ? 'text-[--color-accent]' 
                            : 'text-white/40'
                        }`}>
                          {result.type}
                        </span>
                      </div>
                      {result.type === 'proposal' && (
                        <p className="text-sm text-white/60 line-clamp-2">
                          {(result.item as Proposal).body.substring(0, 120)}...
                        </p>
                      )}
                      {result.type === 'proposal' && (result.item as Proposal).author && (
                        <p className="text-xs text-white/40 mt-1">
                          By {(result.item as Proposal).author}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
            
                          {/* Footer */}
            {results.length > 0 && (
              <div className="px-4 py-2 border-t border-white/10 bg-white/5">
                <div className="flex items-center justify-between text-xs text-white/40">
                  <span>Use ↑↓ to navigate, Enter to select, Esc to close</span>
                  <span>
                    {selectedIndex + 1} of {results.length} result{results.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
