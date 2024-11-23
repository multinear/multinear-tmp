import argparse
import uvicorn
import pathlib
from pathlib import Path
from jinja2 import Template
import re
import tqdm
from rich.console import Console
from rich.table import Table
from datetime import datetime, timezone
from typing import Optional

from .engine.run import run_experiment
from .engine.storage import init_project_db, JobModel, ProjectModel, TaskModel, TaskStatus


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

def format_duration(created_at: str, finished_at: str | None) -> str:
    """Format duration between created_at and finished_at timestamps."""
    if not finished_at:
        return "-"
    
    start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    end = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
    duration = end - start
    
    minutes = duration.seconds // 60
    seconds = duration.seconds % 60
    
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"

def get_score_color(score: float) -> str:
    """Get color for score based on value."""
    if score >= 0.9:
        return "green"
    elif score >= 0.7:
        return "yellow"
    return "red"

def show_recent_runs():
    """
    Show recent experiment runs in a formatted table.
    """
    if not is_project_initialized():
        return

    # Initialize database and get project
    project_id = init_project_db()
    project = ProjectModel.find(project_id)
    
    # Get recent jobs
    jobs = JobModel.list_recent(project_id, limit=10)
    
    # Create and configure the table
    console = Console()
    table = Table(
        title=f"Recent Experiments for {project.name}",
        show_header=True,
        header_style="bold cyan"
    )
    
    # Add columns
    table.add_column("Run ID", style="dim")
    table.add_column("Date & Time")
    table.add_column("Duration")
    # table.add_column("Code Revision")
    table.add_column("Model Version")
    table.add_column("Total Tests", justify="right")
    table.add_column("Score", justify="center")
    table.add_column("Results")
    
    # Add rows
    for job in jobs:
        details = job.details or {}
        status_map = details.get("status_map", {})
        
        # Calculate statistics
        total = len(status_map)
        passed = sum(1 for status in status_map.values() if status == TaskStatus.COMPLETED)
        failed = sum(1 for status in status_map.values() if status == TaskStatus.FAILED)
        regression = total - passed - failed
        score = (passed / total) if total > 0 else 0

        # Get model info
        model = job.get_model_summary()
        
        # Format results bar using unicode blocks
        if total > 0:
            bar_length = 20
            # Calculate exact number of blocks, keeping fractional parts
            pass_ratio = passed / total
            fail_ratio = failed / total
            regr_ratio = regression / total
            
            # Calculate blocks
            pass_blocks = int(pass_ratio * bar_length)
            fail_blocks = int(fail_ratio * bar_length)
            regr_blocks = int(regr_ratio * bar_length)
            
            # Calculate remainder and add it to the last non-zero category
            remainder = bar_length - (pass_blocks + fail_blocks + regr_blocks)
            if remainder > 0:
                if regression > 0:
                    regr_blocks += remainder
                elif failed > 0:
                    fail_blocks += remainder
                else:
                    pass_blocks += remainder
            
            results_bar = (
                f"[green]{'█' * pass_blocks}[/green]"
                f"[red]{'█' * fail_blocks}[/red]"
                f"[yellow]{'█' * regr_blocks}[/yellow]"
            )
        else:
            results_bar = ""
        
        # Add row to table
        table.add_row(
            job.id[-8:],  # Short ID
            job.created_at.strftime("%Y-%m-%d %H:%M"),
            format_duration(
                job.created_at.replace(tzinfo=timezone.utc).isoformat(),
                job.finished_at.replace(tzinfo=timezone.utc).isoformat() if job.finished_at else None
            ),
            # details.get("revision", ""),
            model,
            str(total),
            f"[{get_score_color(score)}]{score:.2f}[/]",
            results_bar
        )
    
    # Print the table
    console.print(table)
    
    # Print legend
    legend = Table.grid(padding=1)
    legend.add_column()
    legend.add_row("[green]█[/green] Pass", "[red]█[/red] Fail", "[yellow]█[/yellow] Regression")
    console.print("\nLegend:", legend)

def format_task_status(status: str) -> str:
    """Get colored status string."""
    if status == TaskStatus.COMPLETED:
        return f"[green]{status}[/green]"
    elif status == TaskStatus.FAILED:
        return f"[red]{status}[/red]"
    return f"[yellow]{status}[/yellow]"

def find_run_by_partial_id(partial_id: str) -> Optional[JobModel]:
    """
    Find a run by partial ID (last N characters).
    Returns the most recent matching run if multiple found.
    """
    if not is_project_initialized():
        return None

    project_id = init_project_db()
    
    # Get recent jobs and find one with matching partial ID
    jobs = JobModel.list_recent(project_id, limit=100)  # Increase limit to search more runs
    
    matching_jobs = [
        job for job in jobs 
        if job.id.endswith(partial_id) or job.id == partial_id
    ]
    
    if not matching_jobs:
        return None
        
    # Return the most recent matching job
    return matching_jobs[0]

