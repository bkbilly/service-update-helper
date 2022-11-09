from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

modules = {}
required_methods = [
    'install',
    'service',
    'get_current_version',
    'get_latest_version',
]

# iterate through the modules in the current package
package_dir = str(Path(__file__).resolve().parent)
for (_, module_name, _) in iter_modules([package_dir]):
    updater = getattr(import_module(f"{__name__}.{module_name}"), 'Updater')
    updater.name = module_name
    meets_requirements = all(item in dir(updater) for item in required_methods)
    if not meets_requirements:
        raise Exception(f"{module_name} does not meet the requirements. Required methods: {','.join(required_methods)}")
    modules[module_name] = updater
