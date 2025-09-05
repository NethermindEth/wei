import { gql } from "@apollo/client/core";

export const GetProposalByIdQuery = gql`
  query GetProposalById($id: String!) {
    proposal(id: $id) {
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
