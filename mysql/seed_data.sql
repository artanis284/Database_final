-- Clean seed script for the final user-provided literature database.
-- It creates only the administrator account and UI preference rows.
-- No demo papers, authors, keywords, favorites, or
-- citations are inserted here.
--
-- Rebuild order:
--   1. mysql/schema.sql
--   2. mysql/seed_data.sql

USE literature_management;

INSERT IGNORE INTO sys_user(username, password_hash, role, email) VALUES
('admin', SHA2('admin123', 256), 'admin', 'admin@example.com');

INSERT IGNORE INTO user_preference(user_id, language)
SELECT user_id, 'zh'
FROM sys_user
WHERE username = 'admin';

SELECT 'Clean seed finished. No demo literature data was inserted.' AS result;
