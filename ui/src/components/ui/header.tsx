"use client";

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { ChevronDownIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { Avatar, DefaultAvatar } from './avatar';

// Protocol/Space interface
export interface Protocol {
  id: string;
  name: string;
  avatar?: string;
  verified?: boolean;
}

interface HeaderProps {
  selectedProtocol: string | null;
  onProtocolChange: (protocolId: string | null) => void;
  onSearch: () => void;
  protocols: Protocol[];
  loading?: boolean;
}

export function Header({ 
  selectedProtocol, 
  onProtocolChange, 
  onSearch, 
  protocols, 
  loading = false 
}: HeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('[data-dropdown]')) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Handle keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        onSearch();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onSearch]);

  const selectedProtocolData = protocols.find(p => p.id === selectedProtocol);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#0b0f14]/95 backdrop-blur supports-[backdrop-filter]:bg-[#0b0f14]/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Left: Wei Logo */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Image
              src="/wei.png"
              alt="Wei logo"
              width={32}
              height={32}
              priority
              className="drop-shadow-[0_0_12px_rgba(25,227,255,0.35)]"
            />
          </div>
          <h1 className="text-lg font-semibold text-white/90">
            Wei – Proposal Analyzer
          </h1>
        </div>

        {/* Center: Protocol Dropdown */}
        <div className="flex-1 max-w-md mx-8" data-dropdown>
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="w-full flex items-center justify-between px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/8 transition-colors focus:outline-none focus:ring-2 focus:ring-[--color-accent]/50"
              disabled={loading}
            >
              <div className="flex items-center gap-2 min-w-0">
                {selectedProtocolData ? (
                  <>
                    <Avatar
                      src={selectedProtocolData.avatar}
                      alt={selectedProtocolData.name}
                      size={20}
                      fallback={<DefaultAvatar name={selectedProtocolData.name} size={20} />}
                    />
                    <span className="text-white/90 truncate">
                      {selectedProtocolData.name}
                      {selectedProtocolData.verified && (
                        <span className="ml-1 text-blue-400">✓</span>
                      )}
                    </span>
                  </>
                ) : (
                  <span className="text-white/60">
                    {loading ? 'Loading protocols...' : 'All Protocols'}
                  </span>
                )}
              </div>
              <ChevronDownIcon 
                className={`w-4 h-4 text-white/60 transition-transform ${
                  isDropdownOpen ? 'rotate-180' : ''
                }`} 
              />
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-[#1a1f26] border border-white/10 rounded-lg shadow-lg max-h-64 overflow-y-auto z-50">
                {/* All Protocols Option */}
                <button
                  onClick={() => {
                    onProtocolChange(null);
                    setIsDropdownOpen(false);
                  }}
                  className={`w-full flex items-center gap-2 px-4 py-2 text-left hover:bg-white/5 transition-colors ${
                    !selectedProtocol ? 'bg-white/10' : ''
                  }`}
                >
                  <span className="text-white/90">All Protocols</span>
                </button>

                {/* Protocol Options */}
                {protocols.map((protocol) => (
                  <button
                    key={protocol.id}
                    onClick={() => {
                      onProtocolChange(protocol.id);
                      setIsDropdownOpen(false);
                    }}
                    className={`w-full flex items-center gap-2 px-4 py-2 text-left hover:bg-white/5 transition-colors ${
                      selectedProtocol === protocol.id ? 'bg-white/10' : ''
                    }`}
                  >
                    <Avatar
                      src={protocol.avatar}
                      alt={protocol.name}
                      size={20}
                      fallback={<DefaultAvatar name={protocol.name} size={20} />}
                    />
                    <span className="text-white/90 truncate">
                      {protocol.name}
                      {protocol.verified && (
                        <span className="ml-1 text-blue-400 text-xs">✓</span>
                      )}
                    </span>
                  </button>
                ))}

                {protocols.length === 0 && !loading && (
                  <div className="px-4 py-2 text-white/60 text-sm">
                    No protocols available
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Search Button */}
        <div className="flex items-center">
          <button
            onClick={onSearch}
            className="flex items-center gap-2 px-3 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/8 transition-colors focus:outline-none focus:ring-2 focus:ring-[--color-accent]/50"
          >
            <MagnifyingGlassIcon className="w-4 h-4 text-white/60" />
            <span className="text-sm text-white/60 hidden sm:inline">
              Search
            </span>
            <kbd className="hidden sm:inline-flex items-center gap-1 px-1.5 py-0.5 text-xs text-white/40 bg-white/10 rounded">
              <span className="text-xs">⌘</span>K
            </kbd>
          </button>
        </div>
      </div>
    </header>
  );
}
