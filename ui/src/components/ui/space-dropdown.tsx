'use client';

import { useState } from 'react';
import type { Space } from '../../types/graphql';

// Simple chevron down icon as SVG
const ChevronDownIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
  </svg>
);


interface SpaceDropdownProps {
  spaces: Space[];
  selectedSpace: Space | null;
  onSpaceSelect: (space: Space | null) => void;
  loading?: boolean;
  placeholder?: string;
}

export function SpaceDropdown({ 
  spaces, 
  selectedSpace, 
  onSpaceSelect, 
  loading = false,
  placeholder = "All Projects"
}: SpaceDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSpaces = spaces.filter(space =>
    space.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSpaceSelect = (space: Space | null) => {
    onSpaceSelect(space);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative w-[500px] min-w-[500px] max-w-[500px] flex-shrink-0">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full max-w-full h-[40px] min-h-[40px] max-h-[40px] flex items-center justify-between px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white hover:bg-white/10 transition-colors"
        disabled={loading}
      >
        <span className="truncate">
          {loading ? 'Loading...' : selectedSpace?.name || placeholder}
        </span>
        <ChevronDownIcon 
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
        />
      </button>

      {isOpen && (
        <div 
          className="absolute z-50 w-[500px] min-w-[500px] max-w-[500px] mt-1 bg-[#1a1f2e] border border-white/10 rounded-lg shadow-lg overflow-hidden h-[240px] min-h-[240px] max-h-[240px] box-border"
        >
          <div className="p-2 border-b border-white/10 h-[48px] min-h-[48px] max-h-[48px]">
            <input
              type="text"
              placeholder="Search spaces..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-2 py-1 bg-white/5 border border-white/10 rounded text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
              autoFocus
            />
          </div>

          <div 
            className="overflow-y-scroll overflow-x-hidden h-[192px] min-h-[192px] max-h-[192px]"
          >
            <button
              onClick={() => handleSpaceSelect(null)}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-white/10 transition-colors ${
                !selectedSpace ? 'bg-white/5 text-blue-400' : 'text-white'
              }`}
            >
              {placeholder}
            </button>

            {filteredSpaces.length > 0 ? (
              filteredSpaces.map((space) => (
                <button
                  key={space.id}
                  onClick={() => handleSpaceSelect(space)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-white/10 transition-colors ${
                    selectedSpace?.id === space.id ? 'bg-white/5 text-blue-400' : 'text-white'
                  }`}
                >
                  {space.name}
                </button>
              ))
            ) : (
              <div className="px-3 py-2 text-sm text-gray-400">
                No spaces found
              </div>
            )}
          </div>
        </div>
      )}

      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
