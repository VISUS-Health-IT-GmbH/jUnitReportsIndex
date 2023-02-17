#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/tables/GeneralInformation.py

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


class GeneralInformation:
    """
    Handle general information on a Job using table "GeneralInformation"

    Functions:  1) create       -> create table if not already exists in database
                2) get          -> returns general information on CI / Git
                3) update       -> changes general information on CI / Git
                4) delete       -> delete table
    """

    def create(self, con: mariadb.connection):
        """
        Creates a new table "GeneralInformation" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        self.delete(con)

        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE GeneralInformation ( \
                job TEXT NOT NULL, \
                git TEXT NOT NULL \
            )"
        )
        con.commit()


    def get(self, con: mariadb.connection) -> dict[str, str]:
        """
        Returns the general information in a database

        :param con: connection to database
        :return: {
                    "job": &lt;CI job URL>,
                    "git": &lt;Git repo URL>
                 }
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                job, git \
            FROM \
                GeneralInformation \
            LIMIT 1"
        )
        row = cursor.fetchone()

        return {
            "job": row[0],
            "git": row[1]
        }


    def update(self, con: mariadb.connection, job: str, git: str):
        """
        Updates the general information in a database

        :param con: connection to database
        :param job: CI job URL
        :param git: Git repo URL
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "SELECT \
                COUNT(*) \
            FROM \
                GeneralInformation"
        )
        row = cursor.fetchone()

        if row[0] != 1:
            cursor.execute(
                "TRUNCATE TABLE GeneralInformation"
            )
            cursor.execute(
                "INSERT INTO GeneralInformation \
                    (job, git) \
                VALUES \
                    (?, ?)",
                (job, git,)
            )
        else:
            cursor.execute(
                "UPDATE GeneralInformation \
                SET \
                    job=?, git=?",
                (job, git,)
            )

        con.commit()


    def delete(self, con: mariadb.connection):
        """
        Deletes the table "GeneralInformation" in database provided using connection

        :param con: connection to database
        :exception mariadb.Error: when errors with the database connection occurred
        """

        cursor = con.cursor()
        cursor.execute(
            "DROP TABLE IF EXISTS GeneralInformation"
        )
        con.commit()
