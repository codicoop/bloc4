# Codi Cooperatiu's Django boilerplate

![lint workflow](https://github.com/codicoop/boilerplate_django/actions/workflows/lint.yml/badge.svg)
![docker workflow](https://github.com/codicoop/boilerplate_django/actions/workflows/docker.yml/badge.svg)

# Instalation guide
In order to install this project, you have to:

1. Import the project.
2. In the root, you have to install the packages necessaries with `npm install`
3. After, if you are going to make changes in the html styles, you have to compile them in order for them to show. You do it with:
`npx tailwindcss -i ./src/assets/styles/input.css -o ./src/assets/styles/output.css --watch`
4. Inside */docker/* folder rename **.env.example** to **.env** and then run  `docker compose up`.
5. From Docker shell ejecute: `python manage.py migrate`.
6. Go to: [localhost:1234](http://localhost:1234)
7. **.env** creates a superuser account with username hola@codi.coop

# Included packages

## Django Post Office
https://github.com/ui/django-post_office

> By 3.6.0, the package still raises the AutoField deprecation warnings.
> We're tracking an issue and a PR that will fix it eventually.

Few features from this library are already set up, but it brings a lot more of
interesting features. If you need anything related to email handling, first check
if it's already included.

The email templates are created using data migrations that contain the subject
and body internationalized in the enabled languages. More about that at the
Internationalization section.

### Removal

This boilerplate assumes that you'll want to send transactional emails. If not:
- Uninstall `django-post-office`
- In settings:
  - Remove it from `INSTALLED_APPS`
  - Remove the `POST_OFFICE` block.
  - The `EMAIL_BACKEND` var is probably pointing to the `post-office` backend,
change it to what you need, or remove it.
  - You can delete the `POST_OFFICE_DEFAULT_BACKEND` var from the environment
variables.
- Remove the 'Django Post Office' set of settings from `settings.py` and from the `.env`
files.
- Delete `/base/post_office.py`
- Delete `/users/migrations/0003_data_emails.py` (if you haven't add more migrations
after that one ofc)

### Features that we're using in the boilerplate

- Having the email templates handled in the admin panel.
- Log all the sent emails and access them in the admin panel.
- Error log in the admin panel, that tracks the failed deliveries.

Note that the `DEFAULT_PRIORITY` setting is 'now', meaning that the emails are
going to be immediately sent instead of added to queue for further processing.

# Included features

## Custom templates for fields and widgets

### Trick to render the fields with the error classes

Might be useful when testing FlowBite design changes.

In `BaseFlowBiteBoundField.get_context` change `if self.errors:` for
`if not self.errors:`.

This trick is a bit limited given that it will not include an error message,
which you will probably also need to render.

### How it works and how to create/modify the field and controls tempaltes

We're using Tailwind with a components library called FlowBite.

We needed to be able to use either the format...

```
{{ form.as_div }}
or
{{ form }}
```

... for simple cases, and the format...

```
{{ form.non_field_errors }}
<div class="something">
  {{ form.subject.as_field_group }}
</div>
<div class="something">
  {{ form.message.as_field_group }}
</div>
<div class="something">
  {{ form.sender.as_field_group }}
</div>
<div class="something">
  {{ form.cc_myself.as_field_group }}
</div>
```

... for more complex layouts.

> **Important**: We're not creating the custom templates for the `form.as_p`,
> `form.as_ul` or other representations, only for `form.as_div` (and just
> `form`, as it default to `as_div`). **Only use the div form representation.**

We studied the possibility of switching to `django-crispy-forms` as it provides
layout control, and looks promising, but we decided to leave it for the future.

We're customizing the form controls' templates using this new django 5 feature:
https://docs.djangoproject.com/en/5.0/topics/forms/#reusable-field-group-templates

There is a template that renders the "field group" at `templates/fields/field_default.html`

We should try to have all the fields work fine with the same base field template,
but if you need a different template for a field, you should create a new one
based on `field_default.html` and set up the field according to the linked
documentation. In that case, consider if it's worth it to first modify the
`field_default.html` to include `block` tags, and then make you custom
template extent `field_default.html` and override only the blocks.

That template covers the elements "around" que actual control. The control
itself, meaning, in example, the `<select>` tag, is what Django calls Widget.

If you need to customize the control, in our tailwind/flowbite approach usually
you'll only need to modify the classes.

For that, you need to create a class extending `BaseFlowBiteBoundField` and
specify the attributes, following the example at the `FlowBiteBoundCharField`
class.

Anything that can be customized by modifying the widget's `attrs` should be done
in this class.

But if you need to modify the HTML structure of the control you'll need
to override its template by copying the original Django template into
`templates/django/forms/widgets` and modify it.
The path to find the original templates should be something similar to:

    /.venv/lib/python3.11/site-packages/django/forms/templates/django/forms/widgets

Moreover, if you're rendering the full form with `{{ form.as_div }}` or
`{{ form }}` (which default to `as_div`) and you need to customize the form's
HTML structure that wraps the fields, there are two things to consider:

- You can change the classes of the div that wraps each field without having to
edit the template. There might be multiple ways to do it. Read
`BaseFlowBiteBoundField.css_classes` comment.
- You can edit the template by modifying the the `templates/django/forms/div.html`
file. At the moment of writing this, this template is exactly the same as the
original one, just put there to make it easier to find it in the future. If you
find a way to change the path of this template programatically, please move it
to a path that fits our structure better.

## Custom user account views and templates

### Removal

If your project is not going to have a Django front-end (i.e. is only an admin
panel backoffice or is 100% headless), delete the following views and their
registration in `users/urls.py`:

- PasswordResetView
- PasswordResetConfirmView
- PasswordResetDoneView
- PasswordResetCompleteView
- signup_view
- login_view
- details_view

Delete the folders:
`templates/profile`
`templates/registration`

If you do this, you might be interested in accessing the default Django views
for account management.
Add this to your URLs to enable them:

    path('accounts/', include('django.contrib.auth.urls')),

### `privacy_policy_accepted` field

Note that this field is `datetime` instead of boolean.
Check the comments in the `set_boolean_datetime` method as well as the `save()`
method of the `UserSignUpForm` class for an implementation example.

## Internationalization

### Restricting available languages

If you want to use a specific subset of Django's available languages, you can
set the `LANGUAGES` setting variable in `settings.py`, for example:

```python
LANGUAGES = [
    ("en", _("English")),
    ("ca", _("Catalan")),
]
```

If you only want to set one language for the website, simply put that one in the
list. Make sure it's the same as the one in the variable `LANGUAGE_CODE`.

### Translated urls

https://docs.djangoproject.com/en/4.0/topics/i18n/translation/#translating-url-patterns

In case you want to remove translated URLs, simply remove the `gettext()`
wrapper they have in the URLConf files. For example:

```python
from django.utils.translation import gettext_lazy as _

path(_("registration/"), ...), # Translated URL
path("registration/", ...) # Non-translated URL
```

### Translated email templates

The password reset template is in english and includes a translation in catalan.
In the `PasswordResetForm` class you'll see an example of how to use translated
templates, with the `mail.send()`'s `language` param.

#### Creating or modifying email templates

Check the example at `base/migrations/0002_data_emails.py`.

If you add a new language, you'll have to create new data migrations for all
existing email templates that create the new translated templates.

### Translated strings in python code and templates

The docker container includes the necessary dependency for the .po files
generation (which is a program called *gettext*).

Therefore, you can generate the .po files regardless of having *gettext* installed
in your system or not.

In the container's terminal, generate the .po files with:

    python manage.py makemessages --all

If you need a more specific command, check `makemessages` documentation.

As stated in Django's documentation, to compile the .po files, the command is:

    python manage.py compilemessages

After that, you should restart the app (i.e., restarting the docker container)
for the translations to load.

### Completely remove internationalization

To completely remove internationalization of a Django project, set the
`USE_I18N` to `False`. This way, the `LANGUAGE_CODE` setting won't be used. You
should then also set the `LANGUAGES` variable to just the one language you plan
on using.

You should also remove all URLs that are inside a `i18n_patterns()` function.
More specifically, remove the redirect from the root page to the translated
root page so as not to have an infinite loop. That is, remove

```python
path("", RootRedirectView.as_view()),
```

and just leave

```python
path("", home_view, name="home"),
```

Finally, remove the language selection widget from the base template.

## `StandardSuccess` view

Currently used by `profile_details_success` url.

We find a good usability pattern to, in some situations, send the user to a
page that only contains the confirmation message and a button to go back.

If your app is full headless or only a backoffice you can remove this class along
with the `users`'s app views.



## `AnonymousRequiredMixin` view mixin

It could be problematic and confusing to allow users to access views like Login,
password restoration or signup while already logged in.

## `LoginRequiredMiddleware` middleware

Usually, to create a protected view (one that requires a logged user), it is
necessary to decorate the view, either through the URLconf or through a Python
decorator on the view itself.

If most of the views in a website need to be protected, this becomes a tedious
and error prone process (it's easy to forget to protect a view). To make things
easier, we included the `LoginRequiredMiddleware` from the
[`django-login-required-middleware`](https://github.com/CleitonDeLima/django-login-required-middleware) package, which protects every view unless specified otherwise.

Our preferred way to specify login non-required views is by setting the
`LOGIN_REQUIRED_IGNORE_PATHS` in the `settings.py` file, although the package
documentation specifies other ways.

**IMPORTANT:** the package defines a set of default views to ignore from the
`auth` views that come with Django. These are:
- `LoginView`
- `PasswordResetView`
- `PasswordResetDoneView`
- `PasswordResetConfirmView`
- `PasswordResetCompleteView`

## `absolute_url` helper

This boilerplate is not including the Django's Sites framework setup, assuming
that the project is going to be for a single site.

The current URL can be obtained in the request data, but in situations where
you don't have a request or you cannot rely on it, we need this URL manually
specified somewhere.

This decorator needs you to declare the `ABSOLUTE_URL` setting.

## `BaseModel`

When an authenticated user interacts with the database, you often want to log
their information to keep track of when and who created which registry.

Extend this abstract model when creating models that share this need.

## `PublicMediaStorage` and `PrivateMediaStorage`

### Removal
If your project is not going to store media (or *dynamic*) files, or if you are
not going to use an S3-compatible service to store them, you can remove:

- `base/storage_backends.py`
- The package `storages`
- The package `boto3` (in case you are not going to use other AWSs)

### Usage
In models, specify the storage method like this:

```python
file_field = models.FileField(
    verbose_name="file name",
    storage=PrivateMediaStorage(),
)
```

It's recommended that by default you always use the private storage method.

## `ModelAdminMixin` and `base.ModelAdmin`

If your project doesn't use the admin panel, you can delete it.

Use `ModelAdmin` or the mixin in combination with `BaseModel` to automatically
fill the `created_by` field when saving new registries.
It also adds this functionality to inlines: if you include any inlines in this
admin that has the `created_by` field, it's going to be filled in the inline's
new registries as well.

## Celery

### Removal

In your env. variables,
- `POST_OFFICE_CELERY_ENABLED` must be disabled.
- `POST_OFFICE_DEFAULT_PRIORITY` must be set to "now".

In `docker/docker-compose.yml`:
- Remove the `boilerplate-celery` and `boilerplate-redis`
services.

Remove the packages redis and django-sendgrid-v5 from the dependencies.

Finally, delete the `apps/celery` app and remove it from `INSTALLED_APPS`.

### Included tasks

The Django Post Office package defines two tasks when the POST_OFFICE_CELERY_ENABLED
setting is enabled:
- post_office.tasks.cleanup_mail
- post_office.tasks.send_queued_mail

Check [its documentation](https://github.com/ui/django-post_office#integration-with-celery)
for more information.

### Debug task

In `apps/celery/celery.py` add this function:

```python
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

```

Then restart the Celery service and the task will be autodetected. If you can
see it at the block `[tasks]` during Celery startup, it worked.

To "queue" the task in Celery, call it with the `delay()` method:
`debug_task.delay()`

The [Celery documentation](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
has examples about it.

# Troubleshooting

## `setuptools` error

When running `poetry install`, if you get this error:

`Can not execute setup.py since setuptools is not available in the build environment.`

Try: `pip install -U setuptools`
In my case, I had `setuptools` v. 60 and got updated to 62.

If it doesn't work for you and you find another solution please add it to this
documentation.

## Gunicorn "slow" and returning `[CRITICAL] WORKER TIMEOUT error`

As long as you keep the nginx layer in the dockerization, you should not face this issue.
But if you removed nginx and access directly to gunicorn, you are probably going to see this
error specially if you use Google Chrome and you open multiple browsers at the same time.

It's explained [here](https://github.com/benoitc/gunicorn/issues/2797#issuecomment-1166303824) along
with the solution.

To avoid that to happen, this boilerplate includes the parameter `--threads=10` in the gunicorn
command.

# Deprecations

## MailQueueHandler

In previous versions the boilerplate included this package.
Now the `mailing_manager` cannot be used anymore because of its dependency
of the `mailqueue` package, which is discontinued.
