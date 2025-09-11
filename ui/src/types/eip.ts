export interface Eip {
  eip_number: number;
  title: string;
  author: string[];
  status: string;
  eip_type: string;
  category?: string;
  created: string;
  requires?: string[];
  description: string;
  content: string;
  github_url: string;
  discussions?: EipDiscussion[];
}

export interface EipDiscussion {
  id: string;
  author: string;
  content: string;
  created_at: string;
  vote?: {
    type: 'for' | 'against' | 'neutral';
  };
}

export interface EipsResponse {
  eips: Eip[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  from_cache: boolean;
}

export interface EipResponse {
  eip: Eip;
  from_cache: boolean;
}

export interface EipFilterRequest {
  eip_type?: string;
  category?: string;
  status?: string;
  author?: string;
  limit?: number;
  page?: number;
  page_size?: number;
}
