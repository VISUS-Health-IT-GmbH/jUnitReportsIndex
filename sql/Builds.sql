-- Remove table from database
DROP TABLE IF EXISTS Builds;

-- Create new table in database
CREATE TABLE Builds (
    id              INTEGER NOT NULL,       -- build id
    branch          VARCHAR(256) NOT NULL,  -- Git branch
    gCommit         TEXT NOT NULL,          -- Git commit hash
    version         TEXT,                   -- (optional) project version
    rc              TEXT,                   -- (optional) project release candidate
    tests_success   INTEGER NOT NULL,       -- number of successful tests
    tests_skipped   INTEGER NOT NULL,       -- number of skipped tests
    tests_flaky     INTEGER NOT NULL,       -- number of flaky tests
    tests_failed    INTEGER NOT NULL,       -- number of failed tests
    type            TEXT,                   -- (optional) build type
    result_path     TEXT NOT NULL,          -- path for jUnit results

    PRIMARY KEY (id, branch),
    FOREIGN KEY (branch) REFERENCES Branches (name) ON DELETE CASCADE
);
