import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Indexer Service API Documentation - Wei',
  description: 'Comprehensive API documentation for the Wei Indexer Service - Data indexing and retrieval for governance proposals',
  keywords: ['API', 'documentation', 'indexer', 'governance', 'proposals', 'data', 'OpenAPI', 'Swagger'],
};

export default function IndexerDocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="indexer-docs-layout">
      {children}
    </div>
  );
}
