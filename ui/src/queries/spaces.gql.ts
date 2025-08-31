import { gql } from "@apollo/client/core";

export const GetSpacesNameAndId = gql`query GetSpacesNameAndId($first: Int = 1000, $skip: Int = 0) {
    spaces(where: {verified: true}, first: $first, skip: $skip) {
      id
      name
      proposalsCount
    }
  }`