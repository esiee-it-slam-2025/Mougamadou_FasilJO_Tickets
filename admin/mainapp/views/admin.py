from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from ..models.event import Event

@staff_member_required
def event_list(request):
    events = Event.objects.all().order_by('start')
    return render(request, 'admin/events.html', {'events': events})