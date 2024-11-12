import argparse
from .core import greet

def main():
    parser = argparse.ArgumentParser(description="Greet someone.")
    parser.add_argument('name', type=str, help='Name of the person to greet')
    
    args = parser.parse_args()
    print(greet(args.name))

if __name__ == '__main__':
    main()
