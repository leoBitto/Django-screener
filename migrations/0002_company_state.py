# Generated by Django 4.1.7 on 2023-02-21 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
