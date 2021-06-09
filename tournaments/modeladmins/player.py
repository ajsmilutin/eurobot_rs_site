from django.contrib import admin
from django.db.models import Q
from tournaments.models import Player, Tournament, Game
from datetime import date


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name',  'school', 'city', 'static_homologation', 'dynamic_homologation')
        }),
    )
    list_display = ('name',  'school', 'city',
                    'static_homologation', 'dynamic_homologation')
    search_fields = ['name'],
    ordering = ['name']


admin.site.register(Player, PlayerAdmin)
