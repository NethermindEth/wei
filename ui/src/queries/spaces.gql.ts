import { gql } from "@apollo/client/core";

export const SpacesQuery = gql`
  query Spaces($first: Int, $skip: Int) {
    spaces(
      first: $first
      skip: $skip
      orderBy: "created"
      where:{verified:true}
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
