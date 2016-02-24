import pandas as pd
import re
import sqlite3 as lite
import os
import pybedtools as bed
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
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

    def __init__(self, excel_file, db, filename):
        self.excel_file = excel_file
        self.db = db
        self.filename = filename

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
                                               'Batch', 'project', 'Order_date', 'Frag_size', 'anneal_temp', 'Other',
                                               'snp_check', 'no_snps', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2',
                                               'action_to_take', 'check_by'],
                                        sheetname=sheetname, index_col=None)
        to_drop = ['Version', 'M13_tag', 'Batch', 'project', 'Order_date', 'Frag_size', 'anneal_temp', 'Other',
                   'snp_check', 'no_snps', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2', 'action_to_take',
                   'check_by']
        df_primers = df_primers_dups.drop(to_drop, axis=1)
        df_primers = df_primers.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_primers = df_primers.reset_index(drop=True)
        gene_name = df_primers.at[0, 'Gene']

        return df_primers_dups, df_primers, gene_name

    def make_csv(self):
        df_primers_dups, df_primers, gene_name = self.get_primers()
        primer_list = []
        names_dup = []
        names = []
        exons = []
        dirs = []
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

        list_position = 0
        primer_seqs = pd.DataFrame([])
        while list_position < len(forwards):
            ser = pd.Series([names[list_position], forwards[list_position], reverses[list_position]])
            primer_seqs = primer_seqs.append(ser, ignore_index=True)
            list_position += 1

        primer_seqs.to_csv('primerseqs.csv', header=None, index=None, sep='\t')

        return names, exons, dirs, primer_list

    def run_pcr(self):

        print "Running virtual PCR..."

        chromosomes = ['chr10.2bit', 'chr11.2bit', 'chr12.2bit', 'chr1.2bit', 'chr13.2bit', 'chr14.2bit', 'chr15.2bit',
                       'chr16.2bit', 'chr17.2bit', 'chr18.2bit', 'chr19.2bit', 'chr20.2bit', 'chr21.2bit', 'chr22.2bit',
                       'chr2.2bit', 'chr3.2bit', 'chr4.2bit', 'chr5.2bit', 'chr6.2bit', 'chr7.2bit', 'chr8.2bit',
                       'chr9.2bit', 'chrX.2bit', 'chrY.2bit']

        for chr in chromosomes:
            os.system(
                "/opt/kentools/isPcr -out=psl /media/genomicdata/ucsc_hg19_by_chr/2bit_chr/%s \
                primerseqs.csv %s.tmp.psl" % (chr, chr[:-5]))

            pslfile = "%s.tmp.psl" % chr[:-5]
            bedfile = "%s.tmp.bed" % chr[:-5]

            if os.path.getsize(pslfile) != 0:
                os.system("/opt/kentools/pslToBed %s %s" % (pslfile, bedfile))
                os.system("rm %s" % pslfile)
                return bedfile
            else:
                os.system("rm %s" % pslfile)

    def get_coords(self):
        bedfile = self.run_pcr()
        tool = bed.BedTool(bedfile)
        start_coords = []
        end_coords = []
        chroms = []
        seq_position = 0
        names, exons, dirs, primer_list = self.make_csv()

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

        df_coords.to_csv('%s.csv' % self.filename, header=None, index=None, sep='\t')
        csv_file = bed.BedTool('%s.csv' % self.filename)
        csv_file.saveas('%s.bed' % self.filename)

        os.system("rm /home/cuser/PycharmProjects/djangobook/mysite/%s.csv" % self.filename)
        os.system(
            "mv /home/cuser/PycharmProjects/djangobook/mysite/%s.bed /media/sf_sarah_share/bedfiles" % self.filename)
        os.system("rm %s" % bedfile)

        return df_coords

    def col_to_string(self, row):
        return str(row['Exon'])

    def add_coords(self):
        df_coords = self.get_coords()
        df_primers_dups, df_primers, gene_name = self.get_primers()
        names, exons, dirs, primer_list = self.make_csv()
        df_coords.insert(4, 'Exon', exons)
        df_coords.insert(5, 'Direction', dirs)

        df_coords['Exon'] = df_coords.apply(self.col_to_string, axis=1)  # converts to string for merging
        df_primers_dups['Exon'] = df_primers_dups.apply(self.col_to_string, axis=1)

        df_all = pd.merge(df_primers_dups, df_coords, how='left', on=['Exon', 'Direction'])
        cols_to_drop = ['chrom']
        df_all = df_all.drop(cols_to_drop, axis=1)
        gene_name = df_all.get_value(0, 'Gene')

        return df_all, gene_name

    def to_db(self):
        curs, con = self.get_cursor()
        df_all, gene_name = self.add_coords()
        '''
        curs.execute("DROP TABLE IF EXISTS Primers")
        curs.execute("DROP TABLE IF EXISTS Genes")
        curs.execute("DROP TABLE IF EXISTS SNPs")

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

        curs.execute("INSERT INTO Genes (Gene) VALUES (?)", (gene_name,))

        primertable_cols_to_drop = ['snp_check', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2', 'action_to_take',
                                    'check_by']
        snptable_cols_to_drop = ['Exon', 'Direction', 'Version', 'Primer_seq', 'Chrom', 'M13_tag', 'Batch', 'project',
                                 'Order_date', 'Frag_size', 'anneal_temp', 'Other', 'no_snps', 'start', 'end']

        df_primertable = df_all.drop(primertable_cols_to_drop, axis=1)
        df_primertable = df_primertable.drop_duplicates(subset=('Gene', 'Exon', 'Direction', 'Chrom'))
        df_snptable = df_all.drop(snptable_cols_to_drop, axis=1)

        df_primertable.to_sql('Primers', con, if_exists='append', index=False)
        df_snptable.to_sql('SNPs', con, if_exists='append', index=False)

        print "Primers successfully added to database."