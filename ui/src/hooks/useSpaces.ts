import { useState, useEffect, useCallback, useRef } from 'react';
import { apolloClient } from '../services/graphql';
import { GetSpacesNameAndId } from '../queries/spaces.gql';

export interface Space {
  id: string;
  name: string;
}

interface SpacesData {
  spaces: Space[];
}

interface UseSpacesResult {
  spaces: Space[];
  loading: boolean;
  error: Error | null;
  loadMore: () => void;
  hasMore: boolean;
  refetch: () => void;
}

export function useSpaces(initialPageSize = 20): UseSpacesResult {
  const [pageSize] = useState(initialPageSize);
  const [skip, setSkip] = useState(0);
  const [allSpaces, setAllSpaces] = useState<Space[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchSpacesRef = useRef<(resetData?: boolean, customSkip?: number) => Promise<void>>(null!);

  fetchSpacesRef.current = async (resetData = true, customSkip?: number) => {
    setLoading(true);
    try {
      const currentSkip = resetData ? 0 : (customSkip ?? skip);
      
      const result = await apolloClient.query<SpacesData>({
        query: GetSpacesNameAndId,
        variables: { first: pageSize, skip: currentSkip },
        fetchPolicy: 'network-only'
      });

      if (result.data?.spaces) {
        if (resetData) {
          setAllSpaces(result.data.spaces);
          setSkip(0);
        } else {
          setAllSpaces(prev => {
            // Simple deduplication and append
            const existingIds = new Set(prev.map(s => s.id));
            const newSpaces = result.data?.spaces?.filter(s => !existingIds.has(s.id)) || [];
            return [...prev, ...newSpaces];
          });
        }
        setHasMore(result.data.spaces.length === pageSize);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch spaces'));
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch only once
  useEffect(() => {
    fetchSpacesRef.current?.(true);
  }, []);

  const loadMore = useCallback(async () => {
    console.log('loadMore called - loading:', loading, 'hasMore:', hasMore, 'skip:', skip);
    if (loading || !hasMore) return;
    
    const newSkip = skip + pageSize;
    console.log('Setting new skip to:', newSkip);
    setSkip(newSkip);
    await fetchSpacesRef.current?.(false, newSkip);
  }, [loading, hasMore, skip, pageSize]);

  const refetch = useCallback(() => {
    fetchSpacesRef.current?.(true);
  }, []);

  return {
    spaces: allSpaces,
    loading,
    error,
    loadMore,
    hasMore,
    refetch
  };
}
