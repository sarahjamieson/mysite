import pandas as pd
import re
import sqlite3 as lite
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django

django.setup()


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

        sheetname = self.get_sheet_name()

        df_primers_dups = pd.read_excel(self.excel_file, header=0, parse_cols='A:M, O:X', skiprows=2,
                                        names=['Gene', 'Exon', 'Direction', 'Version', 'Primer_seq', 'Chrom', 'M13_tag',
                                               'Batch', 'project', 'Order_date', 'Frag_size', 'temp', 'Other',
                                               'snp_check', 'no_snps', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2',
                                               'action', 'check'],
                                        sheetname=sheetname, index_col=None)
        to_drop = ['']
        df_primers = df_primers_dups.drop()
        df_primers = df_primers_dups.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_primers = df_primers.reset_index(drop=True)

        print df_primers_dups
        return df_primers_dups, df_primers

    def make_csv(self):
        df_primers = self.get_primers()
        primer_list = []
        names_dup = []
        names = []
        exons = []
        dirs = []

        for row_index, row in df_primers.iterrows():
            primer_list.append(str(row['Primer_seq']))
            names_dup.append(str(row['Gene']) + "_" + str(row['Exon']) + "_" + str(row['Direction']))
            exons.append(str(row['Exon']))
            dirs.append(str(row['Direction']))
            for item in names_dup:
                if item not in names:
                    names.append(item)

        forwards = primer_list[::2]
        reverses = primer_list[1::2]

        list_position = 0
        primer_seqs = pd.DataFrame([])
        while list_position < len(forwards):
            ser = pd.Series([names[list_position], forwards[list_position], reverses[list_position]])
            primer_seqs = primer_seqs.append(ser, ignore_index=True)
            list_position += 1

        primer_seqs.to_csv('primerseqs.csv', header=None, index=None, sep='\t')

        return names, exons, dirs, primer_list

    def to_db(self):
        curs, con = self.get_cursor()
        df_primers_dups, df_primers = self.get_primers()

        curs.execute("DROP TABLE IF EXISTS Primers")

        curs.execute(
            "CREATE TABLE Primers(Primer_Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Gene TEXT, Exon TEXT, "
            "Direction TEXT, Version REAL, Primer_Seq TEXT, Chrom TEXT, M13_Tag TEXT, Batch TEXT, "
            "Project TEXT, Order_Date TIMESTAMP, Frag_Size REAL, Temp TEXT, "
            "Other TEXT)")

        df_primers_dups.to_sql(unicode('Primers'), con, if_exists='append', index=False)
