"use client";

import { NuqsAdapter } from "nuqs/adapters/next/app";
import * as React from "react";
import { AuthProvider } from "../contexts/auth-context";

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <NuqsAdapter>
      <AuthProvider>
        {children}
      </AuthProvider>
    </NuqsAdapter>
  );
} 