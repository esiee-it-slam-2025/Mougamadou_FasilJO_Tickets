import json
from mainapp.models import Stadium, Team, Event, Ticket
from django.http import JsonResponse
import qrcode
from django.contrib.auth.models import User


def stadiums(request):
    return {}
