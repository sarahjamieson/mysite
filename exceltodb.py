import warnings
from getprimers import ExcelToSQL
import os
warnings.simplefilter("ignore", UserWarning)

"""Module takes an excel file and database as inputs and runs the ExcelToSQL class to add excel files to a database."""

excel_file = raw_input('Enter excel file name with file extension: ')

os.system("cp /media/sf_sarah_share/%s /home/cuser/PycharmProjects/djangobook/mysite/" % excel_file)
filename = raw_input('Save bed file as: ')


db = 'primers.db.sqlite3'

ets = ExcelToSQL(excel_file, db, filename)
ets.make_csv()
ets.to_db()

os.system("rm %s" % excel_file)
