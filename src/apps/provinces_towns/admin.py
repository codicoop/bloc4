from django.contrib import admin

from .models import County, Province, Town


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "autonomous_community",
    )
    ordering = [
        "name",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "province",
    )
    search_fields = ("name__unaccent",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "county",
    )
    list_filter = ("county", "county__province")
    search_fields = ("name__unaccent",)
    ordering = [
        "name",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
