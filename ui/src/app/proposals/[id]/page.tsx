import { Suspense } from "react";
import { ProposalPage } from "../../../components/proposals/proposal-page";

export default async function ProposalDetails({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0b0f14] flex items-center justify-center">
        <div className="text-white/60">Loading proposal...</div>
      </div>
    }>
      <ProposalPage proposalId={id} />
    </Suspense>
  );
}
