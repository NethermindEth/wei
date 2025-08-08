-- Initial schema for the indexer service

-- Create protocols table
CREATE TABLE IF NOT EXISTS protocols (
    id SERIAL PRIMARY KEY,
    chain_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    protocol VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chain_id, name, protocol)
);

-- Create proposals table
CREATE TABLE IF NOT EXISTS proposals (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    protocol_id INTEGER REFERENCES protocols(id),
    choices JSONB,
    author VARCHAR(255) NOT NULL,
    comments JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create actors table
CREATE TABLE IF NOT EXISTS actors (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE,
    ens VARCHAR(255),
    name VARCHAR(255),
    description TEXT,
    voting_power VARCHAR(255),
    protocol_id INTEGER REFERENCES protocols(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create webhook_registrations table
CREATE TABLE IF NOT EXISTS webhook_registrations (
    id VARCHAR(255) PRIMARY KEY,
    url TEXT NOT NULL,
    events JSONB NOT NULL,
    secret VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_proposals_protocol_id ON proposals(protocol_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_author ON proposals(author);
CREATE INDEX IF NOT EXISTS idx_actors_address ON actors(address);
CREATE INDEX IF NOT EXISTS idx_actors_ens ON actors(ens);
CREATE INDEX IF NOT EXISTS idx_actors_protocol_id ON actors(protocol_id); 