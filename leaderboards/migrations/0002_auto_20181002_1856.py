# Generated by Django 2.1 on 2018-10-02 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboards', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='description',
            field=models.CharField(max_length=400),
        ),
    ]
