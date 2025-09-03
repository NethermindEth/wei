import { useState, useEffect } from 'react';
import { apolloClient } from '../services/graphql';
import { SpacesQuery } from '../queries/spaces.gql';

export interface Space {
  id: string;
  name: string;
  about?: string;
  avatar?: string;
  verified?: boolean;
  domain?: string;
  members?: number;
}

interface SpacesData {
  spaces: Space[];
}

interface UseSpacesResult {
  spaces: Space[];
  loading: boolean;
  error: Error | null;
}

export function useSpaces(): UseSpacesResult {
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchSpaces = async () => {
      setLoading(true);
      try {
        const result = await apolloClient.query<SpacesData>({
          query: SpacesQuery,
          variables: {
            first: 1000,
            skip: 0
          }
        });

        if (result.data?.spaces) {
          // Filter out spaces without names and sort by member count
          const validSpaces = result.data.spaces
            .filter(space => space.name)
            .sort((a, b) => (b.members || 0) - (a.members || 0));
          setSpaces(validSpaces);
        }
        setError(null);
      } catch (err) {
        console.error('Failed to fetch spaces:', err);
        setError(err instanceof Error ? err : new Error('Failed to fetch spaces'));
      } finally {
        setLoading(false);
      }
    };

    fetchSpaces();
  }, []);

  return {
    spaces,
    loading,
    error
  };
}
