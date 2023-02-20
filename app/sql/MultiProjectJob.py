#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/sql/MultiProjectJob.py

Copyright (C) 2021-2023, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

from app.sql.tables import Branches, Builds, GeneralInformation, Subprojects, Subprojects_in_Build
from .Connection import *


class MultiProjectJob:
    """
    Database connection to a MariaDB database for a multi project build

    Functions:  1) connection.get       -> connection to database

    Tables:     1) GeneralInformation   -> general information on single project job
                2) Branches             -> information on job branches
                3) Builds               -> information on job builds
                4) Subprojects          -> information on job subprojects
                5) Subprojects_in_Build -> combination table of builds and subprojects
    """

    def __init__(self, info: ConnectionInfo):
        """
        Constructor for class SingleProjectBuild

        :param info: connection information
        """

        self.name = info.database
        self.connection = Connection(info)
        self.general = GeneralInformation()
        self.branches = Branches()
        self.builds = Builds()

        self.subprojects = Subprojects()
        self.subprojects_in_build = Subprojects_in_Build()
