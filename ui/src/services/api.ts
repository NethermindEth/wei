import { getApiUrl, getApiHeaders } from '../config/api';
import { Proposal, AnalysisResponse, ProposalArguments, CustomEvaluationRequest, CustomEvaluationResponse } from '../types/proposal';
import { EipResponse, EipsResponse, EipFilterRequest } from '../types/eip';
import { CacheService } from './cache';

export class ApiService {
  private static baseUrl = getApiUrl('');

  private static async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...getApiHeaders(),
          ...(options.headers || {})
        },
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        // Keep this error log for API errors
        console.error(`API error (${response.status}): ${errorText}`);
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      // Keep this error log for request failures
      console.error(`API request error for ${endpoint}:`, error instanceof Error ? error.message : error);
      throw error;
    }
  }

  static async analyzeProposal(proposal: Proposal): Promise<AnalysisResponse> {
    try {
      // Use a more specific type for the response
      const response = await this.makeRequest<{structured_response?: AnalysisResponse}>('/pre-filter', {
        method: 'POST',
        body: JSON.stringify(proposal),
      });
      
      // Response received successfully
      
      // Check if response has structured_response field
      if (response && response.structured_response) {
        return response.structured_response;
      } else {
        return response as unknown as AnalysisResponse;
      }
    } catch (error) {
      console.error('Error in analyzeProposal:', error instanceof Error ? error.message : error);
      throw error;
    }
  }
  
  static async customEvaluateProposal(request: CustomEvaluationRequest): Promise<CustomEvaluationResponse> {
    return this.makeRequest<CustomEvaluationResponse>('/pre-filter/custom', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request),
    });
  }

  /**
   * Refresh the cache for a proposal analysis and get fresh results
   */
  static async refreshProposalAnalysis(proposal: Proposal): Promise<AnalysisResponse> {
    const query = CacheService.createProposalAnalysisQuery(proposal);
    
    // Refresh the cache first
    await CacheService.refreshCache(query);
    
    // Then get the fresh result
    return this.analyzeProposal(proposal);
  }

  /**
   * Get only the arguments for and against a proposal
   */
  static async getProposalArguments(proposal: Proposal): Promise<{ arguments?: ProposalArguments, from_cache: boolean }> {
    try {
      const response = await this.makeRequest<{ arguments?: ProposalArguments, from_cache: boolean }>('/pre-filter/arguments', {
        method: 'POST',
        body: JSON.stringify(proposal),
      });
      
      // Additional validation to ensure we have valid arguments data
      if (response.arguments) {
        // Ensure both arrays exist and have content
        if (!Array.isArray(response.arguments.for_proposal)) {
          response.arguments.for_proposal = [];
        }
        if (!Array.isArray(response.arguments.against)) {
          response.arguments.against = [];
        }
      }
      
      return response;
    } catch (error) {
      console.error('Error in getProposalArguments:', error instanceof Error ? error.message : error);
      // Re-throw with more context
      throw new Error(
        error instanceof Error 
          ? `Failed to fetch proposal arguments: ${error.message}` 
          : 'Failed to fetch proposal arguments'
      );
    }
  }
  
  /**
   * Get a list of EIPs with pagination
   */
  static async getEips(params: EipFilterRequest = {}): Promise<EipsResponse> {
    try {
      // Build query string from params
      const queryParams = new URLSearchParams();
      if (params.eip_type) queryParams.append('eip_type', params.eip_type);
      if (params.category) queryParams.append('category', params.category);
      if (params.status) queryParams.append('status', params.status);
      if (params.author) queryParams.append('author', params.author);
      if (params.limit) queryParams.append('limit', params.limit.toString());
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.page_size) queryParams.append('page_size', params.page_size.toString());
      
      const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
      
      return this.makeRequest<EipsResponse>(`/eip${queryString}`, {
        method: 'GET',
      });
    } catch (error) {
      console.error('Error in getEips:', error instanceof Error ? error.message : error);
      throw new Error(
        error instanceof Error 
          ? `Failed to fetch EIPs: ${error.message}` 
          : 'Failed to fetch EIPs'
      );
    }
  }

  /**
   * Get a specific EIP by number
   */
  static async getEip(eipNumber: number, includeDiscussions: boolean = false): Promise<EipResponse> {
    try {
      const queryString = includeDiscussions ? '?include_discussions=true' : '';
      
      return this.makeRequest<EipResponse>(`/eip/${eipNumber}${queryString}`, {
        method: 'GET',
      });
    } catch (error) {
      console.error(`Error in getEip ${eipNumber}:`, error instanceof Error ? error.message : error);
      throw new Error(
        error instanceof Error 
          ? `Failed to fetch EIP-${eipNumber}: ${error.message}` 
          : `Failed to fetch EIP-${eipNumber}`
      );
    }
  }
}
