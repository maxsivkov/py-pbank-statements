import os, re
from typing import List
from decimal import Decimal
from confuse import Configuration
def list_files(folder:str, pattern:str = None):
    fn = lambda f: os.path.join(folder, f)
    return [fn(f) for f in os.listdir(folder)] if pattern is None else [fn(f) for f in os.listdir(folder) if re.match(pattern, f)]

def to_decimal(o):
    if isinstance(o, str):
        return Decimal(o.replace(',', '.', 1))
    return o

def get_config(c:Configuration, name:str, f, default:str = None):
    names:List[str] = name.split('.')
    subc = c
    for i, n in enumerate(names):
        if n not in subc.keys(): return default
        if i == len(names) - 1: return f(subc[n]) if n in subc.keys() else default
        subc = subc[n]

    return default

def get_config_str(c:Configuration, name:str, default:str = None) -> str: return get_config(c, name, lambda v : v.as_str(), default)
def get_config_int(c:Configuration, name:str, default:str = None) -> int: return get_config(c, name, lambda v : v.as_number(), default)
