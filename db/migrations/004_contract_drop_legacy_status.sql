-- Unsafe contract step included intentionally for scanner testing.
-- This should be detected because it removes a column directly.

ALTER TABLE orders
    DROP COLUMN legacy_status;
