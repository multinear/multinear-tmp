import argparse
import uvicorn
import pathlib
from pathlib import Path
from jinja2 import Template
import re


MULTINEAR_CONFIG_DIR = '.multinear'

def init_project():
    def slugify(text):
        # Remove special chars, replace spaces with hyphens, convert to lowercase
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[-\s]+', '-', text).strip().lower()

    # Check if .multinear already exists
    multinear_dir = Path(MULTINEAR_CONFIG_DIR)
    if multinear_dir.exists():
        print(f"{MULTINEAR_CONFIG_DIR} directory already exists. Project appears to be already initialized.")
        return
        
    # Create .multinear directory
    multinear_dir.mkdir()
    
    # Get project details from user
    project_name = input("Project name: ").strip()
    default_id = slugify(project_name)
    project_id = input(f"Project ID [{default_id}]: ").strip() or default_id
    description = input("Project description: ").strip()
    
    # Read template
    template_path = Path(__file__).parent / 'templates' / 'config.yaml'
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace template variables
    template = Template(template_content)
    config_content = template.render(
        project_name=project_name,
        project_id=project_id,
        description=description
    )
    
    # Write config file
    config_path = multinear_dir / 'config.yaml'
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"\nProject initialized successfully in {multinear_dir}")
    print("You can now run 'multinear web' to start the server")

def main():
    parser = argparse.ArgumentParser(description="Multinear CLI tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_cmd = subparsers.add_parser('init', help='Initialize a new Multinear project')

    # Web commands
    web_cmd = subparsers.add_parser('web', help='Start platform web server')
    web_dev_cmd = subparsers.add_parser('web_dev', help='Start development web server with auto-reload')
    for cmd in [web_cmd, web_dev_cmd]:
        cmd.add_argument('--port', type=int, default=8000, help='Port to run the server on')
        cmd.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')

    args = parser.parse_args()
    
    if args.command == 'init':
        init_project()
    elif args.command in ['web', 'web_dev']:
        # Check if .multinear directory exists
        if not Path(MULTINEAR_CONFIG_DIR).exists():
            print(f"Error: {MULTINEAR_CONFIG_DIR} directory not found. Please run 'multinear init' first.")
            return
        
        uvicorn_config = {
            "app": "multinear.main:app",
            "host": args.host,
            "port": args.port,
        }
        
        if args.command == 'web_dev':
            # Add Multinear directory and current working directory to watch list
            current_dir = pathlib.Path(__file__).parent
            parent_dir = str(current_dir.parent)
            cwd = str(pathlib.Path.cwd())
            uvicorn_config.update({
                "reload": True,
                "reload_dirs": [parent_dir, cwd],
                "reload_includes": ["*.py", "*.yaml"]
            })
        
        uvicorn.run(**uvicorn_config)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
