'use client';

import React from 'react';
import { Avatar, DefaultAvatar } from '../ui/avatar';

export interface Protocol {
  id: string;
  name: string;
  avatar?: string;
  verified?: boolean;
  domain?: string;
}

interface ProtocolListProps {
  protocols: Protocol[];
  onProtocolSelect?: (protocolId: string) => void;
}

export function ProtocolList({ protocols, onProtocolSelect }: ProtocolListProps) {
  if (protocols.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-white/90 mb-2">No Protocols Found</h2>
        <p className="text-white/60">No protocols are currently available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-white/90 mb-2">
          All Protocols
        </h2>
        <p className="text-white/60 max-w-2xl mx-auto">
          Browse all available protocols and communities. Select any protocol to analyze its community discourse and discussion centers.
        </p>
      </div>

      {/* Protocol Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {protocols.map((protocol) => (
          <ProtocolCard 
            key={protocol.id} 
            protocol={protocol} 
            onSelect={onProtocolSelect}
          />
        ))}
      </div>

      {/* Footer */}
      <div className="text-center text-sm text-white/40 pt-4 border-t border-white/10">
        <p>
          Showing {protocols.length} protocol{protocols.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  );
}

interface ProtocolCardProps {
  protocol: Protocol;
  onSelect?: (protocolId: string) => void;
}

function ProtocolCard({ protocol, onSelect }: ProtocolCardProps) {
  const handleClick = () => {
    if (onSelect) {
      onSelect(protocol.id);
    }
  };

  return (
    <div 
      className={`bg-white/5 border border-white/10 rounded-lg p-6 transition-all hover:bg-white/10 hover:border-white/20 ${onSelect ? 'cursor-pointer' : ''}`}
      onClick={handleClick}
    >
      {/* Protocol Header */}
      <div className="flex items-center gap-4 mb-4">
        <Avatar
          src={protocol.avatar}
          alt={protocol.name}
          size={48}
          fallback={<DefaultAvatar name={protocol.name} size={48} />}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white/90 truncate">
              {protocol.name}
            </h3>
            {protocol.verified && (
              <span className="text-blue-400 text-sm">✓</span>
            )}
          </div>
          <p className="text-white/60 text-sm">
            Protocol
          </p>
        </div>
      </div>

      {/* Action Hint */}
      {onSelect && (
        <div className="text-center pt-3 border-t border-white/10">
          <p className="text-white/50 text-xs">
            Click to analyze community discourse
          </p>
        </div>
      )}
    </div>
  );
}
