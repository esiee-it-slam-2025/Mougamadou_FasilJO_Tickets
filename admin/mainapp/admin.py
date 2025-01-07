from django.contrib import admin
from mainapp.models import Event, Stadium, Team, Ticket  # Ajout de Ticket

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('start', 'stadium', 'team_home', 'team_away', 'score')
    list_filter = ('stadium', 'start')
    search_fields = ('team_home__name', 'team_away__name')
    date_hierarchy = 'start'
    ordering = ('start',)

@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'nickname')
    search_fields = ('name', 'nickname')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'user', 'category', 'price', 'is_used', 'purchase_date')
    list_filter = ('category', 'is_used', 'purchase_date')
    search_fields = ('id', 'user__username')
    ordering = ('-purchase_date',)