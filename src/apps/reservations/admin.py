from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext_lazy as _

from apps.entities.choices import EntityTypesChoices
from apps.reservations.models import Reservation
from apps.reservations.services import send_mail_reservation
from project.admin import ModelAdmin


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    list_display = (
        "title",
        "entity",
        "date",
        "start_time",
        "end_time",
        "room",
        "base_price",
        "is_budgeted",
        "is_paid",
        "status",
        "privacy",
    )
    list_filter = (
        "date",
        "room",
        "is_budgeted",
        "is_paid",
        "entity",
        "privacy",
        "reserved_by",
        "canceled_by",
        "canceled_at",
        "status",
        "activity_type",
        "bloc4_type",
    )
    date_hierarchy = "date"
    search_fields = (
        "title",
        "date",
        "room__name",
        "is_budgeted",
        "is_paid",
        "entity__fiscal_name",
        "privacy",
        "reserved_by__name",
        "status",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "room",
                    "room_field",
                    "reservation_type",
                    "date",
                    "start_time",
                    "end_time",
                    "assistants",
                    "catering",
                    "notes",
                    "activity_type",
                    "bloc4_type",
                    "is_budgeted",
                    "is_paid",
                    "payment_field",
                    "base_price",
                    "entity",
                    "reserved_by",
                    "canceled_by",
                    "canceled_at",
                    "status",
                    "checked_in",
                    "actions_field",
                    "privacy",
                )
            },
        ),
        (
            _("Billing information"),
            {
                "fields": (
                    "is_billed",
                    "billed_by",
                    "billed_at",
                )
            },
        ),
        (
            _("Only for public training"),
            {
                "fields": (
                    "description",
                    "poster",
                    "url",
                ),
            },
        ),
    )
    readonly_fields = (
        "actions_field",
        "room_field",
        "payment_field",
        "billed_by",
        "billed_at",
    )
    superuser_fields = ("status",)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            new_fieldsets = []
            for name, opts in fieldsets:
                filtered_fields = [
                    field
                    for field in opts["fields"]
                    if field not in ("actions_field", "payment_field", "room_field")
                ]
                if filtered_fields:
                    new_fieldsets.append((name, {"fields": filtered_fields}))
            return tuple(new_fieldsets)
        if obj and obj.entity.entity_type in [
            EntityTypesChoices.HOSTED,
            EntityTypesChoices.BLOC4,
        ]:
            new_fieldsets = []
            for name, opts in fieldsets:
                # Filtra el campo que deseas ocultar
                filtered_fields = [
                    field for field in opts["fields"] if field != "payment_field"
                ]
                if filtered_fields:
                    new_fieldsets.append((name, {"fields": filtered_fields}))
            return tuple(new_fieldsets)
        return fieldsets

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
            path(
                "<uuid:reservation_id>/change_room/",
                self.admin_site.admin_view(self.notify_confirmed_room_change),
                name="notify_confirmed_room_change",
            ),
            path(
                "<uuid:reservation_id>/payment_reminder/",
                self.admin_site.admin_view(self.notify_payment_reminder),
                name="notify_payment_reminder",
            ),
            path(
                "<uuid:reservation_id>/notify_date_or_time_changed/",
                self.admin_site.admin_view(self.notify_date_or_time_changed),
                name="notify_date_or_time_changed",
            ),
        ]
        return custom_urls + urls

    @admin.display(description=_("Change room"))
    def room_field(self, obj):
        if not obj:
            return "-"
        confirmed_room_change_msg = _("Are you sure you want to notify the user?")
        confirmed_room_change_url = reverse(
            "admin:notify_confirmed_room_change",
            args=[obj.id],
        )
        confirmed_room_change_text = _("Notify the user the room is changed")
        buttons = [
            self._get_url_with_alert_msg(
                confirmed_room_change_msg,
                confirmed_room_change_url,
                confirmed_room_change_text,
            )
        ]
        return format_html("<br><br>".join(buttons))

    def notify_confirmed_room_change(self, request, reservation_id):
        reservation = Reservation.objects.get(pk=reservation_id)
        send_mail_reservation(reservation, "confirmed_room_change")
        messages.success(
            request,
            _(
                "An email has been sent to the entity to inform"
                " them that the room of the reservation has change."
            ),
        )
        return self._redirect_to_change(reservation.id)

    @admin.display(description=_("Payment reminder"))
    def payment_field(self, obj):
        if not obj or obj.is_paid:
            return "-"
        notify_payment_reminder_msg = _("Are you sure you want to notify the user?")
        notify_payment_reminder_url = reverse(
            "admin:notify_payment_reminder",
            args=[obj.id],
        )
        notify_payment_reminder_text = _("Notify the user a payment reminder")
        buttons = [
            self._get_url_with_alert_msg(
                notify_payment_reminder_msg,
                notify_payment_reminder_url,
                notify_payment_reminder_text,
            )
        ]
        return format_html("<br>".join(buttons))

    def notify_payment_reminder(self, request, reservation_id):
        reservation = Reservation.objects.get(pk=reservation_id)
        send_mail_reservation(reservation, "payment_reminder")
        messages.success(
            request,
            _(
                "An email has been sent to the entity to inform with a "
                "payment reminder."
            ),
        )
        return self._redirect_to_change(reservation.id)

    def notify_date_or_time_changed(self, request, reservation_id):
        reservation = Reservation.objects.get(pk=reservation_id)
        send_mail_reservation(
            reservation,
            "reservation_date_or_time_changed",
        )
        messages.success(
            request,
            _(
                "An email has been sent to the entity to inform with a "
                "payment reminder."
            ),
        )
        return self._redirect_to_change(reservation.id)

    @admin.display(description=_("Actions"))
    def actions_field(self, obj):
        if obj is None:
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

        date_or_time_changed_msg = _(
            "Are you sure you want to notify the user that the date and/or time"
            " of the reservation have changed?"
        )
        date_or_time_changed_url = reverse(
            "admin:notify_date_or_time_changed",
            args=[obj.id],
        )
        date_or_time_changed_text = _(
            "Notify the user that the date and/or time have changed"
        )
        buttons.append(
            self._get_url_with_alert_msg(
                date_or_time_changed_msg,
                date_or_time_changed_url,
                date_or_time_changed_text,
            )
        )
        return format_html("<br>".join(buttons))

    def _get_url_with_alert_msg(self, alert_msg, url, text):
        return (
            '<a class="submit-row" style="color: white; background-color: #417690;" '
            f"href=\"javascript:if(confirm('{escapejs(alert_msg)}')) "
            f"window.location.href = '{url}'\">{text}</a>"
        )

    def notify_confirmed_reservation(self, request, reservation_id):
        reservation = Reservation.objects.get(pk=reservation_id)
        reservation.status = Reservation.StatusChoices.CONFIRMED
        reservation.canceled_by = None
        reservation.canceled_at = None
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
