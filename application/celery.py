import os

from celery import Celery
from celery import Task

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from .utils import get_env


class BaseTaskWithRetry(Task):
    # auto retry the task if these errors will be sent
    autoretry_for = (ObjectDoesNotExist, KeyError)

    # aditional args for retry feature
    retry_kwargs = {'max_retries': 2}

    # This will automatically exponentially backoff when errors arise.
    retry_backoff = True

    # The task execution time limit, in seconds.
    time_limit = 360
    task_time_limit = 360
    soft_time_limit = 360

    # acks_late is also something you should know about.
    # By default Celery first marks the task as ran and then executes it,
    # this prevents a task from running twice in case of an
    # unexpected shutdown. This is a sane default because we cannot
    # guarantee that every task that every developer writes
    # can be safely ran twice.
    acks_late = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Aqui os apps não foram carregados ainda
        # logo esse import no topo não funcionaria
        from notification.celerytasks import post_sync_slack_message

        msg = '{0!r} failed: {1!r}'.format(task_id, exc)
        post_sync_slack_message(msg, "backend-errors")

        super(BaseTaskWithRetry, self).on_failure(exc, task_id, args, kwargs, einfo)


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

# OBS:
# É possível utilizar um outro banco para o celery results.
# https://docs.celeryproject.org/en/latest/userguide/tasks.html#task-result-backends
app = Celery(
    get_env('APP_NAME'),
    broker=get_env('CELERY_BROKER_URL'),
    backend=get_env('CELERY_RESULT_BACKEND', None),
    include=[
        'config.celerytasks',
        'notification.celerytasks',
    ]
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# The periodic task schedules uses the UTC time zone by default, but you can
# change the time zone used using the timezone setting.
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#time-zones
app.conf.timezone = 'America/Sao_Paulo'

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
