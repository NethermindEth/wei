"use client";

import * as React from "react";
import { useQueryState } from "nuqs";
import { ApiService } from "../../services/api";
import { Proposal, LocalAnalysisResult, AnalysisResponse } from "../../types/proposal";
import { ProposalList } from "../proposals/proposal-list";
import { Proposal as GraphQLProposal } from "../../hooks/useProposals";

export function AnalyzerClient() {
  const [proposalId, setProposalId] = useQueryState("q", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<LocalAnalysisResult | null>(null);
  const [backendResult, setBackendResult] = React.useState<AnalysisResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedProposal, setSelectedProposal] = React.useState<GraphQLProposal | null>(null);

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
      console.log('Analyzing proposal:', proposalData);
      const response = await ApiService.analyzeProposal(proposalData);
      console.log('Analysis response:', response);
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

  return (
    <div className="grid gap-4 md:grid-cols-2 max-w-full overflow-hidden h-full">
      <div className="grid gap-4 content-start">
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

      <div className="grid gap-4 content-start overflow-hidden">
        <h2 className="text-lg font-semibold mb-2">Analysis Result</h2>
          
        {backendResult && (
          <div className="rounded-md border border-white/10 bg-white/5 p-4 overflow-hidden">
            <div className="grid gap-2 break-words">
              <div>
                <span className="font-medium">Verdict:</span>{" "}
                <span
                  className={`${backendResult.verdict === "good" ? "text-green-500" : "text-red-500"}`}
                >
                  {backendResult.verdict}
                </span>
              </div>
              <div>
                <span className="font-medium">Conclusion:</span>{" "}
                <span>{backendResult.conclusion}</span>
              </div>
              <div>
                <span className="font-medium">Proposal Quality:</span>
                <ul className="list-disc pl-5">
                  <li>
                    <span className="font-medium">Clarity of Goals:</span> {backendResult.proposal_quality.clarity_of_goals}
                  </li>
                  <li>
                    <span className="font-medium">Completeness:</span> {backendResult.proposal_quality.completeness_of_sections}
                  </li>
                  <li>
                    <span className="font-medium">Level of Detail:</span> {backendResult.proposal_quality.level_of_detail}
                  </li>
                  <li>
                    <span className="font-medium">Community Adaptability:</span> {backendResult.proposal_quality.community_adaptability}
                  </li>
                </ul>
              </div>
              <div>
                <span className="font-medium">Submitter Intentions:</span>
                <ul className="list-disc pl-5">
                  <li>
                    <span className="font-medium">Identity:</span> {backendResult.submitter_intentions.submitter_identity}
                  </li>
                </ul>
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
  );
} 