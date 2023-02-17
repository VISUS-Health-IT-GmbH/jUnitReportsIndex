-- Remove table from database
DROP TABLE IF EXISTS Subprojects_in_Build;

-- Create new table in database
CREATE TABLE Subprojects_in_Build (
    branch          VARCHAR(256) NOT NULL,  -- Git branch
    id              INTEGER NOT NULL,       -- build id
    subproject      VARCHAR(256) NOT NULL,  -- subproject name
    tests_success   INTEGER NOT NULL,       -- number of successful tests
    tests_skipped   INTEGER NOT NULL,       -- number of skipped tests
    tests_flaky     INTEGER NOT NULL,       -- number of flaky tests
    tests_failed    INTEGER NOT NULL,       -- number of failed tests
    result_url      TEXT NOT NULL,          -- URL of test result index.html
    duration        REAL NOT NULL,          -- time it took to test

    PRIMARY KEY (branch, id, subproject),
    FOREIGN KEY (branch, id) REFERENCES Builds (branch, id) ON DELETE CASCADE,
    FOREIGN KEY (subproject) REFERENCES Subprojects (name) ON DELETE CASCADE
);
