"use client";

import * as React from "react";
import { useQueryState } from "nuqs";
import * as Label from "@radix-ui/react-label";
import { ApiService } from "../../services/api";
import { Proposal, LocalAnalysisResult } from "../../types/proposal";
import { MarkdownRenderer } from "./markdown-renderer";

export function AnalyzerClient() {
  const [proposal, setProposal] = useQueryState("q", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<LocalAnalysisResult | null>(null);
  const [backendResult, setBackendResult] = React.useState<string | null>(null);
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
      setBackendResult(response.analysis);
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
              <p className="text-sm font-medium text-[--color-accent]">AI Analysis</p>
            </div>
            <MarkdownRenderer content={backendResult} />
          </div>
        )}
      </div>
    </section>
  );
} 