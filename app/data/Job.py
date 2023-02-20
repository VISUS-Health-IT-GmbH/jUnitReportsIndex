#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/data/Job.py

Copyright (C) 2021-2023, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository or consequential, which may
result from the usage of this software.
"""

import mariadb
import app.sql.MultiProjectJob
import app.sql.SingleProjectJob

from typing import Optional, Union
from app.sql import ConnectionException


class JobConnectionException(Exception):
    """
    Exception thrown when connection for job failed
    """

    def __init__(self, message: str):
        """
        Constructor of class JobConnectionException

        :param message: error message
        """

        super(JobConnectionException, self).__init__(message)
        self.message = message


class JobDatabaseException(Exception):
    """
    Exception thrown when aggregating data for job failed
    """

    def __init__(self, message: str):
        """
        Constructor of class JobDatabaseException

        :param message: error message
        """

        super(JobDatabaseException, self).__init__(message)
        self.message = message


class Job:
    """
    Build data returned to user on REST API when accessing: http://<backend>/<project>
    """

    def __init__(self, project: Union[app.sql.MultiProjectJob, app.sql.SingleProjectJob]):
        """
        Constructor of class "Job"

        :param project: single or multiple project job
        """

        self.project = project


    def get(self) -> dict[str, Union[dict[str, str], list[dict[str, Union[str, int]]]]]:
        """
        Get job specific information in JSON format

        :return: {
                    "general": {
                        "job": <job URL>,
                        "git": <Git URL>
                    }
                } OR {
                    "general": {
                        "job": <job URL>,
                        "git": <Git URL>
                    },
                    "branches": [
                        {
                            "name": <branch name>,
                            "first": <smallest build id>,
                            "last": <highest build id>
                        },
                        ...
                    ]
                }
        :exception JobConnectionException: when connection could not be established
        :exception JobDatabaseException: when SQL data could not be aggregated
        """

        connection: Optional[mariadb.connection] = None

        try:
            connection = self.project.connection.get()

            ret = {
                "general": self.project.general.get(connection)
            }

            branches = self.project.branches.all(connection)
            if branches is not None:
                ret["branches"] = []

                for branch in branches:
                    builds = self.project.builds.all(connection, branch)
                    if builds is None:
                        continue

                    ret["branches"].append(
                        {
                            "name": branch,
                            "first": builds[0]["id"],
                            "last": builds[-1]["id"]
                        }
                    )

                if len(ret["branches"]) == 0:
                    del ret["branches"]

            return ret
        except ConnectionException as err:
            raise JobConnectionException(
                f"Creating connection for project {self.project.name} failed with an exception: {err}"
            ) from None
        except mariadb.Error as err:
            raise JobDatabaseException(
                f"Reading SQL data for project {self.project.name} failed with an exception: {err}"
            ) from None
        finally:
            if connection is not None:
                connection.close()
