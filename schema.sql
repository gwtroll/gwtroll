DROP TABLE IF EXISTS registrations;

CREATE TABLE registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regdate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checkin TIMESTAMP,
    regid INTEGER,
    badgeid INTEGER,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    scaname TEXT,
    lodging TEXT NOT NULL
);
