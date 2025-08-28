'use client';

import React, { Suspense } from 'react';
import AgentDocsClient from '@/components/docs/agent-docs-client';
import { downloadSwaggerSpec } from '@/lib/swagger/loader';

/**
 * Agent Service API Documentation Page
 * 
 * This page provides comprehensive API documentation for the Agent Service,
 * including all endpoints, request/response schemas, and interactive testing.
 */
export default function AgentDocsPage() {
  const handleDownloadSpec = () => {
    downloadSwaggerSpec('agent', 'wei-agent-service-api');
  };

  const handleViewReference = () => {
    // Scroll to the API documentation section
    const docsSection = document.querySelector('.swagger-ui-container');
    if (docsSection) {
      docsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-indigo-600/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-6">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              API Documentation
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Agent Service API
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              AI-powered governance proposal analysis service that provides intelligent insights 
              and structured feedback on DAO proposals.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Version 1.0.0</span>
              </div>
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
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
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Interactive API Documentation</h2>
                <p className="text-blue-100 text-sm">Test endpoints directly from this page</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <Suspense fallback={
              <div className="p-12 text-center">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-6"></div>
                  <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-purple-600 rounded-full animate-spin mx-auto" style={{ animationDelay: '-0.5s' }}></div>
                </div>
                <p className="text-gray-600 text-lg font-medium">Loading API documentation...</p>
                <p className="text-gray-500 text-sm mt-2">Please wait while we prepare the interactive documentation</p>
              </div>
            }>
              <AgentDocsClient />
            </Suspense>
          </div>
        </div>

        {/* Info Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
          {/* Getting Started Card */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Getting Started</h3>
            </div>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-gray-700">
                  <strong>Base URL:</strong> 
                  <code className="ml-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-lg font-mono text-sm">http://localhost:8000</code>
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="text-gray-700">
                  <strong>Authentication:</strong> 
                  <code className="ml-2 bg-purple-100 text-purple-800 px-3 py-1 rounded-lg font-mono text-sm">x-api-key</code> header
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                <span className="text-gray-700">
                  <strong>Content-Type:</strong> 
                  <code className="ml-2 bg-indigo-100 text-blue-800 px-3 py-1 rounded-lg font-mono text-sm">application/json</code>
                </span>
              </div>
            </div>
          </div>

          {/* Key Features Card */}
          <div className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Key Features</h3>
            </div>
            <ul className="space-y-3">
              {[
                'AI-powered proposal quality assessment',
                'Structured analysis with confidence scoring',
                'Submitter intentions analysis',
                'Comprehensive proposal evaluation metrics',
                'Real-time analysis with detailed feedback'
              ].map((feature, index) => (
                <li key={index} className="flex items-center space-x-3 group-hover:translate-x-1 transition-transform duration-300">
                  <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
                  <span className="text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Additional Info Section */}
        <div className="mt-12 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-8 border border-indigo-100">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Ready to Get Started?</h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Explore the interactive API documentation above to understand how to integrate with our AI-powered governance analysis service. 
              Use the &quot;Try it out&quot; feature to test endpoints directly from this page.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button 
                onClick={handleViewReference}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                View API Reference
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
