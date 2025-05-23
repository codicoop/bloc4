"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from project.views import RootRedirectView, home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RootRedirectView.as_view()),
]

urlpatterns += i18n_patterns(
    path("", home_view, name="home"),
    path(_("registration/"), include("apps.users.urls", namespace="registration")),
    path(
        _("reservations/"), include("apps.reservations.urls", namespace="reservations")
    ),
    path(_("rooms/"), include("apps.rooms.urls", namespace="rooms")),
)
