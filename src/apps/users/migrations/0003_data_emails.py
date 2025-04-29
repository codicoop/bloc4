from django.db import migrations

from project.post_office import textify


def populate_mail_templates(apps, schema_editor):
    mail_model = apps.get_model("post_office", "EmailTemplate")

    templates = [
        dict(
            id="password_reset",
            translated_templates={
                "en": {
                    "subject": "Password reset for your account at " "{{project_name}}",
                    "body": """
<p>Hello, {{user_name}},</p>
<p>We're sending you this e-mail because today {{date}} at {{time}}
someone requested the reset of the {{user_email}}'s account password
for {{absolute_url}}.</p>

<p> If it weren't you who requested it,
ignore this message. If you keep receiving this email multiple times,
it could be that someone is trying to access your account. Make sure to
set a long password.
We will appreciate it if you could also warn us about the situation.
</p>

<h3>Password resetting instructions</h3>
<p>To set a new password open this link:
<a href="{{password_reset_url}}">{{password_reset_url}}</a>
</p>
                    """,
                },
                "ca": {
                    "subject": "Reinicialització de contrasenya del teu compte a "
                    "{{project_name}}",
                    "body": """
<p>Hola, {{user_name}},</p>
<p>T'enviem aquest correu electrònic perquè avui {{date}} a les {{time}}
algú ha sol·licitat el reinici de la contrasenya del compte {{user_email}}
de l'aplicació {{absolute_url}}.</p>

<p>Si no has estat tu qui ho ha demanat, ignora aquest missatge.
Si segueixes revent correus com aquest múltiples vegades, podria ser que algú
estigui intentant accedir al teu compte. Assegura't de posar una contrasenya
ben llarga i t'agrairem que ens informis de la situació.
</p>

<h3>Instruccions pel reinici de la contrasenya</h3>
<p>Per establir una nova contrasenya obre aquest enllaç:
<a href="{{password_reset_url}}">{{password_reset_url}}</a>
</p>
                    """,
                },
            },
        ),
        dict(
            id="email_verification",
            translated_templates={
                "en": {
                    "subject": "Email verification code for your account at {{project_name}}",
                    "body": """
    <p>Hello, {{user_name}},</p>
    <p>We're sending you this e-mail because today {{date}} at {{time}}
    you have asked to verify your email {{user_email}}
    for {{absolute_url}}.</p>

    <p>To complete this action and validate your email, enter the code <b>{{ user_code }}</b> by clicking
        on the following link: <a href="{{email_verification_url}}">{{email_verification_url}}</a>
    </p>

    <p> If it weren't you who requested it,
    ignore this message.</p>
                        """,
                },
                "ca": {
                    "subject": "Verificació del correu electrònic del teu compte a {{project_name}}",
                    "body": """
    <p>Hola, {{user_name}},</p>
    <p>T'enviem aquest correu electrònic perquè avui {{date}} a les {{time}}
        heu sol·licitat verificar el vostre correu electrònic {{user_email}}
        per a {{absolute_url}}.</p>
    <p>Per a completar aquesta acció, introduïu el codi <b>{{user_code}}</b> fent clic al següent enllaç: <a href="{{email_verification_url}}">{{email_verification_url}}</a>
    </p>
    <p>Si no has estat tu qui ho ha demanat, ignora aquest missatge.</p>
                        """,
                },
            },
        ),
        dict(
            id="email_registration_pending",
            translated_templates={
                "en": {
                    "subject": "Pending account on {{project_name}}",
                    "body": """
    <p>Hello, {{user_name}},</p>
    <p>We're sending you this e-mail because today {{date}} at {{time}}
    you have registered an account
    for {{absolute_url}} succesfully.</p>

    <p>The request is pending to be validated.</p>

    <p> If it weren't you who requested it,
    ignore this message.</p>
                        """,
                },
                "ca": {
                    "subject": "Compte pendent d'activació a {{project_name}}",
                    "body": """
    <p>Hola, {{user_name}},</p>
    <p>T'enviem aquest correu electrònic perquè avui {{date}} a les {{time}}
        has fet el registre d'un compte per a {{absolute_url}}.</p>
    <p>La sol·licitud està pendent de validar.</p>
    <p>Si no has estat tu qui ho ha demanat, ignora aquest missatge.</p>
                        """,
                },
            },
        ),
        dict(
            id="email_registration_pending_to_bloc4",
            translated_templates={
                "en": {
                    "subject": "Pending account for {{user_entity_name}}",
                    "body": """
    <p>Hello,</p>
    <p>We're sending you this e-mail because today {{date}} at {{time}}
    a new account have registered in {{absolute_url}}.</p>

    <p>The request for the entity {{user_entity_name}} with email {{user_email}} is pending to be validated. If you want to accept the request, go to the <a href="{{user_admin_url}}">user profile</a> an click in the "Verify the account and notify the user" button.</p>

    <p>If you want to reject the request, please, delete de <a href="{{user_admin_url}}">user profile</a> and the entity.</p>
                        """,
                },
                "ca": {
                    "subject": "Compte pendent d'activació per {{user_entity_name}}",
                    "body": """
    <p>Hola,</p>

    <p>T'enviem aquest correu electrònic perquè avui {{date}} a les {{time}}
        s'ha registrat un nou compte a {{absolute_url}}.</p>

    <p>La sol·licitud de l'entitat {{user_entity_name}} amb correu {{user_email}} està pendent de validar.</p>

    <p>Si vols acceptar aquesta petició, has d'anar al <a href="{{user_admin_url}}">perfil d'usuari</a> i fer clic al botó "Verifiqueu el compte i notifiqueu a l'usuari".</p>

    <p>Si vols rebutjar la petició, has d'esborrar el <a href="{{user_admin_url}}">perfil del usuari</a> i la seva entitat.</p>
                        """,
                },
            },
        ),
        dict(
            id="email_account_activated",
            translated_templates={
                "en": {
                    "subject": "Account activated in Bloc4BCN",
                    "body": """
    <p>Hello, {{user_name}},</p>
    <p>We're sending you this e-mail because today {{date}} at {{time}}
    your account in {{absolute_url}} with username {{user_email}} with the entity {{user_entity_name}} is activated.</p>
                        """,
                },
                "ca": {
                    "subject": "Compte activat a Bloc4BCN",
                    "body": """
    <p>Hola, {{user_name}},</p>

    <p>T'enviem aquest correu electrònic perquè avui {{date}} a les {{time}}
        s'ha activat el teu compte a {{absolute_url}} amb nom d'usuari {{user_email}} en l'entitat {{user_entity_name}}.</p>
                        """,
                },
            },
        ),
    ]

    print("")
    for template in templates:
        obj, created = mail_model.objects.update_or_create(
            name=template.get("id"),
            language="",  # Empty language to get the "base" template.
            defaults={
                "name": template.get("id"),
            },
        )
        for lang, translated_template in template.get("translated_templates").items():
            obj.translated_templates.update_or_create(
                name=template.get("id"),
                language=lang,
                defaults={
                    "language": lang,
                    "subject": translated_template.get("subject"),
                    "html_content": translated_template.get("body"),
                    "content": textify(translated_template.get("body")),
                    # name field included due this bug:
                    # https://github.com/ui/django-post_office/issues/214
                    "name": template.get("id"),
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_data_superuser"),
        ("post_office", "__latest__"),
    ]

    operations = [
        migrations.RunPython(populate_mail_templates),
    ]
