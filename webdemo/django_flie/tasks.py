from rq import get_current_job

from utils.Traces import ExperimentTraces
from webdemo.mysite.backend.solverRuns import run_solver

# Just for testing


def learn_formula(task):
    # This creates a Task instance to save the job instance and job result
    
    # Get job
    job = get_current_job()

    task.status = "working"
    task.save()

    # Perform task
    #time.sleep (1)
    try:
        # Compute result

        traces = ExperimentTraces
        traces.readTracesFromString(task.data)

        [formulas, timePassed] = run_solver(5, traces)


        # Save task and mark it finished
        task.result = str(formulas)
        task.status = 'finished'
        task.save()
    except:
        task.result = "sth went wrong"
        task.status = 'error'
        task.save()


    return
