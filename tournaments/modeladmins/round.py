from django.contrib import admin
from django import forms
from tournaments.models import Player, Tournament, Game, Round
import math
import random
from django.utils.functional import curry
import re
from tournaments.pairing import Pairing
from django.db.models import Count


class GameInLineFormAdmin(forms.ModelForm):
    player = forms.ModelChoiceField(queryset=Player.objects.order_by('name'))
    player.label = 'Player'
    opponent = forms.ModelChoiceField(
        queryset=Player.objects.order_by('name'), required=False)
    opponent.label = 'Opponent'

    def __init__(self, *args, **kwargs):
        super(GameInLineFormAdmin, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial', None)
        game = kwargs.get('instance', None)
        if game:
            self.fields['player'].queryset = game.round.tournament.players.order_by(
                'name')
            self.fields['opponent'].queryset = game.round.tournament.players.order_by(
                'name')
        elif initial and initial.has_key('tournament'):
            self.fields['player'].queryset = initial['tournament'].players.order_by(
                'name')
            self.fields['opponent'].queryset = initial['tournament'].players.order_by(
                'name')

    def clean(self):
        cleaned_data = super(GameInLineFormAdmin, self).clean()
        tour = Tournament.objects.get(pk=self.data['tournament'])

        # Check players
        player = cleaned_data.get("player")
        opponent = cleaned_data.get(
            "opponent") if cleaned_data.has_key("opponent") else None
        if player == opponent:
            self._errors["opponent"] = self.error_class(
                [u'Player cannot play with oneself'])
            del cleaned_data["opponent"]

        if tour.players.filter(id=player.id).count() == 0:
            self._errors["player"] = self.error_class(
                [u'%s is not in this tournament.' % player])
            del cleaned_data["player"]

        if opponent is not None and tour.players.filter(id=opponent.id).count() == 0:
            self._errors["opponent"] = self.error_class(
                [u'%s is not in this tournament.' % opponent])
            del cleaned_data["opponent"]

        if tour.players.count() % 2 == 0 and opponent is None:
            self._errors["player"] = self.error_class(
                [u'You cannot have games without opponent in tournament with even players count'])
            del cleaned_data["player"]


        # Check colors
        player_color = cleaned_data.get("player_color")
        opponent_color = cleaned_data.get("opponent_color")

        if player_color != "W" and player_color != "B":
            self._errors["player_color"] = self.error_class(
                [u'Player has incorrect color'])
            del cleaned_data["player_color"]

        if opponent_color != "W" and opponent_color != "B":
            self._errors["opponent_color"] = self.error_class(
                [u'Opponent has incorrect color'])
            del cleaned_data["opponent_color"]

        if player_color == opponent_color:
            self._errors["opponent_color"] = self.error_class(
                [u'Opponent must not have the same color'])
            del cleaned_data["opponent_color"]

        # Check score and status
        player_score = cleaned_data.get("player_score")
        opponent_score = cleaned_data.get("opponent_score")
        status = cleaned_data.get("status")

        total_score = float(player_score) + float(opponent_score)
        if status == 'planned' and total_score > 0:
            self._errors["status"] = self.error_class(
                [u'Planned status is not allowed if game has score'])
            del cleaned_data["status"]
        return cleaned_data


class GameInline(admin.TabularInline):
    model = Game
    form = GameInLineFormAdmin
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):        
        formset = super(GameInline, self).get_formset(request, obj, **kwargs)

        initial = []

        if request.method == "GET" and obj is None and request.GET.has_key('tournament'):
            tournament = Tournament.objects.get(pk=request.GET['tournament'])

            if tournament.round_set.count() == 0:
                players = tournament.players.filter(
                    dynamic_homologation=True).order_by('name')
                half = len(players) / 2
                if players:
                    for i in range(half):
                        initial.append({'player': players[i],
                                        'opponent': players[half + i] if half + i < len(players) else None,
                                        'tournament': tournament,
                                        'player_dummy': False,
                                        'opponent_dummy': False})
                    if len(players) % 2 == 1:
                        index = random.randrange(len(players)-1)
                        initial.append({'player': players[len(players)-1],
                                        'opponent': players[index],
                                        'tournament': tournament,
                                        'player_dummy': False,
                                        'opponent_dummy': True})

                pass
            else:
                players = tournament.players.filter(dynamic_homologation = True).order_by('name')
                players_list = []
                for player in players:
                    if player.dynamic_homologation:
                        players_list.append({
                            'name': player.name,
                            'player': player
                        })
                if players:
                    games = Game.objects.filter(
                        round__tournament=tournament).order_by('round__round_date')
                    games_list = [{'round': game.round.id,
                                  'player': game.player.name,
                                  'player_dummy': game.player_dummy,
                                   'opponent': game.opponent.name if game.opponent else None,
                                   'opponent_dummy': game.opponent_dummy,
                                   'player_score': game.player_score,
                                   'opponent_score': game.opponent_score,
                                   'player_color': game.player_color,
                                   'opponent_color': game.opponent_color,
                                   'is_walkover': game.status == 'walkover'}
                                  for game in games]                    
                    pairing = Pairing(players_list, games_list,
                                      tournament.round_set.count() + 1)
                    pairs = pairing.make_it()                    
                    remaining_players = set(players)
                    paired_players = set()
                    for pair in pairs:
                        paired_players.add(pair[0]['player'])
                        paired_players.add(pair[1]['player'])
                        initial.append({'player': pair[0]['player'],
                                        'opponent': pair[1]['player'],
                                        'tournament': tournament,
                                        'player_dummy': False,
                                        'opponent_dummy': False})
                    remaining_players = remaining_players.difference(
                        paired_players)
                    if len(remaining_players) == 1:
                        remaining = list(remaining_players)[0]
                        player_games = games.filter(player=remaining).filter(player_dummy=False).count()
                        opponent_games = games.filter(opponent=remaining).filter(opponent_dummy=False).count()
                        player_dummy_games = games.filter(player_dummy=True)
                        for game in player_dummy_games:
                            paired_players.remove(game.player)
                        opponent_dummy_games = games.filter(opponent_dummy=True)
                        for game in player_dummy_games:
                            paired_players.remove(game.player)
                        index = random.randrange(len(paired_players))
                        opponent = list(paired_players)[index]
                        if player_games <= opponent_games:
                            initial.append({'player': remaining,
                                            'opponent': opponent,
                                            'tournament': tournament,
                                            'player_dummy': False,
                                            'opponent_dummy': True})
                        else:
                            initial.append({'player': opponent,
                                            'opponent': remaining,
                                            'tournament': tournament,
                                            'player_dummy': True,
                                            'opponent_dummy': False})


            formset.extra = len(initial)

        formset.__init__ = curry(formset.__init__, initial=initial)

        return formset


