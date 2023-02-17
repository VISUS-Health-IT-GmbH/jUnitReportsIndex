#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/data/Build.py

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
import app.sql.MultiProjectJob
import app.sql.SingleProjectJob

from typing import Optional, Union
from app.sql import ConnectionException


class BuildConnectionException(Exception):
    """
    Exception thrown when connection for branch failed
    """

    def __init__(self, message: str):
        """
        Constructor of class BuildConnectionException

        :param message: error message
        """

        super(BuildConnectionException, self).__init__(message)
        self.message = message


class BuildDatabaseException(Exception):
    """
    Exception thrown when aggregating data for build failed
    """

    def __init__(self, message: str):
        """
        Constructor of class BuildDatabaseException

        :param message: error message
        """

        super(BuildDatabaseException, self).__init__(message)
        self.message = message


class Build:
    """
    Build data returned to user on REST API when accessing: http://<backend>/<project>/<branch>/latest
                                                            http://<backend>/<project>/<branch>/<build id>

    Single project index.html   -> http://<backend>/<project>/<branch>/{latest | <build id>}/index.html
    Multi project index.html    -> http://<backend>/<project>/<branch>/{latest | <build id>}/projects/<name>/index.html
    """

    def __init__(self, project: Union[app.sql.MultiProjectJob, app.sql.SingleProjectJob]):
        """
        Constructor of class "Build"

        :param project: single or multiple project job
        """

        self.project = project


    def get(self, branch: str, id: int) -> Optional[
                Union[dict[str, Union[str, int]], dict[str, Union[str, int, list[dict[str, Union[str, int]]]]]]
            ]:
        """
        Get build specific information in JSON format

        :param branch: to get the build from
        :param id: to get the build from
        :return: {
                    "gCommit": <Git commit>,
                    "version": <(optional) version>,
                    "rc": <(optional) release candidate>,
                    "tests_success": <number of successful tests>,
                    "tests_skipped": <number of skipped tests>,
                    "tests_flaky": <number of flaky tests>,
                    "tests_failed": <number of failed tests>,
                    "type": <(optional) build type>,
                    "result_path": <path for jUnit results>
                } OR {
                    "gCommit": <Git commit>,
                    "version": <(optional) version>,
                    "rc": <(optional) release candidate>,
                    "tests_success": <number of successful tests>,
                    "tests_skipped": <number of skipped tests>,
                    "tests_flaky": <number of flaky tests>,
                    "tests_failed": <number of failed tests>,
                    "type": <(optional) build type>,
                    "result_path": <path for jUnit results>,
                    "subprojects": [
                        {
                            "subproject": <project name>,
                            "tests_success": <number of successful tests>,
                            "tests_skipped": <number of skipped tests>,
                            "tests_flaky": <number of flaky tests>,
                            "tests_failed": <number of failed tests>,
                            "result_url": <sub-URL to project index.html>,
                            "duration": <time it took to test>
                        }
                    ]
                } OR None
        :exception BranchConnectionException: when connection could not be established
        :exception BranchDatabaseException: when SQL data could not be aggregated
        """

        connection: Optional[mariadb.connection] = None

        try:
            connection = self.project.connection.get()

            build = self.project.builds.get(connection, id, branch)
            if build is None:
                return None

            if isinstance(self.project, app.sql.SingleProjectJob):
                return build

            build["subprojects"] = self.project.subprojects_in_build.all(connection, branch, id)
            if build["subprojects"] is None:
                return None

            return build
        except ConnectionException as err:
            raise BuildConnectionException(
                f"Creating connection for project {self.project.name} failed with an exception: {err}"
            ) from None
        except mariadb.Error as err:
            raise BuildDatabaseException(
                f"Reading SQL data for project {self.project.name} failed with an exception: {err}"
            ) from None
        finally:
            if connection is not None:
                connection.close()


    def last(self, branch: str) -> Optional[
                Union[dict[str, Union[str, int]], dict[str, Union[str, int, list[dict[str, Union[str, int]]]]]]
            ]:
        """
        Get build last information in JSON format

        :param branch: to get the build from
        :return: {
                    "id": <build id>,
                    "gCommit": <Git commit>,
                    "version": <(optional) version>,
                    "rc": <(optional) release candidate>,
                    "tests_success": <number of successful tests>,
                    "tests_skipped": <number of skipped tests>,
                    "tests_flaky": <number of flaky tests>,
                    "tests_failed": <number of failed tests>,
                    "type": <(optional) build type>,
                    "result_path": <path for jUnit results>
                } OR {
                    "id": <build id>,
                    "gCommit": <Git commit>,
                    "version": <(optional) version>,
                    "rc": <(optional) release candidate>,
                    "tests_success": <number of successful tests>,
                    "tests_skipped": <number of skipped tests>,
                    "tests_flaky": <number of flaky tests>,
                    "tests_failed": <number of failed tests>,
                    "type": <(optional) build type>,
                    "result_path": <path for jUnit results>,
                    "subprojects": [
                        {
                            "subproject": <project name>,
                            "tests_success": <number of successful tests>,
                            "tests_skipped": <number of skipped tests>,
                            "tests_flaky": <number of flaky tests>,
                            "tests_failed": <number of failed tests>,
                            "result_url": <sub-URL to project index.html>,
                            "duration": <time it took to test>
                        }
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

            build = builds[-1]

            if isinstance(self.project, app.sql.SingleProjectJob):
                return build

            build["subprojects"] = self.project.subprojects_in_build.all(connection, branch, build["id"])
            if build["subprojects"] is None:
                return None

            return build
        except ConnectionException as err:
            raise BuildConnectionException(
                f"Creating connection for project {self.project.name} failed with an exception: {err}"
            ) from None
        except mariadb.Error as err:
            raise BuildDatabaseException(
                f"Reading SQL data for project {self.project.name} failed with an exception: {err}"
            ) from None
        finally:
            if connection is not None:
                connection.close()
