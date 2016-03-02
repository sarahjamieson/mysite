import sqlite3
import os


class CheckUpdate(object):
    """Checks if gene name given is currently in the database.

        Args:
            :param: gene to check for.
    """

    def __init__(self, gene):
        self.gene = gene

    def check_update(self):
        """Runs a query on the database to get the value in Gene column.

            Returns:
                :return: result of query.
        """
        con = sqlite3.connect(os.path.join(os.pardir, 'primers.db.sqlite3'))
        curs = con.cursor()

        curs.execute("SELECT Gene FROM Genes WHERE Gene LIKE '%s'" % self.gene)
        result = curs.fetchone()

        return result

