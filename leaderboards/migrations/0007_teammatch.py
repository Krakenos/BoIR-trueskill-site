# Generated by Django 2.1 on 2018-10-08 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leaderboards', '0006_auto_20181008_2036'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.CharField(max_length=200)),
                ('ruleset', models.CharField(max_length=200, null=True)),
                ('video', models.URLField(null=True)),
                ('description', models.CharField(max_length=200, null=True)),
                ('loser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loses', to='leaderboards.Team')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leaderboards.Tournament')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wins', to='leaderboards.Team')),
            ],
        ),
    ]
