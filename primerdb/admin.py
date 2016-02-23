from django.contrib import admin
from models import Primers


class PrimerAdmin(admin.ModelAdmin):
    list_display = ('primerid', 'gene', 'exon', 'direction')
    search_fields = ('gene', 'exon')
    ordering = ('primerid', 'gene', 'exon', 'direction')

admin.site.register(Primers, PrimerAdmin)
