#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/SharedLogic.py

Copyright (C) 2021-2023, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import cherrypy

import app.sql.MultiProjectJob
import app.sql.SingleProjectJob

from app.data.Branch import *
from app.data.Build import *
from app.data.Job import *
from app.util import *


class SharedLogic:
    """
    Shared logic between single and multi subproject job
    """

    def __init__(self, name: str, root_path: str, log: Logging,
                 sql: Union[app.sql.SingleProjectJob, app.sql.MultiProjectJob], branch: Branch, build: Build, job: Job):
        """
        Constructor of class SharedLogic

        :param name: job name
        :param root_path: root path of job data
        :param log: object of "Logging"
        :param sql: object of "app.sql.SingleProjectJob" or "app.sql.MultiProjectJob"
        :param branch: object of "Branch"
        :param build: object of "Build"
        :param job: object of "Job"
        """

        self.name = name
        self.root_path = root_path
        self.log = log
        self.sql = sql
        self.branch = branch
        self.build = build
        self.job = job


    def GET(self, branch: Optional[str] = None, id: Optional[Union[str, int]] = None, *args: str) -> Optional[str]:
        """
        Shared logic for HTTP GET method

        :param branch: encoded branch name
        :param id: "latest" or build id
        :param args: possible parameters for a specific action
        :return: JSON or HTML report
        """

        # 1) get job information
        if branch is None or len(branch) == 0:
            try:
                info = self.job.get()
            except JobConnectionException as err:
                self.log.error(
                    __file__, "GET",
                    f"Retrieving general information for job {self.name} threw a database connection exception",
                    err.message
                )
                cherrypy.response.status = 500
                return
            except JobDatabaseException as err:
                self.log.error(
                    __file__, "GET",
                    f"Retrieving general information for job {self.name} threw a MariaDB SQL exception",
                    err.message
                )
                cherrypy.response.status = 500
                return

            cherrypy.response.status = 200
            return json.dumps(info)

        # 2) get branch information
        if type(branch) is not str:
            cherrypy.response.status = 400
            return

        branch = decodeBranchName(branch)
        if id is None:
            try:
                info = self.branch.get(branch)
                if info is None:
                    cherrypy.response.status = 404
                    return
            except BranchConnectionException as err:
                self.log.error(
                    __file__, "GET",
                    f"Retrieving general information for branch {branch} for job {self.name} threw a database " +
                    "connection exception", err.message
                )
                cherrypy.response.status = 500
                return
            except BranchDatabaseException as err:
                self.log.error(
                    __file__, "GET",
                    f"Retrieving general information for branch {branch} for job {self.name} threw a MariaDB SQL " +
                    "exception", err.message
                )
                cherrypy.response.status = 500
                return

            cherrypy.response.status = 200
            return json.dumps(info)

        # 3) get build information (latest or by id)
        if (type(id) is str and id != "latest") and type(id) not in [str, int]:
            cherrypy.response.status = 400
            return

        if id == "latest":
            try:
                info = self.build.last(branch)
                if info is None:
                    cherrypy.response.status = 404
                    return
                id = int(info["id"])
            except (BuildConnectionException, BuildDatabaseException) as err:
                self.log.error(
                    __file__, "GET",
                    f"Retrieving general information for latest build of branch {branch} for job {self.name} " +
                    "threw a exception while trying to retrieve actual build id", err.args
                )
                cherrypy.response.status = 500
                return

        try:
            info = self.build.get(branch, id)
            if info is None:
                cherrypy.response.status = 404
                return
            info["id"] = int(id)
        except BuildConnectionException as err:
            self.log.error(
                __file__, "GET",
                f"Retrieving general information for build {id} of branch {branch} for job {self.name} " +
                "threw a database connection exception", err.message
            )
            cherrypy.response.status = 500
            return
        except BuildDatabaseException as err:
            self.log.error(
                __file__, "GET",
                f"Retrieving general information for build {id} of branch {branch} for job {self.name} " +
                "threw a MariaDB SQL exception", err.message
            )
            cherrypy.response.status = 500
            return

        if args is None or len(args) == 0:
            cherrypy.response.status = 200
            return json.dumps(info)

        # 4) get index.html report (or any part of it)
        file, path = resolveFile(info["result_path"], *args)
        if file is None:
            self.log.warning(
                __file__, "GET", f"Retrieving file '{path}' failed as it was not found!"
            )

            cherrypy.response.status = 404
            return

        return file


    def POST(self, metadata_file: Part, zip_file: Part, failed_junit_tests: Optional[Part] = None):
        """
        Shared logic for HTTP POST method

        :param metadata_file: JSON file containing metadata
        :param zip_file: ZIP archive containing build information
        :param failed_junit_tests: TXT file containing all failed jUnit tests (maybe null)
        """

        # 1) check parameters
        try:
            assert metadata_file is not None and type(metadata_file) is Part
            assert zip_file is not None and type(zip_file) is Part

            # failed_junit_tests.txt maybe None -> otherwise check equal to metadata_file / zip_file
            assert (failed_junit_tests is not None and type(failed_junit_tests) is Part) or failed_junit_tests is None
        except AssertionError:
            self.log.error(
                __file__, "POST", f"Adding new test results for job {self.name} failed due metadata / ZIP file " +
                "incorrectly sent!"
            )
            cherrypy.response.status = 400
            return

        # 2) check metadata
        metadata = loadJSON(metadata_file)
        if metadata is None:
            self.log.error(
                __file__, "POST", f"Adding new test results for job {self.name} failed due incorrect JSON metadata!"
            )
            cherrypy.response.status = 400
            return

        metadata_json = parseJUnitMetadata(metadata)
        if metadata_json is None or \
                (isinstance(self.sql, app.sql.MultiProjectJob) and metadata_json["subprojects"] is None):
            self.log.error(
                __file__, "POST", f"Adding new test results for job {self.name} failed due to malformed JSON " +
                f"metadata: {metadata}"
            )
            cherrypy.response.status = 400
            return

        id = metadata_json["id"]
        branch = metadata_json["branch"]
        branch_encoded = encodeBranchName(branch)

        connection: Optional[mariadb.connection] = None

        try:
            connection = self.sql.connection.get()

            # 3) unzip ZIP archive (only if not already exist)
            if self.sql.builds.get(connection, id, branch) is not None or not unzipData(
                zip_file, f"{self.root_path}/data/{self.name}/{branch_encoded}/{id}"
            ):
                self.log.error(
                    __file__, "POST", f"Adding new test results for build {id} for branch {branch} for job " +
                    f"{self.name} failed due to failures unzipping ZIP archive, might already exist!"
                )
                cherrypy.response.status = 409
                return

            tests = parseJUnitXMLResults(f"{self.root_path}/data/{self.name}/{branch_encoded}/{id}")

            # 4) add build data to database (branch, build and optional subproject / subprojects_in_build)
            self.sql.branches.add(connection, branch)
            self.sql.builds.add(
                connection, id, branch, metadata_json["gCommit"], metadata_json["version"], metadata_json["rc"],
                tests["successful"] if tests is not None else 0, tests["skipped"] if tests is not None else 0,
                tests["flaky"] if tests is not None else 0, tests["failed"] if tests is not None else 0,
                metadata_json["type"], f"{self.root_path}/data/{self.name}/{branch_encoded}/{id}"
            )

            if isinstance(self.sql, app.sql.MultiProjectJob):
                for subproject in metadata_json["subprojects"]:
                    self.sql.subprojects.add(connection, subproject)
                    tests = parseJUnitXMLResults(
                        f"{self.root_path}/data/{self.name}/{branch_encoded}/{id}/projects/{subproject}"
                    )
                    duration = parseJUnitHTMLDuration(
                        f"{self.root_path}/data/{self.name}/{branch_encoded}/{id}/projects/{subproject}/index.html"
                    )

                    self.sql.subprojects_in_build.add(
                        connection, branch, id, subproject, tests["successful"] if tests is not None else 0,
                        tests["skipped"] if tests is not None else 0, tests["flaky"] if tests is not None else 0,
                        tests["failed"] if tests is not None else 0,
                        f"{self.name}/{branch_encoded}/{id}/projects/{subproject}/index.html",
                        duration if not None else 0.0
                    )

            # 5) save failed_junit_tests.txt if provided using REST call
            if failed_junit_tests is not None:
                try:
                    content = loadFailedJunitTestsTXT(failed_junit_tests)
                    with open(
                            f"{self.root_path}/data/{self.name}/{branch_encoded}/{id}/failed_junit_tests.txt", "x"
                    ) as f:
                        f.write(content)
                except Exception:
                    self.log.warning(
                        __file__, "POST", f"Saving 'failed_junit_tests.txt' for build {id} for branch {branch} for " +
                        f"job {self.name} failed with an exception. This is not a problem in this case but should " +
                        f"be noted!"
                    )
        except ConnectionException as err:
            self.log.error(
                __file__, "POST", f"Adding new test results for build {id} for branch {branch} for job {self.name} " +
                "failed due to creating connection failed with an exception", err.message
            )
            cherrypy.response.status = 500
            return
        except mariadb.Error as err:
            if isinstance(self.sql, app.sql.MultiProjectJob):
                self.log.error(
                    __file__, "POST", f"Adding new test results for build {id} for branch {branch} for job " +
                    f"{self.name} failed due to writing SQL to table Branches / Builds / Subprojects / " +
                    "Subprojects_in_Build failed with an exception", err
                )
            else:
                self.log.error(
                    __file__, "POST", f"Adding new test results for build {id} for branch {branch} for job " +
                    f"{self.name} failed due to writing SQL to table Branches / Builds failed with an exception", err
                )
            cherrypy.response.status = 500
            return
        finally:
            if connection is not None:
                connection.close()

        self.log.info(
            __file__, "POST", f"Successfully added new test results for build {id} for branch {branch} for job " +
            f"{self.name} with corresponding JSON data: {metadata_json}"
        )

        cherrypy.response.headers["Access-Control-Expose-Headers"] = "Location"
        cherrypy.response.headers["Location"] = f"/{self.name}/{branch_encoded}/{id}"
        cherrypy.response.status = 201


    def PUT(self, input_json: dict[str, Any]):
        """
        Shared logic for HTTP PUT method

        :param input_json: JSON transferred from user
        """

        if input_json is None:
            cherrypy.response.status = 400
            return

        connection: Optional[mariadb.connection] = None

        try:
            job = input_json["job"]
            git = input_json["git"]

            connection = self.sql.connection.get()
            self.sql.general.update(connection, job, git)
        except KeyError as err:
            self.log.error(
                __file__, "PUT", f"Updating general information for job {self.name} failed due to missing JSON " +
                "key-value pair(s)", err
            )
            cherrypy.response.status = 400
            return
        except ConnectionException as err:
            self.log.error(
                __file__, "PUT", f"Updating general information for job {self.name} failed due to creating " +
                "connection failed with an exception", err.message
            )
            cherrypy.response.status = 500
            return
        except mariadb.Error as err:
            self.log.error(
                __file__, "PUT", f"Updating general information for job {self.name} failed due to writing SQL to " +
                "table General failed with an exception", err
            )
            cherrypy.response.status = 500
            return
        finally:
            if connection is not None:
                connection.close()

        self.log.info(
            __file__, "PUT", f"Successfully updated general information for job {self.name} with corresponding JSON " +
            f"data: {input_json}"
        )

        cherrypy.response.status = 204


    def DELETE(self, branch: str, reportsToKeep: Optional[int] = None):
        """
        Shared logic for HTTP DELETE method

        :param branch: encoded branch name
        :param reportsToKeep: how many latest reports should be kept
        """

        if branch is None or type(branch) != str or len(branch) == 0:
            cherrypy.response.status = 400
            return

        branch = decodeBranchName(branch)

        try:
            info = self.branch.get(branch)
            if info is None:
                cherrypy.response.status = 404
                return
        except BranchConnectionException as err:
            self.log.error(
                __file__, "DELETE", f"Deleting some / all builds for branch {branch} for job {self.name} failed " +
                "because branch information could not be resolved due to creating connection failed with an exception",
                err.message
            )
            cherrypy.response.status = 500
            return
        except BranchDatabaseException as err:
            self.log.error(
                __file__, "DELETE", f"Deleting some / all builds for branch {branch} for job {self.name} failed " +
                "because branch information could not be resolved due to MariaDB errors", err.message
            )
            cherrypy.response.status = 500
            return

        connection: Optional[mariadb.connection] = None

        if reportsToKeep is None:
            try:
                connection = self.sql.connection.get()
                if isinstance(self.sql, app.sql.MultiProjectJob):
                    self.sql.subprojects_in_build.rem(connection, branch, None)
                self.sql.builds.rem(connection, None, branch)
                self.sql.branches.rem(connection, branch)
                shutil.rmtree(f"{self.root_path}/data/{self.name}/{encodeBranchName(branch)}", ignore_errors=True)
            except ConnectionException as err:
                self.log.error(
                    __file__, "DELETE", f"Deleting branch {branch} for job {self.name} failed due to creating " +
                    "connection failed with an exception", err.message
                )
                cherrypy.response.status = 500
                return
            except mariadb.Error as err:
                if isinstance(self.sql, app.sql.MultiProjectJob):
                    self.log.error(
                        __file__, "DELETE", f"Deleting branch {branch} for job {self.name} failed due to writing " +
                        "SQL to table Branches / Builds / Subprojects_in_Build failed with an exception", err
                    )
                else:
                    self.log.error(
                        __file__, "DELETE", f"Deleting branch {branch} for job {self.name} failed due to writing " +
                        "SQL to table Branches / Builds failed with an exception", err
                    )
                cherrypy.response.status = 500
                return
            except Exception as err:
                self.log.error(
                    __file__, "DELETE", f"Deleting branch {branch} for job {self.name} failed due to an " +
                    "unforeseen exception", err
                )
                cherrypy.response.status = 500
                return
            finally:
                if connection is not None:
                    connection.close()

            self.log.info(
                __file__, "DELETE", f"Successfully deleted all branch builds for {branch} for job {self.name}!"
            )

            cherrypy.response.status = 202
            return

        try:
            keep = int(reportsToKeep)
            assert keep > 0
        except ValueError:
            self.log.error(
                __file__, "DELETE", f"Deleting branch {branch} for job {self.name} failed because optional " +
                f"number of builds to keep is set to {reportsToKeep} and cannot be parsed to int!"
            )
            cherrypy.response.status = 400
            return
        except AssertionError:
            self.log.error(
                __file__, "DELETE", f"Deleting branch {branch} for job {self.name} failed because optional " +
                f"number of builds to keep {reportsToKeep} is lower than one!"
            )
            cherrypy.response.status = 400
            return

        if keep < len(info["builds"]):
            try:
                connection = self.sql.connection.get()
                for build in info["builds"][:-keep]:
                    if isinstance(self.sql, app.sql.MultiProjectJob):
                        self.sql.subprojects_in_build.rem(connection, branch, build)
                    self.sql.builds.rem(connection, build, branch)
                    shutil.rmtree(
                        f"{self.root_path}/data/{self.name}/{encodeBranchName(branch)}/{build}", ignore_errors=True
                    )
            except ConnectionException as err:
                self.log.error(
                    __file__, "DELETE", f"Deleting builds (keep {keep}) for branch {branch} for job {self.name} " +
                    "failed due to creating connection failed with an exception", err.message
                )
                cherrypy.response.status = 500
                return
            except mariadb.Error as err:
                if isinstance(self.sql, app.sql.MultiProjectJob):
                    self.log.error(
                        __file__, "DELETE", f"Deleting builds (keep {keep}) for branch {branch} for job {self.name} " +
                        "failed due to writing SQL to table Branches / Builds / Subprojects_in_Build failed with an " +
                        "exception", err
                    )
                else:
                    self.log.error(
                        __file__, "DELETE", f"Deleting builds (keep {keep}) for branch {branch} for job {self.name} " +
                        "failed due to writing SQL to table Branches / Builds failed with an exception", err
                    )
                cherrypy.response.status = 500
                return
            except Exception as err:
                self.log.error(
                    __file__, "DELETE", f"Deleting builds (keep {keep}) for branch {branch} for job {self.name} " +
                    "failed due to an unforeseen exception", err
                )
                cherrypy.response.status = 500
                return
            finally:
                if connection is not None:
                    connection.close()

            self.log.info(
                __file__, "DELETE", f"Successfully deleted all but {keep} builds for branch {branch} for job " +
                f"{self.name}!"
            )

        cherrypy.response.status = 202
