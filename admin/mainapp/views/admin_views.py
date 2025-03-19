from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from ..models.event import Event
from ..models.stadium import Stadium
from ..models.team import Team 
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.db.models import Count, Sum

class AdminLoginView(LoginView):
    template_name = 'login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('event_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.get_user().is_superuser:
            form.add_error(None, "Accès réservé aux administrateurs")
            return self.form_invalid(form)
        return super().form_valid(form)

@user_passes_test(lambda u: u.is_superuser)
def event_list(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        score = request.POST.get('score')
        winner_id = request.POST.get('winner_id')
        
        try:
            event = Event.objects.get(id=event_id)
            if score:  # Si un score est fourni
                event.score = score
                if winner_id:  # Si un gagnant est sélectionné
                    event.winner_id = winner_id
                event.save()
        except Event.DoesNotExist:
            pass
            
    events = Event.objects.all().order_by('start')
    stadiums = Stadium.objects.all()
    
    stadium_id = request.GET.get('stadium')
    date = request.GET.get('date')
    
    if stadium_id:
        events = events.filter(stadium_id=stadium_id)
    if date:
        events = events.filter(start__date=date)
        
    return render(request, 'event_list.html', {
        'events': events,
        'stadiums': stadiums
    })

@user_passes_test(lambda u: u.is_superuser)
def tickets_list(request):
    # Récupérer tous les événements avec leurs billets associés
    events = Event.objects.prefetch_related(
        'ticket_set',
        'ticket_set__user'
    ).annotate(
        total_tickets=Count('ticket'),
        total_revenue=Sum('ticket__price')
    ).order_by('start')
    
    event_id = request.GET.get('event')
    if event_id:
        events = events.filter(id=event_id)

    return render(request, 'tickets_list.html', {
        'events': events
    })

@user_passes_test(lambda u: u.is_superuser)
def create_event(request):
    if request.method == 'POST':
        stadium_id = request.POST.get('stadium')
        team_home_id = request.POST.get('team_home')
        team_away_id = request.POST.get('team_away')
        start_date = request.POST.get('start')
        
        try:
            Event.objects.create(
                stadium_id=stadium_id,
                team_home_id=team_home_id if team_home_id else None,
                team_away_id=team_away_id if team_away_id else None,
                start=start_date
            )
            return redirect('event_list')
        except Exception as e:
            error = str(e)
            return render(request, 'create_event.html', {
                'error': error,
                'stadiums': Stadium.objects.all(),
                'teams': Team.objects.all()
            })
    
    return render(request, 'create_event.html', {
        'stadiums': Stadium.objects.all(),
        'teams': Team.objects.all()
    })

@user_passes_test(lambda u: u.is_superuser)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        stadium_id = request.POST.get('stadium')
        team_home_id = request.POST.get('team_home')
        team_away_id = request.POST.get('team_away')
        start = request.POST.get('start')
        score = request.POST.get('score')
        winner_id = request.POST.get('winner_id')
        
        event.stadium_id = stadium_id
        event.team_home_id = team_home_id if team_home_id else None
        event.team_away_id = team_away_id if team_away_id else None
        event.start = start
        event.score = score if score else None
        event.winner_id = winner_id if winner_id else None
        event.save()
        
        return redirect('event_list')
        
    return render(request, 'edit_event.html', {
        'event': event,
        'stadiums': Stadium.objects.all(),
        'teams': Team.objects.all()
    })

@user_passes_test(lambda u: u.is_superuser)
def delete_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event.delete()
    return redirect('event_list')

def logout_view(request):
    logout(request)
    return redirect('admin_login')