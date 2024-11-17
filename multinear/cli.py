import argparse
from .core import greet
import uvicorn

from .api.main import app


def main():
    parser = argparse.ArgumentParser(description="Multinear CLI tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Greet command
    greet_cmd = subparsers.add_parser('greet', help='Greet someone')
    greet_cmd.add_argument('name', type=str, help='Name of the person to greet')

    # Web commands
    web_cmd = subparsers.add_parser('web', help='Start production web server')
    web_dev_cmd = subparsers.add_parser('web_dev', help='Start development web server with auto-reload')
    for cmd in [web_cmd, web_dev_cmd]:
        cmd.add_argument('--port', type=int, default=8000, help='Port to run the server on')
        cmd.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')

    args = parser.parse_args()
    
    if args.command == 'greet':
        print(greet(args.name))
    elif args.command in ['web', 'web_dev']:
        uvicorn.run(
            "multinear.api.main:app",
            host=args.host,
            port=args.port,
            reload=(args.command == 'web_dev')
        )
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
