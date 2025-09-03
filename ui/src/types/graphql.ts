// GraphQL Types for Proposals and Spaces


export interface Space {
  id: string;
  name: string;
  proposalsCount: number;
  avatar: string;
  verified: boolean;
  domain: string;
  members: string[];
}

export interface Proposal {
  id: string;
  title: string;
  body: string;
  author: string;
  space: Space;
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