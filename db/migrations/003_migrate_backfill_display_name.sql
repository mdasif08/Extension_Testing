-- Safe migrate step: backfill new column from old column.

UPDATE customers
SET display_name = full_name
WHERE display_name IS NULL;
