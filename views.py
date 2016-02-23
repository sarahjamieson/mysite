from django.http import HttpResponse
from django.shortcuts import render
from primerdb.models import Primers, Genes, PrimerTable, SNPTable, SNPs


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


def table(request):
    error = False
    gene = Genes.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            primer = PrimerTable(Primers.objects.filter(gene__icontains=q))
            return render(request, 'table.html',
                          {'primers': primer, 'query': q})
    return render(request, 'table_form.html', {'genes': gene, 'error': error})


def snp_table(request, name):
    snp = SNPTable(SNPs.objects.filter(name__icontains=name))
    return render(request, 'snp_table.html', {'snps': snp})
