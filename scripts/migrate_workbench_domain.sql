-- Migration: Add domain column to projects table
-- Version: 2
-- Description: Adds domain column to track which stack/domain the project belongs to.

ALTER TABLE projects ADD COLUMN domain TEXT NOT NULL DEFAULT 'omega_engine';

-- Update schema version
INSERT INTO schema_version (version, description)
VALUES (2, 'Add domain column to projects table');
