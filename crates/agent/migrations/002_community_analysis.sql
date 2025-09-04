-- Add community analysis table for caching research results

CREATE TABLE IF NOT EXISTS community_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(1000) NOT NULL,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_community_analyses_topic ON community_analyses(topic);
CREATE INDEX IF NOT EXISTS idx_community_analyses_expires_at ON community_analyses(expires_at);
CREATE INDEX IF NOT EXISTS idx_community_analyses_created_at ON community_analyses(created_at);

-- Create a unique constraint to prevent duplicate topics
CREATE UNIQUE INDEX IF NOT EXISTS idx_community_analyses_topic_unique ON community_analyses(topic);
