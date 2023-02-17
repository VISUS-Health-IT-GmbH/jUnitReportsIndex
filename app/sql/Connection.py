#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/Connection.py

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

from dataclasses import dataclass


class ConnectionException(Exception):
    """
    Exception thrown when anything with the database connection happens
    """

    def __init__(self, message: str, errors: list = None):
        """
        Constructor of class ConnectionException

        :param message: error message
        :param errors: list of potential errors
        """

        super(ConnectionException, self).__init__(message)
        self.message = message
        self.errors = errors


@dataclass
class ConnectionInfo:
    """
    Information on MariaDB connection
    """

    host: str
    port: int
    user: str
    password: str
    database: str


class Connection:
    """
    Connector to MariaDB
    """

    def __init__(self, info: ConnectionInfo):
        """
        Constructor for class Connection

        :param info: connection information
        """

        self.info = info


    def get(self) -> mariadb.connection:
        """
        Returns a MariaDB connection to the current database

        :return: connection object
        :exception mariadb.Error: when connection could not be established
        """

        try:
            connection = mariadb.connect(
                host=self.info.host,
                port=self.info.port,
                user=self.info.user,
                password=self.info.password,
                database=self.info.database
            )
            connection.autocommit = False
        except mariadb.Error as err:
            raise ConnectionException(
                f"Creating database connection to project '{self.info.database}' threw an exception"
            ) from err

        return connection
