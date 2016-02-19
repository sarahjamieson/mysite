from __future__ import unicode_literals

from django.db import models


class Primers(models.Model):
    primer_id = models.AutoField(primary_key=True, unique=True)
    gene = models.CharField(max_length=10)
    exon = models.CharField(max_length=10)
    direction = models.CharField(max_length=1)
    primer_seq = models.CharField(max_length=30)

    def __unicode__(self):
        return u'%s %s %s %s' % (self.primer_id, self.gene, self.exon, self.direction)


class SNPs(models.Model):
    snp_id = models.AutoField(primary_key=True, unique=True)
    primer_id = models.ForeignKey(Primers, on_delete=models.CASCADE)
    build = models.IntegerField()
    snps = models.IntegerField()

    def __unicode__(self):
        return self.snp_id
