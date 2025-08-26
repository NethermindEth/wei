import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'API Documentation - Wei',
  description: 'Comprehensive API documentation for Wei services - Agent and Indexer APIs',
  keywords: ['API', 'documentation', 'agent', 'indexer', 'governance', 'OpenAPI', 'Swagger'],
};

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="docs-layout">
      {children}
    </div>
  );
}
