from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.rooms.models import Room


@login_required
def room_detail_view(request, id):
    room = get_object_or_404(Room, id=id)
    context = {
        "room": room,
    }
    return render(request, "rooms/room_detail.html", context)
