"use client";

import { NuqsAdapter } from "nuqs/adapters/next/app";
import * as React from "react";

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return <NuqsAdapter>{children}</NuqsAdapter>;
} 