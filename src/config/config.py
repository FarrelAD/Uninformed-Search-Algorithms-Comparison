from jinja2 import Environment, FileSystemLoader
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
IMG_DIR = Path(__file__).parent.parent.parent / "img"
MAPS_DIR = Path(__file__).parent.parent.parent / "maps"

JINJA_ENV = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "templates"))
