# Generated by Django 2.1 on 2018-11-08 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboards', '0016_auto_20181103_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='notability',
            field=models.CharField(default='minor', max_length=200),
        ),
    ]
