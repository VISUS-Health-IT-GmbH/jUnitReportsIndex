-- Remove table from database
DROP TABLE IF EXISTS Branches;

-- Create new table in database
CREATE TABLE Branches (
    name VARCHAR(256) NOT NULL, -- Git branch name

    PRIMARY KEY (name)
);
