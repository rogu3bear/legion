-- Initial schema version
-- Adds example index to agents table
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);

