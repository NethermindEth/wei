'use client';

import React, { useState, useEffect } from 'react';
import SwaggerUIWrapper from './swagger-ui-wrapper';
import { loadSwaggerSpecWithCache, SwaggerSpec } from '../../lib/swagger/loader';

/**
 * Client component for Agent Service API documentation
 *
 * This component handles loading the swagger specification and displays
 * it using the SwaggerUIWrapper component with proper error handling.
 */
export const AgentDocsClient: React.FC = () => {
  const [spec, setSpec] = useState<SwaggerSpec | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      setLoading(true);
      setError(null);

      // Load the agent service swagger specification
      const loadedSpec = loadSwaggerSpecWithCache('agent');
      setSpec(loadedSpec);
    } catch (err) {
      console.error('Failed to load agent service specification:', err);
      setError(err instanceof Error ? err.message : 'Failed to load API documentation');
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="relative mb-8">
          <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
          <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-purple-600 rounded-full animate-spin mx-auto" style={{ animationDelay: '-0.5s' }}></div>
          <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-indigo-600 rounded-full animate-spin mx-auto" style={{ animationDelay: '-1s' }}></div>
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3">Loading Agent Service API Documentation</h3>
        <p className="text-gray-600 text-lg">Please wait while we prepare the interactive documentation</p>
        <div className="mt-6 flex justify-center space-x-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
          <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-12 text-center">
        <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-2xl p-8 max-w-md mx-auto">
          <div className="text-red-600 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
          <h3 className="text-xl font-bold text-red-800 mb-3">
            Failed to Load Documentation
          </h3>
          <p className="text-red-700 mb-6 text-sm leading-relaxed">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-3 rounded-xl font-medium hover:from-red-700 hover:to-red-800 transition-all duration-300 transform hover:scale-105 shadow-lg"
          >
            <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!spec) {
    return (
      <div className="p-12 text-center">
        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 rounded-2xl p-8 max-w-md mx-auto">
          <div className="text-yellow-600 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
          <h3 className="text-xl font-bold text-yellow-800 mb-3">
            No Documentation Available
          </h3>
          <p className="text-yellow-700 text-sm leading-relaxed">
            The API specification could not be loaded. Please check the configuration and try again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <SwaggerUIWrapper
      spec={spec}
      title="Agent Service API"
      description="Interactive API documentation for the Wei Agent Service. Use the 'Try it out' feature to test endpoints directly from this page."
      tryItOutEnabled={true}
      className="agent-docs"
    />
  );
};

export default AgentDocsClient;
