# Generated by Django 3.0.7 on 2021-05-02 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_remove_product_wishlisted'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='wishlisted',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
