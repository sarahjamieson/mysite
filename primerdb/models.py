from __future__ import unicode_literals

from django.db import models
import django_tables2 as table
from django_tables2 import A
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Primers(models.Model):
    primerid = models.AutoField(primary_key=True, unique=True)
    gene = models.CharField(max_length=10)
    exon = models.CharField(max_length=3)
    direction = models.CharField(max_length=1)
    name = models.CharField(max_length=30, default='')
    version = models.IntegerField(blank=True, null=True)
    primer_seq = models.CharField(max_length=30)
    chrom = models.CharField(max_length=2)
    start = models.CharField(max_length=30, default=None)
    end = models.CharField(max_length=30, default=None)
    m13_tag = models.CharField(max_length=1, blank=True)
    batch = models.CharField(max_length=30, blank=True)
    project = models.CharField(max_length=200, default="")
    order_date = models.DateField(blank=True)
    frag_size = models.IntegerField(blank=True)
    anneal_temp = models.CharField(max_length=10, blank=True)
    other = models.CharField(max_length=200, blank=True)
    no_snps = models.IntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        app_label = 'primerdb'
        db_table = 'Primers'


class SNPs(models.Model):
    snp_id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=30, default='')
    snp_check = models.IntegerField(default='')
    rs = models.CharField(max_length=20, default='')
    hgvs = models.CharField(max_length=20, default='')
    freq = models.CharField(max_length=200, default='')
    ss = models.CharField(max_length=100, default='')
    ss_proj = models.CharField(max_length=200, default='')
    other2 = models.CharField(max_length=200, default='')
    action_to_take = models.CharField(max_length=100, default='')
    check_by = models.CharField(max_length=10, default='')

    class Meta:
        app_label = 'primerdb'
        db_table = 'SNPs'


class PrimerTable(table.Table):
    gene = table.Column(verbose_name="Gene", orderable=False, default='')
    exon = table.Column(verbose_name="Exon", orderable=False, default='')
    direction = table.Column(verbose_name="Direction", orderable=False, default='')
    version = table.Column(verbose_name="Version", orderable=False, default='')
    primer_seq = table.Column(verbose_name="Primer Sequence", orderable=False, default='')
    chrom = table.Column(verbose_name="Chromosome", orderable=False, default='')
    start = table.Column(verbose_name="Start coordinate", orderable=False, default='')
    end = table.Column(verbose_name="End coordinate", orderable=False, default='')
    m13_tag = table.Column(verbose_name="M13_Tagged? (Y/N)", orderable=False, default='')
    batch = table.Column(verbose_name="Batch Number", orderable=False, default='')
    project = table.Column(verbose_name="Batch Test MS Project Name", orderable=False, default='')
    order_date = table.Column(verbose_name="Order Date", orderable=False, default='')
    frag_size = table.Column(verbose_name="Fragment Size", orderable=False, default='')
    anneal_temp = table.Column(verbose_name="Annealing Temp(oC)", orderable=False, default='')
    other = table.Column(verbose_name="Other Info", orderable=False, default='')
    no_snps = table.LinkColumn('snp-table', args=[A('name')], verbose_name="Total SNPs", orderable=False, default=0)
    history = HistoricalRecords()

    class Meta:
        model = Primers
        fields = ('gene', 'exon', 'direction', 'version', 'primer_seq', 'chrom', 'start', 'end', 'm13_tag', 'batch',
                  'project', 'order_date', 'frag_size', 'anneal_temp', 'other', 'no_snps')


class SNPTable(table.Table):
    snp_check = table.Column(verbose_name="SNP Check Build", orderable=False, default='')
    rs = table.Column(verbose_name="dbSNP rs number", orderable=False, default='')
    hgvs = table.Column(verbose_name="HGVS", orderable=False, default='')
    freq = table.Column(verbose_name="Frequency Data", orderable=False, default='')
    ss = table.Column(verbose_name="ss refs", orderable=False, default='')
    ss_proj = table.Column(verbose_name="Projects creating ss refs", orderable=False, default='')
    other2 = table.Column(verbose_name="Other Info", orderable=False, default='')
    action_to_take = table.Column(verbose_name="Action To Be Taken", orderable=False, default='')
    check_by = table.Column(verbose_name="Checked by", orderable=False, default='')

    class Meta:
        model = SNPs
        fields = ('snp_check', 'rs', 'hgvs', 'freq', 'ss', 'ss_proj', 'other2', 'action_to_take', 'check_by')


class Genes(models.Model):
    gene_id = models.AutoField(primary_key=True, unique=True)
    gene = models.CharField(max_length=10)

    class Meta:
        app_label = 'primerdb'
        db_table = 'Genes'
        ordering = ['gene', 'gene_id']


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.username


class AuditLog(models.Model):
    ActionId = models.AutoField(primary_key=True, unique=True)
    Datetime = models.DateTimeField()
    Info = models.CharField(max_length=100)
    Username = models.CharField(max_length=6)
    Previous_file = models.CharField(max_length=200, default='')

    class Meta:
        app_label = 'primerdb'
        db_table = 'AuditLog'


class AuditTable(table.Table):
    ActionId = table.Column(orderable=False, default='')
    Datetime = table.Column(orderable=False, default='')
    Info = table.Column(orderable=False, default='')
    Username = table.Column(orderable=False, default='')
    Previous_file = table.Column(orderable=False, default='')

    class Meta:
        model = AuditLog
        fields = ('Action_id', 'Datetime', 'Info', 'Username')