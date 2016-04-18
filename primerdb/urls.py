from django.conf.urls import url
from django.contrib import admin

from primerdb.views import primerdatabase, snp_table, upload_file, user_login, index, user_logout, \
    audit_trail, download

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name='index'),
    url(r'^search/$', primerdatabase, name='search'),
    url(r'^snps/(?P<name>[-\w]+)/$', snp_table, name='snp-table'),  # use "[-\w]+" to cope with "-" in search.
    url(r'^upload/$', upload_file, name='upload'),
    url(r'^login/$', user_login, name='login'),
    url(r'^logout/$', user_logout, name='logout'),
    url(r'^audit_trail/$', audit_trail, name='audit_trail'),
    url(r'^download/(?P<archived_filename>[-\w]+)', download, name='download'),
]