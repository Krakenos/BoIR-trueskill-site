# Generated by Django 2.1 on 2018-10-03 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboards', '0004_auto_20181003_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='other_matches_played',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='other_tournaments_played',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='seeded_matches_played',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='seeded_tournaments_played',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='unseeded_matches_played',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='unseeded_tournaments_played',
            field=models.IntegerField(null=True),
        ),
    ]
