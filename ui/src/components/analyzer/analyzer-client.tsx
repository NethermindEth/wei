"use client";

import * as React from "react";
import { useMemo } from "react";
import { useQueryState } from "nuqs";

import { ProposalList } from "../proposals/proposal-list";
import { Proposal as GraphQLProposal, useProposals } from "../../hooks/useProposals";
import { Header, Protocol } from "../ui/header";
import { SearchModal } from "../ui/search-modal";
import { useSpaces } from "../../hooks/useSpaces";
import { Tabs } from "../ui/tabs";
import { CommunityAnalysis } from "../community/CommunityAnalysis";
import { ProtocolList } from "../protocols/ProtocolList";
import { ProposalPage } from "../proposals/proposal-page";

export function AnalyzerClient() {
  const [selectedSpaceId, setSelectedSpaceId] = useQueryState("space", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [activeTab, setActiveTab] = useQueryState("tab", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
    defaultValue: "proposals"
  });
  const [proposalId, setProposalId] = useQueryState("proposal", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  
  const [isSearchModalOpen, setIsSearchModalOpen] = React.useState(false);
  
  // Fetch spaces for the protocol dropdown
  const { spaces, loading: spacesLoading } = useSpaces();
  
  // Fetch proposals for search functionality
  const { proposals: allProposals } = useProposals(1000); // Get more proposals for search

    const handleSelectProposal = async (proposal: GraphQLProposal) => {
    setProposalId(proposal.id);
    // If proposal has a space, switch to that space/protocol
    if (proposal.space?.id) {
      setSelectedSpaceId(proposal.space.id);
    }
    // Switch to proposals tab when selecting a proposal
    setActiveTab("proposals");
  };
  


  // Convert spaces to protocols for the header
  const protocols: Protocol[] = useMemo(
    () => spaces.map(space => ({
      id: space.id,
      name: space.name,
      avatar: space.avatar,
      verified: space.verified,
      domain: space.domain
    })),
    [spaces]
  );

  const handleProtocolChange = (protocolId: string | null) => {
    setSelectedSpaceId(protocolId);
    // Keep current tab unless we're switching to "All Protocols" and not on proposals tab
    if (!protocolId && activeTab === "protocol") {
    setActiveTab("proposals");
    }
  };

  const handleSearch = () => {
    setIsSearchModalOpen(true);
  };

  const handleSelectProtocolFromSearch = (protocolId: string) => {
    setSelectedSpaceId(protocolId);
    setActiveTab("proposals");
  };

  const handleTabChange = (tabId: string) => {
    if (tabId !== "proposals" && proposalId) {
      // Clear proposal selection when switching away from proposals tab
      setProposalId(null);
    }
    setActiveTab(tabId);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f14]">
      <Header
        selectedProtocol={selectedSpaceId}
        onProtocolChange={handleProtocolChange}
        onSearch={handleSearch}
        protocols={protocols}
        loading={spacesLoading}
      />
      
      <main className="flex-1 container mx-auto px-4 py-6">
        <Tabs
          tabs={[
            { id: "protocol", label: "Protocol" },
            { id: "stakeholders", label: "Stakeholders" },
            { id: "proposals", label: "Proposals" }
          ]}
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
        
        <div className="mt-6">
          {activeTab === "protocol" && selectedSpaceId && (
            <CommunityAnalysis topic={selectedSpaceId} variant="protocol" />
          )}
          
          {activeTab === "protocol" && !selectedSpaceId && (
            <ProtocolList 
              protocols={protocols} 
              onProtocolSelect={handleProtocolChange}
            />
          )}
          
          {activeTab === "stakeholders" && (
            <div className="text-center py-12">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Stakeholders</h2>
              <p className="text-white/60">Stakeholder information and analysis will be displayed here.</p>
            </div>
          )}
          
          {activeTab === "proposals" && !proposalId && (
            <div className="max-w-2xl mx-auto">
              <ProposalList 
                onSelectProposal={handleSelectProposal} 
                selectedProposalId={undefined}
                spaceId={selectedSpaceId}
              />
            </div>
          )}

          {activeTab === "proposals" && proposalId && (
            <ProposalPage proposalId={proposalId} />
          )}
        </div>
      </main>

      <SearchModal
        isOpen={isSearchModalOpen}
        onClose={() => setIsSearchModalOpen(false)}
        proposals={allProposals}
        protocols={protocols}
        onSelectProposal={handleSelectProposal}
        onSelectProtocol={handleSelectProtocolFromSearch}
      />
    </div>
  );
} 