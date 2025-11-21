-- Microsoft Login Event Counter Database Schema
-- Version: 1.0.0

-- Login events table
CREATE TABLE IF NOT EXISTS login_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,              -- ISO 8601 UTC: "2025-11-21T14:30:00Z"
    unix_timestamp INTEGER NOT NULL,      -- Unix epoch for efficient range queries
    detected_via TEXT NOT NULL            -- Detection method: "connect_sequence", "http_redirect", "oauth_callback"
);

-- Index for efficient time-based queries
CREATE INDEX IF NOT EXISTS idx_login_events_unix_time ON login_events(unix_timestamp);

-- Proxy metadata table
CREATE TABLE IF NOT EXISTS proxy_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Initialize metadata
INSERT OR IGNORE INTO proxy_metadata (key, value) VALUES
    ('schema_version', '1.0.0'),
    ('created_at', datetime('now'));
