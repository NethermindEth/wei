import { getApiUrl, getApiHeaders } from '../config/api';
import { Proposal, AnalysisResponse, CustomEvaluationRequest, CustomEvaluationResponse } from '../types/proposal';
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
        console.error(`API error (${response.status}): ${errorText}`);
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request error for ${endpoint}:`, error);
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
      
      // Debug logging
      
      // Check if response has structured_response field
      if (response && response.structured_response) {
        return response.structured_response;
      } else {
        return response as unknown as AnalysisResponse;
      }
    } catch (error) {
      console.error('Error in analyzeProposal:', error);
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
}
