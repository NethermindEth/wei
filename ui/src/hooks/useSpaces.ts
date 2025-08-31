'use client';

import { useState, useEffect } from 'react';
import { apolloClient } from '../services/graphql';
import { GetSpacesNameAndId } from '../queries/spaces.gql';
import { Space, GetSpacesNameAndIdResponse } from '../types/graphql';

export function useSpaces() {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSpaces() {
      try {
        setLoading(true);
        const result = await apolloClient.query<GetSpacesNameAndIdResponse>({
          query: GetSpacesNameAndId,
          variables: { first: 1000, skip: 0 },
          fetchPolicy: 'cache-first'
        });

        if (result.data?.spaces) {
          const spacesWithProposals = result.data.spaces.filter(space => space.proposalsCount > 0);
          setSpaces(spacesWithProposals);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch spaces');
        setSpaces([]);
      } finally {
        setLoading(false);
      }
    }

    fetchSpaces();
  }, []);

  return { spaces, loading, error };
}
