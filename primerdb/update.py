import sqlite3


class CheckUpdate(object):

    def __init__(self, gene):
        self.gene = gene

    def check_update(self):
        con = sqlite3.connect('primers.db.sqlite3')
        curs = con.cursor()

        curs.execute("SELECT Gene FROM Genes WHERE Gene LIKE '%s'" % self.gene)
        result = curs.fetchone()

        return result

