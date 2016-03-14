class CheckSNPs(object):
    """Checks extracted SNP data for valid data entries.

       Note:
           Checks are only performed on the three columns with consistent data input.

       Args:
           :param snp_df: data frame to be checked.
    """

    def __init__(self, snp_df):
        self.snp_df = snp_df

    def check_rs(self):
        """Returns the number of errors in the 'dbSNP rs' column (IDs should all begin with "rs")."""
        import re
        check = 0
        for row_index, row in self.snp_df.iterrows():
            if row['rs'] is not None:
                if not re.match("rs(.*)", str(row['rs'])):
                    check += 1
                    print "Error: invalid dbSNP rs number, see row", row_index+4  # prints row in excel doc
        return check

    def check_hgvs(self):
        """Returns the number of errors in the 'HGVS' column (Nomenclature should begin with "c.")."""
        import re
        check = 0
        for row_index, row in self.snp_df.iterrows():
            if row['hgvs'] is not None:
                if not re.match("c(.*)", str(row['hgvs'])):
                    check += 1
                    print "Error: invalid HGVS nomenclature, see row", row_index+4  # prints row in excel doc
        return check

    def check_all(self):
        """Returns all checks as a list"""
        return self.check_rs() + self.check_hgvs()
