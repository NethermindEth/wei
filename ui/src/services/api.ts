import { getApiUrl, getApiHeaders } from '../config/api';
import { Proposal, AnalysisResponse, CustomEvaluationRequest, CustomEvaluationResponse } from '../types/proposal';

export class ApiService {
  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = getApiUrl(endpoint);
    
    try {
      // Create a new options object to avoid header overrides
      const mergedOptions = { ...options };
      
      // Ensure headers are properly merged
      mergedOptions.headers = {
        ...getApiHeaders(),
        ...(options.headers || {})
      };
      
      const response = await fetch(url, mergedOptions);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  static async analyzeProposal(proposal: Proposal): Promise<AnalysisResponse> {
    return this.makeRequest<AnalysisResponse>('/pre-filter', {
      method: 'POST',
      body: JSON.stringify(proposal),
    });
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
}
