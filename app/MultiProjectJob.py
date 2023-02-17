#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/MultiProjectJob.py

Copyright (C) 2021, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import app.sql.MultiProjectJob

from .SharedLogic import *
from app.data import *
from app.sql.Connection import *
from app.util import *


@cherrypy.expose
class MultiProjectJob:
    """
    Interface for all multi project jobs
    """

    def __init__(self, name: str, root_path: str):
        """
        Constructor of class SingleProjectJob

        :param name: job name
        :param root_path: root path of application
        """

        self.name = name
        self.root_path = root_path

        self.log = Logging(f"{self.root_path}/log/{self.name}.log")
        self.sql = app.sql.MultiProjectJob(
            ConnectionInfo("127.0.0.1", 3306, "root", "N0t$0$3cur3D4t4b4$3P4$$w0rd", self.name)
        )

        self.branch = Branch(self.sql)
        self.build = Build(self.sql)
        self.job = Job(self.sql)

        self.sharedlogic = SharedLogic(self.name, self.root_path, self.log, self.sql, self.branch, self.build, self.job)


    def GET(self, branch: Optional[str] = None, id: Optional[Union[str, int]] = None, *args: str):
        """
        Depicts every route regarding a single project job to show / request information

        Routes:     1) /                                                -> general information on all branches
                    2) /<branch>                                        -> all information on specific branch
                    3) /<branch>/latest                                 -> all information on latest build
                    4) /<branch>/latest/index.html                      -> report on latest build of specific branch
                    5) /<branch>/latest/projects/<name>/index.html      -> report on project on latest build
                    6) /<branch>/<build id>/                            -> all information on distinct build
                    7) /<branch>/<build id>/index.html                  -> report on distinct build of specific branch
                    8) /<branch>/<build id>/projects/<name>/index.html  -> report on project of distinct build

        HTTP-Code:  1) 200, correct request
                    2) 400, parameter is incorrect
                    3) 404, information regarding branch or build not found
                    4) 500, server error

        :param branch: encoded branch name
        :param id: "latest" or build id
        :param args: possible parameters for a specific action
        :return: JSON or HTML report
        """

        return self.sharedlogic.GET(branch, id, *args)


    def POST(self, metadata_file: Part, zip_file: Part):
        """
        Depicts the route to upload files

        Routes:     1) /   -> uploads new build information

        HTTP-Code:  1) 201, correct upload
                    2) 400, metadata / ZIP archive missing / not correct
                    3) 409, when build already exists or unzipping fails
                    4) 500, server error

        :param metadata_file: JSON file containing metadata
        :param zip_file: ZIP archive containing build information
        :return: None, only sets: cherrypy.response.headers["Location"] = "/<job>/<branch>/<build id>"
        """

        self.sharedlogic.POST(metadata_file, zip_file)


    @cherrypy.tools.json_in()
    def PUT(self):
        """
        Updates general information on job

        HTTP-Code:  1) 204, correct update
                    2) 400, JSON sent not correct or missing
                    3) 500, server error
        """

        self.sharedlogic.PUT(cherrypy.request.json)


    def DELETE(self, branch: str, reportsToKeep: Optional[int] = None):
        """
        Deletes a branch and optionally keep builds

        Routes:     1) /<Branch>                -> deletes everything on specific branch
                    2) /<Branch>/<Cnt. Reports> -> deletes everything but last <Cnt. Reports> reports

        HTTP-Code:  1) 202, delete done (deletion in the file system cannot be checked)
                    2) 400, any parameter wrong
                    3) 404, information regarding branch not found
                    4) 500, server error

        :param branch: encoded branch name
        :param reportsToKeep: how many latest reports should be kept
        """

        self.sharedlogic.DELETE(branch, reportsToKeep)
