import sqlite3
import csv

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

#cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
#            ('First Post', 'Content for the first post')
#            )

#cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
#            ('Second Post', 'Content for the second post')
#            )

# Opening the person-records.csv file
file = open('import.csv')
 
# Reading the contents of the 
# person-records.csv file
contents = csv.reader(file)
 
# SQL query to insert data into the
# person table
insert_records = "INSERT INTO registrations (fname, lname, scaname, lodging) VALUES(?, ?, ?, ?)"
 
# Importing the contents of the file 
# into our person table
cur.executemany(insert_records, contents)
 
connection.commit()
connection.close()