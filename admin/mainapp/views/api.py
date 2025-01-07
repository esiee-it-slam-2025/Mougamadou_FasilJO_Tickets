from django.http import JsonResponse
from mainapp.models.stadium import Stadium
from mainapp.models.event import Event
from mainapp.models.team import Team
from mainapp.models.ticket import Ticket
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


def stadiums(request):
    # Récupérer tous les stades (plus besoin de prefetch_related car on ne veut plus les événements)
    all_stadiums = Stadium.objects.all()
    
    stadiums_data = []
    for stadium in all_stadiums:
        stadium_info = {
            'id': stadium.id,
            'name': stadium.name,
            'location': stadium.location
        }
        stadiums_data.append(stadium_info)
    
    return JsonResponse({
        'stadiums': stadiums_data,
        'total': len(stadiums_data)
    }, safe=False)

def teams(request):
    # Récupérer toutes les équipes
    all_teams = Team.objects.all()
    
    teams_data = []
    for team in all_teams:
        team_info = {
            'id': team.id,
            'name': team.name,
            'code': team.code,
            'nickname': team.nickname,
            'flag_url': team.flag
        }
        teams_data.append(team_info)
    
    return JsonResponse({
        'teams': teams_data,
        'total': len(teams_data)
    }, safe=False)

def events(request):
    # Récupérer tous les événements avec leurs relations
    all_events = Event.objects.select_related(
        'stadium',
        'team_home',
        'team_away',
        'winner'
    ).order_by('start')
    
    events_data = []
    for event in all_events:
        event_info = {
            'id': event.id,
            'date': event.start.strftime('%Y-%m-%d %H:%M'),
            'stadium': {
                'id': event.stadium.id,
                'name': event.stadium.name,
                'location': event.stadium.location
            },
            'team_home': {
                'id': event.team_home.id,
                'name': event.team_home.name,
                'code': event.team_home.code,
                'nickname': event.team_home.nickname
            } if event.team_home else None,
            'team_away': {
                'id': event.team_away.id,
                'name': event.team_away.name,
                'code': event.team_away.code,
                'nickname': event.team_away.nickname
            } if event.team_away else None,
            'score': event.score,
            'status': 'upcoming' if not event.score else 'completed'
        }
        
        if event.winner:
            event_info['winner'] = {
                'id': event.winner.id,
                'name': event.winner.name,
                'code': event.winner.code,
                'nickname': event.winner.nickname
            }
            
        events_data.append(event_info)
    
    return JsonResponse({
        'events': events_data,
        'total': len(events_data)
    }, safe=False)

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Cette méthode nécessite une requête POST'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'error': 'Username et password sont requis'
            }, status=400)
            
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Générer ou récupérer le token
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'success': True,
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_superuser': user.is_superuser
                }
            })
        else:
            return JsonResponse({
                'error': 'Identifiants invalides'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON invalide'
        }, status=400)
    
@csrf_exempt
@api_view(['POST'])     
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def buy_ticket(request):
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Cette méthode nécessite une requête POST'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        event_id = data.get('event_id')
        tickets_to_buy = data.get('tickets', [])  # Liste de {category: "SILVER", quantity: 2}

        if not event_id or not tickets_to_buy:
            return JsonResponse({
                'error': 'event_id et tickets sont requis'
            }, status=400)

        # Vérifier que l'événement existe
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({
                'error': 'Événement non trouvé'
            }, status=404)

        created_tickets = []
        total_price = 0

        # Créer les tickets pour chaque catégorie demandée
        for ticket_info in tickets_to_buy:
            category = ticket_info.get('category')
            quantity = int(ticket_info.get('quantity', 1))

            if category not in dict(Ticket.CATEGORY_CHOICES):
                return JsonResponse({
                    'error': f'Catégorie invalide: {category}'
                }, status=400)

           
            prices = {
                'SILVER': 100,
                'GOLD': 200,
                'PLATINUM': 300
            }
            price = prices[category]

            for _ in range(quantity):
                ticket = Ticket.objects.create(
                    event=event,
                    user=request.user,
                    category=category,
                    price=price
                )
                created_tickets.append({
                    'id': ticket.id,  # C'est l'UUID qui sera utilisé dans le QR Code
                    'category': ticket.category,
                    'price': str(ticket.price)
                })
                total_price += price

        return JsonResponse({
            'success': True,
            'tickets': created_tickets,
            'total_price': str(total_price)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON invalide'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
    
def get_ticket_info(request, ticket_id):
    # Récupérer le ticket avec l'UUID fourni
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Préparer les informations détaillées du ticket
    ticket_info = {
        'id': ticket.id,
        'event': {
            'id': ticket.event.id,
            'start': ticket.event.start.strftime('%Y-%m-%d %H:%M'),
            'stadium': {
                'name': ticket.event.stadium.name,
                'location': ticket.event.stadium.location
            }
        },
        'category': ticket.category,
        'price': str(ticket.price),
        'is_used': ticket.is_used,
        'purchase_date': ticket.purchase_date.strftime('%Y-%m-%d %H:%M'),
        'user': {
            'id': ticket.user.id,
            'username': ticket.user.username
        }
    }
    return JsonResponse(ticket_info) 