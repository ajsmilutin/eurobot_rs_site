from __future__ import unicode_literals

from django.db import models
from mezzanine.core.models import  RichText
from mezzanine.pages.models import Page
from mezzanine.pages.page_processors import processor_for
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    school = models.CharField(max_length=200)
    register_date = models.DateField('registration date', auto_now_add=True)
    static_homologation = models.BooleanField(default=False)
    dynamic_homologation = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Tournament(models.Model):

    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    players = models.ManyToManyField(Player)

    def __unicode__(self):
        return self.name

    def players_count(self):
        return self.players.count()


class Round(models.Model):
    tournament = models.ForeignKey(Tournament)
    name = models.CharField(max_length=200)
    round_date = models.DateTimeField()

    def __unicode__(self):
        return self.tournament.name + " - " + self.name


class Game(models.Model):
    GAME_STATUSES = (
        (_('planned'), _('Planned')),
        (_('finished'), _('Finished'))
    )

    PLAYER_COLOR = (
        ('W', 'White'),
        ('B', 'Black'),
    )

    round = models.ForeignKey(Round)
    player = models.ForeignKey(Player, related_name="player_a")
    player_color = models.CharField(max_length=1,
                                    choices=PLAYER_COLOR,
                                    default='W')
    player_score = models.PositiveIntegerField(default=0)
    player_dummy = models.BooleanField(default = False)
    opponent_score = models.PositiveIntegerField(default=0)
    opponent_color = models.CharField(max_length=1,
                                      choices=PLAYER_COLOR,
                                      default='B')
    opponent_dummy = models.BooleanField(default = False)
    opponent = models.ForeignKey(
        Player, related_name="player_b", null=True, blank=True)
    
    status = models.CharField(max_length=10,
                              choices=GAME_STATUSES,
                              default='planned')

    def __unicode__(self):
        return str(self.player) + " " + str(self.player_score) + ":" + str(self.opponent_score) + " " + str(self.opponent)

class EliminationGame(models.Model):
    tournament = models.ForeignKey(Tournament)
    name = models.CharField(max_length=200)
    game_date = models.DateTimeField()
    player = models.ForeignKey(Player, related_name="player_1")
    opponent = models.ForeignKey(Player,related_name="player_2", null=True, blank=True)
    player_score_0 = models.PositiveIntegerField(default=0)
    opponent_score_0 = models.PositiveIntegerField(default=0)
    player_score_1 = models.PositiveIntegerField(default=0)
    opponent_score_1 = models.PositiveIntegerField(default=0)
    player_score_2 = models.PositiveIntegerField(default=0)
    opponent_score_2 = models.PositiveIntegerField(default=0)
    games_finished = models.PositiveIntegerField(default=0)

    def player_wins(self):
        return (self.player_score_0 > self.opponent_score_0 and self.player_score_1 > self.opponent_score_1) or (self.player_score_0 > self.opponent_score_0 and self.player_score_2 > self.opponent_score_2) or (self.player_score_2 > self.opponent_score_2 and self.player_score_1 > self.opponent_score_1)

    def opponent_wins(self):
        return (self.player_score_0 < self.opponent_score_0 and self.player_score_1 < self.opponent_score_1) or (self.player_score_0 < self.opponent_score_0 and self.player_score_2 < self.opponent_score_2) or (self.player_score_2 < self.opponent_score_2 and self.player_score_1 < self.opponent_score_1)        

class TournamentInfo(Page, RichText):    
    tournament = models.ForeignKey(Tournament)    
    def can_add(self, request):
        return True


@processor_for(TournamentInfo)
def tournament_info(request, page):    
    players = page.tournamentinfo.tournament.players.order_by('name')
    return {"players": players, "tournament": page.tournamentinfo.tournament}


class TournamentStandings(Page, RichText):    
    tournament = models.ForeignKey(Tournament)
    first_place = models.ForeignKey(Player, related_name="p1", blank=True, null=True)
    second_place = models.ForeignKey(Player, related_name="p2", blank=True, null=True)
    third_place = models.ForeignKey(Player, related_name="p3", blank=True, null=True)

class TournamentRounds(Page, RichText):    
    tournament = models.ForeignKey(Tournament)    

@processor_for(TournamentStandings)
def tournament_standings(request, page):    
    tournament_id = page.tournamentstandings.tournament
    rounds = Round.objects.filter(tournament=tournament_id).order_by('round_date')        
    games = Game.objects.filter(round__tournament=tournament_id).order_by('round__round_date')
    players = page.tournamentstandings.tournament.players.order_by('name')
    
    players_info = []
    for player in players:
        first_games_score = games.filter(player=player.id).filter(player_dummy=False).aggregate(score=Sum('player_score'))
        second_games_score = games.filter(opponent = player.id).filter(opponent_dummy = False).aggregate(score = Sum('opponent_score'))
        total_score = first_games_score['score'] if first_games_score['score'] is not None else 0 
        total_score = total_score + \
            (second_games_score['score']
            if second_games_score['score'] is not None else 0)
        players_info.append({'player': find_player(player.id, players),
                            'games': [],
                            'score': total_score
                            })
    players_info = sorted(players_info, key=lambda elem: elem['score'], reverse= True)

    if players_info:                               
        for game in games:
            info = next(info for info in players_info if info['player'].id == game.player_id and not game.player_dummy)
            info['games'].append({'game': game,
                                    'player': find_player(game.player_id, players),
                                    'opponent': find_player(game.opponent_id, players)
                                    })
            info = next((info for info in players_info if info['player'].id == game.opponent_id and not game.opponent_dummy), None)
            if info:
                info['games'].append({'game': game,
                                    'player': find_player(game.player_id, players),
                                    'opponent': find_player(game.opponent_id, players)
                                    })
    return {'rounds': rounds, 'players_info': players_info, "third_place": page.tournamentstandings.third_place, "second_place": page.tournamentstandings.second_place, "first_place": page.tournamentstandings.first_place}

@processor_for(TournamentRounds)
def tournament_rounds(request, page):    
    tournament_id = page.tournamentrounds.tournament
    rounds = Round.objects.filter(tournament=tournament_id).order_by('round_date')
    games = Game.objects.filter(round__tournament=tournament_id).order_by('round__round_date')
    players = page.tournamentrounds.tournament.players.order_by('name')    
    elimination = EliminationGame.objects.filter(tournament=tournament_id).order_by('-pk')
    
    rounds_info = []
    for rnd in rounds:
        rounds_info.append({'round': rnd, 'games': []})
    for game in games:
        info = next(info for info in rounds_info if info['round'].id == game.round_id)
        info['games'].append({'game': game,
                              'player': find_player(game.player_id, players),                              
                              'opponent': find_player(game.opponent_id, players)
                              })
    context = dict()
    context['rounds_info'] = rounds_info
    print(context)    
    return {'elimination_info': elimination, 'rounds_info': rounds_info, 'tournament': page.tournamentrounds.tournament}
    
def find_player(player_id, players):
    return next((player for player in players if player.id == player_id), None)
