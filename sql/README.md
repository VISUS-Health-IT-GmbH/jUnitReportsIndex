# SQL-Dateien

In diesem Ordner sind die SQL-Skripte abgelegt, die benoetigt werden, um ein Single Project oder Multi Project Job in
der MariaDB anzulegen.

- *Branches.sql* legt die Tabelle an
- *Builds.sql* legt die Tabelle an
- *GeneralInformation.sql* legt die Tabelle an
- *Subprojects.sql* legt die Tabelle an
- *Subprojects_in_Build.sql* legt die Tabelle an

## Multi Project Job

Bei solch einem Job muessen die folgenden SQL-Skripte nacheinander ausgefuehrt werden:

- GeneralInformation
- Branches
- Builds
- Subprojects
- Subprojects_in_Build

## Single Project Job

Bei solch einem Job muessen die folgenden SQL-Skripte nacheinander ausgefuehrt werden:

- GeneralInformation
- Branches
- Builds

