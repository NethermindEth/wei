'use client';

import React, { Suspense } from 'react';
import IndexerDocsClient from '@/components/docs/indexer-docs-client';
import { downloadSwaggerSpec } from '@/lib/swagger/loader';

/**
 * Indexer Service API Documentation Page
 * 
 * This page provides comprehensive API documentation for the Indexer Service,
 * including all endpoints, request/response schemas, and interactive testing.
 */
export default function IndexerDocsPage() {
  const handleDownloadSpec = () => {
    downloadSwaggerSpec('indexer', 'wei-indexer-service-api');
  };

  const handleViewReference = () => {
    // Scroll to the API documentation section
    const docsSection = document.querySelector('.swagger-ui-container');
    if (docsSection) {
      docsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-green-50 to-emerald-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-green-600/10 via-emerald-600/10 to-teal-600/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-green-100 text-green-800 text-sm font-medium mb-6">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
              Data Indexing Service
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 bg-clip-text text-transparent">
              Indexer Service API
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              Data indexing and retrieval service for governance proposals, actors, and protocols 
              across multiple networks with powerful search and filtering capabilities.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Version 1.0.0</span>
              </div>
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">OAS 3.0</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        {/* API Documentation Card */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Interactive API Documentation</h2>
                <p className="text-green-100 text-sm">Explore and test data indexing endpoints</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <Suspense fallback={
              <div className="p-12 text-center">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-green-200 border-t-green-600 rounded-full animate-spin mx-auto mb-6"></div>
                  <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-emerald-600 rounded-full animate-spin mx-auto" style={{ animationDelay: '-0.5s' }}></div>
                </div>
                <p className="text-gray-600 text-lg font-medium">Loading API documentation...</p>
                <p className="text-gray-500 text-sm mt-2">Please wait while we prepare the interactive documentation</p>
              </div>
            }>
              <IndexerDocsClient />
            </Suspense>
          </div>
        </div>

        {/* Info Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
          {/* Getting Started Card */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Getting Started</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-700 text-sm">
                  <strong>Base URL:</strong> 
                  <code className="ml-2 bg-green-100 text-green-800 px-2 py-1 rounded-lg font-mono text-xs">http://localhost:8001</code>
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                <span className="text-gray-700 text-sm">
                  <strong>Authentication:</strong> No authentication required
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
                <span className="text-gray-700 text-sm">
                  <strong>Content-Type:</strong> 
                  <code className="ml-2 bg-teal-100 text-teal-800 px-2 py-1 rounded-lg font-mono text-xs">application/json</code>
                </span>
              </div>
            </div>
          </div>

          {/* Key Features Card */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Key Features</h3>
            </div>
            <ul className="space-y-2">
              {[
                'Multi-network proposal indexing',
                'Advanced search & filtering',
                'Account information & voting history',
                'Webhook registration',
                'High-performance data access'
              ].map((feature, index) => (
                <li key={index} className="flex items-center space-x-3 group-hover:translate-x-1 transition-transform duration-300">
                  <div className="w-2 h-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"></div>
                  <span className="text-gray-700 text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Data Sources Card */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Data Sources</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
                <span className="text-gray-700 text-sm">
                  <strong>Networks:</strong> Ethereum, Polygon, Arbitrum, Optimism
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-700 text-sm">
                  <strong>Data Types:</strong> Proposals, votes, accounts, protocols
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                <span className="text-gray-700 text-sm">
                  <strong>Updates:</strong> Real-time indexing with configurable intervals
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Info Section */}
        <div className="mt-12 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-8 border border-green-100">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Explore Data?</h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Dive into the interactive API documentation above to discover how to access and query governance data 
              across multiple networks. Use the search and filtering capabilities to find exactly what you need.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button 
                onClick={handleViewReference}
                className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                Explore API Reference
              </button>
              <button 
                onClick={handleDownloadSpec}
                className="bg-white text-gray-700 px-6 py-3 rounded-xl font-medium hover:bg-gray-50 transition-all duration-300 border border-gray-200 shadow-sm"
              >
                Download OpenAPI Spec
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
