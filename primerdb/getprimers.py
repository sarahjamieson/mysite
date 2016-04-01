import pandas as pd
import re
import sqlite3 as lite
import os
from pybedtools import BedTool
import django
from checkprimers import CheckPrimers
from checksnps import CheckSNPs
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()


class GetPrimers(object):
    """Extracts data from excel spread sheet and imports it into a sqlite database.

        Args:
           :param excel_file: excel file to be imported.
           :param db: database the excel file should be imported into.
           :param filename: name to give BED file produced.
    """

    def __init__(self, excel_file, db):
        self.excel_file = excel_file
        self.db = db
        global con, curs
        con = lite.connect(self.db)  # Creates a database if it doesn't already exist.
        curs = con.cursor()

    def get_sheet_name(self):
        """Returns the sheetname to be used to import data from."""

        xl = pd.ExcelFile(self.excel_file)
        sheet_names = xl.sheet_names
        for item in sheet_names:
            if re.match("(.*)Current primers", item, re.IGNORECASE):  # Only extracts most recent primers.
                sheet_name = item
                return sheet_name

    def get_primers(self, sheetname):
        """Extracts and checks primer data from sheet.

           Returns:
               :return: df_primers_dups data frame containing extracted data which may include duplicates.
               :return: df_primers data frame containing only data necessary to get genome coordinates.
        """
        df_primers_dups = pd.read_excel(self.excel_file, header=0, parse_cols='A:M, O:X', skiprows=2,
                                        names=['Gene', 'Exon', 'Direction', 'Version', 'Primer_seq', 'Chrom', 'M13_tag',
                                               'Batch', 'project', 'Order_date', 'Frag_size', 'anneal_temp', 'Other',
                                               'snp_check', 'no_snps', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2',
                                               'action_to_take', 'check_by'],
                                        sheetname=sheetname, index_col=None)
        to_drop = ['Version', 'M13_tag', 'Batch', 'project', 'Order_date', 'Frag_size', 'anneal_temp', 'Other',
                   'snp_check', 'no_snps', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2', 'action_to_take',
                   'check_by']
        df_primers_dups = df_primers_dups.where((pd.notnull(df_primers_dups)), None)
        df_primers = df_primers_dups.drop(to_drop, axis=1)
        df_primers = df_primers.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_primers = df_primers.reset_index(drop=True)

        return df_primers_dups, df_primers

    def run_pcr(self, csv):
        """Runs virtual PCR on a CSV file using the isPcr and pslToBed tools installed from UCSC.

            Returns:
                :return: bedfile with coordinates, get_coords pulls out this data.
        """

        print "Running virtual PCR..."

        chromosomes = ['chr1.2bit', 'chr11.2bit', 'chr12.2bit', 'chrX.2bit', 'chr13.2bit', 'chr14.2bit', 'chr15.2bit',
                       'chr16.2bit', 'chr17.2bit', 'chr18.2bit', 'chr19.2bit', 'chr20.2bit', 'chr21.2bit', 'chr22.2bit',
                       'chr2.2bit', 'chr3.2bit', 'chr4.2bit', 'chr5.2bit', 'chr6.2bit', 'chr7.2bit', 'chr8.2bit',
                       'chr9.2bit', 'chr10.2bit', 'chrY.2bit']

        for chr in chromosomes:
            os.system(
                "/opt/kentools/isPcr -out=psl /media/genomicdata/ucsc_hg19_by_chr/2bit_chr/%s \
                %s %s.tmp.psl" % (chr, csv, chr[:-5]))

            pslfile = "%s.tmp.psl" % chr[:-5]
            bedfile = "%s.tmp.bed" % chr[:-5]

            # Only converts a non-empty psl file to a bed file, and removes all psl files in folder.
            if os.path.getsize(pslfile) != 0:
                os.system("/opt/kentools/pslToBed %s %s" % (pslfile, bedfile))
                os.system("rm %s" % pslfile)
                return bedfile
            else:
                os.system("rm %s" % pslfile)

    def get_coords(self, df_primers):
        """Extracts coordinates from bed file of PCR products then calculates the start and end coordinates for each
            primer.

            Returns:
                :return: df_coords dataframe with chromosome, start and end coordinates, and a name
                            (format "Gene_ExonDirection") for each primer.
        """
        primer_list = []
        names_dup = []
        names = []
        exons = []
        dirs = []
        start_coords = []
        end_coords = []
        chroms = []
        seq_position = 0
        list_position = 0
        primer_seqs = pd.DataFrame([])
        csv = 'primerseqs.csv'

        for row_index, row in df_primers.iterrows():
            primer_list.append(str(row['Primer_seq']))
            names_dup.append(str(row['Gene']) + '_' + str(row['Exon']) + str(row['Direction']))
            exons.append(str(row['Exon']))
            dirs.append(str(row['Direction']))
            for item in names_dup:
                if item not in names:
                    names.append(item)

        forwards = primer_list[::2]
        reverses = primer_list[1::2]

        while list_position < len(forwards):
            ser = pd.Series([names[list_position], forwards[list_position], reverses[list_position]])
            primer_seqs = primer_seqs.append(ser, ignore_index=True)
            list_position += 1

        primer_seqs.to_csv(csv, header=None, index=None, sep='\t')

        bedfile = self.run_pcr(csv)
        tool = BedTool(bedfile)

        for row in tool:
            chroms.append(row.chrom)
            start_coords.append(row.start)
            end_coords.append(row.start + len(primer_list[seq_position]))
            chroms.append(row.chrom)
            end_coords.append(row.end)
            start_coords.append(row.end - len(primer_list[seq_position + 1]))
            seq_position += 1

        df_coords = pd.DataFrame([])
        df_coords.insert(0, 'chrom', chroms)
        df_coords.insert(1, 'start', start_coords)
        df_coords.insert(2, 'end', end_coords)
        df_coords.insert(3, 'name', names)

        # Cannot directly convert a dataframe into a BED file (needs to be CSV first).
        bed = os.path.splitext(bedfile)[0]
        df_coords.to_csv('%s.csv' % bed, header=None, index=None, sep='\t')
        csv_file = BedTool('%s.csv' % bed)
        csv_file.saveas('%s.bed' % bed)

        # Removes unnecessary files and moves BED file into shared folder. (add /primerdb/tests for unit testing)
        os.system("rm /home/cuser/PycharmProjects/djangobook/mysite/%s.csv" % bed)
        os.system("mv /home/cuser/PycharmProjects/djangobook/mysite/%s.bed /media/sf_sarah_share/bedfiles" %
                  bed)

        df_coords.insert(4, 'Exon', exons)
        df_coords.insert(5, 'Direction', dirs)

        return df_coords

    def col_to_string(self, row):
        """Converts values in the Exon column into string values which makes merging dataframes easier."""

        return str(row['Exon'])

    def combine_coords_primers(self, df_coords, df_primers_dups):
        """Adds primer coordinates to original dataframe df_primers_dups.

            Returns:
                :return: df_all dataframe, df_primers_dups merged with df_coords.
                :return: gene_name, this will be added to the Genes table and used to check if already in database.
        """
        df_coords['Exon'] = df_coords.apply(self.col_to_string, axis=1)
        df_primers_dups['Exon'] = df_primers_dups.apply(self.col_to_string, axis=1)

        # Merge based on Exon and Direction columns
        df_combined = pd.merge(df_primers_dups, df_coords, how='left', on=['Exon', 'Direction'])

        # There is already a Chromosome column in df_primers_dups
        cols_to_drop = ['chrom']
        df_combined = df_combined.drop(cols_to_drop, axis=1)

        gene_name = df_combined.get_value(0, 'Gene')

        return df_combined, gene_name

    def check_in_db(self, gene):
        curs.execute("SELECT Gene FROM Genes WHERE Gene LIKE '%s'" % gene)
        result = curs.fetchone()

        return result

    def to_db(self, df_combined, gene_name):
        """Creates tables and inserts data into SQLite database.

            Note:
                The commented out section should only be used for the first file to initially set up the tables.
        """

        '''
        curs.execute("CREATE TABLE Primers(PrimerId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Gene TEXT, Exon TEXT, "
                     "Direction TEXT, Version INTEGER, Primer_Seq TEXT, Chrom TEXT, M13_Tag TEXT, Batch TEXT, "
                     "Project TEXT, Order_date TEXT, Frag_size INTEGER, Anneal_Temp TEXT, Other TEXT, "
                     "snp_check INTEGER, no_snps INTEGER, rs TEXT, hgvs TEXT, freq TEXT, ss TEXT, ss_proj TEXT, "
                     "other2 TEXT, action_to_take TEXT, check_by TEXT, start TEXT, end TEXT, name TEXT)")

        curs.execute("CREATE TABLE SNPs(SNP_Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Gene TEXT, Exon TEXT, "
                     "Direction TEXT, snp_check INTEGER, rs TEXT, hgvs TEXT, freq TEXT, ss TEXT, ss_proj TEXT, "
                     "other2 TEXT, action_to_take TEXT, check_by TEXT, name TEXT)")

        curs.execute("CREATE TABLE Genes(Gene_Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Gene TEXT)")
        '''

        # Checks if gene is already in the database
        uni_gene = '(u\'%s\',)' % gene_name
        gene = self.check_in_db(gene_name)

        primertable_cols_to_drop = ['snp_check', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2', 'action_to_take',
                                    'check_by']
        snptable_cols_to_drop = ['Exon', 'Direction', 'Version', 'Primer_seq', 'Chrom', 'M13_tag', 'Batch', 'project',
                                 'Order_date', 'Frag_size', 'anneal_temp', 'Other', 'no_snps', 'start', 'end']

        df_primertable = df_combined.drop(primertable_cols_to_drop, axis=1)
        df_primertable = df_primertable.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_snptable = df_combined.drop(snptable_cols_to_drop, axis=1)

        primer_check = CheckPrimers(df_primertable)
        primer_errors = primer_check.check_all()
        snp_check = CheckSNPs(df_snptable)
        snp_errors = snp_check.check_all()
        if primer_errors == 0 and snp_errors == 0:
            # If the gene is already in the database, it will delete existing data and insert new data.
            if str(uni_gene) == str(gene):
                curs.execute("DELETE FROM Primers WHERE Gene='%s'" % gene_name)
                curs.execute("DELETE FROM Genes WHERE Gene='%s'" % gene_name)
                curs.execute("DELETE FROM SNPs WHERE Gene='%s'" % gene_name)

            curs.execute("INSERT INTO Genes (Gene) VALUES (?)", (gene_name,))
            df_primertable.to_sql('Primers', con, if_exists='append', index=False)
            df_snptable.to_sql('SNPs', con, if_exists='append', index=False)

            print "Primers successfully added to database."
        else:
            print "Primers not added to database. Fix errors and try again."

        con.commit()

    def all(self):
        sheetname = self.get_sheet_name()
        df_primers_dups, df_primers = self.get_primers(sheetname)
        df_coords = self.get_coords(df_primers)
        df_combined, gene = self.combine_coords_primers(df_coords, df_primers_dups)
        self.to_db(df_combined, gene)



