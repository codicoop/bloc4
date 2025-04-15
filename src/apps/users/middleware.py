from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, reverse


class VerificationRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        view_name = resolve(request.path_info).view_name
        view_names = settings.VERIFICATION_REQUIRED_IGNORE_VIEW_NAMES
        if (
            view_name not in view_names
            and request.user.is_authenticated
            and
            (
                not request.user.email_verified or not request.user.entity
            )
        ):
            return redirect(reverse("registration:profile_details"))
        return self.get_response(request)
