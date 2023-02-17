-- Remove table from database
DROP TABLE IF EXISTS Subprojects;

-- Create new table in database
CREATE TABLE Subprojects (
    name VARCHAR(256) NOT NULL, -- subproject name

    PRIMARY KEY (name)
);
