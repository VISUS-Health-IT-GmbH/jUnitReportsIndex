#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/tables/Builds.py

Copyright (C) 2021, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import mariadb

from typing import Any, Optional


class Builds:
    """
    Handle general information on a build using table "Builds"

    Functions:  1) create       -> create table if not already exists in database
                2) add          -> add information on new build
                3) get          -> returns information regarding specific build
                4) all          -> returns information regarding all builds of a branch
                5) cnt          -> returns number of rows in table of a branch
                6) rem          -> remove build from table
                7) delete       -> delete table
    """

    def create(self, con: mariadb.connection):
        """
        Creates a new table "Builds" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        self.delete(con)

        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE Builds ( \
                id              INTEGER NOT NULL, \
                branch          VARCHAR(256) NOT NULL, \
                gCommit         TEXT NOT NULL, \
                version         TEXT, \
                rc              TEXT, \
                tests_success   INTEGER NOT NULL, \
                tests_skipped   INTEGER NOT NULL, \
                tests_flaky     INTEGER NOT NULL, \
                tests_failed    INTEGER NOT NULL, \
                type            TEXT, \
                result_path     TEXT NOT NULL, \
                PRIMARY KEY (id, branch), \
                FOREIGN KEY (branch) REFERENCES Branches (name) ON DELETE CASCADE \
            )"
        )
        con.commit()


    def add(self, con: mariadb.connection, id: int, branch: str, gCommit: str, version: Optional[str],
            rc: Optional[str], tests_success: int, tests_skipped: int, tests_flaky: int, tests_failed: int,
            type: Optional[str], result_path: str) -> bool:
        """
        Creates a new build

        :param con: connection to database
        :param id: build id
        :param branch: Git branch
        :param gCommit: Git commit hash
        :param version: (optional) project version
        :param rc: (optional) project release candidate
        :param tests_success: number of successful tests
        :param tests_skipped: number of skipped tests
        :param tests_flaky: number of flaky tests
        :param tests_failed: number of failed tests
        :param type: (optional) build type
        :param result_path: path for jUnit results
        :return: True when build does not already exist, False otherwise
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Builds \
            WHERE \
                id=? AND branch=?",
            (id, branch,)
        )
        row = cursor.fetchone()

        if row[0] != 0:
            return False

        cursor.execute(
            "INSERT INTO Builds \
                (id, branch, gCommit, version, rc, tests_success, tests_skipped, tests_flaky, tests_failed, type, \
                result_path) \
            VALUES \
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                id, branch, gCommit, version, rc, tests_success, tests_skipped, tests_flaky, tests_failed, type,
                result_path,
            )
        )
        con.commit()

        return True


    def get(self, con: mariadb.connection, id: int, branch: str) -> Optional[dict[str, Any]]:
        """
        Returns information on a distinct build of a specific branch

        :param con: connection to database
        :param id: build id
        :param branch: branch name
        :return:
                {
                    "gCommit": &lt;Git commit hash>,
                    "version": &lt;(optional) project version>,
                    "rc": &lt;(optional) project release candidate>,
                    "tests_success": &lt;number of successful tests>,
                    "tests_skipped": &lt;number of skipped tests>,
                    "tests_flaky": &lt;number of flaky tests>,
                    "tests_failed": &lt;number of failed tests>,
                    "type": &lt;(optional) build type>,
                    "result_path": &lt;path for jUnit results>,
                } or None
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                gCommit, version, rc, tests_success, tests_skipped, tests_flaky, tests_failed, type, result_path \
            FROM \
                Builds \
            WHERE \
                id=? AND branch=?",
            (id, branch,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "gCommit": row[0],
            "version": row[1],
            "rc": row[2],
            "tests_success": row[3],
            "tests_skipped": row[4],
            "tests_flaky": row[5],
            "tests_failed": row[6],
            "type": row[7],
            "result_path": row[8]
        }


    def all(self, con: mariadb.connection, branch: str) -> Optional[list[dict[str, Any]]]:
        """
        Returns base information on all builds of a specific branch

        :param con: connection to database
        :param branch: branch name
        :return: [
                    {
                        "id": &lt;build id>,
                        "gCommit": &lt;Git commit hash>,
                        "version": &lt;(optional) project version>,
                        "rc": &lt;(optional) project release candidate>,
                        "tests_success": &lt;number of successful tests>,
                        "tests_skipped": &lt;number of skipped tests>,
                        "tests_flaky": &lt;number of flaky tests>,
                        "tests_failed": &lt;number of failed tests>,
                        "type": &lt;(optional) build type>,
                        "result_path": &lt;path for jUnit results>,
                    },
                    ...
                 ] or None
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                id, gCommit, version, rc, tests_success, tests_skipped, tests_flaky, tests_failed, type, result_path \
            FROM \
                Builds \
            WHERE \
                branch=? \
            ORDER BY \
                id ASC",
            (branch,)
        )
        rows = cursor.fetchall()

        if len(rows) == 0:
            return None

        return [
            {
                "id": row[0],
                "gCommit": row[1],
                "version": row[2],
                "rc": row[3],
                "tests_success": row[4],
                "tests_skipped": row[5],
                "tests_flaky": row[6],
                "tests_failed": row[7],
                "type": row[8],
                "result_path": row[9]
            } for row in rows
        ]


    def cnt(self, con: mariadb.connection, branch: str):
        """
        Returns the number of all builds of a specific branch

        :param con: connection to database
        :param branch: branch name
        :return: number of builds with given branch
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Builds \
            WHERE \
                branch=?",
            (branch,)
        )
        return cursor.fetchone()[0]


    def rem(self, con: mariadb.connection, id: Optional[int], branch: str):
        """
        Deletes a distinct branch

        :param con: existing connection to database
        :param id: (optional) build id
        :param branch: branch name
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        if not id:
            cursor.execute(
                "DELETE FROM \
                    Builds \
                WHERE \
                    branch=?",
                (branch,)
            )
        else:
            cursor.execute(
                "DELETE FROM \
                    Builds \
                WHERE \
                    id=? AND branch=?",
                (id, branch,)
            )
        con.commit()


    def delete(self, con: mariadb.connection):
        """
        Deletes the table "Builds" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "DROP TABLE IF EXISTS Builds"
        )
        con.commit()
