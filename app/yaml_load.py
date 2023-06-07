
from typing import Dict
import yaml

def load_yaml(file_path: str) -> Dict:
    """ Load a yaml file into memory """
    return yaml.safe_load(open(file_path, encoding='utf-8'))
