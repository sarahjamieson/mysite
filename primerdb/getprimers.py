import pandas as pd
import re
import sqlite3 as lite
import os
from pybedtools import BedTool
import django
from checkprimers import CheckPrimers
from pandas import ExcelWriter
import datetime
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()


class GetPrimers(object):
    """Extracts data from excel spread sheet and imports it into a sqlite database.
           :param excel_file: excel file to be imported.
           :param db: database the excel file should be imported into.
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
            if re.match('(.*)Current primers', item, re.IGNORECASE):  # Only extracts most recent primers.
                sheet_name = item
                return sheet_name

    def get_primers(self, sheetname):
        """Extracts primer data from sheet.
           Function reads an excel sheet using pandas and stores this in the df_primers_dups data frame (contains
           duplicated rows).The df_primers data frame will go on to be used in the virtual PCR so irrelevant columns
           are dropped and any duplicate rows are removed.
               :param sheetname: sheet data to be extracted from
               :return df_primers_dups: data frame containing extracted data which may include duplicates.
               :return df_primers: data frame containing only data necessary to get genome coordinates.
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

        df_primers_dups = df_primers_dups.where((pd.notnull(df_primers_dups)), None)  # easier to work with than NaN
        df_primers = df_primers_dups.drop(to_drop, axis=1)
        df_primers = df_primers.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_primers = df_primers.reset_index(drop=True)

        return df_primers_dups, df_primers

    def run_pcr(self, csv):
        """Runs virtual PCR on a CSV file using the isPcr and pslToBed tools installed from UCSC.
                :param csv: a csv file is need as an input with format "name, forward, reverse".
                :return bedfile: with results of virtual PCR if there is a match.
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
        """Generates csv file for virtual PCR and imports results into a pandas data frame.
                :param df_primers: data frame of primer data.
                :return df_coords: data frame with chromosome, start and end coordinates, and a name
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
        csv = '%s.csv' % self.excel_file[:-5]

        # (1) Gets sequences, exons and directions, splits the sequences into F+R and combines into series and then csv.
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

        # (2) Runs virtual PCR on generated csv.
        bedfile = self.run_pcr(csv)
        tool = BedTool(bedfile)

        # (3) Uses results to calculate start and end position of each primer (results give PCR product). Adds to df.
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

        # (4) Generates a bed file from df_coords (not currently used in application).
        bed = os.path.splitext(bedfile)[0]
        df_coords.to_csv('%s.csv' % bed, header=None, index=None, sep='\t')  # cannot directly convert to bed.
        csv_file = BedTool('%s.csv' % bed)
        csv_file.saveas('%s.bed' % bed)

        df_coords.insert(4, 'Exon', exons)  # not need in bed file so added after.
        df_coords.insert(5, 'Direction', dirs)

        # Removes unnecessary files and moves BED file into shared folder. (add /primerdb/tests for unit testing)
        os.system("rm /home/cuser/PycharmProjects/django_apps/mysite/%s.csv" % bed)
        os.system("mv /home/cuser/PycharmProjects/django_apps/mysite/%s.bed /media/sf_sarah_share/bedfiles" %
                  bed)
        os.system("rm /home/cuser/PycharmProjects/django_apps/mysite/%s" % csv)

        return df_coords

    def col_to_string(self, row):
        """Converts values in the Exon column into string values which makes merging data frames easier.
            :param row: for every row in Exon column.
            :return string of value.
        """

        return str(row['Exon'])

    def combine_coords_primers(self, df_coords, df_primers_dups):
        """Adds primer coordinates to original df_primers_dups data frame.
                :param df_primers_dups: data frame with primer data from excel.
                :param df_coords: data frame with chrom, start, end, name, exon, direction.
                :return df_combined: data frame of merge between df_coords and df_primers_dups.
                :return gene_name: this will be added to the Genes table and used to check if already in database.
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
        """Queries the database to check if data for a particular gene is already present.
            :param gene: a gene name to check against the database.
            :return result: query result which will be a gene if already in database and None if not.
        """
        curs.execute("SELECT Gene FROM Genes WHERE Gene LIKE '%s'" % gene)
        result = curs.fetchone()

        return result

    def to_db(self, df_combined, gene_name):
        """Creates tables and adds data into the database.
           Function modifies the given data frame to generate three tables in the database (Primers, SNPs, Genes) and
           performs data checks. If data for a particular gene is already in the database, this is overridden and the
           previous data is saved to an excel document (archived_files).
                The commented out section should only be used for the first file to initially set up the tables.
                :param gene_name: gene to check against database.
                :param df_combined: data frame to be inserted into database.
                :return info: description of action performed (for audit log).
                :return archived_filename: filename the previous data is saved under (for audit log).
        """

        # (1) Creates database schema
        curs.execute("CREATE TABLE IF NOT EXISTS Primers(PrimerId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                     "Gene TEXT, Exon TEXT, Direction TEXT, Version INTEGER, Primer_Seq TEXT, Chrom TEXT, M13_Tag TEXT"
                     ", Batch TEXT, Project TEXT, Order_date TEXT, Frag_size INTEGER, Anneal_Temp TEXT, Other TEXT, "
                     "snp_check INTEGER, no_snps INTEGER, rs TEXT, hgvs TEXT, freq TEXT, ss TEXT, ss_proj TEXT, "
                     "other2 TEXT, action_to_take TEXT, check_by TEXT, start TEXT, end TEXT, name TEXT)")

        curs.execute("CREATE TABLE IF NOT EXISTS SNPs(SNP_Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Gene TEXT, "
                     "Exon TEXT, Direction TEXT, snp_check INTEGER, rs TEXT, hgvs TEXT, freq TEXT, ss TEXT, "
                     "ss_proj TEXT, other2 TEXT, action_to_take TEXT, check_by TEXT, name TEXT)")

        curs.execute("CREATE TABLE IF NOT EXISTS Genes(Gene_Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Gene TEXT)")

        # (2) Drops unnecessary columns to make two tables and removes duplicates.
        primertable_cols_to_drop = ['snp_check', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2', 'action_to_take',
                                    'check_by']
        snptable_cols_to_drop = ['Exon', 'Direction', 'Version', 'Primer_seq', 'Chrom', 'M13_tag', 'Batch', 'project',
                                 'Order_date', 'Frag_size', 'anneal_temp', 'Other', 'no_snps', 'start', 'end']

        df_primertable = df_combined.drop(primertable_cols_to_drop, axis=1)
        df_primertable = df_primertable.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_snptable = df_combined.drop(snptable_cols_to_drop, axis=1)

        # (3) Performs data checks using CheckPrimers and CheckSNPs classes.
        check = CheckPrimers(df_primertable, df_snptable)
        total_errors, error_details = check.check_all()

        # (4) Checks if gene data already in database.
        uni_gene = '(u\'%s\',)' % gene_name
        gene = self.check_in_db(gene_name)   # this outputs a unicode string

        # (5) Adds to database if no errors. Overrides data if already present.
        archived_filename = None
        if total_errors == 0:
            if str(uni_gene) == str(gene):
                # Add query to data frame then save to excel.
                get_old_query = "SELECT p.Gene, p.Exon, p.Direction, p.Version, p.Primer_seq, p.Chrom, p.M13_Tag, " \
                                "p.Batch, p.Project, p.Order_date, p.Frag_size, p.Anneal_Temp, p.Other, s.snp_check, " \
                                "p.no_snps, s.rs, s.hgvs, s.freq, s.ss, s.ss_proj, s.other2, s.action_to_take, " \
                                "s.check_by FROM SNPs s LEFT JOIN Primers p ON s.name = p.name WHERE p.Gene='%s'" % \
                                gene_name
                today_date = datetime.datetime.now().strftime("%d-%m-%Y_%H%M")
                df_sql = pd.read_sql_query(get_old_query, con=con)
                archived_filename = '%s_%s' % (gene_name, today_date)
                writer = ExcelWriter('%s.xlsx' % archived_filename)
                df_sql.to_excel(writer, '%s' % today_date, index=False)
                writer.save()
                os.system("mv /home/cuser/PycharmProjects/django_apps/mysite/%s.xlsx "
                          "/home/cuser/PycharmProjects/django_apps/mysite/primerdb/archived_files/" % archived_filename)

                curs.execute("DELETE FROM Primers WHERE Gene='%s'" % gene_name)
                curs.execute("DELETE FROM Genes WHERE Gene='%s'" % gene_name)
                curs.execute("DELETE FROM SNPs WHERE Gene='%s'" % gene_name)

                info = "Data updated."

            else:
                info = "New gene added."

            # Insert new data into SQL tables.
            curs.execute("INSERT INTO Genes (Gene) VALUES (?)", (gene_name,))
            df_primertable.to_sql('Primers', con, if_exists='append', index=False)
            df_snptable.to_sql('SNPs', con, if_exists='append', index=False)

            print "Primers successfully added to database."
        else:
            info = error_details

        con.commit()
        return info, archived_filename

    def all(self):
        """Combines all methods"""
        sheetname = self.get_sheet_name()
        df_primers_dups, df_primers = self.get_primers(sheetname)
        df_coords = self.get_coords(df_primers)
        df_combined, gene = self.combine_coords_primers(df_coords, df_primers_dups)
        info, archived_filename = self.to_db(df_combined, gene)
        os.system("rm /home/cuser/PycharmProjects/django_apps/mysite/%s" % self.excel_file)
        return info, archived_filename



