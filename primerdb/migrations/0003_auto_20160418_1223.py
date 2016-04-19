# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-18 11:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('primerdb', '0002_auto_20160308_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('ActionId', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('Datetime', models.DateTimeField()),
                ('Info', models.CharField(max_length=100)),
                ('Username', models.CharField(max_length=6)),
                ('Previous_file', models.CharField(default='', max_length=200)),
            ],
            options={
                'db_table': 'AuditLog',
            },
        ),
        migrations.CreateModel(
            name='HistoricalPrimers',
            fields=[
                ('primerid', models.IntegerField(blank=True, db_index=True)),
                ('gene', models.CharField(max_length=10)),
                ('exon', models.CharField(max_length=3)),
                ('direction', models.CharField(max_length=1)),
                ('name', models.CharField(default='', max_length=30)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('primer_seq', models.CharField(max_length=30)),
                ('chrom', models.CharField(max_length=2)),
                ('start', models.CharField(default=None, max_length=30)),
                ('end', models.CharField(default=None, max_length=30)),
                ('m13_tag', models.CharField(blank=True, max_length=1)),
                ('batch', models.CharField(blank=True, max_length=30)),
                ('project', models.CharField(default='', max_length=200)),
                ('order_date', models.DateField(blank=True)),
                ('frag_size', models.IntegerField(blank=True)),
                ('anneal_temp', models.CharField(blank=True, max_length=10)),
                ('other', models.CharField(blank=True, max_length=200)),
                ('no_snps', models.IntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical primers',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='primers',
            name='anneal_temp',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='primers',
            name='batch',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='primers',
            name='frag_size',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='primers',
            name='m13_tag',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AlterField(
            model_name='primers',
            name='order_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='primers',
            name='other',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='primers',
            name='version',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]