#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/util/Utilities.py

Copyright (C) 2021, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import os.path

from cherrypy.lib.static import serve_file


def encodeBranchName(branch: str) -> str:
    """
    Replaces slashes ("/") in branch with double hyphens ("--")

    :param branch: decoded branch name
    :return: encoded branch name
    """

    return branch.replace("/", "--")


def decodeBranchName(branch: str) -> str:
    """
    Replaces double hyphens ("--") in branch with slashes ("/")

    :param branch: encoded branch name
    :return: decoded branch name
    """

    return branch.replace("--", "/")


def resolveFile(result_path: str, *args: str):
    """
    Tries to resolve a file (part of jUnit report)

    :param result_path: path to jUnit report of specific build of specific branch
    :param args: additional arguments from URL
    :return: file if found or None AND final path (for debugging)
    """

    final_path = os.path.normpath(os.path.join(result_path, "/".join(args)))
    if not os.path.exists(final_path) or not os.path.isfile(final_path):
        return None, final_path

    return serve_file(final_path), final_path
