"use client";

import * as React from "react";

interface HeroCtaProps {
  targetId?: string;
}

export function HeroCta({ targetId = "proposal" }: HeroCtaProps) {
  function onClick() {
    const el = document.getElementById(targetId) as HTMLTextAreaElement | null;
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    setTimeout(() => el.focus(), 250);
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className="accent-glow rounded-lg bg-gradient-to-br from-[--color-accent] to-[--color-accent-2] text-[#04141f] font-medium px-5 py-2.5 transition hover:brightness-110 border border-white/15 shadow"
      aria-controls={targetId}
    >
      Analyze
    </button>
  );
} 