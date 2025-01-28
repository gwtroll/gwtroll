# gwtroll
Gulf Wars Troll System

DB Upgrades:
All Prod and Dev DBs should be on the same migrations (alembic) version.
If a code change requires a change to the DB schema, "flask db migrate" should be run on that dev environment.
That will create a new version file that will get synced with GitHub.
All systems, including the one that made the change will need to run "flask db upgrade" which will apply that change file to the DB and change the version number in the alembic_version table.
"flask db history" can be run to see the entire history of DB changes.