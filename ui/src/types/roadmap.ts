// Outcome-Driven Roadmap Types
// Based on the JSON Schema v1.0.0 specification

export interface RoadmapRequest {
  subject: string;
  kind: 'protocol' | 'DAO' | 'company' | 'country' | 'product' | 'other';
  scope: string;
  from?: string; // YYYY-MM-DD
  to?: string;   // YYYY-MM-DD
}

export interface RoadmapResponse {
  schema_version: string;
  domain: Domain;
  streams: string[];
  fitness_functions: FitnessFunction[];
  problems: Problem[];
  interventions: Intervention[];
  proposals?: Proposal[];
  links: Link[];
  sources: Source[];
  metadata?: Metadata;
}

export interface Domain {
  name: string;
  kind: string;
  scope: string;
  as_of: string; // ISO date
  research_window?: {
    from: string; // ISO date
    to: string;   // ISO date
  };
}

export interface FitnessFunction {
  id: string;
  name: string;
  stream: string;
  description?: string;
  unit?: string;
  direction: 'higher_is_better' | 'lower_is_better' | 'range';
  target?: {
    operator: '<=' | '>=' | 'between' | '==';
    value?: string | number | boolean;
    min?: number | string;
    max?: number | string;
  };
  current?: {
    value?: string | number | boolean;
    measured_at?: string; // ISO date
    source_ids?: string[];
  };
}

export interface Problem {
  id: string;
  title: string;
  stream: string;
  severity: 'High' | 'Medium' | 'Low';
  horizon: 'Now' | 'Next' | 'Later';
  fitness_function_id?: string;
  target?: string;
  current?: string;
  risk?: string;
  exit_criteria: string;
  status?: 'open' | 'monitoring' | 'resolved' | 'unclear';
  evidence?: {
    source_ids?: string[];
    notes?: string;
  };
}

export interface Intervention {
  id: string;
  title: string;
  label?: string;
  stream: string;
  status: 'shipped' | 'in_flight' | 'planned' | 'research' | 'abandoned' | 'stale' | 'unclear';
  stage?: string;
  release?: string;
  timeframe?: string;
  goal?: string;
  deps?: string[];
  risk_notes?: string;
  live_validation?: {
    verdict: 'live' | 'stale' | 'abandoned' | 'unclear';
    confidence?: number; // 0-1
    summary?: string;
    signals?: Signal[];
  };
  evidence?: {
    source_ids?: string[];
    notes?: string;
  };
}

export interface Signal {
  type: string;
  value?: string | number | boolean;
  observed_at: string; // ISO date
  source_id: string;
}

export interface Proposal {
  id: string;
  title: string;
  stage: 'Draft' | 'Review' | 'Vote' | 'Approved' | 'Implementing' | 'Done';
  owner?: string;
  problem_id?: string;
  linked_item_ids?: string[];
  notes?: string;
}

export interface Link {
  problem_id: string;
  intervention_id: string;
  link_quality: 'high' | 'medium' | 'low' | 'unclear';
  rationale?: string;
  source_ids?: string[];
}

export interface Source {
  id: string;
  type: string;
  title: string;
  url: string;
  published_at?: string; // ISO date
  retrieved_at: string; // ISO date
  credibility?: 'high' | 'medium' | 'low';
  notes?: string;
}

export interface Metadata {
  generator?: string;
  generated_at?: string; // ISO date-time
  notes?: string;
}

// UI-specific types for the roadmap component
export type ViewType = 'timeline' | 'kanban' | 'matrix' | 'problems' | 'proposals' | 'dependencies';

export interface RoadmapFilters {
  search: string;
  streams: string[];
  statuses: string[];
  releases: string[];
  severities: string[];
  horizons: string[];
}

export interface RoadmapStats {
  totalInterventions: number;
  totalProblems: number;
  totalProposals: number;
  byStatus: Record<string, number>;
  bySeverity: Record<string, number>;
  byHorizon: Record<string, number>;
}
