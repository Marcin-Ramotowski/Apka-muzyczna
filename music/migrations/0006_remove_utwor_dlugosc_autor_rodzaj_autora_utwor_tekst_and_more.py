# Generated by Django 4.1.5 on 2023-02-19 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_alter_utwor_dlugosc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='utwor',
            name='dlugosc',
        ),
        migrations.AddField(
            model_name='autor',
            name='rodzaj_autora',
            field=models.CharField(choices=[('ONE', 'osoba'), ('MUL', 'zespół')], default='osoba', max_length=6),
        ),
        migrations.AddField(
            model_name='utwor',
            name='tekst',
            field=models.CharField(default='', max_length=5000),
        ),
        migrations.AlterField(
            model_name='album',
            name='wiecej_info',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='autor',
            name='imie',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='autor',
            name='nazwisko',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='autor',
            name='pseudonim',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='autor',
            name='wiecej_info',
            field=models.TextField(null=True),
        ),
    ]
