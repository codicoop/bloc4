from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.rooms.views import room_detail_view

app_name = "rooms"
urlpatterns = [
    path(
        _("<uuid:id>/"),
        room_detail_view,
        name="room_detail",
    ),
]
