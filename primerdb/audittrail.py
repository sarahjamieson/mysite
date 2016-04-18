import sqlite3 as lite


class AuditTrail(object):
    def __init__(self):
        global con, curs
        con = lite.connect('primers.db.sqlite3')
        curs = con.cursor()

        curs.execute("CREATE TABLE IF NOT EXISTS AuditLog(ActionId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                     "Datetime TEXT, Info TEXT, Username TEXT, Previous_file TEXT)")

    def add_to_log(self, datetime, info, username, filename):
        curs.execute("INSERT INTO AuditLog (Datetime, Info, Username, Previous_File) VALUES (?, ?, ?, ?)",
                     (datetime, info, username, filename))
        con.commit()