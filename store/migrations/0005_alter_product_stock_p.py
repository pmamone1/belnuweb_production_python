# Generated by Django 4.0 on 2022-07-21 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_rename_stock_product_stock_p'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock_p',
            field=models.IntegerField(default=1, verbose_name='Stock_p'),
        ),
    ]