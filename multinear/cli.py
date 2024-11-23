import argparse
import uvicorn
import pathlib
from pathlib import Path
from jinja2 import Template
import re
import tqdm
from rich.console import Console
from rich.table import Table
import yaml

from .engine.run import run_experiment
from .engine.storage import init_project_db, JobModel, ProjectModel, TaskModel


MULTINEAR_CONFIG_DIR = '.multinear'

def init_project():
    def slugify(text):
        # Convert text to a slug suitable for URLs or identifiers
        # Remove special characters, replace spaces/hyphens, convert to lowercase
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[-\s]+', '-', text).strip().lower()

    # Check if the project has already been initialized
    multinear_dir = Path(MULTINEAR_CONFIG_DIR)
    if multinear_dir.exists():
        print(f"{MULTINEAR_CONFIG_DIR} directory already exists. Project appears to be already initialized.")
        return
        
    # Create the .multinear directory for project configuration
    multinear_dir.mkdir()
    
    # Prompt the user for project details
    project_name = input("Project name: ").strip()
    default_id = slugify(project_name)
    project_id = input(f"Project ID [{default_id}]: ").strip() or default_id
    description = input("Project description: ").strip()
    
    # Read the configuration template
    template_path = Path(__file__).parent / 'templates' / 'config.yaml'
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Render the template with user-provided details
    template = Template(template_content)
    config_content = template.render(
        project_name=project_name,
        project_id=project_id,
        description=description
    )
    
    # Write the rendered configuration to config.yaml
    config_path = multinear_dir / 'config.yaml'
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"\nProject initialized successfully in {multinear_dir}")
    print("You can now run 'multinear web' to start the server")

def run_experiment_command():
    """
    CLI command to execute run_experiment with progress tracking and summaries.
    """
    # Initialize the configuration and database
    project_id = init_project_db()
    job_id = JobModel.start(project_id)
    job = JobModel.find(job_id)
    
    # Initialize Rich consoles
    console = Console()
    console_plain = Console(no_color=True, force_terminal=False, width=120)
    
    # Execute the experiment with progress tracking
    results = []
    project = ProjectModel.find(project_id)
    pbar = None
    
    try:
        for update in run_experiment(project.to_dict(), job_id):
            results.append(update)
            
            # Add status map from TaskModel to the update
            update["status_map"] = TaskModel.get_status_map(job_id)
            
            # Update job status in the database
            job.update(
                status=update["status"],
                total_tasks=update.get("total", 0),
                current_task=update.get("current"),
                details=update
            )
            
            # Initialize progress bar when we get total tasks
            if pbar is None and update.get("total") is not None:
                pbar = tqdm.tqdm(total=update["total"], desc="Running Experiment")
            
            # Update progress bar if initialized
            if pbar is not None and update.get("current") is not None:
                pbar.n = update["current"]
                pbar.refresh()
            
            # Update Rich console with status
            table = Table(title="Experiment Status")
            table.add_column("Status", justify="left", style="cyan", no_wrap=True)
            table.add_column("Details", style="magenta")
            
            table.add_row(update["status"], update.get("details", ""))
            console.clear()
            console.print(table)
        
        # Mark the job as finished upon successful completion
        job.finish()
        
    except Exception as e:
        # Handle exceptions and update the job as failed
        print(f"Error running experiment: {e}")
        job.update(
            status="failed",
            details={
                "error": str(e),
                "status_map": TaskModel.get_status_map(job_id)
            }
        )
    finally:
        # Close progress bar if it was initialized
        if pbar is not None:
            pbar.close()
    
    # Generate summary
    summary_table = Table(title="Experiment Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta")
    
    summary_table.add_row("Job ID", job_id)
    summary_table.add_row("Final Status", results[-1]["status"])
    summary_table.add_row("Total Tasks", str(results[-1].get("total", 0)))
    summary_table.add_row("Completed Tasks", str(results[-1].get("current", 0)))
    
    console.print(summary_table)
    
    # Write summary to .multinear/last_output.txt using capture
    with console_plain.capture() as capture:
        console_plain.print(summary_table)
    plain_output = capture.get()
    
    with open(Path(MULTINEAR_CONFIG_DIR) / "last_output.txt", "w") as f:
        f.write(plain_output)

def is_project_initialized():
    """
    Check if the project has been initialized (has .multinear directory).
    Exits with error message if not initialized.

    Returns:
        bool: True if initialized, False otherwise
    """
    if not Path(MULTINEAR_CONFIG_DIR).exists():
        print(f"Error: {MULTINEAR_CONFIG_DIR} directory not found. Please run 'multinear init' first.")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Multinear CLI tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Define the 'init' command
    init_cmd = subparsers.add_parser('init', help='Initialize a new Multinear project')

    # Define the 'run' command
    run_cmd = subparsers.add_parser('run_experiment', help='Run experiment and track progress')

    # Define the 'web' and 'web_dev' commands
    web_cmd = subparsers.add_parser('web', help='Start platform web server')
    web_dev_cmd = subparsers.add_parser('web_dev', help='Start development web server with auto-reload')
    for cmd in [web_cmd, web_dev_cmd]:
        cmd.add_argument('--port', type=int, default=8000, help='Port to run the server on')
        cmd.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')

    args = parser.parse_args()
    
    if args.command == 'init':
        init_project()
    elif args.command == 'run_experiment':
        if not is_project_initialized(): return
        run_experiment_command()
    elif args.command in ['web', 'web_dev']:
        if not is_project_initialized(): return
        
        uvicorn_config = {
            "app": "multinear.main:app",
            "host": args.host,
            "port": args.port,
        }
        
        if args.command == 'web_dev':
            # Add project directories to watch list for auto-reload
            current_dir = pathlib.Path(__file__).parent
            parent_dir = str(current_dir.parent)
            cwd = str(pathlib.Path.cwd())
            uvicorn_config.update({
                "reload": True,
                "reload_dirs": [parent_dir, cwd],
                "reload_includes": ["*.py", "*.yaml"]
            })
        
        # Run the Uvicorn server with the specified configuration
        uvicorn.run(**uvicorn_config)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
