from django.urls import path
from django.contrib import admin
from .views import stadiums, teams, events, login_view, buy_ticket, get_ticket_info

urlpatterns = (
    path('admin/', admin.site.urls),
    
    path("api/stadiums", stadiums),
    path("api/teams/", teams, name='teams'), 
    path("api/events/", events, name='events'),
    path("api/login/", login_view, name='login'),
    path("api/buyTicket/", buy_ticket, name='buy_ticket'),
    path("api/getInfo/<str:ticket_id>/", get_ticket_info, name='get_ticket_info'),
)
