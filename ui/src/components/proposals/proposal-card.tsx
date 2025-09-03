"use client";

import React, { useState } from 'react';
import { Proposal } from '../../hooks/useProposals';
import { Modal } from '../ui/modal';
import ReactMarkdown from 'react-markdown';
import '../ui/markdown-styles.css';

interface ProposalCardProps {
  proposal: Proposal;
  onClick: (proposal: Proposal) => void;
  isSelected: boolean;
}

export function ProposalCard({ proposal, onClick, isSelected }: ProposalCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const previewText = proposal.body
    ? proposal.body.split('\n')[0] || ''
    : '';
  
  const truncatedPreview = previewText.length > 50 
    ? `${previewText.substring(0, 50)}...` 
    : previewText;

  const handleCardClick = () => {
    // Always call the onClick handler for analysis on the main page
    onClick(proposal);
  };

  const handleViewFullContent = (e: React.MouseEvent) => {
    e.stopPropagation(); 
    setIsModalOpen(true);
  };

  return (
    <>
      <div 
        className={`p-4 rounded-lg border cursor-pointer transition-colors overflow-visible flex flex-col min-h-[120px] w-full ${
          isSelected 
            ? 'border-[--color-accent] bg-white/10' 
            : 'border-white/10 bg-white/5 hover:bg-white/8'
        }`}
        onClick={handleCardClick}
        style={{ boxSizing: 'border-box' }}
      >
        <h3 className="font-medium text-white/90 mb-2 break-words">{proposal.title}</h3>
        <p className="text-sm text-white/70 mb-3 break-words">{truncatedPreview}</p>
        <div className="flex items-center justify-between mt-auto flex-wrap gap-2">
          <span className="text-xs text-[#9fb5cc] truncate">{proposal.author ? `By: ${proposal.author}` : ''}</span>
          <button 
            onClick={handleViewFullContent}
            className="text-xs px-2 py-1 bg-white/10 hover:bg-white/20 rounded text-white/80 transition-colors shrink-0"
          >
            View Full Content
          </button>
        </div>
      </div>

      <Modal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        title={proposal.title}
      >
        <div className="text-white/90 max-w-none markdown-content">
          <ReactMarkdown
            components={{
              h1: (props) => <h1 className="text-xl font-bold mb-4" {...props} />,
              h2: (props) => <h2 className="text-lg font-bold mb-3" {...props} />,
              h3: (props) => <h3 className="text-md font-bold mb-2" {...props} />,
              p: (props) => <p className="mb-4" {...props} />,
              ul: (props) => <ul className="list-disc pl-5 mb-4" {...props} />,
              ol: (props) => <ol className="list-decimal pl-5 mb-4" {...props} />,
              li: (props) => <li className="mb-1" {...props} />,
              a: (props) => <a className="text-blue-400 hover:underline" {...props} />,
              code: ({inline, ...props}: {inline?: boolean, children?: React.ReactNode, className?: string}) => 
                inline ? <code className="bg-gray-800 px-1 rounded text-sm" {...props} /> : <code {...props} />,
              pre: (props) => <pre className="bg-gray-800 p-3 rounded mb-4 overflow-x-auto" {...props} />
            }}
          >
            {proposal.body || ''}
          </ReactMarkdown>
        </div>
      </Modal>
    </>
  );
}
