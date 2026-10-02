"""Load a V3 numerical object without changing the legacy configuration parser."""

from copy import deepcopy
import importlib
import importlib.util
from pathlib import Path


def parse_object_config(configuration):
    """Support installed modules and the original explicit filepath contract."""
    config = deepcopy(configuration)
    if ("module" in config) == ("filepath" in config):
        raise ValueError("object config requires exactly one of module or filepath")
    name = config.pop("object_name")
    if "module" in config:
        module = importlib.import_module(config.pop("module"))
    else:
        path = Path(config.pop("filepath")).expanduser()
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot import configured object file: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return getattr(module, name)(**config)
