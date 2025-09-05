"use client";

import * as React from "react";

import { ChevronDownIcon, ChevronUpIcon, ArrowPathIcon, ClockIcon, PaperAirplaneIcon } from "@heroicons/react/24/outline";
import { CommunityAnalysis } from "../community/CommunityAnalysis";
import { Proposal } from "../../hooks/useProposals";
import { useProposal } from "../../hooks/useProposal";
import { ApiService } from "../../services/api";
import { AnalysisResponse, CustomEvaluationRequest, CustomEvaluationResponse } from "../../types/proposal";
import ReactMarkdown from 'react-markdown';
import { RelatedProposals } from "./related-proposals";

// Status badge component for consistent styling
const StatusBadge = ({ status }: { status?: string }) => {
  if (!status) return <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-500/20 text-gray-400">UNKNOWN</span>;
  
  const getStatusStyle = (status: string) => {
    switch(status.toLowerCase()) {
      case 'pass':
        return 'bg-green-500/20 text-green-400';
      case 'fail':
        return 'bg-red-500/20 text-red-400';
      case 'warning':
        return 'bg-orange-500/20 text-orange-400';
      case 'neutral':
        return 'bg-blue-500/20 text-blue-400';
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

interface ProposalPageProps {
  proposalId: string;
}

export function ProposalPage({ proposalId }: ProposalPageProps) {
  const [isLoading, setIsLoading] = React.useState(false);
  const [backendResult, setBackendResult] = React.useState<AnalysisResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [isProposalExpanded, setIsProposalExpanded] = React.useState(false);
  const [activeSection, setActiveSection] = React.useState<'feedback' | 'discussion' | 'related'>('feedback');
  
  // Custom evaluation states
  const [customCriteria, setCustomCriteria] = React.useState<string>("");
  const [isCustomEvaluating, setIsCustomEvaluating] = React.useState(false);
  const [customResults, setCustomResults] = React.useState<Array<CustomEvaluationResponse & { timestamp: number, criteria: string }>>([]);

  // Fetch the specific proposal by ID directly
  const { proposal: selectedProposal, loading: proposalLoading, error: proposalError } = useProposal(proposalId);

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
      
    
      
      setBackendResult(response);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-analyze the proposal when it's loaded
  React.useEffect(() => {
    if (selectedProposal) {
      // Auto-analyze the proposal when it's loaded
      analyzeProposal(selectedProposal);
    }
  }, [selectedProposal, analyzeProposal]);

  const handleRefreshAnalysis = async () => {
    if (selectedProposal) {
      await analyzeProposal(selectedProposal, true);
    }
  };

  const handleCustomCriteriaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCustomCriteria(e.target.value);
  };

  const handleCustomEvaluate = async () => {
    if (!selectedProposal) {
      setError("Please select a proposal to evaluate");
      return;
    }

    if (!customCriteria.trim()) {
      setError("Please enter custom criteria");
      return;
    }

    setIsCustomEvaluating(true);
    setError(null);

    try {
      const content = `${selectedProposal.title}\n\n${selectedProposal.body}`;
      const request: CustomEvaluationRequest = {
        content,
        custom_criteria: customCriteria
      };

      const response = await ApiService.customEvaluateProposal(request);
      
      // Validate the response structure
      if (!response.summary || !response.response_map || typeof response.response_map !== 'object') {
        throw new Error('Invalid response format from custom evaluation');
      }
      
      // Add the new result to the array with timestamp and criteria
      setCustomResults(prevResults => [
        ...prevResults,
        {
          ...response,
          timestamp: Date.now(),
          criteria: customCriteria
        }
      ]);
      
      // Clear the criteria input for the next evaluation
      setCustomCriteria("");
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Custom evaluation failed');
    } finally {
      setIsCustomEvaluating(false);
    }
  };


  if (proposalLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-white/60 mb-2">Loading proposal...</div>
          <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }
  
  if (!selectedProposal) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-white/60 mb-2">
            {proposalError ? proposalError.message : `Proposal with ID "${proposalId}" not found`}
          </div>
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
                          <div className="border-b border-white/10 pb-4">
                            <h3 className="text-md font-semibold mb-2 text-white/90">Summary</h3>
                            <div className="mb-2">
                              <p className="text-white/80">{backendResult.summary}</p>
                            </div>
                          </div>
                      
                        
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
                              <p className="text-white/70">{backendResult.language_quality.justification}</p>
                            </div>
                          )}
                          {backendResult.language_quality?.suggestions && backendResult.language_quality.suggestions.length > 0 && (
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
                    {/* Custom Evaluation Results */}
                    {customResults.length > 0 && (
                      <div className="mt-6 space-y-6">
                        <h3 className="text-lg font-semibold mb-2">Custom Evaluation Results</h3>
                        
                        {/* Map through all results in the array */}
                        {customResults.map((result, resultIndex) => (
                          <div key={resultIndex} className="rounded-md border border-white/10 bg-white/5 p-4 mb-4">
                            <div className="grid gap-4 break-words">
                              {/* Evaluation timestamp and criteria */}
                              <div className="flex justify-between items-center border-b border-white/10 pb-2 mb-2">
                                <h4 className="text-md font-semibold">
                                  Evaluation #{resultIndex + 1}
                                </h4>
                                <span className="text-xs text-white/60">
                                  {new Date(result.timestamp).toLocaleString()}
                                </span>
                              </div>
                              
                              {/* Criteria used */}
                              <div className="border-b border-white/10 pb-3">
                                <h5 className="text-sm font-medium mb-1 text-white/80">Criteria Used:</h5>
                                <p className="text-white/70 text-sm whitespace-pre-wrap">{result.criteria}</p>
                              </div>
                              
                              {/* Summary removed - now displayed in the proposal feedback section */}
                              
                              {/* Custom Criteria Results */}
                              {result.response_map && Object.entries(result.response_map).map(([criteriaName, evaluation]) => (
                                <div key={criteriaName} className="border-b border-white/10 pb-3">
                                  <h5 className="text-md font-semibold mb-2">{criteriaName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-medium text-white/80">Status:</span>
                                    <StatusBadge status={evaluation.status} />
                                  </div>
                                  {evaluation.justification && (
                                    <div className="mb-1">
                                      <span className="font-medium text-white/80">Justification:</span>{" "}
                                      <span className="text-white/70">{evaluation.justification}</span>
                                    </div>
                                  )}
                                  {evaluation.suggestions?.length > 0 && (
                                    <div>
                                      <span className="font-medium text-white/80">Suggestions:</span>
                                      <ul className="list-disc pl-5 text-white/70">
                                        {evaluation.suggestions.map((suggestion, index) => (
                                          <li key={index}>{suggestion}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              ))}
                              
                              {/* Show message if no criteria in response_map */}
                              {result.response_map && Object.keys(result.response_map).length === 0 && (
                                <div className="text-amber-400">
                                  No evaluation criteria were found in the response.
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Custom Evaluation Loading */}
                    {isCustomEvaluating && (
                      <div className="flex items-center justify-center h-full mt-4">
                        <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mr-2"></div>
                        <p className="text-white/70 text-sm">Running custom evaluation...</p>
                      </div>
                    )}
                    
                    {/* Custom Evaluation Input */}
                    <div className="border-t border-white/10 pt-4 mt-6">
                      <h3 className="text-md font-semibold mb-2 text-white/90">Custom Evaluation</h3>
                      <div className="mb-3">
                        <label htmlFor="customCriteria" className="block text-sm font-medium mb-1 text-white/80">
                          Enter Custom Criteria
                        </label>
                        <textarea
                          id="customCriteria"
                          className="w-full min-h-[100px] p-2 rounded-md bg-white/5 border border-white/10 text-sm font-mono text-white/90 mb-2"
                          placeholder={`Please evaluate this proposal focusing on:
1. Budget justification - Is the budget well justified and detailed?
2. Milestone clarity - Are there clear, measurable milestones?
3. Technical feasibility - Is the proposal technically sound?`}
                          value={customCriteria}
                          onChange={handleCustomCriteriaChange}
                        />
                        <div className="flex justify-end">
                          <button
                            onClick={handleCustomEvaluate}
                            disabled={isCustomEvaluating || !selectedProposal || !customCriteria.trim()}
                            className="inline-flex h-9 items-center justify-center gap-2 px-4 py-2 rounded-md bg-[--color-accent] text-white shadow transition-colors hover:bg-[--color-accent]/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[--color-accent] disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
                            aria-label="Run Custom Evaluation"
                          >
                            {isCustomEvaluating ? (
                              <>
                                <div className="h-4 w-4 border-2 border-t-white border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                                <span className="text-sm font-medium">Evaluating...</span>
                              </>
                            ) : (
                              <>
                                <PaperAirplaneIcon className="h-4 w-4 -rotate-45" />
                                <span className="text-sm font-medium">Evaluate</span>
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
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
              </div>
            </div>
  );
}
