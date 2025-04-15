from django.conf import settings
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.shortcuts import redirect

from project.services import user_have_entity_and_verified_email


class AnonymousRequiredMixin(AccessMixin):
    """Verify that the current user is not authenticated."""

    # For the django-login-required-mixin
    login_required = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        url = settings.LOGIN_REDIRECT_URL if settings.LOGIN_REDIRECT_URL else ""
        return redirect(url)


class UserHaveEntityAndVerifiedEmail(UserPassesTestMixin):
    """
    By default we use function based views, in which we use this decorator to
    prevent users without a verified email to access:
    @user_passes_test(
    user_have_entity_and_verified_email,
    login_url=reverse_lazy("registration:profile_details"),
)
    This mixin is for those cases in which we're using CBVs.
    """
    def test_func(self):
        return user_have_entity_and_verified_email(self.request.user)
