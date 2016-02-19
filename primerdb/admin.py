from django.contrib import admin
from models import Primers, SNPs


class PrimerAdmin(admin.ModelAdmin):
    list_display = ('primer_id', 'gene', 'exon', 'direction')
    search_fields = ('gene', 'exon')
    ordering = ('primer_id', 'gene', 'exon', 'direction')

admin.site.register(Primers, PrimerAdmin)
admin.site.register(SNPs)
