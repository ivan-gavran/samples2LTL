import uuid

from django.db import models

class Task(models.Model):
    # A model to save information about an asynchronous task
    created_on = models.DateTimeField(auto_now_add=True)
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, default='waiting')
    data = models.TextField(default='')
    result = models.TextField(blank=True, null=True)