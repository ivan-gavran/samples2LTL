from django_rq import job
from rq import get_current_job

from .models import Task

# Just for testing
import time


def learn_formula(task):
    # This creates a Task instance to save the job instance and job result
    
    # Get job
    job = get_current_job()

    task.status = "working"
    task.save()

    # Perform task
    time.sleep (1)

    # Compute result
    result = task.data

    # Save task and mark it finished
    task.result = result
    task.status = 'finished'
    task.save()

    return
