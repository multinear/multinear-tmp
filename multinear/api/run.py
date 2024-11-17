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
    config_path = project_folder / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
        
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Construct path to engine.py
    engine_path = project_folder / "engine.py"
    
    if not engine_path.exists():
        raise FileNotFoundError(f"Engine file not found at {engine_path}")
    
    # Dynamically load the engine module
    spec = importlib.util.spec_from_file_location("engine", engine_path)
    engine_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_module)
    
    # Check if run_single exists in the module
    if not hasattr(engine_module, "run_single"):
        raise AttributeError(f"run_single function not found in {engine_path}")
    
    # Run the experiment
    try:
        results = []
        task_status_map = {}  # Track status of each evaluation
        total_tasks = len(config["evals"])
        
        yield {"status": ExperimentStatus.STARTING, "total": total_tasks}
        
        for i, test in enumerate(config["evals"]):
            eval_id = test.get("id", f"eval_{i}")
            task_status_map[eval_id] = ExperimentStatus.RUNNING
            current_task = i + 1
            
            yield {
                "status": ExperimentStatus.RUNNING,
                "current": current_task,
                "total": total_tasks,
                "details": f"Running eval {current_task}/{total_tasks}",
                "status_map": task_status_map
            }
            
            try:
                fail_simulate = config.get("meta", {}).get("fail_simulate", None)
                if fail_simulate is not None and random.random() < fail_simulate:
                    raise Exception("Simulated failure")

                result = engine_module.run_single(**test)
                results.append(result)
                task_status_map[eval_id] = ExperimentStatus.COMPLETED
            except Exception as e:
                results.append({"error": str(e)})
                task_status_map[eval_id] = ExperimentStatus.FAILED
        
        yield {
            "status": ExperimentStatus.COMPLETED,
            "current": total_tasks,
            "total": total_tasks,
            "results": results,
            "status_map": task_status_map
        }

    except Exception as e:
        # Update status map for any remaining evals
        for i, test in enumerate(config["evals"]):
            eval_id = test.get("id", f"eval_{i}")
            if eval_id not in task_status_map:
                task_status_map[eval_id] = ExperimentStatus.FAILED

        yield {
            "status": ExperimentStatus.FAILED,
            "total": total_tasks,
            "error": str(e),
            "status_map": task_status_map
        }
