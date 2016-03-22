import unittest
import pandas as pd
from primerdb.checkprimers import CheckPrimers
from primerdb.checksnps import CheckSNPs


class TestCheckData(unittest.TestCase):
    def setUp(self):
        df_primers = pd.read_excel('dummy_excel_errors.xlsx', header=0, parse_cols='A:M, O:X', skiprows=2,
                                   names=['Gene', 'Exon', 'Direction', 'Version', 'Primer_seq', 'Chrom', 'M13_tag',
                                          'Batch', 'project', 'Order_date', 'Frag_size', 'anneal_temp', 'Other',
                                          'snp_check', 'no_snps', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2',
                                          'action_to_take', 'check_by'],
                                   index_col=None)
        df_primers = df_primers.where((pd.notnull(df_primers)), None)
        self.checkprimers = CheckPrimers(df_primers)
        self.checksnps = CheckSNPs(df_primers)

    def testCheckGene(self):
        errors = self.checkprimers.check_gene()
        self.assertEqual(errors, 2, msg="Expected 2 errors, got: " + str(errors))

    def testCheckExon(self):
        errors = self.checkprimers.check_exon()
        self.assertEqual(errors, 2, msg="Expected 2 errors, got: " + str(errors))

    def testCheckDirection(self):
        errors = self.checkprimers.check_direction()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckVersion(self):
        errors = self.checkprimers.check_version()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckSeq(self):
        errors = self.checkprimers.check_seq()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckChrom(self):
        errors = self.checkprimers.check_chrom()
        self.assertEqual(errors, 2, msg="Expected 2 errors, got: " + str(errors))

    def testCheckTag(self):
        errors = self.checkprimers.check_tag()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckBatch(self):
        errors = self.checkprimers.check_batch()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckDate(self):
        errors = self.checkprimers.check_dates()
        self.assertEqual(errors, 2, msg="Expected 2 errors, got: " + str(errors))

    def testCheckFrag(self):
        errors = self.checkprimers.check_frag_size()
        self.assertEqual(errors, 3, msg="Expected 3 errors, got: " + str(errors))

    def testCheckTemp(self):
        errors = self.checkprimers.check_anneal_temp()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckSNPs(self):
        errors = self.checkprimers.check_no_snps()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckRS(self):
        errors = self.checksnps.check_rs()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))

    def testCheckHGVS(self):
        errors = self.checksnps.check_hgvs()
        self.assertEqual(errors, 1, msg="Expected 1 error, got: " + str(errors))
