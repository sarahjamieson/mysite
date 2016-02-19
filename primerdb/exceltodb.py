import warnings
from getprimers import ExcelToSQL
warnings.simplefilter("ignore", UserWarning)

"""Module takes an excel file and database as inputs and runs the ExcelToSQL class to add excel files to a database."""

excel_file = '/home/cuser/COL4A5_practice.xlsx'

db = 'primers.db.sqlite3'

ets = ExcelToSQL(excel_file, db)
ets.to_db()
