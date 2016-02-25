from django.shortcuts import render
from primerdb.models import Primers, Genes, PrimerTable, SNPTable, SNPs
from primerdb.forms import UploadFileForm
from getprimers import ExcelToSQL
import os


def primerdatabase(request):
    """Gets query (gene name) from search box in primerdb_form.html, checks it against the PrimerTable and outputs
        result into primerdatabase.html.
        :param request:
    """
    error = False
    gene = Genes.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            primer = PrimerTable(Primers.objects.filter(gene__icontains=q))
            return render(request, 'primerdb/primerdatabase.html',
                          {'primers': primer, 'query': q})
    return render(request, 'primerdb/primerdb_form.html', {'genes': gene, 'error': error})


def snp_table(request, name):
    """Searches SNP table for name and outputs results to snp_table.html.
        :param name: links between SNP and Primer tables.
        :param request:
    """
    snp = SNPTable(SNPs.objects.filter(name__icontains=name))
    return render(request, 'primerdb/snp_table.html', {'snps': snp})


def handle_uploaded_file(filename):
    """Uploads the file in chunks.
        :param filename: file to upload.
    """
    filepath = os.path.join('primerdb', filename.name)
    with open(filepath, 'wb') as destination:
        for chunk in filename.chunks():
            destination.write(chunk)
    return filepath


def upload_file(request):
    """Passes file data from request into a form, uploads it and adds it to the database.
        :param request:
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)  # Passed to form's constructor to bind data to form.
        if form.is_valid():
            filepath = handle_uploaded_file(request.FILES['file'])
            excel_to_db(filepath)
            return render(request, 'primerdb/results.html')
    else:
        form = UploadFileForm()
    return render(request, 'primerdb/upload_file.html', {'form': form})


def excel_to_db(excel_file):
    """Takes an excel file and adds it to the database.
        :param excel_file:
    """
    db = 'primers.db.sqlite3'
    bedfile = excel_file + "_bedfile"
    ets = ExcelToSQL(excel_file, db, bedfile)
    ets.make_csv()
    ets.to_db()
    os.system("rm %s" % excel_file)
    os.system("rm primerseqs.csv")


def db_confirm(request):
    """Requests access to results.html - a page to confirm primers have been added to the database.
        :param request:
    """
    return render(request, 'primerdb/results.html')
