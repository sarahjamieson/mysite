from django.test import TestCase
from primerdb.getprimers import GetPrimers
import pandas as pd


class TestGetPrimers(TestCase):

    def setUp(self):
        self.getprimers = GetPrimers('dummy_example.xlsx', 'test.db.sqlite3', 'dummy')
        self.curs, self.con = self.getprimers.get_cursor()
        self.sheetname = self.getprimers.get_sheet_name()
        self.df_primers_dups, self.df_primers = self.getprimers.get_primers()
        self.names, self.exons, self.dirs, self.primer_list = self.getprimers.make_csv()
        self.bedfile = self.getprimers.run_pcr()
        self.df_coords = self.getprimers.get_coords()
        self.exon_string = self.getprimers.col_to_string()
        self.df_all, self.gene = self.getprimers.add_coords()

    def testGetSheet(self):
        self.assertIsNotNone(self.sheetname, msg="Sheet_name is empty")  # tests sheetname has been obtained
        self.assertIn('Current primers', self.sheetname, msg="Selected sheetname does not contain 'Current primers'")

    def testGetPrimers(self):
        self.assertIsInstance(self.df_primers, pd.DataFrame, msg="df_primers is not a data frame")
        self.assertEqual(len(self.df_primers), 10, msg="Incorrect number of rows")
        self.assertEqual(len(self.df_primers.columns), 5, msg="Incorrect number of columns")
        self.assertEqual(str(self.df_primers.iat[8, 4]), 'GTGCAATGAAGACAATGCTCC', "Entry does not match predicted")

        self.assertIsInstance(self.df_primers_dups, pd.DataFrame, msg="df_primers is not a data frame")
        self.assertEqual(len(self.df_primers_dups), 11, msg="Incorrect number of rows")
        self.assertEqual(len(self.df_primers_dups.columns), 23, msg="Incorrect number of columns")
        self.assertEqual(str(self.df_primers_dups.iat[5, 4]), 'TGAATCTCAACCATGCCTGT', "Entry does not match predicted")

    def testMakeCSV(self):
        self.assertEqual(len(self.names), )