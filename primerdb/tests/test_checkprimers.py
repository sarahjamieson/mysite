import unittest
import pandas as pd
from primerdb.checkprimers import CheckPrimers


class TestCheckPrimers(unittest.TestCase):

    def setUp(self):
        df_primers = pd.read_excel('dummy_excel_errors.xlsx', header=0, parse_cols='A:M, O:X', skiprows=2,
                                   index_col=None)
        self.checkprimers = CheckPrimers(df_primers)

    def testCheckGene(self):
        errors = self.checkprimers.check_gene()
        self.assertEqual(errors, 2, msg="")