def show_run_details(partial_id: str):
    """
    Show detailed information about a specific run.
    """
    # Find the run
    job = find_run_by_partial_id(partial_id)
    if not job:
        print(f"Error: No run found matching ID '{partial_id}'")
        return
    
    project = ProjectModel.find(job.project_id)
    tasks = TaskModel.list(job.id)
    
    console = Console()
    
    # Header
    console.print(f"\n[bold]Run: {job.id[-8:]} (Full ID: {job.id})[/bold]")
    console.print(f"Project: {project.name}")
    console.print(f"Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary Card
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    
    summary.add_row("Status", format_task_status(job.status))
    summary.add_row("Total Tasks", str(len(tasks)))
    summary.add_row("Model", job.details.get("model", "N/A") if job.details else "N/A")
    
    console.print("\n[bold]Summary[/bold]")
    console.print(summary)
    
    # Tasks Table
    tasks_table = Table(
        title="\nTasks",
        show_header=True,
        header_style="bold cyan"
    )
    
    tasks_table.add_column("Task ID", style="dim")
    tasks_table.add_column("Started")
    tasks_table.add_column("Duration")
    tasks_table.add_column("Model")
    tasks_table.add_column("Status")
    tasks_table.add_column("Score", justify="right")
    
    for task in tasks:
        # Format duration
        duration = format_duration(
            task.created_at.replace(tzinfo=timezone.utc).isoformat(),
            task.finished_at.replace(tzinfo=timezone.utc).isoformat() if task.finished_at else None
        )
        
        # Format score with color
        score = task.eval_score or 0
        score_color = get_score_color(score)
        score_text = f"[{score_color}]{score:.2f}[/]"
        
        tasks_table.add_row(
            task.id[-8:],
            task.created_at.strftime("%H:%M:%S"),
            duration,
            task.task_details.get("model", "N/A") if task.task_details else "N/A",
            format_task_status(task.status),
            score_text
        )
    
    console.print(tasks_table)
    
    # Detailed Task View
    for task in tasks:
        console.print(f"\n[bold cyan]Task Details: {task.id[-8:]}[/bold cyan]")
        
        # Task Information
        task_details = Table(show_header=False, box=None)
        task_details.add_column("Field", style="cyan")
        task_details.add_column("Value")
        
        task_details.add_row("Status", format_task_status(task.status))
        task_details.add_row("Created", task.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        if task.finished_at:
            task_details.add_row("Finished", task.finished_at.strftime("%Y-%m-%d %H:%M:%S"))
        task_details.add_row("Duration", format_duration(
            task.created_at.replace(tzinfo=timezone.utc).isoformat(),
            task.finished_at.replace(tzinfo=timezone.utc).isoformat() if task.finished_at else None
        ))
        
        console.print(task_details)
        
        # Input
        if task.task_input:
            console.print("\n[bold]Input:[/bold]")
            input_text = task.task_input['str'] if isinstance(task.task_input, dict) and 'str' in task.task_input else str(task.task_input)
            console.print(input_text)
        
        # Output
        if task.task_output:
            console.print("\n[bold]Output:[/bold]")
            output_text = task.task_output['str'] if isinstance(task.task_output, dict) and 'str' in task.task_output else str(task.task_output)
            console.print(output_text)
        
        # Evaluation Results
        if task.eval_details:
            console.print("\n[bold]Evaluation Results:[/bold]")
            eval_table = Table(show_header=True)
            eval_table.add_column("Criterion")
            eval_table.add_column("Score", justify="right")
            eval_table.add_column("Rationale")
            
            for eval in task.eval_details.get("evaluations", []):
                score = eval["score"]
                score_color = get_score_color(score)
                eval_table.add_row(
                    eval["criterion"],
                    f"[{score_color}]{score:.2f}[/]",
                    eval["rationale"]
                )
            
            console.print(eval_table)
        
        # console.print("\n" + "─" * 80)  # Separator between tasks

def main():
    parser = argparse.ArgumentParser(description="Multinear CLI tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Define the 'init' command
    init_cmd = subparsers.add_parser('init', help='Initialize a new Multinear project')

    # Define the 'run' command
    run_cmd = subparsers.add_parser('run', help='Run experiment and track progress')

    # Define the 'recent' command
    recent_cmd = subparsers.add_parser('recent', help='Show recent experiment runs')

    # Define the 'details' command
    details_cmd = subparsers.add_parser('details', help='Show detailed information about a specific run')
    details_cmd.add_argument('run_id', help='ID of the run to show')

    # Define the 'web' and 'web_dev' commands
    web_cmd = subparsers.add_parser('web', help='Start platform web server')
    web_dev_cmd = subparsers.add_parser('web_dev', help='Start development web server with auto-reload')
    for cmd in [web_cmd, web_dev_cmd]:
        cmd.add_argument('--port', type=int, default=8000, help='Port to run the server on')
        cmd.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')

    args = parser.parse_args()
    
    if args.command == 'init':
        init_project()
    elif args.command == 'run':
        if not is_project_initialized(): return
        run_experiment_command()
    elif args.command == 'recent':
        show_recent_runs()
    elif args.command == 'details':
        show_run_details(args.run_id)
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
