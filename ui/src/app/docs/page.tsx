'use client';

import React from 'react';
import Link from 'next/link';
import { downloadSwaggerSpec } from '@/lib/swagger/loader';

/**
 * Main API Documentation Index Page
 * 
 * This page serves as the entry point for all API documentation,
 * providing navigation to individual service documentation pages.
 */
export default function DocsIndexPage() {
  const handleDownloadAllSpecs = () => {
    // Download both specifications
    downloadSwaggerSpec('agent', 'wei-agent-service-api');
    setTimeout(() => {
      downloadSwaggerSpec('indexer', 'wei-indexer-service-api');
    }, 500); // Small delay to prevent browser blocking multiple downloads
  };

  const services = [
    {
      name: 'Agent Service',
      description: 'AI-powered governance proposal analysis service that provides intelligent insights and structured feedback on DAO proposals.',
      href: '/docs/agent',
      color: 'blue',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      features: [
        'AI-powered proposal quality assessment',
        'Structured analysis with confidence scoring',
        'Submitter intentions analysis',
        'Comprehensive proposal evaluation metrics',
        'Real-time analysis with detailed feedback'
      ],
      endpoints: [
        { method: 'POST', path: '/analyze', description: 'Analyze a proposal' },
        { method: 'GET', path: '/analyze/{id}', description: 'Get analysis by ID' },
        { method: 'GET', path: '/analyses/proposal/{id}', description: 'Get analyses for a proposal' },
        { method: 'GET', path: '/health', description: 'Health check' }
      ]
    },
    {
      name: 'Indexer Service',
      description: 'Data indexing and retrieval service for governance proposals, actors, and protocols across multiple networks.',
      href: '/docs/indexer',
      color: 'green',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
      ),
      features: [
        'Multi-network proposal indexing and retrieval',
        'Advanced search and filtering capabilities',
        'Account information and voting history',
        'Webhook registration for real-time updates',
        'High-performance data access with caching'
      ],
      endpoints: [
        { method: 'GET', path: '/proposals/{id}', description: 'Get proposal by ID' },
        { method: 'GET', path: '/proposals/network/{network}', description: 'Get proposals by network' },
        { method: 'GET', path: '/proposals/search', description: 'Search proposals' },
        { method: 'GET', path: '/accounts', description: 'Get account information' },
        { method: 'POST', path: '/hooks', description: 'Register webhook' },
        { method: 'GET', path: '/health', description: 'Health check' }
      ]
    }
  ];

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
              API Documentation Hub
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Wei API Documentation
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              Comprehensive API documentation for all Wei services. Explore our powerful APIs for 
              governance proposal analysis and data indexing across multiple networks.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4">
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">2 Services</span>
              </div>
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">OpenAPI 3.0</span>
              </div>
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Interactive Docs</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        {/* Service Cards */}
        <div className="grid gap-8 lg:grid-cols-2 mb-16">
          {services.map((service) => (
            <div
              key={service.name}
              className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2"
            >
              {/* Service Header */}
              <div className="flex items-center mb-6">
                <div className={`w-16 h-16 bg-gradient-to-br ${
                  service.color === 'blue' 
                    ? 'from-blue-500 to-purple-600' 
                    : 'from-green-500 to-emerald-600'
                } rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300`}>
                  {service.icon}
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-1">
                    {service.name}
                  </h2>
                  <p className="text-gray-600 text-sm">
                    {service.color === 'blue' ? 'AI Analysis Service' : 'Data Indexing Service'}
                  </p>
                </div>
              </div>

              <p className="text-gray-700 mb-6 leading-relaxed">
                {service.description}
              </p>

              {/* Features */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Key Features
                </h3>
                <ul className="space-y-2">
                  {service.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start group-hover:translate-x-1 transition-transform duration-300">
                      <div className={`w-2 h-2 rounded-full mr-3 mt-2 ${
                        service.color === 'blue' 
                          ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                          : 'bg-gradient-to-r from-green-500 to-emerald-500'
                      }`}></div>
                      <span className="text-gray-700 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Endpoints Preview */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  Available Endpoints
                </h3>
                <div className="space-y-2">
                  {service.endpoints.slice(0, 3).map((endpoint, endpointIndex) => (
                    <div key={endpointIndex} className="flex items-center space-x-3 text-sm group-hover:translate-x-1 transition-transform duration-300">
                      <span className={`px-2 py-1 rounded text-xs font-mono font-semibold ${
                        endpoint.method === 'GET' ? 'bg-green-100 text-green-800 border border-green-200' :
                        endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                        'bg-gray-100 text-gray-800 border border-gray-200'
                      }`}>
                        {endpoint.method}
                      </span>
                      <code className="text-gray-700 font-mono bg-gray-50 px-2 py-1 rounded text-xs">{endpoint.path}</code>
                    </div>
                  ))}
                  {service.endpoints.length > 3 && (
                    <p className="text-gray-500 text-sm mt-2">
                      +{service.endpoints.length - 3} more endpoints available...
                    </p>
                  )}
                </div>
              </div>

              {/* CTA Button */}
              <Link
                href={service.href}
                className={`inline-flex items-center px-6 py-3 rounded-xl font-medium text-white transition-all duration-300 transform hover:scale-105 shadow-lg ${
                  service.color === 'blue' 
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700' 
                    : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700'
                }`}
              >
                View Documentation
                <svg className="ml-2 -mr-1 w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </Link>
            </div>
          ))}
        </div>

        {/* Additional Information */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <svg className="w-6 h-6 text-blue-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Getting Started
          </h3>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="group">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v-1H7v-1H5v-1H3l1-1 1-1 1-1h.586L5.757 9.757A6 6 0 1112.243 2.243L15 5v2z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-900">Authentication</h4>
              </div>
              <p className="text-gray-600 text-sm leading-relaxed">
                Agent Service requires API key authentication via <code className="bg-gray-100 px-2 py-1 rounded-lg font-mono text-xs">x-api-key</code> header.
                Indexer Service endpoints are publicly accessible.
              </p>
            </div>
            <div className="group">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-900">Rate Limits</h4>
              </div>
              <p className="text-gray-600 text-sm leading-relaxed">
                Both services implement rate limiting to ensure fair usage. 
                Check individual endpoint documentation for specific limits.
              </p>
            </div>
            <div className="group">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform duration-300">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L9.172 14.828M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-gray-900">Support</h4>
              </div>
              <p className="text-gray-600 text-sm leading-relaxed">
                For technical support or questions about our APIs, 
                please refer to our GitHub repository or contact the development team.
              </p>
            </div>
          </div>
        </div>

        {/* Download All Specs Section */}
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-100">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Download All API Specifications</h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Get both OpenAPI specifications in JSON format for offline use, 
              integration with your development tools, or API client generation.
            </p>
            <button 
              onClick={handleDownloadAllSpecs}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download All OpenAPI Specs
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
