#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/tables/Branches.py

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

from typing import Optional


class Branches:
    """
    Handle general information on a job using table "Branches"

    Functions:  1) create       -> create table if not already exists in database
                2) add          -> add information on new branch
                3) all          -> returns information regarding all branches
                4) cnt          -> returns number of rows in table
                5) rem          -> remove branch from table
                6) delete       -> delete table
    """

    def create(self, con: mariadb.connection):
        """
        Creates a new table "Branches" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        self.delete(con)

        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE Branches ( \
                name VARCHAR(256) NOT NULL, \
                PRIMARY KEY (name) \
            )"
        )
        con.commit()


    def add(self, con: mariadb.connection, name: str) -> bool:
        """
        Creates a new branch

        :param con: connection to database
        :param name: branch name
        :return: True when branch does not already exist, False otherwise
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Branches \
            WHERE \
                name=?",
            (name,)
        )
        row = cursor.fetchone()

        if row[0] != 0:
            return False

        cursor.execute(
            "INSERT INTO Branches \
                (name) \
            VALUES \
                (?)",
            (name,)
        )
        con.commit()

        return True


    def all(self, con: mariadb.connection) -> Optional[list[str]]:
        """
        Returns base information on all branches

        :param con: connection to database
        :return: [
                    &lt;branch 1 name>,
                    &lt;branch 2 name>,
                    ...
                ] or None
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                * \
            FROM \
                Branches"
        )
        rows = cursor.fetchall()

        if len(rows) == 0:
            return None

        return [
            row[0] for row in rows
        ]


    def cnt(self, con: mariadb.connection) -> int:
        """
        Returns the number of all branches

        :param con: connection to database
        :return: number of branches
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Branches"
        )

        return cursor.fetchone()[0]


    def rem(self, con: mariadb.connection, name: str):
        """
        Deletes a distinct branch

        :param con: existing connection to database
        :param name: branch name
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "DELETE FROM \
                Branches \
            WHERE \
                name=?",
            (name,)
        )
        con.commit()


    def delete(self, con: mariadb.connection):
        """
        Deletes the table "Branches" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "DROP TABLE IF EXISTS Branches"
        )
        con.commit()
