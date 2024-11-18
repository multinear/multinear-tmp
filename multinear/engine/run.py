import importlib.util
from pathlib import Path
from typing import Dict, Any
import yaml
import random

from .storage import TaskModel, TaskStatus


def run_experiment(project_config: Dict[str, Any], job_id: str):
    """
    Run an experiment using the task_runner.run_task function from the project folder
    
    Args:
        project_config: Project configuration dictionary containing folder path
        job_id: ID of the job being run
    
    Yields:
        Dict containing status updates, final results, and status map
    """
    # Get the project folder path
    project_folder = Path(project_config["folder"])
    
    # Load config.yaml from project folder
    config_path = project_folder / ".multinear" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Construct path to task_runner.py
    task_runner_path = project_folder / ".multinear" / "task_runner.py"
    
    if not task_runner_path.exists():
        raise FileNotFoundError(f"Task runner file not found at {task_runner_path}")
    
    # Dynamically load the task runner module
    spec = importlib.util.spec_from_file_location("task_runner", task_runner_path)
    task_runner_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(task_runner_module)
    
    # Check if run_task exists in the module
    if not hasattr(task_runner_module, "run_task"):
        raise AttributeError(f"run_task function not found in {task_runner_path}")
    
    # Run the experiment
    try:
        results = []
        total_tasks = len(config["tasks"])
        
        yield {"status": TaskStatus.STARTING, "total": total_tasks}
        
        for i, task in enumerate(config["tasks"]):
            current_task = i + 1
            
            # Start new task
            task_id = TaskModel.start(
                job_id=job_id,
                task_number=current_task
            )
            
            yield {
                "status": TaskStatus.RUNNING,
                "current": current_task,
                "total": total_tasks,
                "details": f"Running task {current_task}/{total_tasks}"
            }
            
            try:
                fail_simulate = config.get("meta", {}).get("fail_simulate", None)
                if fail_simulate is not None and random.random() < fail_simulate:
                    raise Exception("Simulated failure")

                result = task_runner_module.run_task(**task)
                results.append(result)
                TaskModel.complete(task_id, result=result)
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Error running task {current_task}/{total_tasks}: {error_msg}")
                results.append({"error": error_msg})
                TaskModel.fail(task_id, error=error_msg)
        
        yield {
            "status": TaskStatus.COMPLETED,
            "current": total_tasks,
            "total": total_tasks,
            "results": results
        }

    except Exception as e:
        print(f"Error running experiment: {e}")
        yield {
            "status": TaskStatus.FAILED,
            "total": total_tasks,
            "error": str(e)
        }
