from django.http import HttpResponse
from django.shortcuts import render
from primerdb.models import Primers, Genes, PrimerTable, SNPTable, SNPs
from primerdb.forms import UploadFileForm
from getprimers import ExcelToSQL
import os


def hello(request):
    return HttpResponse("Hello world")


def search_form(request):
    gene = Genes.objects.all()
    return render(request, 'search_form.html', {'genes': gene})


def search(request):
    error = False
    gene = Genes.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            primer = Primers.objects.filter(gene__icontains=q)
            return render(request, 'search_results.html',
                          {'primers': primer, 'query': q})
    return render(request, 'search_form.html', {'genes': gene, 'error': error})


def search_snps(request):
    primer = Primers.objects.all()
    return render(request, 'snp_results.html', {'primers': primer})


def primerdatabase(request):
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
    snp = SNPTable(SNPs.objects.filter(name__icontains=name))
    return render(request, 'primerdb/snp_table.html', {'snps': snp})


def handle_uploaded_file(filename):
    filepath = os.path.join('primerdb', filename.name)
    with open(filepath, 'wb') as destination:
        for chunk in filename.chunks():
            destination.write(chunk)
    return filepath


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filepath = handle_uploaded_file(request.FILES['file'])
            excel_to_db(filepath)
            return render(request, 'primerdb/results.html')
    else:
        form = UploadFileForm()
    return render(request, 'primerdb/upload_file.html', {'form': form})


def excel_to_db(excel_file):
    db = 'primers.db.sqlite3'
    bedfile = excel_file + "_bedfile"
    ets = ExcelToSQL(excel_file, db, bedfile)
    ets.make_csv()
    ets.to_db()
    os.system("rm %s" % excel_file)


def db_confirm(request):
    return render(request, 'primerdb/results.html')