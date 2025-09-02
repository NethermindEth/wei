"use client";

import * as React from "react";
import { useQueryState } from "nuqs";
import { ApiService } from "../../services/api";
import { Proposal, LocalAnalysisResult, AnalysisResponse, CustomEvaluationRequest, CustomEvaluationResponse } from "../../types/proposal";
import { ProposalList } from "../proposals/proposal-list";
import type { Proposal as GraphQLProposal } from "../../types/graphql";

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
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<LocalAnalysisResult | null>(null);
  const [backendResult, setBackendResult] = React.useState<AnalysisResponse | null>(null);
  const [customResult, setCustomResult] = React.useState<CustomEvaluationResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedProposal, setSelectedProposal] = React.useState<GraphQLProposal | null>(null);
  const [customCriteria, setCustomCriteria] = React.useState<string>("");
  const [isCustomEvaluating, setIsCustomEvaluating] = React.useState(false);

  const handleSelectProposal = async (proposal: GraphQLProposal) => {
    setSelectedProposal(proposal);
    setProposalId(proposal.id);
    setResult(null);
    setBackendResult(null);
    setError(null);
    
    await analyzeProposal(proposal);
  };
  
  const analyzeProposal = async (proposal: GraphQLProposal) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const description = `${proposal.title}\n\n${proposal.body}`;
      const proposalData: Proposal = { description };
      const response = await ApiService.analyzeProposal(proposalData);
      
      // Set the response directly - it should match our interface
      setBackendResult(response);
      setResult(null);
    } catch (err) {
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
    setCustomResult(null);

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
      
      setCustomResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Custom evaluation failed');
    } finally {
      setIsCustomEvaluating(false);
    }
  };

  return (
    <div className="grid gap-4 md:grid-cols-[500px_1fr] max-w-full h-screen grid-rows-[1fr] w-full">
      <div className="grid gap-4 h-full overflow-hidden grid-rows-[auto_1fr_auto] max-h-screen min-h-screen w-full min-w-full">
        <ProposalList 
          onSelectProposal={handleSelectProposal} 
          selectedProposalId={proposalId || undefined}
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

      <div className="grid gap-4 h-full grid-rows-[auto_1fr_auto] max-h-screen min-h-screen w-full min-w-full">
        <h2 className="text-lg font-semibold mb-2">Analysis Result</h2>
          
        {/* Results Area - Scrollable Content */}
        <div className="flex-1 overflow-y-auto w-full min-w-full max-w-full pr-2">
          {/* Standard Analysis Results */}
          {backendResult && (
            <div className="rounded-md border border-white/10 bg-white/5 p-4 mb-4 w-full min-w-full max-w-full">
            <div className="grid gap-4 break-words w-full min-w-full max-w-full">
              {/* Summary */}
              {backendResult.summary && (
                <div className="border-b border-white/10 pb-3">
                  <h3 className="text-md font-semibold mb-2">Summary</h3>
                  <p className="text-white/90">{backendResult.summary}</p>
                </div>
              )}
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

        {/* Custom Evaluation Results */}
        {customResult && (
          <div className="rounded-md border border-white/10 bg-white/5 p-4 mb-4 w-full min-w-full max-w-full">
            <div className="grid gap-4 break-words w-full min-w-full max-w-full">
              <h3 className="text-lg font-semibold mb-2">Custom Evaluation Results</h3>
              
              {/* Summary */}
              {customResult.summary && (
                <div className="border-b border-white/10 pb-3">
                  <h4 className="text-md font-semibold mb-2">Summary</h4>
                  <p className="text-white/90">{customResult.summary}</p>
                </div>
              )}
              
              {/* Custom Criteria Results */}
              {customResult.response_map && Object.entries(customResult.response_map).map(([criteriaName, evaluation]) => (
                <div key={criteriaName} className="border-b border-white/10 pb-3">
                  <h4 className="text-md font-semibold mb-2">{criteriaName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium">Status:</span>
                    <StatusBadge status={evaluation.status} />
                  </div>
                  {evaluation.justification && (
                    <div className="mb-1">
                      <span className="font-medium">Justification:</span>{" "}
                      <span>{evaluation.justification}</span>
                    </div>
                  )}
                  {evaluation.suggestions?.length > 0 && (
                    <div>
                      <span className="font-medium">Suggestions:</span>
                      <ul className="list-disc pl-5">
                        {evaluation.suggestions.map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Show message if no criteria in response_map */}
              {customResult.response_map && Object.keys(customResult.response_map).length === 0 && (
                <div className="text-amber-400">
                  No evaluation criteria were found in the response.
                </div>
              )}
            </div>
          </div>
        )}
        
        {result && (
          <div className="grid gap-4 mb-4">
            <div className="grid gap-2">
              <h2 className="text-lg font-semibold">Local Analysis Result</h2>
              <div className="rounded-md border border-white/10 bg-white/5 p-4 overflow-y-auto">
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

          {!backendResult && !result && !customResult && !isLoading && !isCustomEvaluating && (
            <div className="flex items-center justify-center h-full">
              <p className="text-white/70 text-sm italic">Select a proposal to see analysis results</p>
            </div>
          )}

          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mr-2"></div>
              <p className="text-white/70 text-sm">Analyzing proposal...</p>
            </div>
          )}
          
          {isCustomEvaluating && (
            <div className="flex items-center justify-center h-full mt-4">
              <div className="h-4 w-4 border-2 border-t-[--color-accent] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin mr-2"></div>
              <p className="text-white/70 text-sm">Running custom evaluation...</p>
            </div>
          )}
        </div>
        
        {/* Custom Evaluation Input - Fixed at Bottom */}
        <div className="border-t border-white/10 pt-4 mt-2">
          <h3 className="text-md font-semibold mb-2">Custom Evaluation</h3>
          <div className="mb-3">
            <label htmlFor="customCriteria" className="block text-sm font-medium mb-1">
              Enter Custom Criteria
            </label>
            <textarea
              id="customCriteria"
              className="w-full min-h-[100px] p-2 rounded-md bg-white/5 border border-white/10 text-sm font-mono"
              placeholder={`Please evaluate this proposal focusing on:
1. Budget justification - Is the budget well justified and detailed?
2. Milestone clarity - Are there clear, measurable milestones?
3. Technical feasibility - Is the proposal technically sound?`}
              value={customCriteria}
              onChange={handleCustomCriteriaChange}
            />
          </div>
          <button
            onClick={handleCustomEvaluate}
            disabled={isCustomEvaluating || !selectedProposal || !customCriteria.trim()}
            className="inline-flex h-9 items-center justify-center rounded-md bg-[--color-accent] px-4 py-2 text-sm font-medium text-white shadow transition-colors hover:bg-[--color-accent]/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[--color-accent] disabled:pointer-events-none disabled:opacity-50"
          >
            {isCustomEvaluating ? "Evaluating..." : "Run Custom Evaluation"}
          </button>
        </div>
      </div>
    </div>
  );
} 