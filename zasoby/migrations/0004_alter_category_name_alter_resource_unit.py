# Generated by Django 5.1.4 on 2025-02-06 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zasoby', '0003_alter_resource_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='unit',
            field=models.CharField(choices=[('szt.', 'szt.'), ('kg', 'kg'), ('l', 'L'), ('op.', 'op.')], default='szt.', max_length=50),
        ),
    ]
