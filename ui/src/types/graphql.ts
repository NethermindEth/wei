// GraphQL Types for Proposals and Spaces

export interface Proposal {
  id: string;
  title: string;
  body: string;
  author: string;
}

export interface Space {
  id: string;
  name: string;
  proposalsCount: number;
}

// Query Response Types
export interface ProposalsQueryResponse {
  proposals: Proposal[];
}

export interface ProposalsBySpaceIdResponse {
  proposals: Proposal[];
}

export interface GetSpacesNameAndIdResponse {
  spaces: Space[];
}