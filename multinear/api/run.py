import importlib.util
from pathlib import Path
from typing import Dict, Any
import yaml
from enum import Enum

class ExperimentStatus(Enum):
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
        Dict containing status updates and final results
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
        total_evals = len(config["evals"])
        
        yield {"status": ExperimentStatus.STARTING, "total": total_evals}
        
        for i, test in enumerate(config["evals"]):
            yield {
                "status": ExperimentStatus.RUNNING,
                "current": i + 1,
                "total": total_evals,
                "details": f"Running eval {i+1}/{total_evals}"
            }
            results.append(engine_module.run_single(**test))
        
        yield {
            "status": ExperimentStatus.COMPLETED,
            "current": total_evals,
            "total": total_evals,
            "results": results
        }

    except Exception as e:
        yield {
            "status": ExperimentStatus.FAILED,
            "total": total_evals,
            "error": str(e)
        }
