# Generated by Django 5.0.4 on 2024-04-22 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_invoice_items_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='paid',
            new_name='amount_paid',
        ),
    ]
