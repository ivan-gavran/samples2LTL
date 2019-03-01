from rq.timeouts import JobTimeoutException

from .models import Task

def job_exception_handler(job, *exc_info):

    # Get task
    task = job.args[0]

    # Time out exception
    if exc_info[0] is JobTimeoutException:
        task.status = "timeout"

    # Unknown exception
    else:
        task.status = "error"
        task.result = "An unknown error occurred during the execution. Please try again later."

    # Save task
    task.save()

    return True