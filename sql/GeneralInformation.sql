-- Remove table from database
DROP TABLE IF EXISTS GeneralInformation;

-- Create new table in database
CREATE TABLE GeneralInformation (
    job TEXT NOT NULL,  -- CI job URL
    git TEXT NOT NULL   -- Git repository URL
);
