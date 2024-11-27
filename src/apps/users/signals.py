from django.apps import apps
from django.conf import settings
from django.db.backends.utils import logger


def update_user_groups(sender, **kwargs):
    """
    This function is triggered on post_migrate signal.
    That is: after every "migrate" command, even if there are no new
    migrations to apply.
    Signals are defined in the App declaration (apps.py)

    The purpose is to leave all the user groups in the desired state, taking in
    consideration the fact that this will be executed every time,
    even if no changes are needed.

    About django-extra-settings permissions:
    django-extra-settings include its own post_migrate signal:
    https://github.com/fabiocaccamo/django-extra-settings/blob/main/extra_settings/apps.py
    We need its signal to be executed before update_user_groups. This order
    may be related to the order in which apps are included in INSTALLED_APPS.
    A function is included in this file to help you check that the django-extra-settings
    permissions are in order:
    check_constance_permissions()

    About getting the permissions
    In this file, the function print_existing_permissions() is provided to
    help you see each Permission's codename. It can be deduced if you prefer,
    but it also helps to have a full list of available permissions.
    """

    # Administradors
    permissions = {
        "extra_settings": get_permission_codenames("setting", "cv"),
        "admin": get_permission_codenames("logentry", "c"),
        "post_office": get_permission_codenames("email", "v")
        + get_permission_codenames("log", "v")
        + get_permission_codenames("emailtemplate", "v"),
        # post_office also has the 'attachment' model. Not giving access for now.
        "users": get_permission_codenames("user", "vacd"),
        "entities": get_permission_codenames("entity", "vacd")
        + get_permission_codenames("monthly_bonus", "vacd"),
        "reservations": get_permission_codenames("reservation", "vacd"),
        "rooms": get_permission_codenames("room", "vacd"),
    }
    create_group(settings.GROUP_ADMINS, permissions)

    # Superusers
    """
    This block is to clarify which things are meant to be reserved for superusers.
    That means that no other user group declaration should include these.
    - acotags.activity
    - django auth.groups
    """


def create_group(name, permissions):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    group, created = group_model.objects.get_or_create(
        name=name,
    )
    # Using set(), to entirely replace the permissions of this group by the
    # new ones.
    group.permissions.set(get_permissions(permission_model, permissions))
    group.save()
    if created:
        logger.info(f"Grup {name} creat.")
    else:
        logger.info(f"Grup {name} ja existent, permisos actualitzats.")


def get_permissions(permission_model, permissions_dict: dict):
    """
    This function takes all the permissions codenames and contenttype labels
    from the dictionary and returns a list with the queryset of each Permission
    registry.
    We need that to create the m2m relationship between the Group
    and Permission.
    """
    permissions = []
    for content_type__app_label, codenames in permissions_dict.items():
        permissions += permission_model.objects.filter(
            content_type__app_label=content_type__app_label, codename__in=codenames
        )
    return permissions


def get_permission_codenames(base_codename, permissions):
    """
    :param permissions: String containing any of these letters: avcd
    :return: List with all the combinations for the codename.
    """
    strings = []
    if "a" in permissions:
        strings.append(f"add_{base_codename}")
    if "v" in permissions:
        strings.append(f"view_{base_codename}")
    if "c" in permissions:
        strings.append(f"change_{base_codename}")
    if "d" in permissions:
        strings.append(f"delete_{base_codename}")
    return strings


def check_constance_permissions():
    contenttype_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    content_type = contenttype_model.objects.get(
        app_label="extra_settings",
        model="setting",
    )
    logger.info(content_type)
    change_perm = permission_model.objects.filter(
        content_type=content_type,
        codename="change_config",
    )
    view_perm = permission_model.objects.filter(
        content_type=content_type,
        codename="view_config",
    )
    logger.info(f"{change_perm=}, {view_perm=}")


def print_existing_permissions():
    from pprint import pprint

    permission_model = apps.get_model("auth", "Permission")
    for i in permission_model.objects.all():
        pprint(i.__dict__)
