import functools
import logging
import threading

from django.apps import apps as django_apps
from django.db import OperationalError, close_old_connections
from django.utils.timezone import make_aware
from huey.api import Huey
from huey.constants import EmptyData
from huey.storage import BaseStorage, to_blob, to_bytes

logger = logging.getLogger(__name__)


def close_unusable_db_connections():

    def decorator(func):   
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OperationalError:
                close_old_connections()
                raise

        return wrap

    return decorator


class DjangoORMStorage(BaseStorage):
    task_model = None
    schedule_model = None
    keystore_model = None
    dequeue_lock = threading.Lock()

    def __init__(self, name='huey', **kwargs):
        super(DjangoORMStorage, self).__init__(name=name, **kwargs)
        self._local = threading.local()

    @property
    def queue_items(self):
        if self.task_model is None:
            self.task_model = django_apps.get_model("huey_django_orm.HueyTask", require_ready=False)
        return self.task_model.objects.filter(queue=self.name).order_by("-priority", "id")

    @property
    def schedule_tasks(self):
        if self.schedule_model is None:
            self.schedule_model = django_apps.get_model("huey_django_orm.HueySchedule", require_ready=False)
        return self.schedule_model.objects.filter(queue=self.name).order_by("timestamp")

    @property
    def values(self):
        if self.keystore_model is None:
            self.keystore_model = django_apps.get_model("huey_django_orm.HueyKv", require_ready=False)
        return self.keystore_model.objects.filter(queue=self.name)

    @close_unusable_db_connections()
    def dequeue(self):
        with self.dequeue_lock:
            try:
                result = self.queue_items.first()
            except self.task_model.DoesNotExist:
                pass
            else:
                if result is not None:
                    data = result.data
                    result.delete()
                    return to_bytes(data)

    @close_unusable_db_connections()
    def enqueue(self, data, priority=None):
        if self.task_model is None:
            self.task_model = django_apps.get_model("huey_django_orm.HueyTask", require_ready=False)
        self.task_model.objects.create(queue=self.name, data=data, priority=priority)
    
    @close_unusable_db_connections()
    def queue_size(self):
        return self.queue_items.count()

    @close_unusable_db_connections()
    def enqueued_items(self, limit=None):
        items = self.queue_items
        if isinstance(limit, int):
            items = items[0:limit]

        return [to_bytes(i.data) for i in items]

    @close_unusable_db_connections()
    def flush_queue(self):
        self.queue_items.delete()

    @close_unusable_db_connections()
    def add_to_schedule(self, data, ts, utc=None):
        if self.schedule_model is None:
            self.schedule_model = django_apps.get_model("huey_django_orm.HueySchedule", require_ready=False)
        self.schedule_model.objects.create(queue=self.name, data=to_blob(data), timestamp=make_aware(ts))

    @close_unusable_db_connections()
    def read_schedule(self, ts):
        scheduled_tasks = self.schedule_tasks.filter(timestamp__lte=make_aware(ts))

        data = [to_bytes(scheduled_task.data) for scheduled_task in scheduled_tasks]
        scheduled_tasks.delete()

        return data

    @close_unusable_db_connections()
    def schedule_size(self):
        return self.schedule_tasks.count()

    @close_unusable_db_connections()
    def scheduled_items(self, limit=None):
        scheduled_tasks = self.schedule_tasks

        if limit is not None:
            scheduled_tasks = scheduled_tasks[0:limit]

        return [to_bytes(i.data) for i in scheduled_tasks]

    @close_unusable_db_connections()
    def flush_schedule(self):
        self.schedule_tasks.delete()

    @close_unusable_db_connections()
    def put_data(self, key, value, is_result=False):
        if self.keystore_model is None:
            self.keystore_model = django_apps.get_model("huey_django_orm.HueyKv", require_ready=False)
        self.keystore_model.objects.create(queue=self.name, key=key, value=to_blob(value))

    @close_unusable_db_connections()
    def peek_data(self, key):
        try:
            res = self.values.get(key=key)
        except self.keystore_model.DoesNotExist:
            return EmptyData
        else:
            if res is not None:
                return to_bytes(res.value)

    @close_unusable_db_connections()
    def pop_data(self, key):
        try:
            res = self.values.get(key=key)
        except self.keystore_model.DoesNotExist:
            return EmptyData
        else:
            if res is not None:
                data = to_bytes(res.value)
                res.delete()

                return data

    @close_unusable_db_connections()
    def has_data_for_key(self, key):
        return self.peek_data(key) != EmptyData

    @close_unusable_db_connections()
    def put_if_empty(self, key, value):
        if not self.has_data_for_key(key):
            self.put_data(key, value)
            return True
        return False

    @close_unusable_db_connections()
    def result_store_size(self):
        return self.values.count()

    @close_unusable_db_connections()
    def result_items(self):
        return dict((i.key, to_bytes(i.value)) for i in self.values)

    @close_unusable_db_connections()
    def flush_results(self):
        self.values.delete()


class DjangoORMHuey(Huey):
    storage_class = DjangoORMStorage
