from primerdb.getprimers import GetPrimers
import pandas as pd
import unittest
import os


class TestGetPrimers(unittest.TestCase):
    """
    def setUp(self):
        self.setup_test_data()
    """
    @classmethod
    def setUpClass(cls):
        super(TestGetPrimers, cls).setUpClass()
        cls.getprimers = GetPrimers(os.path.join(os.pardir, 'dummy_excel.xlsx'), 'test.db.sqlite3', 'dummy')
        cls.curs, cls.con = cls.getprimers.get_cursor()
        cls.sheetname = cls.getprimers.get_sheet_name()
        cls.df_primers_dups, cls.df_primers = cls.getprimers.get_primers()
        cls.names, cls.exons, cls.dirs, cls.primer_list = cls.getprimers.make_csv()
        cls.run = cls.getprimers.run_pcr()
        cls.df_coords = cls.getprimers.get_coords()
        cls.df_all, cls.gene = cls.getprimers.add_coords()

    """
    def setup_test_data(self):
        self.getprimers = GetPrimers(os.path.join(os.pardir, 'dummy_excel.xlsx'), 'test.db.sqlite3', 'dummy')
        self.curs, self.con = self.getprimers.get_cursor()
        self.sheetname = self.getprimers.get_sheet_name()
        self.df_primers_dups, self.df_primers = self.getprimers.get_primers()
        self.names, self.exons, self.dirs, self.primer_list = self.getprimers.make_csv()
        self.run = self.getprimers.run_pcr()
        self.df_coords = self.getprimers.get_coords()
        self.df_all, self.gene = self.getprimers.add_coords()

    """

    def testGetSheet(self):
        self.assertIsNotNone(self.sheetname, msg="Sheet_name is empty")  # tests sheetname has been obtained
        self.assertIn('Current primers', self.sheetname, msg="Selected sheetname does not contain 'Current primers'")

    def testGetPrimers(self):
        self.assertIsInstance(self.df_primers, pd.DataFrame, msg="df_primers is not a data frame")
        self.assertEqual(len(self.df_primers), 10, msg="Incorrect number of rows")
        self.assertEqual(len(self.df_primers.columns), 5, msg="Incorrect number of columns")
        self.assertEqual(str(self.df_primers.iat[8, 4]), 'GTGCAATGAAGACAATGCTCC', "Entry does not match predicted")

        self.assertIsInstance(self.df_primers_dups, pd.DataFrame, msg="df_primers_dups is not a data frame")
        self.assertEqual(len(self.df_primers_dups), 11, msg="Incorrect number of rows")
        self.assertEqual(len(self.df_primers_dups.columns), 23, msg="Incorrect number of columns")
        self.assertEqual(str(self.df_primers_dups.iat[5, 4]), 'TGAATCTCAACCATGCCTGT', "Entry does not match predicted")

    def testMakeCSV(self):
        self.assertEqual(len(self.names), 11, msg="Names list unexpected size")
        self.assertEqual(len(self.exons), 11, msg="Exons list unexpected size")
        self.assertEqual(len(self.dirs), 11, msg="Directions list unexpected size")
        self.assertEqual(len(self.primer_list), 11, msg="Primer sequences list unexpected size")
        self.assertEqual(str(self.primer_list[3]), 'GGATTGTTGATTTCAGTTGAGC', "Entry does not match predicted")

    def testGetCoords(self):
        self.assertIsInstance(self.df_coords, pd.DataFrame, msg="df_coords is not a data frame")
        self.assertEqual(len(self.df_coords), 10, msg="Incorrect number of rows")
        self.assertEqual(len(self.df_coords.columns), 4, msg="Incorrect number of columns")
        self.assertEqual(str(self.df_coords.iat[3, 3]), 'COL4A5_2R', "Entry does not match predicted")

    def testAddCoords(self):
        self.assertEqual(str(self.gene), 'COL4A5', msg="Incorrect gene name")
        self.assertIsInstance(self.df_all, pd.DataFrame, msg="df_coords is not a data frame")
        self.assertEqual(len(self.df_all), 11, msg="Incorrect number of rows")
        self.assertEqual(len(self.df_all.columns), 26, msg="Incorrect number of columns")
        self.assertEqual(str(self.df_all.iat[4, 10]), '125', msg="Entry does not match predicted")

    def testToDb(self):
        self.getprimers.to_db()

        self.curs.execute("SELECT * FROM 'Primers'")
        primer_result = self.curs.fetchone()
        self.assertIsNotNone(primer_result, msg="Primers table is empty")

        self.curs.execute("SELECT * FROM 'Genes'")
        gene_result = self.curs.fetchone()
        self.assertIsNotNone(gene_result, msg="Genes table is empty")

        self.curs.execute("SELECT * FROM 'SNPs'")
        snp_result = self.curs.fetchone()
        self.assertIsNotNone(snp_result, msg="SNPs table is empty")


    @classmethod
    def tearDownClass(cls):
        super(TestGetPrimers, cls).tearDownClass()

    """
    def setUpClass(cls):
        super(TestGetPrimers, cls).setUpClass()
        cls.getprimers = GetPrimers(os.path.join(os.pardir, 'dummy_excel.xlsx'), 'test.db.sqlite3', 'dummy')
        cls.curs, cls.con = cls.getprimers.get_cursor()
        cls.sheetname = cls.getprimers.get_sheet_name()
        cls.df_primers_dups, cls.df_primers = cls.getprimers.get_primers()
        cls.names, cls.exons, cls.dirs, cls.primer_list = cls.getprimers.make_csv()
        cls.run_pcr()
        cls.df_coords = cls.getprimers.get_coords()
        cls.df_all, cls.gene = cls.getprimers.add_coords()
    """