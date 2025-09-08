import { gql } from "@apollo/client/core";

export const SpacesQuery = gql`
  query Spaces($first: Int, $skip: Int) {
    spaces(
      first: $first
      skip: $skip
      where:{verified:true}
      orderBy: "created"
      orderDirection: desc
    ) {
      id
      name
      about
      avatar
      domain
      members
    }
  }
`;
