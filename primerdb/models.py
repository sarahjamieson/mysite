from __future__ import unicode_literals

from django.db import models


class Primers(models.Model):
    primer_id = models.AutoField(primary_key=True, unique=True)
    gene = models.CharField(max_length=10)
    exon = models.CharField(max_length=10)
    direction = models.CharField(max_length=1)
    version = models.IntegerField()
    primer_seq = models.CharField(max_length=30)
    chrom = models.CharField(max_length=2)
    m13_tag = models.CharField(max_length=1)
    batch = models.CharField(max_length=30)
    project = models.CharField(max_length=200)
    order_date = models.DateTimeField()
    frag_size = models.IntegerField()
    temp = models.CharField(max_length=10)
    other = models.CharField(max_length=200)

    def __str__(self):
        return '%s %s %s %s' % (self.primer_id, self.gene, self.exon, self.direction)

    class Meta:
        app_label = 'primerdb'
        db_table = 'Primers'

