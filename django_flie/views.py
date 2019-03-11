from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site


import django_rq

from .models import Task
from .tasks import learn_formula

def index(request):
    return render(request, 'django_flie/index.html')

def syntax(request):
    return render(request, 'django_flie/syntax.html')

def learn(request):
    # Get input data
    #pdb.set_trace()
    data = request.GET.get('input', None)
    baseUrl = get_current_site(request)


    # Get default queue
    queue = django_rq.get_queue('default') #, is_async=False)

    # Create task (only with data)
    task = Task.objects.create(
        data = data,
    )
    #task.save()

    # Create and queue job
    job = queue.enqueue(learn_formula, args=[task, baseUrl], timeout=60)

    # Generate response
    json_response = {
        'task_id': task.task_id,
    }

    return JsonResponse(json_response)

def result(request):
    # Get job ID
    job_id = request.GET.get('task_id', None)

    # Query task in database
    tasks = Task.objects.filter(task_id=job_id)
    print(tasks)

    # Task has already started executing or is finished
    if len(tasks) == 1:
      json_response = {
        'status' : tasks[0].status,
        'result': tasks[0].result,
      }
      return JsonResponse(json_response)

    # Task does not exist or is queued
    else:
      json_response = {
        'status' : 'unknown',
        'result': None,
      }

      return JsonResponse(json_response)
