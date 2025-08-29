"use client";

import React, { useState, useRef, useEffect } from 'react';
// Using simple SVG icons instead of heroicons to avoid dependency issues
const ChevronDownIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
  </svg>
);

const MagnifyingGlassIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
  </svg>
);

export interface Space {
  id: string;
  name: string;
}

interface SpaceSelectorProps {
  spaces: Space[];
  selectedSpace: Space | null;
  onSpaceSelect: (space: Space | null) => void;
  loading?: boolean;
  placeholder?: string;
  hasMore?: boolean;
  onLoadMore?: () => void;
}

export function SpaceSelector({ 
  spaces, 
  selectedSpace, 
  onSpaceSelect, 
  loading = false,
  placeholder = "All Projects",
  hasMore = false,
  onLoadMore
}: SpaceSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Filter spaces based on search term
  const filteredSpaces = spaces.filter(space =>
    space.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus input when dropdown opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Handle scroll to load more
  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer || !onLoadMore || !hasMore || !isOpen) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
      // More generous threshold for triggering load more
      if (scrollTop + clientHeight >= scrollHeight - 10) {
        console.log('Triggering loadMore for spaces');
        onLoadMore();
      }
    };

    scrollContainer.addEventListener('scroll', handleScroll, { passive: true });
    return () => scrollContainer.removeEventListener('scroll', handleScroll);
  }, [onLoadMore, hasMore, isOpen]);

  const handleSpaceSelect = (space: Space | null) => {
    onSpaceSelect(space);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleToggle = () => {
    if (!loading) {
      setIsOpen(!isOpen);
      setSearchTerm('');
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={handleToggle}
        disabled={loading}
        className="w-full flex items-center justify-between px-3 py-2 bg-[#1a2332] border border-[#2d3748] rounded-lg text-white/90 hover:border-[#4a5568] focus:outline-none focus:border-[#63b3ed] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span className="truncate">
          {loading ? 'Loading projects...' : selectedSpace ? selectedSpace.name : placeholder}
        </span>
        <ChevronDownIcon 
          className={`w-4 h-4 text-white/60 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-[#1a2332] border border-[#2d3748] rounded-lg shadow-lg max-h-64 flex flex-col overflow-hidden">
          {/* Search Input */}
          <div className="p-2 border-b border-[#2d3748]">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
              <input
                ref={inputRef}
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search projects..."
                className="w-full pl-10 pr-3 py-2 bg-[#0f172a] border border-[#2d3748] rounded text-white/90 placeholder-white/40 focus:outline-none focus:border-[#63b3ed] text-sm"
              />
            </div>
          </div>

          {/* Options */}
          <div 
            ref={scrollContainerRef}
            className="flex-1 overflow-y-auto overflow-x-hidden" 
            style={{ maxHeight: '180px' }}
          >
            {/* All Projects Option */}
            <button
              onClick={() => handleSpaceSelect(null)}
              className={`w-full px-3 py-2 text-left hover:bg-[#2d3748] transition-colors ${
                !selectedSpace ? 'bg-[#2d3748] text-[#63b3ed]' : 'text-white/90'
              }`}
            >
              {placeholder}
            </button>

            {/* Filtered Spaces */}
            {filteredSpaces.length > 0 ? (
              filteredSpaces.map((space) => (
                <button
                  key={space.id}
                  onClick={() => handleSpaceSelect(space)}
                  className={`w-full px-3 py-2 text-left hover:bg-[#2d3748] transition-colors truncate ${
                    selectedSpace?.id === space.id ? 'bg-[#2d3748] text-[#63b3ed]' : 'text-white/90'
                  }`}
                >
                  {space.name}
                </button>
              ))
            ) : searchTerm ? (
              <div className="px-3 py-2 text-white/60 text-sm">
                No projects found matching &ldquo;{searchTerm}&rdquo;
              </div>
            ) : (
              <div className="px-3 py-2 text-white/60 text-sm">
                No projects available
              </div>
            )}
            
            {/* Load More Indicator */}
            {hasMore && !searchTerm && (
              <div className="px-3 py-2 text-center text-white/60 text-sm">
                {loading ? 'Loading more...' : 'Scroll for more'}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
