CREATE TABLE IF NOT EXISTS samanvay_workspaces (
    workspace_id VARCHAR(64) PRIMARY KEY,
    owner_subject VARCHAR(200) NOT NULL,
    public_read BOOLEAN NOT NULL DEFAULT FALSE,
    database_image BYTEA NOT NULL,
    revision BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- The bytea image is the durable copy of a bounded workspace registry. Requests
-- lock one row FOR UPDATE, operate on an in-memory SQLite image, and update this
-- row transactionally. Do not use an ephemeral deployed filesystem as storage.
