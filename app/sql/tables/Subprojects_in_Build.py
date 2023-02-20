#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/tables/Subprojects_in_Build.py

Copyright (C) 2021-2023, VISUS Health IT GmbH
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


class Subprojects_in_Build:
    """
    Handle general information on a build using table "Subprojects_in_Build"

    Functions:  1) create       -> create table if not already exists in database
                2) add          -> add information on new build
                3) get          -> returns information regarding specific build
                4) all          -> returns information regarding all builds of a branch
                5) cnt          -> returns number of rows in table of a branch
                6) rem          -> remove combination from table
                7) delete       -> delete table
    """

    def create(self, con: mariadb.connection):
        """
        Creates a new table "Subprojects_in_Build" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        self.delete(con)

        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE Subprojects_in_Build ( \
                branch          VARCHAR(256) NOT NULL, \
                id              INTEGER NOT NULL, \
                subproject      VARCHAR(256) NOT NULL, \
                tests_success   INTEGER NOT NULL, \
                tests_skipped   INTEGER NOT NULL, \
                tests_flaky     INTEGER NOT NULL, \
                tests_failed    INTEGER NOT NULL, \
                result_url      TEXT NOT NULL, \
                duration        REAL NOT NULL, \
                PRIMARY KEY (branch, id, subproject), \
                FOREIGN KEY (branch, id) REFERENCES Builds (branch, id) ON DELETE CASCADE, \
                FOREIGN KEY (subproject) REFERENCES Subprojects (name) ON DELETE CASCADE \
            )"
        )
        con.commit()


    def add(self, con: mariadb.connection, branch: str, id: int, subproject: str, tests_success: int,
            tests_skipped: int, tests_flaky: int, tests_failed: int, result_url: str, duration: float) -> bool:
        """
        Creates a new combination

        :param con: connection to database
        :param branch: Git branch
        :param id: build id
        :param subproject: subproject name
        :param tests_success: number of successful tests
        :param tests_skipped: number of skipped tests
        :param tests_flaky: number of flaky tests
        :param tests_failed: number of failed tests
        :param result_url: URL of test result index.html
        :param duration: time it took to test
        :return: True when combination does not already exist, False otherwise
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Subprojects_in_Build \
            WHERE \
                branch=? AND id=? AND subproject=?",
            (branch, id, subproject,)
        )
        row = cursor.fetchone()

        if row[0] != 0:
            return False

        cursor.execute(
            "INSERT INTO Subprojects_in_Build \
                (branch, id, subproject, tests_success, tests_skipped, tests_flaky, tests_failed, result_url, \
                duration) \
            VALUES \
                (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (branch, id, subproject, tests_success, tests_skipped, tests_flaky, tests_failed, result_url, duration,)
        )
        con.commit()

        return True


    def get(self, con: mariadb.connection, branch: str, id: int, subproject: str) -> Optional[dict[str, Any]]:
        """
        Returns a specific combination

        :param con: connection to database
        :param branch: branch name
        :param id: build id
        :param subproject: subproject name
        :return:
                {
                    "tests_success": &lt;number of successful tests>,
                    "tests_skipped": &lt;number of skipped tests>,
                    "tests_flaky": &lt;number of flaky tests>,
                    "tests_failed": &lt;number of failed tests>,
                    "result_url": &lt;URL of test result index.html>,
                    "duration": &lt;time it took to test>,
                } or None
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                tests_success, tests_skipped, tests_flaky, tests_failed, result_url, duration \
            FROM \
                Subprojects_in_Build \
            WHERE \
                branch=? AND id=? AND subproject=?",
            (branch, id, subproject,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "tests_success": row[0],
            "tests_skipped": row[1],
            "tests_flaky": row[2],
            "tests_failed": row[3],
            "result_url": row[4],
            "duration": row[5]
        }


    def all(self, con: mariadb.connection, branch: str, id: int) -> Optional[list[dict[str, Any]]]:
        """
        Returns all combinations

        :param con: connection to database
        :param branch: branch name
        :param id: build id
        :return: [
                    {
                        "subproject": &lt;subproject name>,
                        "tests_success": &lt;number of successful tests>,
                        "tests_skipped": &lt;number of skipped tests>,
                        "tests_flaky": &lt;number of flaky tests>,
                        "tests_failed": &lt;number of failed tests>,
                        "result_url": &lt;URL of test result index.html>,
                        "duration": &lt;time it took to test>,
                    },
                    ...
                 ] or None
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                subproject, tests_success, tests_skipped, tests_flaky, tests_failed, result_url, duration \
            FROM \
                Subprojects_in_Build \
            WHERE \
                branch=? AND id=?",
            (branch, id,)
        )
        rows = cursor.fetchall()

        if len(rows) == 0:
            return None

        return [
            {
                "subproject": row[0],
                "tests_success": row[1],
                "tests_skipped": row[2],
                "tests_flaky": row[3],
                "tests_failed": row[4],
                "result_url": row[5],
                "duration": row[6]
            } for row in rows
        ]


    def cnt(self, con: mariadb.connection, branch: str, id: int):
        """
        Returns the number of subprojects in specific build

        :param con: connection to database
        :param branch: branch name
        :param id: build id
        :return: number of builds with given branch
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Subprojects_in_Build \
            WHERE \
                branch=? AND id=?",
            (branch, id,)
        )
        return cursor.fetchone()[0]


    def rem(self, con: mariadb.connection, branch: str, id: Optional[int]):
        """
        Deletes a specific combination

        :param con: existing connection to database
        :param branch: branch name
        :param id: (optional) build id
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        if id is None:
            cursor.execute(
                "DELETE FROM \
                    Subprojects_in_Build \
                WHERE \
                    branch=?",
                (branch,)
            )
        else:
            cursor.execute(
                "DELETE FROM \
                    Subprojects_in_Build \
                WHERE \
                    branch=? AND id=?",
                (branch, id,)
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
            "DROP TABLE IF EXISTS Subprojects_in_Build"
        )
        con.commit()
