/**
 * Swagger specification loader utilities
 * 
 * This module provides functions for loading and managing OpenAPI specifications
 * with proper error handling, caching, and validation.
 */

import agentSpec from './agent-swagger.json';
import indexerSpec from './indexer-swagger.json';

export interface SwaggerSpec {
  openapi: string;
  info: {
    title: string;
    description: string;
    version: string;
  };
  paths: Record<string, unknown>;
  components?: Record<string, unknown>;
  tags?: Array<{ name: string; description: string }>;
}

/**
 * Load a swagger specification by name
 * 
 * @param specName - Name of the specification to load
 * @returns The parsed specification
 * @throws Error if the specification name is invalid
 */
export function loadSwaggerSpec(specName: string): SwaggerSpec {
  const specs: Record<string, SwaggerSpec> = {
    agent: agentSpec as SwaggerSpec,
    indexer: indexerSpec as SwaggerSpec,
  };

  if (!specs[specName]) {
    throw new Error(`Unknown specification: ${specName}`);
  }

  const spec = specs[specName];
  
  // Validate the specification
  const validation = validateSwaggerSpec(spec);
  if (!validation.isValid) {
    throw new Error(`Invalid swagger specification: ${validation.errors.join(', ')}`);
  }
  
  return spec;
}

/**
 * Validate a swagger specification object
 * 
 * @param spec - The swagger specification to validate
 * @returns Object containing validation result and any errors
 */
export function validateSwaggerSpec(spec: unknown): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check if spec is an object
  if (!spec || typeof spec !== 'object') {
    errors.push('Specification must be an object');
    return { isValid: false, errors };
  }
  
  const specObj = spec as Record<string, unknown>;
  
  // Check required top-level properties
  if (!specObj.openapi) {
    errors.push('Missing required property: openapi');
  }
  
  if (!specObj.info) {
    errors.push('Missing required property: info');
  } else {
    const info = specObj.info as Record<string, unknown>;
    if (!info.title) errors.push('Missing required property: info.title');
    if (!info.version) errors.push('Missing required property: info.version');
  }
  
  if (!specObj.paths) {
    errors.push('Missing required property: paths');
  }
  
  // Check if paths object has at least one endpoint
  if (specObj.paths && typeof specObj.paths === 'object') {
    const paths = specObj.paths as Record<string, unknown>;
    if (Object.keys(paths).length === 0) {
      errors.push('Paths object must contain at least one endpoint');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Get available swagger specifications
 * 
 * @returns Array of available specification names
 */
export function getAvailableSpecs(): string[] {
  return ['agent', 'indexer'];
}

/**
 * Cache for loaded specifications to avoid repeated processing
 */
const specCache = new Map<string, SwaggerSpec>();

/**
 * Load a swagger specification with caching
 * 
 * @param specName - Name of the specification to load
 * @param forceRefresh - Whether to force refresh the cache
 * @returns The cached or newly loaded specification
 */
export function loadSwaggerSpecWithCache(
  specName: string, 
  forceRefresh: boolean = false
): SwaggerSpec {
  // Check cache first
  if (!forceRefresh && specCache.has(specName)) {
    return specCache.get(specName)!;
  }
  
  // Load and cache the specification
  const spec = loadSwaggerSpec(specName);
  
  // Cache the validated specification
  specCache.set(specName, spec);
  
  return spec;
}

/**
 * Clear the specification cache
 * 
 * @param specName - Optional specific specification to clear, or all if not provided
 */
export function clearSpecCache(specName?: string): void {
  if (specName) {
    specCache.delete(specName);
  } else {
    specCache.clear();
  }
}

/**
 * Download a swagger specification as a JSON file
 * 
 * @param specName - Name of the specification to download
 * @param filename - Optional custom filename (without extension)
 */
export function downloadSwaggerSpec(specName: string, filename?: string): void {
  try {
    const spec = loadSwaggerSpec(specName);
    const defaultFilename = filename || `${specName}-api-spec`;
    
    // Create blob with the specification
    const blob = new Blob([JSON.stringify(spec, null, 2)], {
      type: 'application/json'
    });
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${defaultFilename}.json`;
    
    // Trigger download
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error(`Failed to download ${specName} specification:`, error);
    // You could show a toast notification here
  }
}
