from django.http import HttpResponse
from django.shortcuts import render
from primerdb.models import Primers, Genes


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
    return render(request, 'snp_results.html')

