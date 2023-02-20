# jUnitReportsIndex: Sammler fuer jUnit-Ergebnisse

Der Server aggregiert die Ergebnisse der auf den Gradle-Buildknoten laufenden jUnit-Tests und stellt diese dem
Entwickler zur Einsicht bereit.

## Routen

Der jUnitReportsIndex kann in der *server.py* um ein neues Interface erweitert werden, dazu ist vorher eine Ausfuehrung
der SQL-Dateien notwendig, um die Tabellen in der MariaDB zu erstellen. Es besteht die Moeglichkeit, Daten fuer einen
Single Project oder Multi Subproject Job anzulegen.

### Single Project Job

Dabei besteht der Job nur aus einem einzigen Projekt, keine weiteren Unterprojekte sind vorhanden. Es steht
dementsprechend ein kleiner Teil des REST-Interface zur Verfuegung.

In der folgenden Tabelle sind exemplarisch am fiktiven Job "REPLACE_ME_2" die Routen angegeben:

| Route                                                            | Methode | Bedeutung                                                            |
|------------------------------------------------------------------|---------|----------------------------------------------------------------------|
| http://srv-backend:12346/REPLACE_ME_2                            | POST    | Neue Ergebnisse an den Server schicken                               |
| http://srv-backend:12346/REPLACE_ME_2                            | PUT     | Angaben zu Job / Git-Repository aendern                              |
| http://srv-backend:12346/REPLACE_ME_2                            | GET     | JSON zu allen verfuegbaren Branches + generelle Infos                |
| http://srv-backend:12346/REPLACE_ME_2/{branch}                   | GET     | JSON mit generellen Infos zum Branch                                 |
| http://srv-backend:12346/REPLACE_ME_2/{branch}/{id}              | GET     | JSON mit generellen Infos zum Build vom Branch                       |
| http://srv-backend:12346/REPLACE_ME_2/{branch}/{id}/index.html   | GET     | jUnit-Report zum Build vom Branch                                    |
| http://srv-backend:12346/REPLACE_ME_2/{branch}/latest            | GET     | JSON mit generellen Infos zum letzten Build vom Branch               |
| http://srv-backend:12346/REPLACE_ME_2/{branch}/latest/index.html | GET     | jUnit-Report zum letzten Build vom Branch                            |
| http://srv-backend:12346/REPLACE_ME_2/{branch}                   | DELETE  | Loescht Branch mit all seinen Build-Reports                          |
| http://srv-backend:12346/REPLACE_ME_2/{branch}/{numToKeep}       | DELETE  | Loescht alle Build-Reports vom Branch ausser die letzten {numToKeep} |

#### Upload von Ergebnissen

Der Upload von neuen Testergebnissen besteht aus einem ZIP-Archiv und einer JSON-Datei (enthaelt Metadaten). Das ZIP-
Archiv hat ungefaehr den folgenden Inhalt:

- *index.html* (jUnit-Report)
- *classes* (jUnit-Reports einzelner Klassen)
- *css* (CSS für HTML)
- *js* (JavaScript für HTML)
- *packages* (jUnit-Reposts ganzer Pakete)
- *xmlresults* (jUnit-Reports in XML-Form)

Die JSON-Datei hat ungefaehr den folgenden Inhalt:

```json
{
  "id": "Build-Id (Jenkins-Job) [int]",
  "branch": "Branch-Name (Git-Repository) [str]",
  "commit": "Git-Commit [str]",
  "version": "(Optional) Job-Version [str]",
  "rc": "(Optional) Job-Release-Candidate [str]",
  "type": "(Optional) Job-Typ [str]"
}
```

#### Aenderungen generelle Infos

Das ist aequivalent zum Multi Subproject Job! Dazu muessen die folgenden Informationen per JSON mit uebergeben werden:

```json
{
  "job": "Link zum Jenkins-Job [str]",
  "git": "Link zum Git-Repository [str]"
}
```

#### Rueckgabe Job-Informationen

Das ist aequivalent zum Multi Subproject Job! Anhand des fiktiven Job "REPLACE_ME_2" gibt es die folgenden moeglichen
Rueckgaben (Route /REPLACE_ME_2):

1. Es gibt noch keinen Branch mit Build-Informationen

```json
{
  "general": {
    "job": "Link zum Jenkins-Job [str]",
    "git": "Link zum Git-Repository [str]"
  }
}
```

2. Es gibt mindestens einen Branch mit Build-Informationen

