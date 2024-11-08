from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import escapejs, format_html
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from apps.users.services import send_registration_pending_mail
from project.admin import ModelAdminMixin


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.validated = timezone.now()
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(ModelAdminMixin, BaseUserAdmin):
    list_display = (
        "email",
        "full_name",
        "entity",
        "is_janitor",
        "is_staff",
        "is_verified",
    )
    list_filter = ("entity", "is_superuser", "is_janitor", "is_staff", "is_verified")
    search_fields = (
        "email",
        "name",
        "surnames",
        "entity__fiscal_name",
        "entity__nif",
        "is_janitor",
        "is_verified",
    )
    ordering = ("email",)
    fieldsets = (("Autenticació", {"fields": ("email", "password")}),)
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            "Autenticació",
            {"classes": ("wide",), "fields": ("email", "password1", "password2")},
        ),
    )
    # common_fieldsets is not a standard ModelAdmin attribute. We extend
    # get_fieldsets to avoid having to repeat info in fieldsets and add_fieldsets.
    common_fieldsets = (
        (
            "Dades",
            {
                "fields": (
                    "name",
                    "surnames",
                    "entity",
                )
            },
        ),
        (
            "Permisos i autoritzacions",
            {
                "fields": (
                    "is_janitor",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "actions_field",
                    "email_verified",
                    # Hiding these fields until we have permission groups and
                    # we actually need to add the explanation:
                    # "roles_explanation_field",
                    # "groups",
                ),
            },
        ),
        (
            "Registre",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    superuser_fields = ("is_superuser",)
    readonly_fields = (
        "roles_explanation_field",
        "email_verified",
        "actions_field",
        "is_verified",
    )

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj) + self.common_fieldsets

    @admin.display(description="Informació rols d'usuari")
    def roles_explanation_field(self, obj):
        return format_html(
            """
            <ul>
              <li>Admins: accés a la configuració i personalització del
                backoffice, al llistat d'emails enviats pel sistema i a les
                plantilles de les notificacions. També pot editar els camps
                "Is staff" i "Is active" de la fitxa d'usuaris.
              </li>
            </ul>
            """
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<uuid:id>/verified_account/",
                self.admin_site.admin_view(self.notify_verified_account),
                name="notify_verified_account",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="Accions")
    def actions_field(self, obj):
        if not obj or obj.is_verified:
            return "-"
        confirmed_verification_msg = _(
            "Are you sure you want to confirm the account and notify the user?"
        )
        confirmed_verification_url = reverse(
            "admin:notify_verified_account",
            args=[obj.id],
        )
        confirmed_verification_text = _("Verify the account and notify the user")
        buttons = [
            self._get_url_with_alert_msg(
                confirmed_verification_msg,
                confirmed_verification_url,
                confirmed_verification_text,
            )
        ]
        return format_html("<br class='grp-button grp-default'><br>".join(buttons))

    def _get_url_with_alert_msg(self, alert_msg, url, text):
        return (
            '<a class="grp-button grp-default" '
            f"href=\"javascript:if(confirm('{escapejs(alert_msg)}')) "
            f"window.location.href = '{url}'\">{text}</a>"
        )

    def notify_verified_account(self, request, id):
        user = User.objects.get(pk=id)
        user.is_active = True
        user.is_verified = True
        user.save()
        send_registration_pending_mail(user, "email_account_activated", user.email)
        messages.success(
            request,
            _(
                "An email has been sent to the user to inform"
                " that the account is active."
            ),
        )
        return self._redirect_to_change(user.id)

    def _redirect_to_change(self, id):
        return HttpResponseRedirect(reverse("admin:users_user_change", args=(id,)))
