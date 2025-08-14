"use client";

import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  const [viewMode, setViewMode] = React.useState<"html" | "raw">("html");

  if (!content) return null;

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Toggle Controls */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => setViewMode("html")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            viewMode === "html"
              ? "bg-white/10 text-[#9fb5cc] font-semibold"
              : "bg-[--color-accent]  text-white  hover:bg-white/20 hover:text-white"
          }`}
        >
          HTML View
        </button>
        <button
          type="button"
          onClick={() => setViewMode("raw")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            viewMode === "raw"
              ? "bg-white/10 text-[#9fb5cc] font-semibold"
              : "bg-[--color-accent] text-white hover:bg-white/20 hover:text-white"
          }`}
        >
          Raw Markdown
        </button>
      </div>

      {/* Content Display */}
      {viewMode === "html" ? (
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Custom styling for different Markdown elements
              h1: ({ children }) => (
                <h1 className="text-lg font-semibold text-[--color-accent] mb-2">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-base font-semibold text-[--color-accent] mb-2">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold text-[--color-accent] mb-1">{children}</h3>
              ),
              p: ({ children }) => (
                <p className="text-sm leading-relaxed mb-2">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc pl-6 marker:text-[--color-accent] mb-2">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal pl-6 marker:text-[--color-accent] mb-2">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="text-sm mb-1">{children}</li>
              ),
              code: ({ children, className }) => {
                const isInline = !className;
                if (isInline) {
                  return (
                    <code className="bg-white/10 px-1.5 py-0.5 rounded text-[--color-accent-2] text-xs font-mono">
                      {children}
                    </code>
                  );
                }
                return (
                  <code className="block bg-white/10 p-3 rounded text-[--color-accent-2] text-xs font-mono overflow-x-auto">
                    {children}
                  </code>
                );
              },
              pre: ({ children }) => (
                <pre className="bg-white/10 p-3 rounded text-[--color-accent-2] text-xs font-mono overflow-x-auto mb-2">
                  {children}
                </pre>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-[--color-accent] pl-4 italic text-[#9fb5cc] mb-2">
                  {children}
                </blockquote>
              ),
              table: ({ children }) => (
                <div className="overflow-x-auto mb-2">
                  <table className="min-w-full border border-white/20 rounded">
                    {children}
                  </table>
                </div>
              ),
              th: ({ children }) => (
                <th className="border border-white/20 px-3 py-2 text-left text-sm font-medium bg-white/5">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="border border-white/20 px-3 py-2 text-sm">
                  {children}
                </td>
              ),
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[--color-accent] hover:text-[--color-accent-2] underline"
                >
                  {children}
                </a>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-white">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-[#9fb5cc]">{children}</em>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      ) : (
        <div className="bg-[#04141f] border border-white/20 rounded-lg p-4">
          <pre className="text-xs text-[#9fb5cc] font-mono whitespace-pre-wrap overflow-x-auto">
            {content}
          </pre>
        </div>
      )}
    </div>
  );
}
