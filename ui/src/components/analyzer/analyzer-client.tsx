"use client";

import * as React from "react";
import { useQueryState } from "nuqs";
import * as Label from "@radix-ui/react-label";

interface AnalysisResult {
  summary: string;
  risks: string[];
  score: number; // 0..100
}

function analyzeLocally(input: string): AnalysisResult {
  const text = input.trim();
  if (!text) return { summary: "", risks: [], score: 0 };

  const lengthScore = Math.min(100, Math.floor(text.length / 8));
  const hasNumbers = /\d/.test(text) ? 10 : 0;
  const hasLinks = /(https?:\/\/|ipfs:\/\/)/i.test(text) ? -10 : 0;
  const hasAudit = /(audit|security|risk|mitigate)/i.test(text) ? 15 : 0;
  const hasTimeline = /(day|week|month|q\d|deadline|epoch)/i.test(text) ? 10 : 0;

  const score = Math.max(
    0,
    Math.min(100, lengthScore + hasNumbers + hasLinks + hasAudit + hasTimeline)
  );

  const risks: string[] = [];
  if (!/rationale|motivation/i.test(text)) risks.push("Missing rationale section");
  if (!/budget|fund|cost|amount/i.test(text)) risks.push("No budget details");
  if (!/timeline|milestone|deliverable/i.test(text))
    risks.push("No timeline or milestones");
  if (/multi[- ]?sig|multisig/i.test(text) && !/signer|threshold/i.test(text))
    risks.push("Multisig mentioned without signer/threshold details");

  const summary =
    score > 70
      ? "Proposal appears well-formed with reasonable detail."
      : score > 40
      ? "Proposal has promise but lacks important specifics."
      : "Proposal is likely incomplete and requires substantial clarification.";

  return { summary, risks, score };
}

export function AnalyzerClient() {
  const [proposal, setProposal] = useQueryState("q", {
    history: "push",
    shallow: true,
    clearOnDefault: true,
  });
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<AnalysisResult | null>(null);

  function onAnalyze() {
    if (!proposal?.trim()) {
      setResult(null);
      return;
    }
    setIsLoading(true);
    // Simulate compute delay
    setTimeout(() => {
      const r = analyzeLocally(proposal);
      setResult(r);
      setIsLoading(false);
    }, 300);
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
        {!result && <p className="text-sm text-[#7d93ab]">Feedback will appear here.</p>}
        {result && (
          <div className="grid gap-3">
            <div className="flex items-center gap-3">
              <div
                aria-label="score"
                className="h-8 w-8 rounded-full grid place-items-center font-semibold text-[#04141f]"
                style={{ background: `conic-gradient(var(--accent) ${result.score}%, #0b2233 0)` }}
              >
                <span className="text-[10px] text-white/90">{result.score}</span>
              </div>
              <p className="text-sm">{result.summary}</p>
            </div>
            {result.risks.length > 0 && (
              <ul className="list-disc pl-6 marker:text-[--color-accent] text-sm">
                {result.risks.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </section>
  );
} 