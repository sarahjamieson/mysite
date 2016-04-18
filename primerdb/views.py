from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from primerdb.models import Primers, Genes, PrimerTable, SNPTable, SNPs, AuditLog, AuditTable
from primerdb.forms import UploadFileForm
from getprimers import GetPrimers
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
import os
from audittrail import AuditTrail
import datetime
from wsgiref.util import FileWrapper
import re
from django.contrib.auth.models import User


def index(request):
    gene = Genes.objects.all()
    return render(request, 'primerdb/index.html', {'genes': gene})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        request.session['user'] = username
        password = request.POST['password']
        request.session['password'] = password
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                if re.match('(.*)00', password):
                    return HttpResponseRedirect('/primerdatabase/password_reset/')
                else:
                    current_time = datetime.datetime.utcnow()
                    info = "Successful login"
                    login(request, user)
                    audit = AuditTrail()
                    audit.add_to_log(current_time, info, username, None)
                    return HttpResponseRedirect('/primerdatabase/')
            else:
                current_time = datetime.datetime.utcnow()
                info = "Failed login: account has been disabled"
                login(request, user)
                audit = AuditTrail()
                audit.add_to_log(current_time, info, username, None)
                return HttpResponse("Your account is disabled.")
        else:
            current_time = datetime.datetime.utcnow()
            info = "Failed login: incorrect details"
            audit = AuditTrail()
            audit.add_to_log(current_time, info, username, None)
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return HttpResponseRedirect('/primerdatabase/')


def change_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        request.session['user'] = username
        password = request.POST['password']
        request.session['password'] = password
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        return HttpResponseRedirect('/primerdatabase/')
    else:
        return render(request, 'primerdb/reset.html')


def user_logout(request):
    username = request.session['user']
    info = "User logged out"
    current_time = datetime.datetime.utcnow()
    audit = AuditTrail()
    audit.add_to_log(current_time, info, username, None)
    logout(request)
    return HttpResponseRedirect('/primerdatabase/')


@login_required
def primerdatabase(request):
    """Gets query (gene name) from search box in primerdb_form.html, checks it against the PrimerTable and outputs
        result into search.html.
        :param request: HttpRequest object to link to page.
        :return: moves to search results if valid, remains on page if not.
    """
    error = False
    gene = Genes.objects.all()
    if 'q' in request.GET:
        q = request.GET['q']  # gets the input query
        if not q:
            error = True
        else:
            primer = PrimerTable(Primers.objects.filter(gene__icontains=q))

            # Records action in audit log
            current_time = datetime.datetime.utcnow()
            info = "Searched for primers in %s gene" % q.upper()
            username = request.session['user']
            audit = AuditTrail()
            audit.add_to_log(current_time, info, username, None)

            return render(request, 'primerdb/search.html', {'primers': primer, 'query': q})

    return render(request, 'primerdb/primerdb_form.html', {'genes': gene, 'error': error})


@login_required()
def audit_trail(request):
    """Presents all audit logs in page.
        :param request: HttpRequest object to link to page.
        :return: presents results in auditrail.html template.
    """
    trails = AuditTable(AuditLog.objects.all())
    return render(request, 'primerdb/audit_trail.html', {'trails': trails})


@login_required()
def snp_table(request, name):
    """Searches SNP table for name and outputs results to snp_table.html.
        :param name: links between SNP and Primer tables.
        :param request: HttpRequest object to link to page.
        :return: presents results in snp_table.html template.
    """
    snp = SNPTable(SNPs.objects.filter(name__icontains=name))

    # Records activity in audit log.
    current_time = datetime.datetime.utcnow()
    info = "Searched for SNPs in %s primer" % name
    username = request.session['user']
    audit = AuditTrail()
    audit.add_to_log(current_time, info, username, None)

    return render(request, 'primerdb/snp_table.html', {'snps': snp})


def handle_uploaded_file(filename):
    """Uploads file in chunks.
        :param filename: file to upload.
        :return filepath: location of the file which has been uploaded.
    """
    filepath = os.path.join('primerdb', filename.name)
    with open(filepath, 'wb') as destination:  # wb = file opened for writing in binary mode.
        for chunk in filename.chunks():
            destination.write(chunk)
    return filepath


@login_required()
def upload_file(request):
    """Passes file data from request into a form, uploads it and adds it to the database.
        :param request: HttpRequest object to link to page.
        :return: HttpResponse if successfully uploaded, remains on page if not.
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)  # Passed to form's constructor to bind data to form.
        if form.is_valid():
            filepath = handle_uploaded_file(request.FILES['file'])
            change, archived_filename = excel_to_db(filepath)  # Runs GetPrimers class on input file.

            # Records activity in audit log.
            current_time = datetime.datetime.utcnow()
            username = request.session['user']
            audit = AuditTrail()

            if change == "Data updated." or change == "New gene added.":
                info = "Successfully uploaded file %s. %s" % (filepath, change)
                audit.add_to_log(current_time, info, username, archived_filename)
                return HttpResponse("Primers successfully added to database.")
            else:
                info = "Failed to upload file: errors in data"
                audit.add_to_log(current_time, info, username, archived_filename)
                return render(request, 'primerdb/errors.html', {'errors': change})
        else:
            # Records activity in audit log.
            current_time = datetime.datetime.utcnow()
            info = "Failed to upload file: file invalid"
            username = request.session['user']
            audit = AuditTrail()
            audit.add_to_log(current_time, info, username, None)
    else:
        form = UploadFileForm()
    return render(request, 'primerdb/upload.html', {'form': form})


def excel_to_db(excel_file):
    """Takes an excel file and adds it to the database.
        :param excel_file: uploaded excel file.
        :return change: details of the activity (for audit log).
        :return archived_filename: filename for previous data if overridden (for audit log).
    """
    db = 'primers.db.sqlite3'
    ets = GetPrimers(excel_file, db)
    change, archived_filename = ets.all()
    return change, archived_filename


def download(request, archived_filename):
    """Downloads a given excel file.
        :param request: HttpRequest object to link to download.
        :param archived_filename: filename available for download.
        :return response: HttpResponse of downloading file.
    """
    file_with_ext = 'primerdb/archived_files/%s.xlsx' % archived_filename
    wrapper = FileWrapper(file(file_with_ext))
    response = HttpResponse(wrapper, content_type='application/vnd.ms-excel')
    response['Content-Length'] = os.path.getsize(file_with_ext)
    response['Content-Disposition'] = 'attachment; archived_filename="%s"' % file_with_ext
    return response