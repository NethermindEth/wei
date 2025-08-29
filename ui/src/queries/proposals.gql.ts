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


export const GetProposalsBySpaceId = gql`query ProposalsBySpaceId( $space: String! $first: Int = 1000
        $skip: Int = 0) {
  proposals(
    where: { space: $space }
    first: $first
    skip: $skip
    orderBy: "created"
  ) {
 id
      title
      body
      author
  }
}
`