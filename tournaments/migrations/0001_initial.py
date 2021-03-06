# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-06-07 12:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pages', '0004_auto_20170411_0504'),
    ]

    operations = [
        migrations.CreateModel(
            name='EliminationGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('game_date', models.DateTimeField()),
                ('player_score_0', models.PositiveIntegerField(default=0)),
                ('opponent_score_0', models.PositiveIntegerField(default=0)),
                ('player_score_1', models.PositiveIntegerField(default=0)),
                ('opponent_score_1', models.PositiveIntegerField(default=0)),
                ('player_score_2', models.PositiveIntegerField(default=0)),
                ('opponent_score_2', models.PositiveIntegerField(default=0)),
                ('games_finished', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_color', models.CharField(choices=[('W', 'White'), ('B', 'Black')], default='W', max_length=1)),
                ('player_score', models.PositiveIntegerField(default=0)),
                ('player_dummy', models.BooleanField(default=False)),
                ('opponent_score', models.PositiveIntegerField(default=0)),
                ('opponent_color', models.CharField(choices=[('W', 'White'), ('B', 'Black')], default='B', max_length=1)),
                ('opponent_dummy', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('finished', 'Finished')], default='planned', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('school', models.CharField(max_length=200)),
                ('register_date', models.DateField(auto_now_add=True, verbose_name='registration date')),
                ('static_homologation', models.BooleanField(default=False)),
                ('dynamic_homologation', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('round_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('players', models.ManyToManyField(to='tournaments.Player')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentInfo',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Page')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.Tournament')),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page',),
        ),
        migrations.CreateModel(
            name='TournamentRounds',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Page')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.Tournament')),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page',),
        ),
        migrations.CreateModel(
            name='TournamentStandings',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pages.Page')),
                ('first_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p1', to='tournaments.Player')),
                ('second_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p2', to='tournaments.Player')),
                ('third_place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p3', to='tournaments.Player')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.Tournament')),
            ],
            options={
                'ordering': ('_order',),
            },
            bases=('pages.page',),
        ),
        migrations.AddField(
            model_name='round',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.Tournament'),
        ),
        migrations.AddField(
            model_name='game',
            name='opponent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_b', to='tournaments.Player'),
        ),
        migrations.AddField(
            model_name='game',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_a', to='tournaments.Player'),
        ),
        migrations.AddField(
            model_name='game',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.Round'),
        ),
        migrations.AddField(
            model_name='eliminationgame',
            name='opponent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_2', to='tournaments.Player'),
        ),
        migrations.AddField(
            model_name='eliminationgame',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_1', to='tournaments.Player'),
        ),
        migrations.AddField(
            model_name='eliminationgame',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.Tournament'),
        ),
    ]
