-- The workaround as Redshift doesn't support the ALTER COLUMN ddl
-- NOTE: Redshift does NOT allow UPDATE after DROPPING columns, they
-- must be done at the end of transaction

BEGIN;

--  ALTER TABLE activity_stream_stats_daily ALTER COLUMN addon_version TYPE VARCHAR(64);
ALTER TABLE activity_stream_stats_daily ADD COLUMN addon_version_temp VARCHAR(64) DEFAULT 'n/a' NOT NULL;
UPDATE activity_stream_stats_daily SET addon_version_temp = addon_version;

--  ALTER TABLE activity_stream_stats_daily ALTER COLUMN page TYPE VARCHAR(64);
ALTER TABLE activity_stream_stats_daily ADD COLUMN page_temp VARCHAR(64) DEFAULT 'NEW_TAB' NOT NULL;
UPDATE activity_stream_stats_daily SET page_temp = page;
UPDATE activity_stream_stats_daily SET page_temp = 'TIMELINE_BOOKMARKS' WHERE page_temp = 'TIMELINE_BOOKMAR';

--  ALTER TABLE activity_stream_events_daily ALTER COLUMN addon_version TYPE VARCHAR(64);
ALTER TABLE activity_stream_events_daily ADD COLUMN addon_version_temp VARCHAR(64) DEFAULT 'n/a' NOT NULL;
UPDATE activity_stream_events_daily SET addon_version_temp = addon_version;

--  ALTER TABLE activity_stream_events_daily ALTER COLUMN page TYPE VARCHAR(64);
ALTER TABLE activity_stream_events_daily ADD COLUMN page_temp VARCHAR(64) DEFAULT 'NEW_TAB' NOT NULL;
UPDATE activity_stream_events_daily SET page_temp = page;
UPDATE activity_stream_events_daily SET page_temp = 'TIMELINE_BOOKMARKS' WHERE page_temp = 'TIMELINE_BOOKMAR';

ALTER TABLE activity_stream_stats_daily DROP COLUMN addon_version;
ALTER TABLE activity_stream_stats_daily RENAME COLUMN addon_version_temp TO addon_version;
ALTER TABLE activity_stream_stats_daily DROP COLUMN page;
ALTER TABLE activity_stream_stats_daily RENAME COLUMN page_temp TO page;
ALTER TABLE activity_stream_events_daily DROP COLUMN addon_version;
ALTER TABLE activity_stream_events_daily RENAME COLUMN addon_version_temp TO addon_version;
ALTER TABLE activity_stream_events_daily DROP COLUMN page;
ALTER TABLE activity_stream_events_daily RENAME COLUMN page_temp TO page;
COMMIT;
