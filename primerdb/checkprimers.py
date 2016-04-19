class CheckPrimers(object):
    """Checks extracted Primer data for valid data entries

        Note:
           Checks are only performed on columns with consistent data entries.
        Args:
            :param primer_df: data frame to be checked.
    """

    def __init__(self, primer_df, snp_df):
        self.primer_df = primer_df
        self.snp_df = snp_df
        global specials, error_details, check
        specials = ['?', '!', '~', '@', '#', '^', '&', '+', ':', ';', '%', '{', '}', '[', ']', ',']
        error_details = []
        check = 0

    def check_gene(self):
        """Returns the number of errors in the 'Gene' column (checks for special characters)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            for char in row['Gene']:
                if char in specials:
                    check += 1
                    error = "Special character found in column 'Gene', see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_exon(self):
        """Returns the number of errors in the 'Exon' column (checks for special characters)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            for char in str(row['Exon']):
                if char in specials:
                    check += 1
                    error = "Special character found in column 'Exon', see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_direction(self):
        """Returns the number of errors in the 'Direction' column (should only contain "F" or "R")."""
        global check, error_details
        direction_list = ['F', 'R']
        for row_index, row in self.primer_df.iterrows():
            if row['Direction'] not in direction_list:
                check += 1
                error = "Invalid primer direction, see row %s in file" % (row_index + 4)
                error_details.append(error)

    def check_version(self):
        """Returns the number of errors in the 'Version' column (should be a numerical value)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            if (row['Version'] is not None) and (not isinstance(row['Version'], float)) and (
                    not isinstance(row['Version'], int)):
                check += 1
                error = "Version number not a valid entry, see row %s in file" % (row_index + 4)
                error_details.append(error)

    def check_seq(self):
        """Returns the number of errors in the 'Primer-Seq' column (should only contain "A", "T", "C" or "G")."""
        nuc_list = ['A', 'T', 'C', 'G']
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            for letter in row['Primer_seq'].strip():
                if letter not in nuc_list:
                    check += 1
                    error = "Invalid DNA primer sequence, see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_tag(self):
        """Returns the number of errors in the 'M13_tag' column (should only contain "Y" or "N")."""
        global check, error_details
        tag_list = ['Y', 'N']
        for row_index, row in self.primer_df.iterrows():
            if (row['M13_tag'] is not None) and (row['M13_tag'].upper() not in tag_list):
                check += 1
                error = "M13_tag not a valid entry, see row %s in file" % (row_index + 4)
                error_details.append(error)

    def check_batch(self):
        """Returns the number of errors in the 'Batch_no' column (checks for special characters)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            if row['Batch'] is not None:
                for char in row['Batch']:
                    if char in specials:
                        check += 1
                        error = "Special character found in column 'Batch_no', see row %s in file" % (row_index + 4)
                        error_details.append(error)

    def check_dates(self):
        """Returns the number of errors in the 'Order_date' column (should be a datetime object)."""
        import datetime
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            if row['Order_date'] is not None:
                if isinstance(row['Order_date'], datetime.date):
                    check += 0
                else:
                    check += 1
                    error = "Order date not a valid date, see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_frag_size(self):
        """Returns the number of errors in the 'Frag_size' column (should be numerical and a valid length)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            if row['Frag_size'] is not None:
                if (not isinstance(row['Frag_size'], float)) and (not isinstance(row['Frag_size'], int)):
                    check += 1
                    error = "Fragment size not a valid entry, see row %s in file" % (row_index + 4)
                    error_details.append(error)
                elif (row['Frag_size'] < 0) or (row['Frag_size'] > 1000):
                    check += 1
                    error = "Fragment size not within acceptable range, see row %s" % (row_index + 4)
                    error_details.append(error)

    def check_anneal_temp(self):
        """Returns the number of errors in the 'Anneal_temp' column (should be numerical and a valid temperature)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            if row['anneal_temp'] is not None:
                if (isinstance(row['anneal_temp'], float)) or (isinstance(row['anneal_temp'], int)):
                    if (row['anneal_temp'] < 0) or (row['anneal_temp'] > 150):
                        check += 1
                        error = "Annealing temperature not within acceptable range, see row %s in file" \
                                % (row_index + 4)
                        error_details.append(error)

    def check_chrom(self):
        """Returns the number of errors in the 'Chrom' column (should be 1-23, X or Y)."""
        global check, error_details
        chromosomes = [range(1, 23), 'X', 'Y']
        for row_index, row in self.primer_df.iterrows():
            if row['Chrom'] is not None:
                if row['Chrom'] not in chromosomes:
                    check += 1
                    error = "Invalid chromosome, see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_no_snps(self):
        """Returns the number of errors in the 'Total SNPs' column (this should be a numerical value)."""
        global check, error_details
        for row_index, row in self.primer_df.iterrows():
            if row['no_snps'] is not None:
                if (not isinstance(row['no_snps'], float)) and (not isinstance(row['no_snps'], int)):
                    check += 1
                    error = "Invalid entry in 'Total_SNPs' column, see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_rs(self):
        """Returns the number of errors in the 'dbSNP rs' column (IDs should all begin with "rs")."""
        import re
        global check, error_details
        for row_index, row in self.snp_df.iterrows():
            if row['rs'] is not None:
                if not re.match("rs(.*)", str(row['rs'])):
                    check += 1
                    error = "Invalid dbSNP rs number, see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_hgvs(self):
        """Returns the number of errors in the 'HGVS' column (Nomenclature should begin with "c.")."""
        import re
        global check, error_details
        for row_index, row in self.snp_df.iterrows():
            if row['hgvs'] is not None:
                if not re.match("c(.*)", str(row['hgvs'])):
                    check += 1
                    error = "Invalid HGVS nomenclature, see row %s in file" % (row_index + 4)
                    error_details.append(error)

    def check_all(self):
        """Returns all checks as a list"""
        self.check_gene()
        self.check_exon()
        self.check_direction()
        self.check_version()
        self.check_seq()
        self.check_tag()
        self.check_batch()
        self.check_dates()
        self.check_frag_size()
        self.check_anneal_temp()
        self.check_chrom()
        self.check_no_snps()
        self.check_rs()
        self.check_hgvs()

        return check, error_details
