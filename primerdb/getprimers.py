import pandas as pd
import re
import sqlite3 as lite
from models import Primers


class ExcelToSQL(object):
    """Extracts data from excel spread sheet and imports into a sqlite database.

        Note:
            The data extraction is split into three functions to create three separate, linked tables within the
            database.

        Args:
           :param excel_file: excel file to be imported.
           :param db: database the excel file should be imported into.
    """

    def __init__(self, excel_file, db):
        self.excel_file = excel_file
        self.db = db

    def get_cursor(self):
        """Creates a connection to the database.

           Returns:
               :return: con (connection) for commit in to_sql function.
               :return: curs (cursor) to execute SQL queries.
        """

        con = lite.connect(
            self.db)  # This will create the database if it doesn't already exist.
        curs = con.cursor()

        return curs, con

    def get_sheet_name(self):
        """Returns the sheetname to be used to import data from."""

        xl = pd.ExcelFile(self.excel_file)
        sheet_names = xl.sheet_names
        for item in sheet_names:
            if re.match("(.*)Current primers", item, re.IGNORECASE):  # Only extracts most recent primers
                sheet_name = item

        return sheet_name

    def get_primers(self):
        """Extracts and checks primer data from sheet.

           Returns:
               :return: df_primers data frame containing extracted data.
               :return: primer_faults, the number of total errors in the primer data.
        """

        sheet_name = self.get_sheet_name()

        df_primers = pd.read_excel(self.excel_file, header=0, parse_cols='A:C,E', skiprows=2,
                                   names=['Gene', 'Exon', 'Direction', 'Primer_seq'],
                                   sheetname=sheet_name, index_col=None)

        return df_primers

    def to_db(self):
        self.get_cursor()
        self.get_sheet_name()
        df_primers = self.get_primers()
        for row_index, row in df_primers:
            p1 = Primers(gene=row['Gene'], exon=row['Exon'], direction=row['Direction'], primer_seq=row['Primer_seq'])
            p1.save()

