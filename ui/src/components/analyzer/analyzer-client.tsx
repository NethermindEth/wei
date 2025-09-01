"use client";

import * as React from "react";
import { useQueryState } from "nuqs";
import { ApiService } from "../../services/api";
import { Proposal, LocalAnalysisResult, AnalysisResponse } from "../../types/proposal";
import { ProposalList } from "../proposals/proposal-list";
import { Proposal as GraphQLProposal, useProposals } from "../../hooks/useProposals";
import { Header, Protocol } from "../ui/header";
import { SearchModal } from "../ui/search-modal";
import { useSpaces } from "../../hooks/useSpaces";
import { Tabs } from "../ui/tabs";

// Status badge component for consistent styling
const StatusBadge = ({ status }: { status?: string }) => {
  if (!status) return <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-500/20 text-gray-400">UNKNOWN</span>;
  
  const getStatusStyle = (status: string) => {
    switch(status.toLowerCase()) {
      case 'pass':
        return 'bg-green-500/20 text-green-400';
      case 'fail':
        return 'bg-red-500/20 text-red-400';
      case 'n/a':
      default:
        return 'bg-yellow-500/20 text-yellow-400';
    }
  };
  
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusStyle(status)}`}>
      {status.toUpperCase()}
    </span>
  );
};

export function AnalyzerClient() {
  const [proposalId, setProposalId] = useQueryState("q", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [selectedSpaceId, setSelectedSpaceId] = useQueryState("space", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<LocalAnalysisResult | null>(null);
  const [backendResult, setBackendResult] = React.useState<AnalysisResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedProposal, setSelectedProposal] = React.useState<GraphQLProposal | null>(null);
  const [isSearchModalOpen, setIsSearchModalOpen] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState("proposals");
  
  // Fetch spaces for the protocol dropdown
  const { spaces, loading: spacesLoading } = useSpaces();
  
  // Fetch proposals for search functionality
  const { proposals: allProposals } = useProposals(1000); // Get more proposals for search

  const handleSelectProposal = async (proposal: GraphQLProposal) => {
    setSelectedProposal(proposal);
    setProposalId(proposal.id);
    setResult(null);
    setBackendResult(null);
    setError(null);
    setActiveTab("proposals"); // Switch to proposals tab when a proposal is selected
    
    // If proposal has a space, switch to that space/protocol
    if (proposal.space?.id) {
      setSelectedSpaceId(proposal.space.id);
    }
    
    await analyzeProposal(proposal);
  };
  
  const analyzeProposal = async (proposal: GraphQLProposal) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const description = `${proposal.title}\n\n${proposal.body}`;
      const proposalData: Proposal = { description };
      console.log('Analyzing proposal:', proposalData);
      const response = await ApiService.analyzeProposal(proposalData);
      console.log('Analysis response:', response);
      
      // Set the response directly - it should match our interface
      setBackendResult(response);
      setResult(null);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  async function onAnalyze() {
    if (!selectedProposal) {
      setError("Please select a proposal to analyze");
      return;
    }
    
    await analyzeProposal(selectedProposal);
  }

  // Convert spaces to protocols for the header
  const protocols: Protocol[] = spaces.map(space => ({
    id: space.id,
    name: space.name,
    avatar: space.avatar,
    verified: space.verified
  }));

  const handleProtocolChange = (protocolId: string | null) => {
    setSelectedSpaceId(protocolId);
  };

  const handleSearch = () => {
    setIsSearchModalOpen(true);
  };

  const handleSelectProtocolFromSearch = (protocolId: string) => {
    setSelectedSpaceId(protocolId);
    // Don't change tab when selecting a protocol from search
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
          onTabChange={setActiveTab}
        />
        
        <div className="mt-6">
          {activeTab === "protocol" && (
            <div className="text-center py-12">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Protocol Information</h2>
              <p className="text-white/60">Protocol overview and details will be displayed here.</p>
            </div>
          )}
          
          {activeTab === "stakeholders" && (
            <div className="text-center py-12">
              <h2 className="text-xl font-semibold text-white/90 mb-2">Stakeholders</h2>
              <p className="text-white/60">Stakeholder information and analysis will be displayed here.</p>
            </div>
          )}
          
          {activeTab === "proposals" && (
            <div className="grid gap-4 md:grid-cols-2 max-w-full overflow-hidden h-full">
              <div className="grid gap-4 content-start">
                <ProposalList 
                  onSelectProposal={handleSelectProposal} 
                  selectedProposalId={proposalId || undefined}
                  spaceId={selectedSpaceId}
                />

                <div className="flex items-center gap-2">
                  <button
                    onClick={onAnalyze}
                    disabled={isLoading || !selectedProposal}
                    className="inline-flex h-9 items-center justify-center rounded-md bg-[--color-accent] px-4 py-2 text-sm font-medium text-white shadow transition-colors hover:bg-[--color-accent]/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[--color-accent] disabled:pointer-events-none disabled:opacity-50"
                  >
                    {isLoading ? "Analyzing..." : "Analyze Selected"}
                  </button>
                  {error && <div className="text-red-500 text-sm">{error}</div>}
                </div>
              </div>

              <div className="grid gap-4 content-start overflow-hidden">
                <h2 className="text-lg font-semibold mb-2">Analysis Result</h2>
          
        {backendResult && (
          <div className="rounded-md border border-white/10 bg-white/5 p-4 overflow-hidden">
            <div className="grid gap-4 break-words">
              {/* Goals & Motivation */}
              <div className="border-b border-white/10 pb-3">
                <h3 className="text-md font-semibold mb-2">Goals & Motivation</h3>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Status:</span>
                  <StatusBadge status={backendResult.goals_and_motivation?.status} />
                </div>
                {backendResult.goals_and_motivation?.justification && (
                  <div className="mb-1">
                    <span className="font-medium">Justification:</span>{" "}
                    <span>{backendResult.goals_and_motivation.justification}</span>
                  </div>
                )}
                {backendResult.goals_and_motivation?.suggestions?.length > 0 && (
                  <div>
                    <span className="font-medium">Suggestions:</span>
                    <ul className="list-disc pl-5">
                      {backendResult.goals_and_motivation.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Measurable Outcomes */}
              <div className="border-b border-white/10 pb-3">
                <h3 className="text-md font-semibold mb-2">Measurable Outcomes</h3>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Status:</span>
                  <StatusBadge status={backendResult.measurable_outcomes?.status} />
                </div>
                {backendResult.measurable_outcomes?.justification && (
                  <div className="mb-1">
                    <span className="font-medium">Justification:</span>{" "}
                    <span>{backendResult.measurable_outcomes.justification}</span>
                  </div>
                )}
                {backendResult.measurable_outcomes?.suggestions?.length > 0 && (
                  <div>
                    <span className="font-medium">Suggestions:</span>
                    <ul className="list-disc pl-5">
                      {backendResult.measurable_outcomes.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Budget */}
              <div className="border-b border-white/10 pb-3">
                <h3 className="text-md font-semibold mb-2">Budget</h3>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Status:</span>
                  <StatusBadge status={backendResult.budget?.status} />
                </div>
                {backendResult.budget?.justification && (
                  <div className="mb-1">
                    <span className="font-medium">Justification:</span>{" "}
                    <span>{backendResult.budget.justification}</span>
                  </div>
                )}
                {backendResult.budget?.suggestions?.length > 0 && (
                  <div>
                    <span className="font-medium">Suggestions:</span>
                    <ul className="list-disc pl-5">
                      {backendResult.budget.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Technical Specifications */}
              <div className="border-b border-white/10 pb-3">
                <h3 className="text-md font-semibold mb-2">Technical Specifications</h3>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Status:</span>
                  <StatusBadge status={backendResult.technical_specifications?.status} />
                </div>
                {backendResult.technical_specifications?.justification && (
                  <div className="mb-1">
                    <span className="font-medium">Justification:</span>{" "}
                    <span>{backendResult.technical_specifications.justification}</span>
                  </div>
                )}
                {backendResult.technical_specifications?.suggestions?.length > 0 && (
                  <div>
                    <span className="font-medium">Suggestions:</span>
                    <ul className="list-disc pl-5">
                      {backendResult.technical_specifications.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Language Quality */}
              <div>
                <h3 className="text-md font-semibold mb-2">Language Quality</h3>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">Status:</span>
                  <StatusBadge status={backendResult.language_quality?.status} />
                </div>
                {backendResult.language_quality?.justification && (
                  <div className="mb-1">
                    <span className="font-medium">Justification:</span>{" "}
                    <span>{backendResult.language_quality.justification}</span>
                  </div>
                )}
                {backendResult.language_quality?.suggestions?.length > 0 && (
                  <div>
                    <span className="font-medium">Suggestions:</span>
                    <ul className="list-disc pl-5">
                      {backendResult.language_quality.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        {result && (
          <div className="grid gap-4 overflow-hidden">
            <div className="grid gap-2">
              <h2 className="text-lg font-semibold">Local Analysis Result</h2>
              <div className="rounded-md border border-white/10 bg-white/5 p-4 overflow-hidden">
                <div className="grid gap-2 break-words">
                  <div>
                    <span className="font-medium">Summary:</span>{" "}
                    <span>{result.summary}</span>
                  </div>
                  <div>
                    <span className="font-medium">Score:</span>{" "}
                    <span className={`${result.score > 50 ? "text-green-500" : "text-red-500"}`}>
                      {result.score}/100
                    </span>
                  </div>
                  {result.risks.length > 0 && (
                    <div>
                      <span className="font-medium">Risks:</span>
                      <ul className="list-disc pl-5">
                        {result.risks.map((risk, index) => (
                          <li key={index}>{risk}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {!backendResult && !result && !isLoading && (
          <div className="flex items-center mt-4">
            <p className="text-white/70 text-sm italic">Select a proposal to see analysis results</p>
          </div>
        )}

                {isLoading && (
                  <div className="flex items-center mt-4">
                    <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mr-2"></div>
                    <p className="text-white/70 text-sm">Analyzing proposal...</p>
                  </div>
                )}
              </div>
            </div>
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