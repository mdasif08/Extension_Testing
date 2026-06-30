-- Unsafe direct rename included intentionally for scanner testing.
-- This should be detected because direct renames can break older application versions.

ALTER TABLE customers
    RENAME COLUMN full_name TO legal_name;
