import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Agent Service API Documentation - Wei',
  description: 'Comprehensive API documentation for the Wei Agent Service - AI-powered governance proposal analysis',
  keywords: ['API', 'documentation', 'agent', 'governance', 'proposal', 'analysis', 'OpenAPI', 'Swagger'],
};

export default function AgentDocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="agent-docs-layout">
      {children}
    </div>
  );
}
