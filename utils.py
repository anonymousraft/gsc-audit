import yaml
from pathlib import Path
from rich.logging import RichHandler
import logging

def load_config(path: str = 'config.yaml') -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    return yaml.safe_load(p.read_text())


def init_logger(log_file: str = None, level: str = 'INFO'):
    handlers = [RichHandler(rich_tracebacks=True)]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
    return logging.getLogger('GSC_Audit')