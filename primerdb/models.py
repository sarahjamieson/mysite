from __future__ import unicode_literals

from django.db import models


class Primers(models.Model):
    primer_id = models.AutoField(primary_key=True, unique=True)
    gene = models.CharField(max_length=10)
    exon = models.CharField(max_length=10)
    direction = models.CharField(max_length=1)
    primer_seq = models.CharField(max_length=30)

    def __str__(self):
        return '%s %s %s %s' % (self.primer_id, self.gene, self.exon, self.direction)

    class Meta:
        app_label = 'primerdb'
        db_table = 'Primers'