```json
{
  "general": {
    "job": "Link zum Jenkins-Job [str]",
    "git": "Link zum Git-Repository [str]"
  },
  "branches": [
    {
      "name": "Branch-Name [str]",
      "first": "kleinste Build-Id [int]",
      "last": "groesste Build-Id [int]"
    }
  ]
}
```

#### Rueckgabe Branch-Informationen

Das ist aequivalent zum Multi Subproject Job! Anhand des fiktiven Job "REPLACE_ME_2" gibt es die folgende Rueckgabe
(Route /REPLACE_ME_2/{Branch}):

```json
{
  "first": "kleinste Build-Id [int]",
  "last": "groesste Build-Id [int]",
  "builds": [
    "Build-Id 1 [int]", "Build-Id 2 [int]", "..."
  ]
}
```

#### Rueckgabe Build-Informationen

Das ist NICHT aequivalent zum Multi Subproject Job! Anhand des fiktiven Job "REPLACE_ME_2" gilt es fuer folgende
Rueckgabe (Route /REPLACE_ME_2/{Branch}/latest bzw. /REPLACE_ME_2/{Branch}/{Build-Id}):

```json
{
  "id": "Build-Id [int]",
  "gCommit": "Git-Commit-Hash [str]",
  "version": "(Optionale) Version [str]",
  "rc": "(Optionaler) Release Candidate [str]",
  "tests_success": "Anzahl erfolgreicher Tests [int]",
  "tests_skipped": "Anzahl uebersprungender Tests [int]",
  "tests_flaky": "Anzahl Blinkertests [int]",
  "tests_failed": "Anzahl fehlgeschlagener Tests [int]",
  "type": "(Optionaler) Build-Typ [str]",
  "result_path": "Lokaler Pfad der Testergebnisse [str]"
}
```

### Multi Subproject Job

Dabei besteht der Job aus mehreren Unterprojekten, das Hauptprojekt enthaelt keine Tests. Es steht dementsprechend ein
groesserer Teil des REST-Interface zur Verfügung.

In der folgenden Tabelle sind exemplarisch am fiktiven Job "REPLACE_ME_1" die Routen angegeben:

| Route                                                                                  | Methode | Bedeutung                                                            |
|----------------------------------------------------------------------------------------|---------|----------------------------------------------------------------------|
| http://srv-backend:12346/REPLACE_ME_1                                                  | POST    | Neue Ergebnisse an den Server schicken                               |
| http://srv-backend:12346/REPLACE_ME_1                                                  | PUT     | Angaben zu Job / Git-Repository aendern                              |
| http://srv-backend:12346/REPLACE_ME_1                                                  | GET     | JSON zu allen verfügbaren Branches + generelle Infos                 |
| http://srv-backend:12346/REPLACE_ME_1/{branch}                                         | GET     | JSON mit generellen Infos zum Branch                                 |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/{id}                                    | GET     | JSON mit generellen Infos zum Build vom Branch                       |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/{id}/index.html                         | GET     | jUnit-Report zum Build vom Branch                                    |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/{id}/projects/{subprojekt}/index.html   | GET     | jUnit-Report zum Subprojekt vom Build vom Branch                     |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/latest                                  | GET     | JSON mit generellen Infos zum letzten Build vom Branch               |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/latest/index.html                       | GET     | jUnit-Report zum letzten Build vom Branch                            |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/latest/projects/{subprojekt}/index.html | GET     | jUnit-Report zum Subprojekt vom letzten Build vom Branch             |
| http://srv-backend:12346/REPLACE_ME_1/{branch}                                         | DELETE  | Loescht Branch mit all seinen Build-Reports                          |
| http://srv-backend:12346/REPLACE_ME_1/{branch}/{numToKeep}                             | DELETE  | Loescht alle Build-Reports vom Branch ausser die letzten {numToKeep} |

#### Upload von Ergebnissen

Der Upload von neuen Testergebnissen besteht aus einem ZIP-Archiv und einer JSON-Datei (enthaelt Metadaten). Das ZIP-
Archiv hat ungefaehr den folgenden Inhalt:

- *index.html* (jUnit-Report)
- *classes* (jUnit-Reports einzelner Klassen)
- *css* (CSS für HTML)
- *js* (JavaScript für HTML)
- *packages* (jUnit-Reposts ganzer Pakete)
- *projects* (jUnit-Reports der Unterprojekte)

Die JSON-Datei hat ungefaehr den folgenden Inhalt:

