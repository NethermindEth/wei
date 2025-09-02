import { gql } from "@apollo/client/core";

export const ProposalsQuery = gql`
  query Proposals($first: Int, $skip: Int, $space: String) {
    proposals(
      first: $first
      skip: $skip
      orderBy: "created"
      orderDirection: desc
      where: { space: $space }
    ) {
      id
      title
      body
      author
      space {
        id
        name
        avatar
        verified
      }
    }
  }
`;

export const AllProposalsQuery = gql`
  query AllProposals($first: Int, $skip: Int) {
    proposals(
      first: $first
      skip: $skip
      orderBy: "created"
      orderDirection: desc
    ) {
      id
      title
      body
      author
      space {
        id
        name
        avatar
        verified
      }
    }
  }
`;