import warnings
from getprimers import GetPrimers
import os
warnings.simplefilter("ignore", UserWarning)


def excel_to_db():
    """Takes an excel file, extracts primer information and adds this to a database."""

    excel_file = raw_input('Enter excel file name with file extension: ')
    filename = raw_input('Save bed file as: ')
    db = os.path.join(os.pardir, 'primers.db.sqlite3')

    os.system("cp /media/sf_sarah_share/%s /home/cuser/PycharmProjects/djangobook/mysite/primerdb" % excel_file)

    ets = GetPrimers(excel_file, db, filename)
    ets.make_csv()
    ets.to_db()

    os.system("rm %s" % excel_file)
    os.system("rm primerseqs.csv")

excel_to_db()

