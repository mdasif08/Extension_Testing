-- Safe expand step: add new nullable column first.

ALTER TABLE customers
    ADD COLUMN display_name TEXT;
