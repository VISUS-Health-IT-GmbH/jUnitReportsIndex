#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
server.py

Copyright (C) 2021, VISUS Health IT GmbH
This software and supporting documentation were developed by
  VISUS Health IT GmbH
  Gesundheitscampus-Sued 15
  D-44801 Bochum, Germany
  http://www.visus.com
  mailto:info@visus.com

-> see LICENCE at root of repository
"""

import os
import cherrypy

from app import MultiProjectJob, SingleProjectJob

# ======================================================================================================================
#   Server-Tools
# ======================================================================================================================
def secure_headers():
    """
    Fuegt jeder Antwort an den Client sicherheitsrelevante HTTP-Header hinzu

    1) Strict-Transport-Security            -> nur Refresh einer Seite inklusive Subdomains
    2) X-Frame-Options                      -> Einbettung verbieten
    3) X-XSS-Protection                     -> Cross Site Scripting entgegenwirken
    4) X-Content-Type-Options               -> beim Daten hochladen nicht austricksen lassen
    5) Content-Security-Policy              -> Sicherheit gegen Attacken bieten
    6) Server                               -> von CherryPy gesetztes Feld, das Info ueber Server enthaelt, leeren
    7) X-Permitted-Cross-Domain-Policies    -> Einbindung Webseiten-Inhalte in irgendeiner Form verbieten
    """

    cherrypy.response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    cherrypy.response.headers["X-Frame-Options"] = "DENY"
    cherrypy.response.headers["X-XSS-Protection"] = "1; mode=block"
    cherrypy.response.headers["X-Content-Type-Options"] = "nosniff"
    cherrypy.response.headers["Content-Security-Policy"] = "default-app 'self'"
    cherrypy.response.headers["Server"] = "none"
    cherrypy.response.headers["X-Permitted-Cross-Domain-Policies"] = "none"


def CORS():
    """ Handhabt CORS (Cross-Origin-Resource-Sharing) bei JavaScript-Requests """

    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


# ======================================================================================================================
#   Server-Konfiguration
# ======================================================================================================================
root_path = os.path.dirname(os.path.abspath(__file__))

# Konfigurationen fuer alle REST-Schnittstellen
rest_config = {
    "/": {
        "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
        "tools.CORS.on": True
    }
}


# ======================================================================================================================
#   MAIN-Routine
# ======================================================================================================================
if __name__ == "__main__":
    # 1) Einbinden der URL-Pfade
    # ==========================
    cherrypy.tree.mount(MultiProjectJob("REPLACE_ME_1", root_path), "/REPLACE_ME_1", config=rest_config)
    # ^
    # add additional multi project jobs here after initializing the databases

    cherrypy.tree.mount(SingleProjectJob("REPLACE_ME_2", root_path), "/REPLACE_ME_2", config=rest_config)
    # ^
    # add additional single project jobs here after initializing the databases

    # 2) Erweiterte Konfiguration
    # ===========================
    cherrypy.tools.secureheaders = cherrypy.Tool("before_finalize", secure_headers, priority=60)
    cherrypy.tools.CORS = cherrypy.Tool("before_handler", CORS)

    cherrypy.config.update({
        "server.socket_port": 12346,
        "server.socket_host": "0.0.0.0"
    })

    # 3) Server starten
    # =================
    cherrypy.engine.start()
    cherrypy.engine.block()
