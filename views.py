from django.http import HttpResponse
from django.shortcuts import render
from primerdb.models import Primers
import datetime


def hello(request):
    return HttpResponse("Hello world")


def search_form(request):
    return render(request, 'search_form.html')


def search(request):
    error = False
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            primer = Primers.objects.filter(gene__icontains=q)
            return render(request, 'search_results.html',
                        {'primers': primer, 'query': q})
    return render(request, 'search_form.html', {'error': error})

