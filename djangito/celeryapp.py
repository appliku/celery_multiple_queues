import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangito.settings')

app = Celery('djangito')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.redbeat_redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.conf.broker_pool_limit = 1
app.conf.broker_heartbeat = None
app.conf.broker_connection_timeout = 30
app.conf.worker_prefetch_multiplier = 1

app.conf.beat_schedule = {
    'update_contact_lists_numbers': {
        'task': 'update_contact_lists_numbers',
        'schedule': 60,
        'options': {
            'ignore_result': True,
            'expires': 60,
            'queue': 'default',
        }
    },
}
