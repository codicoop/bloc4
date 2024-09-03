from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext_lazy as _

from apps.reservations.models import Reservation
from apps.reservations.services import send_mail_reservation
from project.admin import ModelAdmin


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    list_display = (
        "title",
        "date",
        "start_time",
        "end_time",
        "room",
        "total_price",
        "privacy",
        "entity",
        "status",
    )
    list_filter = (
        "title",
        "date",
        "room",
        "is_paid",
        "entity",
        "privacy",
        "reserved_by",
        "canceled_by",
        "canceled_at",
        "status",
    )
    search_fields = (
        "title",
        "date",
        "room",
        "is_paid",
        "entity",
        "privacy",
        "reserved_by",
        "canceled_by",
        "canceled_at",
        "status",
    )
    fieldsets = (
        (None, {
            'fields': (
                "room",
                "title",
                "date",
                "start_time",
                "end_time",
                "assistants",
                "catering",
                "notes",
                "is_paid",
                "total_price",
                "entity",
                "reserved_by",
                "canceled_by",
                "canceled_at",
                "status",
                "actions_field",
                "privacy",)
        }),
        (_("Only for public training"), {
            'fields': (
                "description",
                "poster",
                "url",),
        }),
    )
    readonly_fields = ("actions_field", "total_price")


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<uuid:reservation_id>/confirm_reservation/",
                self.admin_site.admin_view(self.notify_confirmed_reservation),
                name="notify_confirmed_reservation",
            ),
            path(
                "<uuid:reservation_id>/reject_reservation/",
                self.admin_site.admin_view(self.notify_rejected_reservation),
                name="notify_rejected_reservation",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="Accions")
    def actions_field(self, obj):
        if not obj.id:
            return "-"
        confirmed_reservation_msg = _(
            "Are you sure you want to confirm the reservation and notify the user?"
        )
        confirmed_reservation_url = reverse(
            "admin:notify_confirmed_reservation",
            args=[obj.id],
        )
        confirmed_reservation_text = _("Confirm reservation and notify the user")
        buttons = [
            self._get_url_with_alert_msg(
                confirmed_reservation_msg,
                confirmed_reservation_url,
                confirmed_reservation_text,
            )
        ]

        rejected_reservation_msg = _(
            "Are you sure you want to reject the reservation and notify the user?"
        )
        rejected_reservation_url = reverse(
            "admin:notify_rejected_reservation",
            args=[obj.id],
        )
        rejected_reservation_text = _(
            "Confirm rejection of reservation and notify the user"
        )
        buttons.append(
            self._get_url_with_alert_msg(
                rejected_reservation_msg,
                rejected_reservation_url,
                rejected_reservation_text,
            )
        )
        return format_html("<br><br>".join(buttons))

    def _get_url_with_alert_msg(self, alert_msg, url, text):
        return (
            '<a class="grp-button grp-default" '
            f"href=\"javascript:if(confirm('{escapejs(alert_msg)}')) "
            f"window.location.href = '{url}'\">{text}</a>"
        )

    def notify_confirmed_reservation(self, request, reservation_id):
        reservation = Reservation.objects.get(pk=reservation_id)
        reservation.status = Reservation.StatusChoices.CONFIRMED
        reservation.save()
        send_mail_reservation(reservation, "reservation_confirmed_user")
        messages.success(
            request,
            _(
                "An email has been sent to the entity to inform"
                " them that the room reservation has been confirmed."
            ),
        )
        return self._redirect_to_change(reservation.id)

    def notify_rejected_reservation(self, request, reservation_id):
        reservation = Reservation.objects.get(pk=reservation_id)
        reservation.status = Reservation.StatusChoices.REFUSED
        reservation.save()
        send_mail_reservation(reservation, "reservation_rejected_user")
        messages.success(
            request,
            _(
                "An email has been sent to the entity to inform"
                " them that the room reservation has been rejected."
            ),
        )
        return self._redirect_to_change(reservation.id)

    def _redirect_to_change(self, id):
        return HttpResponseRedirect(
            reverse("admin:reservations_reservation_change", args=(id,))
        )