class RoundFormAdmin(forms.ModelForm):
    def clean(self):
        cleaned_data = super(RoundFormAdmin, self).clean()

        tour = cleaned_data.get("tournament")
        if tour is not None:
            if self.instance.pk is None and tour.round_set.count() > 0:
                prev_round = tour.round_set.order_by("-round_date")[0]
                if prev_round.game_set.count() == 0:
                    raise forms.ValidationError(
                        "The previous round doesn't have any games.")
                elif prev_round.game_set.filter(status="planned").count() > 0:
                    raise forms.ValidationError(
                        "The previous round has unfinished games.")

        return cleaned_data

    pass


class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'add_tournament_link', 'round_date')
    list_filter = ['round_date']
    date_hierarchy = 'round_date'
    search_fields = ['tournament__name', 'name']
    ordering = ['-round_date']
    inlines = [GameInline]
    form = RoundFormAdmin

    class Media:
        css = {"all": ("css/additional_admin.css",)}

    # def get_model_perms(self, request):
    #     """
    #     Return empty perms dict thus hiding the model from admin index.
    #     """
    #     return {}

    def add_tournament_link(self, round):
        return '<a href="../tournament/?q={0:s}">{0:s}</a>'.format(round.tournament.name)
    add_tournament_link.short_description = 'Tournament'
    add_tournament_link.allow_tags = True


admin.site.register(Round, RoundAdmin)
