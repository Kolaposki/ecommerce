# Generated by Django 3.0.7 on 2021-05-01 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='categorylang',
            name='lang',
            field=models.CharField(choices=[], max_length=6),
        ),
        migrations.AlterField(
            model_name='productlang',
            name='lang',
            field=models.CharField(choices=[], max_length=6),
        ),
    ]
