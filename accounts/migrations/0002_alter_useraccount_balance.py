# Generated by Django 4.2.13 on 2024-06-15 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]
