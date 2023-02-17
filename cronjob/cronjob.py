#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cronjob/cronjob.py

Copyright (C) 2021, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import requests
import datetime
import shutil
import os


# I) URL zentral festlegen
url = "http://127.0.0.1:12346/"

# II) Log-Datei fuer eventuelle Fehler-Einträge öffnen
logfile = open("cronjob.log", "a+")
logfile.write(f"{datetime.datetime.now()} Cronjob run started! ----------- \n")

# III) Zu bearbeitende Jobs festlegen
jobs = [
    "REPLACE_ME_1"
    , "REPLACE_ME_2"
    # ^
    # add additional project jobs here for automatic cleanup using the cronjob
]


def get_branches(job: str) -> list:
    """
    Requests general information from own REST-API and reads all currently known branch names from it

    :param job: which endpoint to use
    :return: list of branch names
    """

    # 1) Anfrage an URL machen und Antwort als JSON (dictionary speichern)
    backend_data = requests.get(url+job).json()

    # 2) Aus gespeicherter Antwort Liste mit Slash-freien Branchnamen erstellen
    try:
        branches = [x["name"].replace("/", "--") for x in backend_data["branches"]]
    except KeyError:
        logfile.write(f"{datetime.datetime.now()} No branches found for job {job} , skipping get_branches(). \n")
        return []

    # 3) Rückgabe
    return branches


def delete_branch_builds(branches: list, job: str):
    """ 
    Iterates over list of branches and makes a DELETE http request for each one

    :param branches: list of encoded branch names to delete old builds from
    :param job: which endpoint to use
    """

    # 1) Ueber alle Branches iterieren
    for branch in branches:
        # 2) Anfrage an DELETE-Route stellen und Statuscode speichern (hierbei die letzten 12 Builds behalten)
        status = requests.delete(url + job + f"/{branch}/12").status_code

        # 3) Bei abweichenden Status-Codes: ins Log schreiben
        if status != 202:
            logfile.write(f"{datetime.datetime.now()} WARNING: cronjob.py encountered an unexpected status code: "
                          f":[{status}] for branch {branch} and job {job} \n")


def remove_readonly(func, path, excinfo):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """

    import os
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


def delete_leftover_folders():
    """
    Retrieves the oldest known build id for each branch and deletes folders with older build ids
    """

    # 1) Dict initialisierenm, dass Branches und ihre aeltesten Build-Ids enthaelt
    branches = {}

    # 2) Anfrage an Backend stellen und Informationen ueber Branches auslesesn
    try:
        branch_info_backend = requests.get(url+job).json()["branches"]
    except KeyError as e:
        logfile.write(f"{datetime.datetime.now()} No branches found for job " + job +
                      " , skipping delete_leftover_folders(). \n")
        return

    # 3) branches-Objekt mit den erhaltenen Informationen fuellen
    for item in branch_info_backend:
        branches[item["name"].replace("/", "--")] = item["first"]

    # 4) data-Verzeichnis durchgehen und Branch-Unterordner nach ueberflüssigen IDs durchsuchen
    # 4.1) data-Ordner-Pfad festlegen
    data_dir = os.path.normpath(os.path.join(os.getcwd(), f'../data/{job}'))

    # 4.2) Unterordner für alle Branches durchgehen
    for branch_dir in os.listdir(data_dir):
        # 4.3) Falls das gefundene Objekt ein Ordner ist, weiter durch die enthaltenen Build-Ordner iterieren
        if os.path.isdir(os.path.join(data_dir, branch_dir)):
            # 4.4) Jeden Build-Ordner pruefen
            for build_dir in os.listdir(os.path.join(data_dir, branch_dir)):
                # 4.5) Falls die in branches enthaltene, aelteste Build-ID groesser ist als Build-ID im Ordnernamen...
                if branches[branch_dir] > int(build_dir):
                    try:
                        # 4.6) ...loeschen
                        shutil.rmtree(os.path.join(data_dir, branch_dir, build_dir), onerror=remove_readonly)
                        logfile.write(f"{datetime.datetime.now()} cronjob.py DELETED "
                                      f"{os.path.join(data_dir, branch_dir, build_dir)} for job {job} \n")
                    except Exception as e:
                        logfile.write(
                            f"{datetime.datetime.now()} WARNING: cronjob.py encountered an error"
                            f" when trying to delete [{os.path.join(data_dir, branch_dir, build_dir)} for job {job}, "
                            f"{str(e)}]  \n")


for job in jobs:
    # III) Skript starten
    delete_branch_builds(get_branches(job), job)
delete_leftover_folders()

# IV) Erfolgreichen Durchlauf im Log nachtragen
logfile.write(f"{datetime.datetime.now()} Cronjob run finished for jobs {jobs}! ----------- \n")

# V) Log-Datei schließen
logfile.close()
