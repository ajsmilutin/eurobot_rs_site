from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import TournamentInfo, TournamentStandings, TournamentRounds
# Register your models here.
admin.site.register(TournamentInfo, PageAdmin)
admin.site.register(TournamentStandings, PageAdmin)
admin.site.register(TournamentRounds, PageAdmin)
from .modeladmins import player
from .modeladmins import tournament
from .modeladmins import round
