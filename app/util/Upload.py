#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app/util/Upload.py

Copyright (C) 2021, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import io
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

from cherrypy._cpreqbody import Part
from typing import Any, Optional


def loadJSON(metadata: Part) -> Optional[dict[str, Any]]:
    """
    Tries to resolve JSON (in CherryPy object)

    :param metadata: JSON (in CherryPy object)
    :return: JSON dict if worked correctly, None otherwise
    """

    data = None
    try:
        data = io.BytesIO()
        while True:
            bits = metadata.file.read(8192)
            if not bits:
                break
            data.write(bits)
        data.seek(0)

        return json.loads(data.read().decode("UTF-8"))
    except Exception:
        return None
    finally:
        if data is not None:
            data.close()
            del data


def parseJUnitMetadata(metadata: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Parses metadata JSON file and maps keys / values

    :param metadata: JSON object with metadata from POST
    :return: {
                "branch": <Git branch>,
                "id": <build id>,
                "gCommit": <Git commit>,
                "version": <(optional) version>,
                "rc": <(optional) release candidate>,
                "type": <(optional) build type>,
                "subprojects": <(optional) list of subprojects>
            } or None
    """

    try:
        ret = {
            "branch": metadata["branch"],
            "id": int(metadata["id"])
        }

        if "commit" in metadata:
            ret["gCommit"] = metadata["commit"]
        elif "git_commit" in metadata:
            ret["gCommit"] = metadata["git_commit"]
        else:
            # Git commit is necessary not optional
            raise KeyError

        if "type" in metadata:
            ret["type"] = metadata["type"]
        elif "build_version" in metadata:
            ret["type"] = metadata["build_version"]
        else:
            ret["type"] = None

        if "subprojects" in metadata:
            ret["subprojects"] = list(metadata["subprojects"])
        elif "projects" in metadata:
            ret["subprojects"] = list(metadata["projects"])
        else:
            ret["subprojects"] = None

        ret["version"] = metadata["version"] if "version" in metadata else None
        ret["rc"] = metadata["rc"] if "rc" in metadata else None

        return ret
    except (KeyError, ValueError):
        return None


def unzipData(zip: Part, path: str) -> bool:
    """
    Tries to unzip a ZIP archive (in CherryPy object) to a given path

    :param zip: ZIP archive (in CherryPy object)
    :param path: to unzip content to
    :return: True if everything worked correctly, False otherwise
    """

    data = None
    try:
        data = io.BytesIO()
        while True:
            bits = zip.file.read(524288)
            if not bits:
                break
            data.write(bits)
        data.seek(0)

        with zipfile.ZipFile(data, "r") as out:
            out.extractall(path)
    except Exception:
        shutil.rmtree(path, ignore_errors=True)
        return False
    finally:
        if data is not None:
            data.close()
            del data

    return True


def parseJUnitXMLResults(path: str) -> Optional[dict[str, int]]:
    """
    Parses jUnit XML results and resolves number of successful / skipped / flaky / failed tests

    :param path: where XML files can be found
    :return: {
                "successful": <number of tests>,
                "skipped": <number of tests>,
                "flaky": <number of tests>,
                "failed": <number of tests>
            } or None
    """

    all_tests = 0
    ret = {
        "successful": 0,
        "skipped": 0,
        "flaky": 0,
        "failed": 0
    }

    try:
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(".xml"):
                    data = ET.parse(os.path.join(root, file)).getroot()

                    # get number of all tests
                    all_tests += int(data.attrib["tests"])

                    # all skipped tests
                    ret["skipped"] += int(data.attrib["skipped"])

                    # all flaky tests
                    flaky = len(data.findall(".//testcase/flakyFailure"))
                    ret["flaky"] += flaky

                    # all failed tests
                    ret["failed"] += int(data.attrib["failures"]) - flaky
    except (KeyError, ValueError):
        return None

    # all successful tests
    ret["successful"] = all_tests - (ret["flaky"] + ret["failed"])
    return ret


def parseJUnitHTMLDuration(path: str) -> Optional[float]:
    """
    Parses jUnit HTML report and resolves duration

    :param path: where HTML report is located
    :return: duration in seconds or None
    """

    summary = None

    with open(path) as file:
        html = file.read()
        html = re.sub(r'<(.*?)>', '', html)
        html = html.replace('\r', '').replace('\n', '').split(" ")

        for part in html:
            # format is always "Summary1tests2failures3ignored4m56.07sduration100%successfulIgnored"
            if part.startswith("Summary") and "tests" in part:
                summary = part
                break

    duration = summary.split("ignored", 1)[1].split("duration", 1)[0]
    try:
        if duration.find("h") < 0:
            hours = 0.0
        else:
            hours, duration = duration.split("h", maxsplit=1)
            hours = float(hours)

        if duration.find("m") < 0:
            minutes = 0.0
        else:
            minutes, duration = duration.split("m", maxsplit=1)
            minutes = float(minutes)

        seconds = 0.0 if duration.find("s") < 0 else float(duration.split("s")[0])

        return round(seconds + minutes*60.0 + hours*3600.0, 3)
    except ValueError:
        return None


def loadFailedJunitTestsTXT(failed: Part) -> Optional[str]:
    """
    Tries to resolve text content (in CherryPy object)

    :param failed: text content (in CherryPy object)
    :return: python string if worked correctly, None otherwise
    """

    data = None
    try:
        data = io.BytesIO()
        while True:
            bits = failed.file.read(512)
            if not bits:
                break
            data.write(bits)
        data.seek(0)

        return str(data.read().decode("UTF-8"))
    except Exception:
        return None
    finally:
        if data is not None:
            data.close()
            del data
