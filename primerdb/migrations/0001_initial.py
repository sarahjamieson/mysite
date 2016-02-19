# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-17 11:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Primers',
            fields=[
                ('primer_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('gene', models.CharField(max_length=10)),
                ('exon', models.CharField(max_length=10)),
                ('direction', models.CharField(max_length=1)),
                ('primer_seq', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SNPs',
            fields=[
                ('snp_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('build', models.IntegerField()),
                ('snps', models.IntegerField()),
                ('primer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='primerdb.Primers')),
            ],
        ),
    ]
