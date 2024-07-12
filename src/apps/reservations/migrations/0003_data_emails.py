from django.db import migrations

from project.post_office import textify


def populate_mail_templates(apps, schema_editor):
    mail_model = apps.get_model("post_office", "EmailTemplate")

    templates = [
        dict(
            id="reservation_request_user",
            translated_templates={
                "en": {
                    "subject": "You have requested a new room reservation in Bloc4",
                    "body": """
            <p>Hello {{reserved_by}}!</p>
            <p>We're sending you this e-mail because today {{current_date}} at {{current_time}}
            you have requested a new reservation on Bloc4.</p>

            <p>Below are the details of the reservation request:</p>
             <ul>
                <li>Room reserved: {{room}}</li>
                <li>Date: {{date_reservation}}</li>
                <li>Start time: {{start_time_reservation}}</li>
                <li>End time: {{end_time_reservation}}</li>
                <li>Reserved by the entity: {{entity}}</li>
                <li>Responsible person: {{reserved_by}}</li>
                <li>Total price: {{total_price}}</li>
            </ul>

            <p>The current status of the reservation is {{status}},
            when Bloc4 confirms the reservation request you will receive an email informing you of this.</p>

                    """,
                },
                "ca": {
                    "subject": "Has sol·licitat una nova reserva de sala a Bloc4",
                    "body": """
            <p>Hola {{reserved_by}}!</p>
            <p>Us enviarem aquest correu electrònic perquè avui {{current_date}} a {{current_time}}
            has sol·licitat una nova reserva de sala al Bloc4.</p>

            <p>A continuació es detallen les dades de la sol·licitud de la reserva:</p>
             <ul>
                <li>Sala reservada: {{room}}</li>
                <li>Data: {{date_reservation}}</li>
                <li>Hora d'inici: {{start_time_reservation}}</li>
                <li>Hora de finalització: {{end_time_reservation}}</li>
                <li>Reservada per l'entitat: {{entity}}</li>
                <li>Persona responsable: {{reserved_by}}</li>
                <li>Preu total: {{total_price}}</li>
            </ul>

            <p>L'estat actual de la reserva és {{status}},
            quan Bloc4 confirmi la sol·licitud de la reserva rebrà un correu electrònic informant-lo.
            </p>
                    """,
                },
            },
        ),
        dict(
            id="reservation_confirmed_user",
            translated_templates={
                "en": {
                    "subject": "Your Bloc4 reservation is confirmed",
                    "body": """
            <p>Hello {{reserved_by}}!</p>
            <p>We're sending you this e-mail because
            Bloc4 has confirmed your room reservation request.</p>

            <p>Here are the details of your reservation:</p>
             <ul>
                <li>Room reserved: {{room}}</li>
                <li>Date: {{date_reservation}}</li>
                <li>Start time: {{start_time_reservation}}</li>
                <li>End time: {{end_time_reservation}}</li>
                <li>Reserved by the entity: {{entity}}</li>
                <li>Responsible person: {{reserved_by}}</li>
                <li>Total price: {{total_price}}</li>
            </ul>

                        """,
                },
                "ca": {
                    "subject": "La teva reserva Bloc4 està confirmada",
                    "body": """
            <p>Hola {{reserved_by}}!</p>
            <p>T'enviarem aquest correu electrònic perquè
            Bloc4 ha confirmat la vostra sol·licitud de reserva de sala.</p>

            <p>Aquí tens els detalls de la teva reserva:</p>
             <ul>
                <li>Sala reservada {{room}}</li>
                <li>Data: {{date_reservation}}</li>
                <li>Hora d'inici: {{start_time_reservation}}</li>
                <li>Hora de finalització: {{end_time_reservation}}</li>
                <li>Reservada per l'entitat: {{entity}}</li>
                <li>Persona responsable: {{reserved_by}}</li>
                <li>Preu total: {{total_price}}</li>
            </ul>
                        """,
                },
            },
        ),
        dict(
            id="reservation_rejected_user",
            translated_templates={
                "en": {
                    "subject": "Your Bloc4 reservation has been rejected",
                    "body": """
        <p>Hello {{reserved_by}}!</p>
        <p>We are sending you this e-mail because
        Bloc4 has rejected your reservation request for room {{room}}
         for date {{date_reservation}} with start time {{start_time_reservation}}
          and end time {{end_time_reservation}}.</p>
                                """,
                    },
                    "ca": {
                        "subject": "S'ha rebutjat la vostra reserva Bloc4",
                        "body": """
        <p>Hola {{reserved_by}}!</p>
        <p>T'enviem aquest e-mail perquè
            Bloc4 ha rebutjat la seva sol·licitud de reserva per a la sala {{room}}
            per a la data {{date_reservation}} amb hora d'inici {{start_time_reservation}}
             i hora finalització {{end_time_reservation}}</p>
                                """,
                },
            },
        ),
        dict(
            id="reservation_canceled_user",
            translated_templates={
                "en": {
                    "subject": "Your Bloc4 reservation has been cancelled",
                    "body": """
    <p>Hello {{canceled_by}}!</p>
    <p>We are sending you this e-mail because your Bloc4 reservation for
     room {{room}} on {{date_reservation}} with
      start time {{start_time_reservation}}
      and end time {{end_time_reservation}} has been cancelled.</p>

                            """,
                },
                "ca": {
                    "subject": "La teva reserva en Bloc4 ha estat cancel·lada",
                    "body": """
    <p>Hola {{canceled_by}}!</p>
    <p>T'enviem aquest e-mail perquè la teva reserva
     de Bloc4 per a la sala {{room}} el dia {{date_reservation}}
     amb hora d'inici {{start_time_reservation}}
     i hora de finalització {{end_time_reservation}} ha estat cancel·lada.
    </p>
                            """,
                },
            },
        ),
        dict(
            id="reservation_request_bloc4",
            translated_templates={
                "en": {
                    "subject": "{{reserved_by}} has made a new reservation request",
                    "body": """
        <p>Hello reservation manager!</p>
        <br><br>
        <p>Today {{current_date}} at {{current_time}} we have
         received a new reservation.</p>
        <p>These are the details:</p>
         <ul>
            <li>Room reserved: {{room}}</li>
            <li>Date: {{date_reservation}}</li>
            <li>Start time: {{start_time_reservation}}</li>
            <li>End time: {{end_time_reservation}}</li>
            <li>Reserved by the entity: {{entity}}</li>
            <li>Responsible person: {{reserved_by}}</li>
            <li>Total price: {{total_price}}</li>
        </ul>

        <p>The current status of the reservation is <b>{{ status }}</b>.</p>
        <p>You can manage the request for this reservation in the
         application administrator at the following link:
         <a href="{{reservation_url_admin}}">{{reservation_url_admin}}</a>
         </p>


                """,
                },
                "ca": {
                    "subject": "{{reserved_by}} ha fet una nova sol·licitud de reserva",
                    "body": """
        <p>Hola gestor de reserves!</p>
        <br><br>
        <p>Avui {{current_date}} a {{current_time}} hem rebut una nova reserva.</p>
        <p>Aquests són els detalls:</p>
         <ul>
            <li>Sala reservada: {{room}}</li>
            <li>Data: {{date_reservation}}</li>
            <li>Hora d'inici: {{start_time_reservation}}</li>
            <li>Hora de finalització: {{end_time_reservation}}</li>
            <li>Reservada per l'entitat: {{entity}}</li>
            <li>Persona responsable: {{reserved_by}}</li>
            <li>Preu total: {{total_price}}</li>
        </ul>

        <p>L'estat actual de la reserva és <b>{{status}}</b>.</p>
        <p>Podeu gestionar la sol·licitud d'aquesta reserva a
        administrador de l'aplicació en el següent enllaç:
        <a href="{{reservation_url_admin}}">{{reservation_url_admin}}</a>
        </p>
                """,
                },
            },
        ),
        dict(
            id="reservation_canceled_bloc4",
            translated_templates={
                "en": {
                    "subject": "{{canceled_by}} has cancelled the reservation",
                    "body": """
    <p>Hello reservation manager!</p>
    <br><br>
    <p>{{canceled_by}} has cancelled the reservation of the room
     {{room}} for {{date_reservation}} with start time {{start_time_reservation}}
      and end time {{end_time_reservation}}</p>

                            """,
                },
                "ca": {
                    "subject": "{{canceled_by}} ha cancel·lat la seva reserva",
                    "body": """
    <p>Hola gestor de reserves!</p>
    <br><br>
    <p>{{canceled_by}} ha cancel·lat la reserva de la sala
    {{room}} per a {{date_reservation}} amb hora d'inici {{start_time_reservation}}
     i hora de finalització {{end_time_reservation}}</p>
                            """,
                },
            },
        ),
    ]

    print("")
    for template in templates:
        obj, created = mail_model.objects.update_or_create(
            name=template.get("id"),
            defaults={
                "name": template.get("id"),
            },
        )
        for lang, translated_template in template.get("translated_templates").items():
            obj.translated_templates.create(
                language=lang,
                subject=translated_template.get("subject"),
                html_content=translated_template.get("body"),
                content=textify(translated_template.get("body")),
                # name field included due this bug:
                # https://github.com/ui/django-post_office/issues/214
                name=template.get("id"),
            )


class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0001_initial'),
        ('reservations', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(populate_mail_templates),
    ]
