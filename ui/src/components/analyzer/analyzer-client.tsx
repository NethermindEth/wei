"use client";

import * as React from "react";
import { useQueryState } from "nuqs";
import * as Label from "@radix-ui/react-label";
import { ApiService } from "../../services/api";
import { Proposal, LocalAnalysisResult, AnalysisResponse } from "../../types/proposal";

export function AnalyzerClient() {
  const [proposal, setProposal] = useQueryState("q", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<LocalAnalysisResult | null>(null);
  const [backendResult, setBackendResult] = React.useState<AnalysisResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  async function onAnalyze() {
    if (!proposal?.trim()) {
      setResult(null);
      setBackendResult(null);
      setError(null);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const proposalData: Proposal = { description: proposal };
      const response = await ApiService.analyzeProposal(proposalData);
      setBackendResult(response);
      setResult(null);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="w-full max-w-3xl grid gap-4">
      <div className="grid gap-2">
        <Label.Root htmlFor="proposal" className="text-sm text-[#9fb5cc]">
          Governance proposal
        </Label.Root>
        <textarea
          id="proposal"
          value={proposal ?? ""}
          onChange={(e) => setProposal(e.target.value)}
          placeholder="Paste proposal text..."
          rows={8}
          className="accent-glow w-full resize-y rounded-xl bg-white/5 text-white/90 placeholder:text-[#7d93ab] px-4 py-3 outline-none focus:ring-2 focus:ring-[--color-accent] border border-white/10"
        />
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isLoading || !proposal?.trim()}
          className="accent-glow rounded-lg bg-gradient-to-br from-[--color-accent] to-[--color-accent-2] text-white font-semibold px-4 py-2 transition disabled:opacity-40 hover:brightness-110 border border-white/15 shadow"
        >
          {isLoading ? "Analyzing…" : "Analyze"}
        </button>

        <span className="text-xs text-[#7d93ab]">URL saves your text with `?q=`</span>
      </div>

      <div className="grid gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
        {!result && !backendResult && !error && (
          <p className="text-sm text-[#7d93ab]">Feedback will appear here.</p>
        )}

        {/* Error Display */}
        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-3">
            <p className="text-sm text-red-400">
              <strong>Error:</strong> {error}
            </p>
            <p className="text-xs text-red-300 mt-1">
              Falling back to local analysis...
            </p>
          </div>
        )}

        {/* Backend Analysis Result */}
        {backendResult && (
          <div className="grid gap-3">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-full bg-[--color-accent] grid place-items-center">
                <span className="text-[10px] text-[#04141f] font-bold">AI</span>
              </div>
              <p className="text-sm font-medium text-[--color-accent]">
                AI Analysis: <span className={`${backendResult.verdict === 'good' ? 'text-green-400' : 'text-red-400'}`}>
                  {backendResult.verdict.toUpperCase()}
                </span>
              </p>
            </div>
            
            {/* Conclusion */}
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <h3 className="text-sm font-semibold text-[--color-accent] mb-2">Conclusion</h3>
              <p className="text-sm">{backendResult.conclusion}</p>
            </div>
            
            {/* Proposal Quality */}
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <h3 className="text-sm font-semibold text-[--color-accent] mb-2">Proposal Quality</h3>
              <div className="grid gap-2">
                <div className="grid grid-cols-2 gap-1">
                  <p className="text-xs text-[#9fb5cc]">Clarity of Goals:</p>
                  <p className="text-xs">{backendResult.proposal_quality.clarity_of_goals}</p>
                </div>
                <div className="grid grid-cols-2 gap-1">
                  <p className="text-xs text-[#9fb5cc]">Completeness:</p>
                  <p className="text-xs">{backendResult.proposal_quality.completeness_of_sections}</p>
                </div>
                <div className="grid grid-cols-2 gap-1">
                  <p className="text-xs text-[#9fb5cc]">Level of Detail:</p>
                  <p className="text-xs">{backendResult.proposal_quality.level_of_detail}</p>
                </div>
                <div className="grid grid-cols-2 gap-1">
                  <p className="text-xs text-[#9fb5cc]">Community Adaptability:</p>
                  <p className="text-xs">{backendResult.proposal_quality.community_adaptability}</p>
                </div>
                
                {backendResult.proposal_quality.assumptions_made.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Assumptions Made:</p>
                    <ul className="list-disc pl-5 text-xs space-y-1">
                      {backendResult.proposal_quality.assumptions_made.map((assumption, i) => (
                        <li key={i}>{assumption}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {backendResult.proposal_quality.missing_elements.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Missing Elements:</p>
                    <ul className="list-disc pl-5 text-xs space-y-1">
                      {backendResult.proposal_quality.missing_elements.map((element, i) => (
                        <li key={i}>{element}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
            
            {/* Submitter Intentions */}
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <h3 className="text-sm font-semibold text-[--color-accent] mb-2">Submitter Analysis</h3>
              <p className="text-xs mb-2">{backendResult.submitter_intentions.submitter_identity}</p>
              
              {backendResult.submitter_intentions.inferred_interests.length > 0 && (
                <div className="mb-2">
                  <p className="text-xs font-medium mb-1">Inferred Interests:</p>
                  <ul className="list-disc pl-5 text-xs space-y-1">
                    {backendResult.submitter_intentions.inferred_interests.map((interest, i) => (
                      <li key={i}>{interest}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {backendResult.submitter_intentions.social_activity.length > 0 && (
                <div className="mb-2">
                  <p className="text-xs font-medium mb-1">Social Activity:</p>
                  <ul className="list-disc pl-5 text-xs space-y-1">
                    {backendResult.submitter_intentions.social_activity.map((activity, i) => (
                      <li key={i}>{activity}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {backendResult.submitter_intentions.strategic_positioning.length > 0 && (
                <div>
                  <p className="text-xs font-medium mb-1">Strategic Positioning:</p>
                  <ul className="list-disc pl-5 text-xs space-y-1">
                    {backendResult.submitter_intentions.strategic_positioning.map((position, i) => (
                      <li key={i}>{position}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            
            {/* Raw JSON View */}
            <details className="text-xs">
              <summary className="cursor-pointer text-[#9fb5cc] hover:text-white transition-colors">View Raw JSON</summary>
              <pre className="mt-2 p-3 bg-[#04141f] border border-white/10 rounded-lg overflow-x-auto">
                {JSON.stringify(backendResult, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </section>
  );
} 