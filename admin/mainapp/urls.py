from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from .views import stadiums, teams, events, login_view, buy_ticket, get_ticket_info, my_tickets, register_view, mark_ticket_used
from mainapp.views import admin_views

urlpatterns = (

    #path mon interface admin
    path('custom-admin/login/', admin_views.AdminLoginView.as_view(), name='admin_login'),
    path('custom-admin/events/', admin_views.event_list, name='event_list'),
    path('custom-admin/logout/', admin_views.logout_view, name='admin_logout'),

    
    path("api/stadiums", stadiums),
    path("api/teams/", teams, name='teams'), 
    path("api/events/", events, name='events'),
    path("api/login/", login_view, name='login'),
    path("api/buyTicket/", buy_ticket, name='buy_ticket'),
    path("api/getInfo/<str:ticket_id>/", get_ticket_info, name='get_ticket_info'),
    path("api/myTickets/", my_tickets, name='my_tickets'),
    path("api/register/", register_view, name='register'),
    path('custom-admin/tickets/', admin_views.tickets_list, name='tickets_list'),
    path('custom-admin/events/create/', admin_views.create_event, name='create_event'),
    path('custom-admin/events/<int:event_id>/edit/', admin_views.edit_event, name='edit_event'),
    path('custom-admin/events/<int:event_id>/delete/', admin_views.delete_event, name='delete_event'),
    path('api/markTicketUsed/<str:ticket_id>/', mark_ticket_used, name='mark_ticket_used'),

    #path interface admin django
    path('admin/', admin.site.urls),
)