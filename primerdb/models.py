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
    start = models.CharField(max_length=30, default=None)
    end = models.CharField(max_length=30, default=None)
    m13_tag = models.CharField(max_length=1)
    batch = models.CharField(max_length=30)
    project = models.CharField(max_length=200, default="")
    order_date = models.CharField(max_length=20)
    frag_size = models.IntegerField()
    anneal_temp = models.CharField(max_length=10)
    other = models.CharField(max_length=200)
    snp_check = models.IntegerField()
    no_snps = models.IntegerField()
    rs = models.CharField(max_length=20)
    hgvs = models.CharField(max_length=20)
    freq = models.CharField(max_length=200)
    ss = models.CharField(max_length=100)
    ss_proj = models.CharField(max_length=200)
    other2 = models.CharField(max_length=200)
    action_to_take = models.CharField(max_length=100)
    check_by = models.CharField(max_length=10)

    class Meta:
        app_label = 'primerdb'
        db_table = 'Primers'


class Genes(models.Model):
    gene_id = models.AutoField(primary_key=True, unique=True)
    gene = models.CharField(max_length=10)

    class Meta:
        app_label = 'primerdb'
        db_table = 'Genes'


