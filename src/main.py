import sys
import os

# Add the project root directory to Python's search path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import sys
import os

# Add the project root directory to Python's search path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.game.engine import GameEngine

def main():
    game = GameEngine()
    game.run()

if __name__ == "__main__":
    main()
