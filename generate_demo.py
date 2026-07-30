import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.managers.demo_manager import DemoProjectManager

if __name__ == "__main__":
    path = DemoProjectManager.generate_demo_project()
    print(f"demo_project.zanime generated at {path}")

