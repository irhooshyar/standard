import os
from pathlib import Path

from abdal import config


def apply(path):
    path = Path(config.BASE_PATH, path)
    if not os.path.exists(path):
        os.makedirs(path)