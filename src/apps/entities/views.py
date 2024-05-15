from django.shortcuts import get_object_or_404, render

from apps.entities.forms import EntityForm
from apps.entities.models import Entity


def list_view(request):
    context = {"data": Entity.objects.all()}
    return render(request, "list.html", context)


def detail_view(request, id):
    obj = get_object_or_404(Entity, pk=id)
    form = EntityForm(instance=obj)
    return render(request, "details.html", {"form": form})
