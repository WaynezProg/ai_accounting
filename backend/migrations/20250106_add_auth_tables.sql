-- Migration: add users.timezone, refresh_tokens, oauth_login_codes
-- NOTE: This script is intended to be run once on existing databases.

ALTER TABLE users ADD COLUMN timezone TEXT DEFAULT 'Asia/Taipei';

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    token_hash TEXT NOT NULL UNIQUE,
    issued_at DATETIME NOT NULL,
    last_used_at DATETIME NOT NULL,
    expires_at DATETIME,
    revoked_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS oauth_login_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    code_hash TEXT NOT NULL UNIQUE,
    issued_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
