import { Suspense } from "react";
import { AnalyzerClient } from "../components/analyzer/analyzer-client";

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0b0f14] flex items-center justify-center">
      <div className="text-white/60">Loading...</div>
    </div>}>
      <AnalyzerClient />
    </Suspense>
  );
}
