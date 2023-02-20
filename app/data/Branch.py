#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/data/Branch.py

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
import app.sql.MultiProjectJob
import app.sql.SingleProjectJob

from typing import Optional, Union
from app.sql import ConnectionException


class BranchConnectionException(Exception):
    """
    Exception thrown when connection for branch failed
    """

    def __init__(self, message: str):
        """
        Constructor of class BranchConnectionException

        :param message: error message
        """

        super(BranchConnectionException, self).__init__(message)
        self.message = message


class BranchDatabaseException(Exception):
    """
    Exception thrown when aggregating data for branch failed
    """

    def __init__(self, message: str):
        """
        Constructor of class BranchDatabaseException

        :param message: error message
        """

        super(BranchDatabaseException, self).__init__(message)
        self.message = message


class Branch:
    """
    Build data returned to user on REST API when accessing: http://<backend>/<project>/<branch>
    """

    def __init__(self, project: Union[app.sql.MultiProjectJob, app.sql.SingleProjectJob]):
        """
        Constructor of class "Branch"

        :param project: single or multiple project job
        """

        self.project = project


    def get(self, branch: str) -> Optional[dict[str, Union[int, list[int]]]]:
        """
        Get branch specific information in JSON format

        :param branch: to get the builds from
        :return: {
                    "first": <smallest build id>,
                    "last": <highest build id>,
                    "builds": [
                        <build id>,
                        ...
                    ]
                } OR None
        :exception BranchConnectionException: when connection could not be established
        :exception BranchDatabaseException: when SQL data could not be aggregated
        """

        connection: Optional[mariadb.connection] = None

        try:
            connection = self.project.connection.get()

            builds = self.project.builds.all(connection, branch)
            if builds is None:
                return None

            return {
                "first": builds[0]["id"],
                "last": builds[-1]["id"],
                "builds": [
                    build["id"] for build in builds
                ]
            }
        except ConnectionException as err:
            raise BranchConnectionException(
                f"Creating connection for project {self.project.name} failed with an exception: {err}"
            ) from None
        except mariadb.Error as err:
            raise BranchDatabaseException(
                f"Reading SQL data for project {self.project.name} failed with an exception: {err}"
            ) from None
        finally:
            if connection is not None:
                connection.close()
