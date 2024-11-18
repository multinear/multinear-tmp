import importlib.util
from pathlib import Path
from typing import Dict, Any
import yaml
import random


class ExperimentStatus:
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


def run_experiment(project_config: Dict[str, Any]):
    """
    Run an experiment using the engine.run_single function from the project folder
    
    Args:
        project_config: Project configuration dictionary containing folder path
    
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
    
    # Check if run_single exists in the module
    if not hasattr(task_runner_module, "run_single"):
        raise AttributeError(f"run_single function not found in {task_runner_path}")
    
    # Run the experiment
    try:
        results = []
        task_status_map = {}  # Track status of each task
        total_tasks = len(config["tasks"])
        
        yield {"status": ExperimentStatus.STARTING, "total": total_tasks}
        
        for i, task in enumerate(config["tasks"]):
            task_id = task.get("id", f"task_{i}")
            task_status_map[task_id] = ExperimentStatus.RUNNING
            current_task = i + 1
            
            yield {
                "status": ExperimentStatus.RUNNING,
                "current": current_task,
                "total": total_tasks,
                "details": f"Running task {current_task}/{total_tasks}",
                "status_map": task_status_map
            }
            
            try:
                fail_simulate = config.get("meta", {}).get("fail_simulate", None)
                if fail_simulate is not None and random.random() < fail_simulate:
                    raise Exception("Simulated failure")

                result = task_runner_module.run_single(**task)
                results.append(result)
                task_status_map[task_id] = ExperimentStatus.COMPLETED
            except Exception as e:
                print(f"Error running task {current_task}/{total_tasks}: {e}")
                results.append({"error": str(e)})
                task_status_map[task_id] = ExperimentStatus.FAILED
        
        yield {
            "status": ExperimentStatus.COMPLETED,
            "current": total_tasks,
            "total": total_tasks,
            "results": results,
            "status_map": task_status_map
        }

    except Exception as e:
        print(f"Error running experiment: {e}")
        # Update status map for any remaining tasks
        for i, task in enumerate(config["tasks"]):
            task_id = task.get("id", f"task_{i}")
            if task_id not in task_status_map:
                task_status_map[task_id] = ExperimentStatus.FAILED

        yield {
            "status": ExperimentStatus.FAILED,
            "total": total_tasks,
            "error": str(e),
            "status_map": task_status_map
        }
