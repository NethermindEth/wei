-- Add generic cache table for caching all API responses

CREATE TABLE IF NOT EXISTS cache_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(1000) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_cache_entries_cache_key ON cache_entries(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_entries_expires_at ON cache_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_cache_entries_created_at ON cache_entries(created_at);

-- Create a unique constraint to prevent duplicate cache keys
CREATE UNIQUE INDEX IF NOT EXISTS idx_cache_entries_cache_key_unique ON cache_entries(cache_key);

-- Migrate existing community_analyses to the new cache table
INSERT INTO cache_entries (id, cache_key, data, created_at, expires_at, metadata)
SELECT 
    id,
    CONCAT('community:', topic) as cache_key,
    jsonb_build_object(
        'result', response_data,
        'from_cache', true,
        'created_at', created_at,
        'expires_at', expires_at
    ) as data,
    created_at,
    expires_at,
    jsonb_build_object('type', 'community_analysis', 'topic', topic) as metadata
FROM community_analyses
ON CONFLICT (cache_key) DO NOTHING;
