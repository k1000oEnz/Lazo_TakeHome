import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import init_db

if __name__ == "__main__":
    init_db()
    print("Tables created")
