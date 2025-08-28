'use client';

import React, { useEffect, useRef } from 'react';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import { SwaggerSpec } from '../../lib/swagger/loader';

interface SwaggerUIWrapperProps {
  /**
   * The swagger specification to display
   */
  spec: SwaggerSpec;
  /**
   * Custom title for the documentation
   */
  title?: string;
  /**
   * Custom description for the documentation
   */
  description?: string;
  /**
   * Whether to show the try it out functionality
   */
  tryItOutEnabled?: boolean;
  /**
   * Custom CSS class names
   */
  className?: string;
}

/**
 * Generic Swagger UI wrapper component for displaying API documentation
 * 
 * This component provides a clean, production-ready interface for displaying
 * OpenAPI specifications with customizable options and proper error handling.
 */
export const SwaggerUIWrapper: React.FC<SwaggerUIWrapperProps> = ({
  spec,
  title,
  description,
  tryItOutEnabled = true,
  className = '',
}) => {
  const swaggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Clean up any existing Swagger UI instances
    if (swaggerRef.current) {
      const existingSwagger = swaggerRef.current.querySelector('.swagger-ui');
      if (existingSwagger) {
        existingSwagger.remove();
      }
    }
  }, [spec]);

  // Custom Swagger UI configuration
  const swaggerConfig = {
    spec,
    dom_id: `#swagger-ui-${Date.now()}`, // Unique ID to prevent conflicts
    deepLinking: true,
    displayOperationId: false,
    defaultModelsExpandDepth: 1,
    defaultModelExpandDepth: 1,
    defaultModelRendering: 'example' as const,
    displayRequestDuration: true,
    docExpansion: 'list' as const,
    filter: true,
    maxDisplayedTags: 20,
    showExtensions: true,
    showCommonExtensions: true,
    tryItOutEnabled,
    requestInterceptor: (request: Record<string, unknown>) => {
      // Add any custom request headers or modifications here
      return request;
    },
    responseInterceptor: (response: Record<string, unknown>) => {
      // Add any custom response handling here
      return response;
    },
    onComplete: () => {
      // Custom completion handler
      console.log('Swagger UI loaded successfully');
    },
    onFailure: (data: Record<string, unknown>) => {
      // Custom error handler
      console.error('Swagger UI failed to load:', data);
    },
  };

  return (
    <div className={`swagger-ui-container ${className}`}>
      {title && (
        <div className="swagger-header mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
              {description && (
                <p className="text-gray-600 text-lg mt-1">{description}</p>
              )}
            </div>
          </div>
          
          {/* API Info Badges */}
          <div className="flex flex-wrap gap-3 mb-6">
            <div className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 rounded-full text-sm font-medium border border-green-200">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Version 1.0.0
            </div>
            <div className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 rounded-full text-sm font-medium border border-blue-200">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
              OAS 3.0
            </div>
            <div className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 rounded-full text-sm font-medium border border-purple-200">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
              Interactive
            </div>
          </div>
        </div>
      )}

      <div
        ref={swaggerRef}
        className="swagger-ui-wrapper"
        style={{ 
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}
      >
        <SwaggerUI {...swaggerConfig} />
      </div>
      
      {/* Custom CSS for Swagger UI */}
      <style dangerouslySetInnerHTML={{
        __html: `
          .swagger-ui .topbar {
            display: none;
          }
          
          .swagger-ui .info {
            margin: 0 0 20px 0;
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 12px;
            border: 1px solid #e2e8f0;
          }
          
          .swagger-ui .info .title {
            color: #1e293b;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
          }
          
          .swagger-ui .info .description {
            color: #475569;
            font-size: 16px;
            line-height: 1.6;
          }
          
          .swagger-ui .scheme-container {
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          }
          
          .swagger-ui .opblock {
            border-radius: 12px;
            margin: 16px 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
          }
          
          .swagger-ui .opblock.opblock-get {
            border-color: #3b82f6;
          }
          
          .swagger-ui .opblock.opblock-post {
            border-color: #10b981;
          }
          
          .swagger-ui .opblock.opblock-put {
            border-color: #f59e0b;
          }
          
          .swagger-ui .opblock.opblock-delete {
            border-color: #ef4444;
          }
          
          .swagger-ui .opblock-summary {
            border-radius: 12px 12px 0 0;
          }
          
          .swagger-ui .opblock-summary-method {
            border-radius: 8px;
            font-weight: 600;
          }
          
          .swagger-ui .btn.execute {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
          }
          
          .swagger-ui .btn.execute:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 25px -5px rgba(59, 130, 246, 0.4);
          }
          
          .swagger-ui .btn.try-out__btn {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
          }
          
          .swagger-ui .btn.try-out__btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 25px -5px rgba(139, 92, 246, 0.4);
          }
          
          .swagger-ui .responses-table {
            border-radius: 8px;
            overflow: hidden;
          }
          
          .swagger-ui .responses-table th {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            color: #1e293b;
            font-weight: 600;
          }
          
          .swagger-ui .model {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
          }
          
          .swagger-ui .model-title {
            color: #1e293b;
            font-weight: 600;
          }
          
          .swagger-ui .parameter__name {
            color: #1e293b;
            font-weight: 600;
          }
          
          .swagger-ui .parameter__type {
            color: #64748b;
            font-size: 12px;
          }
          
          .swagger-ui .parameter__required {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
          }
        `
      }} />
    </div>
  );
};

export default SwaggerUIWrapper;
