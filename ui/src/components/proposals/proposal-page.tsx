"use client";

import * as React from "react";

import { ChevronDownIcon, ChevronUpIcon, ArrowPathIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";
import { CommunityAnalysis } from "../community/CommunityAnalysis";
import { Proposal, useProposals } from "../../hooks/useProposals";
import { ApiService } from "../../services/api";
import { AnalysisResponse, ProposalArguments } from "../../types/proposal";
import ReactMarkdown from 'react-markdown';
import { RelatedProposals } from "./related-proposals";

interface ProposalPageProps {
  proposalId: string;
}

interface ArgumentsState {
  status: 'idle' | 'loading' | 'success' | 'error';
  data: ProposalArguments | null;
  error: string | null;
}
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



export function ProposalPage({ proposalId }: ProposalPageProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  const [backendResult, setBackendResult] = React.useState<AnalysisResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [argumentsState, setArgumentsState] = React.useState<ArgumentsState>({ status: 'idle', data: null, error: null });
  const [selectedProposal, setSelectedProposal] = React.useState<Proposal | null>(null);
  const [isProposalExpanded, setIsProposalExpanded] = React.useState(false);
  const [activeSection, setActiveSection] = React.useState<'feedback' | 'discussion' | 'related' | 'arguments'>('feedback');

  // Fetch proposals for search functionality
  const { proposals: allProposals } = useProposals(1000);

  const analyzeProposal = React.useCallback(async (proposal: Proposal, forceRefresh = false) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const description = `${proposal.title}\n\n${proposal.body}`;
      const proposalData = { description };
      console.log('Analyzing proposal:', proposalData);
      
      const response = forceRefresh 
        ? await ApiService.refreshProposalAnalysis(proposalData)
        : await ApiService.analyzeProposal(proposalData);
      
      console.log('Analysis response:', response);
      
      setBackendResult(response);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  const fetchProposalArguments = React.useCallback(async (proposal: Proposal) => {
    setArgumentsState({ status: 'loading', data: null, error: null });
    
    try {
      const description = `${proposal.title}\n\n${proposal.body}`;
      const proposalData = { description };
      
      const result = await ApiService.getProposalArguments(proposalData);
      
      if (result.arguments) {
        setArgumentsState({ status: 'success', data: result.arguments, error: null });
      } else {
        setArgumentsState({ status: 'error', data: null, error: 'No arguments data received from analysis' });
      }
    } catch (err) {
      console.error('Error fetching proposal arguments:', err);
      setArgumentsState({ status: 'error', data: null, error: 'Failed to fetch proposal arguments. Please try again.' });
    }
  }, []);

  // Find the specific proposal by ID
  React.useEffect(() => {
    if (allProposals.length > 0) {
      const proposal = allProposals.find(p => p.id === proposalId);
      
      if (proposal) {
        setSelectedProposal(proposal);
        // Auto-analyze the proposal when it's loaded
        analyzeProposal(proposal);
        // Fetch proposal arguments separately
        fetchProposalArguments(proposal);
      }
    }
  }, [allProposals, proposalId, analyzeProposal, fetchProposalArguments]);

  const handleRefreshAnalysis = async () => {
    if (selectedProposal) {
      await Promise.all([
        analyzeProposal(selectedProposal, true),
        fetchProposalArguments(selectedProposal)
      ]);
    }
  };


  if (!selectedProposal) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-white/60 mb-2">
            {allProposals.length === 0 ? "Loading proposals..." : `Proposal with ID "${proposalId}" not found`}
          </div>
          {allProposals.length === 0 && (
            <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mx-auto"></div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-6">
              {/* Left Sidebar Navigation */}
              <div className="w-64 flex-shrink-0">
                <div className="bg-white/5 border border-white/10 rounded-lg p-4 sticky top-6">
                  <h3 className="text-lg font-semibold text-white/90 mb-4">Analysis Sections</h3>
                  <nav className="space-y-2">
                    <button
                      onClick={() => setActiveSection('feedback')}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        activeSection === 'feedback'
                          ? 'bg-blue-600 text-white'
                          : 'text-white/70 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      Proposal Feedback
                    </button>
                    <button
                      onClick={() => setActiveSection('discussion')}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        activeSection === 'discussion'
                          ? 'bg-blue-600 text-white'
                          : 'text-white/70 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      Discussion Centers
                    </button>
                    <button
                      onClick={() => setActiveSection('related')}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        activeSection === 'related'
                          ? 'bg-blue-600 text-white'
                          : 'text-white/70 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      Related Proposals
                    </button>
                    <button
                      onClick={() => setActiveSection('arguments')}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                        activeSection === 'arguments'
                          ? 'bg-blue-600 text-white'
                          : 'text-white/70 hover:text-white hover:bg-white/10'
                      }`}
                    >
                      Proposal Arguments
                    </button>
                  </nav>
                </div>
              </div>

              {/* Main Content Area */}
              <div className="flex-1 max-w-4xl space-y-6">
              {/* Proposal Title */}
              <div className="mb-4">
                <h1 className="text-2xl font-semibold text-white/90 mb-3 break-words">
                  {selectedProposal.space?.id ? (
                    <a
                      href={`https://snapshot.org/#/${selectedProposal.space.id}/proposal/${selectedProposal.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-[--color-accent] transition-colors hover:underline"
                      title="View original proposal on Snapshot"
                    >
                      {selectedProposal.title}
                    </a>
                  ) : (
                    selectedProposal.title
                  )}
                </h1>
                <div className="flex items-center gap-4 text-sm text-white/60">
                  {selectedProposal.author && (
                    <span>By: {selectedProposal.author}</span>
                  )}
                  {selectedProposal.space && (
                    <span>Space: {selectedProposal.space.name}</span>
                  )}
                </div>
              </div>

              {/* Proposal Content Dropdown */}
              <div className="rounded-lg border border-white/10 bg-white/5 overflow-hidden">
                <button
                  onClick={() => setIsProposalExpanded(!isProposalExpanded)}
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                >
                  <h2 className="text-lg font-semibold text-white/90">
                    Proposal Content
                  </h2>
                  <div className="ml-4 flex-shrink-0">
                    {isProposalExpanded ? (
                      <ChevronUpIcon className="w-5 h-5 text-white/60" />
                    ) : (
                      <ChevronDownIcon className="w-5 h-5 text-white/60" />
                    )}
                  </div>
                </button>
                
                {isProposalExpanded && (
                  <div className="px-6 pb-6 border-t border-white/10">
                    <div className="prose prose-invert max-w-none mt-4">
                      <ReactMarkdown
                        components={{
                          h1: (props) => <h1 className="text-xl font-bold mb-4 text-white/90" {...props} />,
                          h2: (props) => <h2 className="text-lg font-bold mb-3 text-white/90" {...props} />,
                          h3: (props) => <h3 className="text-md font-bold mb-2 text-white/90" {...props} />,
                          p: (props) => <p className="mb-4 text-white/80" {...props} />,
                          ul: (props) => <ul className="list-disc pl-5 mb-4 text-white/80" {...props} />,
                          ol: (props) => <ol className="list-decimal pl-5 mb-4 text-white/80" {...props} />,
                          li: (props) => <li className="mb-1" {...props} />,
                          a: (props) => <a className="text-blue-400 hover:underline" {...props} />,
                          code: ({inline, ...props}: {inline?: boolean, children?: React.ReactNode, className?: string}) => 
                            inline ? <code className="bg-gray-800 px-1 rounded text-sm text-white/90" {...props} /> : <code {...props} />,
                          pre: (props) => <pre className="bg-gray-800 p-3 rounded mb-4 overflow-x-auto text-white/90" {...props} />
                        }}
                      >
                        {selectedProposal.body || ''}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>


                {/* Dynamic Content Based on Active Section */}
                {activeSection === 'feedback' && (
                  <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-semibold text-white/90">Proposal Feedback</h2>
                      
                      {backendResult && !isLoading && (
                        <div className="flex items-center gap-4">
                          {/* Cache metadata */}
                          <div className="flex items-center gap-4 text-sm text-white/60">
                            {backendResult.from_cache && (
                              <div className="flex items-center gap-1">
                                <ClockIcon className="w-4 h-4" />
                                <span>Cached result</span>
                              </div>
                            )}
                          </div>
                          
                          {/* Refresh button */}
                          <button
                            onClick={handleRefreshAnalysis}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-3 py-2 text-sm text-white/70 hover:text-white bg-white/5 hover:bg-white/10 rounded-lg transition-colors"
                          >
                            <ArrowPathIcon className="w-4 h-4" />
                            Refresh
                          </button>
                        </div>
                      )}
                    </div>
                    
                    {isLoading && (
                      <div className="flex items-center">
                        <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mr-2"></div>
                        <p className="text-white/70 text-sm">Analyzing proposal...</p>
                      </div>
                    )}

                    {error && (
                      <div className="text-red-400 text-sm mb-4">{error}</div>
                    )}

                    {backendResult && !isLoading && (
                      <div className="space-y-6">
                        {/* Goals & Motivation */}
                        <div className="border-b border-white/10 pb-4">
                          <h3 className="text-md font-semibold mb-2 text-white/90">Goals & Motivation</h3>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-white/80">Status:</span>
                            <StatusBadge status={backendResult.goals_and_motivation?.status} />
                          </div>
                          {backendResult.goals_and_motivation?.justification && (
                            <div className="mb-2">
                              <span className="font-medium text-white/80">Justification:</span>{" "}
                              <span className="text-white/70">{backendResult.goals_and_motivation.justification}</span>
                            </div>
                          )}
                          {backendResult.goals_and_motivation?.suggestions?.length > 0 && (
                            <div>
                              <span className="font-medium text-white/80">Suggestions:</span>
                              <ul className="list-disc pl-5 text-white/70">
                                {backendResult.goals_and_motivation.suggestions.map((suggestion, index) => (
                                  <li key={index}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {/* Measurable Outcomes */}
                        <div className="border-b border-white/10 pb-4">
                          <h3 className="text-md font-semibold mb-2 text-white/90">Measurable Outcomes</h3>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-white/80">Status:</span>
                            <StatusBadge status={backendResult.measurable_outcomes?.status} />
                          </div>
                          {backendResult.measurable_outcomes?.justification && (
                            <div className="mb-2">
                              <span className="font-medium text-white/80">Justification:</span>{" "}
                              <span className="text-white/70">{backendResult.measurable_outcomes.justification}</span>
                            </div>
                          )}
                          {backendResult.measurable_outcomes?.suggestions?.length > 0 && (
                            <div>
                              <span className="font-medium text-white/80">Suggestions:</span>
                              <ul className="list-disc pl-5 text-white/70">
                                {backendResult.measurable_outcomes.suggestions.map((suggestion, index) => (
                                  <li key={index}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {/* Budget */}
                        <div className="border-b border-white/10 pb-4">
                          <h3 className="text-md font-semibold mb-2 text-white/90">Budget</h3>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-white/80">Status:</span>
                            <StatusBadge status={backendResult.budget?.status} />
                          </div>
                          {backendResult.budget?.justification && (
                            <div className="mb-2">
                              <span className="font-medium text-white/80">Justification:</span>{" "}
                              <span className="text-white/70">{backendResult.budget.justification}</span>
                            </div>
                          )}
                          {backendResult.budget?.suggestions?.length > 0 && (
                            <div>
                              <span className="font-medium text-white/80">Suggestions:</span>
                              <ul className="list-disc pl-5 text-white/70">
                                {backendResult.budget.suggestions.map((suggestion, index) => (
                                  <li key={index}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {/* Technical Specifications */}
                        <div className="border-b border-white/10 pb-4">
                          <h3 className="text-md font-semibold mb-2 text-white/90">Technical Specifications</h3>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-white/80">Status:</span>
                            <StatusBadge status={backendResult.technical_specifications?.status} />
                          </div>
                          {backendResult.technical_specifications?.justification && (
                            <div className="mb-2">
                              <span className="font-medium text-white/80">Justification:</span>{" "}
                              <span className="text-white/70">{backendResult.technical_specifications.justification}</span>
                            </div>
                          )}
                          {backendResult.technical_specifications?.suggestions?.length > 0 && (
                            <div>
                              <span className="font-medium text-white/80">Suggestions:</span>
                              <ul className="list-disc pl-5 text-white/70">
                                {backendResult.technical_specifications.suggestions.map((suggestion, index) => (
                                  <li key={index}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {/* Language Quality */}
                        <div className="border-b border-white/10 pb-4">
                          <h3 className="text-md font-semibold mb-2 text-white/90">Language Quality</h3>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium text-white/80">Status:</span>
                            <StatusBadge status={backendResult.language_quality?.status} />
                          </div>
                          {backendResult.language_quality?.justification && (
                            <div className="mb-2">
                              <span className="font-medium text-white/80">Justification:</span>{" "}
                              <span className="text-white/70">{backendResult.language_quality.justification}</span>
                            </div>
                          )}
                          {backendResult.language_quality?.suggestions?.length > 0 && (
                            <div>
                              <span className="font-medium text-white/80">Suggestions:</span>
                              <ul className="list-disc pl-5 text-white/70">
                                {backendResult.language_quality.suggestions.map((suggestion, index) => (
                                  <li key={index}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

            
                      </div>
                    )}

                    {!backendResult && !isLoading && !error && (
                      <div className="text-white/60 text-sm italic">
                        Analysis will appear here once the proposal is processed.
                      </div>
                    )}
                  </div>
                )}

                {activeSection === 'discussion' && (
                  <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                    <CommunityAnalysis 
                      topic={selectedProposal.title}
                      variant="proposal"
                    />
                  </div>
                )}

                {activeSection === 'related' && (
                  <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                    <RelatedProposals 
                      proposalText={selectedProposal.body || ''}
                      proposalTitle={selectedProposal.title}
                    />
                  </div>
                )}
                
                {activeSection === 'arguments' && (
                  <div className="rounded-lg border border-white/10 bg-white/5 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-semibold text-white/90">Proposal Arguments</h2>
                      <button
                        onClick={() => selectedProposal && fetchProposalArguments(selectedProposal)}
                        className="flex items-center gap-1 text-sm text-white/60 hover:text-white transition-colors"
                        disabled={argumentsState.status === 'loading'}
                      >
                        <ArrowPathIcon className={`w-4 h-4 ${argumentsState.status === 'loading' ? 'animate-spin' : ''}`} />
                        <span>Refresh</span>
                      </button>
                    </div>
                    
                    {argumentsState.status === 'loading' ? (
                      <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30"></div>
                        <span className="ml-3 text-white/60">Analyzing arguments...</span>
                      </div>
                    ) : argumentsState.status === 'success' && argumentsState.data ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Arguments For */}
                        <div className="bg-green-500/10 rounded-lg p-4 border border-green-500/20 shadow-sm">
                          <h4 className="font-medium text-green-400 mb-3 flex items-center">
                            <CheckCircleIcon className="w-5 h-5 mr-2" />
                            Supporting Arguments
                          </h4>
                          {argumentsState.data.for_proposal?.length > 0 ? (
                            <ul className="space-y-2 text-white/80">
                              {argumentsState.data.for_proposal.map((arg, index) => (
                                <li key={index} className="flex items-start">
                                  <span className="text-green-400 mr-2">•</span>
                                  <span>{arg}</span>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-white/50 italic">No supporting arguments found.</p>
                          )}
                        </div>
                        
                        {/* Arguments Against */}
                        <div className="bg-red-500/10 rounded-lg p-4 border border-red-500/20 shadow-sm">
                          <h4 className="font-medium text-red-400 mb-3 flex items-center">
                            <XCircleIcon className="w-5 h-5 mr-2" />
                            Opposing Arguments
                          </h4>
                          {argumentsState.data.against?.length > 0 ? (
                            <ul className="space-y-2 text-white/80">
                              {argumentsState.data.against.map((arg, index) => (
                                <li key={index} className="flex items-start">
                                  <span className="text-red-400 mr-2">•</span>
                                  <span>{arg}</span>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-white/50 italic">No opposing arguments found.</p>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        {argumentsState.error ? (
                          <div className="mb-4">
                            <p className="text-red-400 mb-2">{argumentsState.error}</p>
                            <p className="text-white/60">Please try again or check the proposal content.</p>
                          </div>
                        ) : (
                          <p className="text-white/60 mb-4">No arguments analysis available</p>
                        )}
                        <button
                          onClick={() => selectedProposal && fetchProposalArguments(selectedProposal)}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                        >
                          {argumentsState.error ? 'Retry Analysis' : 'Analyze Arguments'}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
  );
}
