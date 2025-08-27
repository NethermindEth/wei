import { gql } from "@apollo/client/core";

export const ProposalsQuery = gql`
  query Proposals( $first: Int = 1000
        $skip: Int = 0){
    proposals(first: $first, skip: $skip, orderBy: "created") {
      id
      title
      body
      author
    }
  }
`;