```json
{
  "id": "Build-Id (Jenkins-Job) [int]",
  "branch": "Branch-Name (Git-Repository) [str]",
  "commit": "Git-Commit [str]",
  "version": "(Optional) Job-Version [str]",
  "rc": "(Optional) Job-Release-Candidate [str]",
  "type": "(Optional) Job-Typ [str]",
  "subprojects": [
    "Subprojekt 1 [str]", "Subprojekt 2 [str]", "..."
  ]
}
```

#### Aenderungen generelle Infos

Das ist aequivalent zum Single Project Job! Dazu muessen die folgenden Informationen per JSON mit uebergeben werden:

```json
{
  "job": "Link zum Jenkins-Job [str]",
  "git": "Link zum Git-Repository [str]"
}
```

#### Rueckgabe Job-Informationen

Das ist aequivalent zum Single Project Job! Anhand des fiktiven Job "REPLACE_ME_1" gibt es die folgenden moeglichen
Rueckgaben (Route /REPLACE_ME_1):

1. Es gibt noch keinen Branch mit Build-Informationen

```json
{
  "general": {
    "job": "Link zum Jenkins-Job [str]",
    "git": "Link zum Git-Repository [str]"
  }
}
```

2. Es gibt mindestens einen Branch mit Build-Informationen

```json
{
  "general": {
    "job": "Link zum Jenkins-Job [str]",
    "git": "Link zum Git-Repository [str]"
  },
  "branches": [
    {
      "name": "Branch-Name [str]",
      "first": "kleinste Build-Id [int]",
      "last": "groesste Build-Id [int]"
    }
  ]
}
```

#### Rueckgabe Branch-Informationen

Das ist aequivalent zum Single Project Job! Anhand des fiktiven Job "REPLACE_ME_1" gibt es die folgende Rueckgabe
(Route /REPLACE_ME_1/{Branch}):

```json
{
  "first": "kleinste Build-Id [int]",
  "last": "groesste Build-Id [int]",
  "builds": [
    "Build-Id 1 [int]", "Build-Id 2 [int]", "..."
  ]
}
```

#### Rueckgabe Build-Informationen

Das ist NICHT aequivalent zum Single Project Job! Anhand des fiktiven Job "REPLACE_ME_1" gilt es für folgende Rueckgabe
(Route /REPLACE_ME_1/{Branch}/latest bzw. /REPLACE_ME_1/{Branch}/{Build-Id}):

```json
{
  "id": "Build-Id [int]",
  "gCommit": "Git-Commit-Hash [str]",
  "version": "(Optionale) Version [str]",
  "rc": "(Optionaler) Release Candidate [str]",
  "tests_success": "Anzahl erfolgreicher Tests [int]",
  "tests_skipped": "Anzahl uebersprungender Tests [int]",
  "tests_flaky": "Anzahl Blinkertests [int]",
  "tests_failed": "Anzahl fehlgeschlagener Tests [int]",
  "type": "(Optionaler) Build-Typ [str]",
  "result_path": "Lokaler Pfad der Testergebnisse [str]",
  "subprojects": [
    {
      "subproject": "Subprojekt 1 Name [str]",
      "tests_success": "Anzahl erfolgreicher Tests [int]",
      "tests_skipped": "Anzahl uebersprungender Tests [int]",
      "tests_flaky": "Anzahl Blinkertests [int]",
      "tests_failed": "Anzahl fehlgeschlagener Tests [int]",
      "result_url": "Sub-URL zu Unterprojekt-Report [str]",
      "duration": "Durchführungs-Dauer [float]"
    }, {
      "subproject": "Subprojekt 2 Name [str]",
      "tests_success": "Anzahl erfolgreicher Tests [int]",
      "tests_skipped": "Anzahl uebersprungender Tests [int]",
      "tests_flaky": "Anzahl Blinkertests [int]",
      "tests_failed": "Anzahl fehlgeschlagener Tests [int]",
      "result_url": "Sub-URL zu Unterprojekt-Report [str]",
      "duration": "Durchführungs-Dauer [float]"
    }, "..."
  ]
}
```

## Verwendung

Mit 'python server.py' (bzw. 'python3 server.py') wird der Webserver gestartet.

## Installation

Im Ordner *install* befindet sich das Installationsskript für den Web-Server.

## Entwicklungsumgebung

- Python 3.10.x
- Pakete aus der requirements.txt (bspw. fuer die virtuelle Umgebung / Einbindung in der PyCharm IDE)
