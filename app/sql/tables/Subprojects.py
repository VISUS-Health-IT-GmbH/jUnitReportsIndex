#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/tables/Subprojects.py

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

from typing import Optional


class Subprojects:
    """
    Handle general information on subproject using table "Subprojects"

    Functions:  1) create       -> create table if not already exists in database
                2) add          -> add information on new subproject
                3) all          -> returns information regarding all subprojects
                4) cnt          -> returns number of rows in table
                5) rem          -> remove subproject from table
                6) delete       -> delete table
    """

    def create(self, con: mariadb.connection):
        """
        Creates a new table "Subprojects" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        self.delete(con)

        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE Subprojects ( \
                name VARCHAR(256) NOT NULL, \
                PRIMARY KEY (name) \
            )"
        )
        con.commit()


    def add(self, con: mariadb.connection, name: str) -> bool:
        """
        Creates a new subproject

        :param con: connection to database
        :param name: subproject name
        :return: True when subproject does not already exist, False otherwise
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Subprojects \
            WHERE \
                name=?",
            (name,)
        )
        row = cursor.fetchone()

        if row[0] != 0:
            return False

        cursor.execute(
            "INSERT INTO Subprojects \
                (name) \
            VALUES \
                (?)",
            (name,)
        )
        con.commit()

        return True


    def all(self, con: mariadb.connection) -> Optional[list]:
        """
        Returns base information on all subproject

        :param con: connection to database
        :return: [
                    &lt;subproject 1 name>,
                    &lt;subproject 2 name>,
                    ...
                ] or None
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT * FROM Subprojects"
        )
        rows = cursor.fetchall()

        if len(rows) == 0:
            return None

        return [
            row[0] for row in rows
        ]


    def cnt(self, con: mariadb.connection) -> int:
        """
        Returns the number of all subprojects

        :param con: connection to database
        :return: number of subprojects
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                Subprojects"
        )

        return cursor.fetchone()[0]


    def rem(self, con: mariadb.connection, name: str):
        """
        Deletes a distinct subproject

        :param con: existing connection to database
        :param name: project name
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "DELETE FROM \
                Subprojects \
            WHERE \
                name=?",
            (name,)
        )
        con.commit()


    def delete(self, con: mariadb.connection):
        """
        Deletes the table "Subprojects" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "DROP TABLE IF EXISTS Subprojects"
        )
        con.commit()
