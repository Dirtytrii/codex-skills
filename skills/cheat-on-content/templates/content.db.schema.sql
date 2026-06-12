-- cheat-on-content / content.db.schema
--
-- SQLite schema for the calibration pool when scale demands it.
-- Schema is largely lifted from the 视频分析 reference implementation:
--   - articles: one row per piece of content (candidate or published)
--   - scoring_history: append-only log of every scoring event (version traceability)
--   - bumps: append-only log of rubric upgrades
--
-- Created by tools/md-to-sqlite.py during the markdown → SQLite migration
-- (typically triggered when calibration_samples >= 30).
--
-- After migration, predictions/*.md remain on disk as the human-readable
-- source of truth. articles.db is the queryable secondary index.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ==================== articles ====================
-- One row per piece of content. Mirrors the candidate-schema.md fields plus
-- the lifecycle fields (published, performance, retro).

CREATE TABLE IF NOT EXISTS articles (
    id                            TEXT PRIMARY KEY,         -- 12-char sha256 prefix
    title                         TEXT NOT NULL,
    source                        TEXT NOT NULL,            -- e.g. 'pool:manual', 'trend:hackernews'
    snapshot_text                 TEXT,                     -- the scoring input (full text or summary)
    snapshot_at                   TEXT NOT NULL,            -- ISO 8601
    url                           TEXT,
    category                      TEXT,
    tier                          TEXT CHECK (tier IS NULL OR tier IN ('tier1','tier2','tier3','skip','risky','done')),
    read_status                   TEXT CHECK (read_status IS NULL OR read_status IN ('unread','skimmed','deep_read','done')),
    note                          TEXT,

    -- Scoring (current values; history in scoring_history)
    emotional_resonance           INTEGER CHECK (emotional_resonance IS NULL OR (emotional_resonance BETWEEN 0 AND 5)),
    social_resonance              INTEGER CHECK (social_resonance IS NULL OR (social_resonance BETWEEN 0 AND 5)),
    hook_potential                INTEGER CHECK (hook_potential IS NULL OR (hook_potential BETWEEN 0 AND 5)),
    quotable_lines                INTEGER CHECK (quotable_lines IS NULL OR (quotable_lines BETWEEN 0 AND 5)),
    narrativity                   INTEGER CHECK (narrativity IS NULL OR (narrativity BETWEEN 0 AND 5)),
    audience_breadth              INTEGER CHECK (audience_breadth IS NULL OR (audience_breadth BETWEEN 0 AND 5)),
    satire_depth                  INTEGER CHECK (satire_depth IS NULL OR (satire_depth BETWEEN 0 AND 5)),
    -- Future-version dimensions (NULL until rubric upgrades introduce them)
    memetic_shareability          INTEGER CHECK (memetic_shareability IS NULL OR (memetic_shareability BETWEEN 0 AND 5)),
    topic_shareability            INTEGER CHECK (topic_shareability IS NULL OR (topic_shareability BETWEEN 0 AND 5)),

    composite_score               REAL,
    scored_under_rubric_version   TEXT,

    -- Prediction (latest snapshot from predictions/<id>.md)
    predicted_plays_bucket        TEXT,                     -- e.g. '30-100w'
    prediction_reason             TEXT,                     -- one-line summary
    prediction_file               TEXT,                     -- path to immutable prediction file
    blind_status                  TEXT CHECK (blind_status IS NULL OR blind_status IN ('confirmed_no_data_seen', 'reconstructed', 'integrity_warning')),

    -- Publish lifecycle
    published_at                  TEXT,                     -- ISO 8601
    platform                      TEXT,                     -- 'youtube', 'bilibili', 'douyin', 'wechat', etc.
    platform_url                  TEXT,
    matched_video_folder          TEXT,                     -- path to videos/<...>/

    -- Performance (T+N data, populated by /cheat-retro)
    actual_plays                  INTEGER,
    actual_likes                  INTEGER,
    actual_comments               INTEGER,
    actual_shares                 INTEGER,
    actual_saves                  INTEGER,
    performance_synced_at         TEXT,                     -- ISO 8601 of last data fetch
    performance_window_days       INTEGER,                  -- T+N where N is

    -- Bookkeeping
    created_at                    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at                    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_articles_tier         ON articles(tier);
CREATE INDEX IF NOT EXISTS idx_articles_read_status  ON articles(read_status);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_composite    ON articles(composite_score DESC);
CREATE INDEX IF NOT EXISTS idx_articles_rubric_ver   ON articles(scored_under_rubric_version);

-- updated_at trigger
CREATE TRIGGER IF NOT EXISTS articles_updated_at
AFTER UPDATE ON articles
FOR EACH ROW
BEGIN
    UPDATE articles SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ==================== scoring_history ====================
-- Append-only log of every scoring event. Used for version traceability,
-- rollback, and counterfactual analysis ("what would the v3 score have been
-- for this v2-scored article?").

CREATE TABLE IF NOT EXISTS scoring_history (
    id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id                    TEXT NOT NULL REFERENCES articles(id),
    rubric_version                TEXT NOT NULL,
    scored_at                     TEXT NOT NULL DEFAULT (datetime('now')),
    scored_by                     TEXT,                     -- 'auto' / 'manual' / 'bump-rescore' / etc.

    -- Scores at the time of this event
    emotional_resonance           INTEGER,
    social_resonance              INTEGER,
    hook_potential                INTEGER,
    quotable_lines                INTEGER,
    narrativity                   INTEGER,
    audience_breadth              INTEGER,
    satire_depth                  INTEGER,
    memetic_shareability          INTEGER,
    topic_shareability            INTEGER,
    composite_score               REAL,

    -- Free-form note (e.g. "post-hoc rescore for v2.1 bump validation")
    note                          TEXT
);

CREATE INDEX IF NOT EXISTS idx_scoring_history_article  ON scoring_history(article_id);
CREATE INDEX IF NOT EXISTS idx_scoring_history_rubric   ON scoring_history(rubric_version);
CREATE INDEX IF NOT EXISTS idx_scoring_history_scored   ON scoring_history(scored_at);

-- ==================== bumps ====================
-- Append-only log of rubric upgrades. One row per successful bump.

CREATE TABLE IF NOT EXISTS bumps (
    id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    from_version                  TEXT NOT NULL,
    to_version                    TEXT NOT NULL,
    bumped_at                     TEXT NOT NULL DEFAULT (datetime('now')),
    formula_before                TEXT NOT NULL,            -- full formula string
    formula_after                 TEXT NOT NULL,
    calibration_pool_size         INTEGER NOT NULL,
    rank_consistency              REAL,                     -- e.g. 0.8 for 4/5
    pairwise_no_regression        BOOLEAN,
    cross_model_audit             TEXT CHECK (cross_model_audit IS NULL OR cross_model_audit IN ('PASS', 'REJECT', 'SKIPPED')),
    cross_model_reasoning         TEXT,                     -- audit reviewer's verbatim reasoning
    memo                          TEXT,                     -- human-written upgrade memo
    triggered_by                  TEXT                      -- e.g. 'consecutive_directional_errors'
);

-- ==================== views ====================
-- Convenience views for common queries.

CREATE VIEW IF NOT EXISTS calibration_pool AS
SELECT
    a.*,
    (CAST(a.actual_plays AS REAL) / 10000.0) AS actual_plays_w
FROM articles a
WHERE a.actual_plays IS NOT NULL
  AND a.published_at IS NOT NULL
  AND a.prediction_file IS NOT NULL
ORDER BY a.composite_score DESC;

CREATE VIEW IF NOT EXISTS pending_retros AS
SELECT a.*
FROM articles a
WHERE a.published_at IS NOT NULL
  AND a.actual_plays IS NULL
ORDER BY a.published_at ASC;

CREATE VIEW IF NOT EXISTS top_candidates AS
SELECT a.*
FROM articles a
WHERE a.tier IN ('tier1', 'tier2')
  AND a.published_at IS NULL
  AND a.composite_score IS NOT NULL
ORDER BY
    CASE a.tier WHEN 'tier1' THEN 0 WHEN 'tier2' THEN 1 ELSE 2 END,
    a.composite_score DESC;

-- ==================== schema_meta ====================
-- Schema version for future migrations.

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR REPLACE INTO schema_meta (key, value) VALUES
    ('schema_version', '1.0'),
    ('created_at', datetime('now')),
    ('source', 'cheat-on-content templates/content.db.schema.sql');
