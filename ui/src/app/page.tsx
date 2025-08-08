import Image from "next/image";
import { Suspense } from "react";
import { AnalyzerClient } from "../components/analyzer/analyzer-client";

export default function Home() {
  return (
    <main className="min-h-dvh flex flex-col items-center justify-center gap-10 sm:gap-14 px-4 py-10">
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="relative">
          <Image
            src="/wei.png"
            alt="wei logo"
            width={160}
            height={160}
            priority
            className="drop-shadow-[0_0_24px_rgba(25,227,255,0.35)]"
          />
          <div className="pointer-events-none absolute inset-0 rounded-full blur-2xl opacity-50" />
        </div>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">
          wei – Governance Proposal Analyzer
        </h1>
        <p className="max-w-prose text-balance text-sm sm:text-base text-[#9fb5cc]">
          Paste a proposal, press Analyze, and get concise feedback.
        </p>
      </div>

      <Suspense fallback={<div className="h-[360px] w-full max-w-3xl rounded-xl bg-white/5" />}>
        <AnalyzerClient />
      </Suspense>
    </main>
  );
}
