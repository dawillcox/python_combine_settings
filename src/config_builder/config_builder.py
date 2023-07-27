import yaml
import json
import collections
import platformdirs
from os import path, environ
from typing import Union, List
import copy


class LoadConfigException(Exception):
    pass


LEGAL_EXTS: set = set(['yml', 'yaml', 'json'])


def load_config(config_name: str,
                application: str = None,
                base_config: Union[dict, str] = None,
                overrides: str = None,
                ) -> dict:
    """
    Load a configuration by merging multiple files.

    :param config_name: Name of each configuration file to load.
    :param application: (optional) Application name to use with platformdirs
    :param base_config: (optional) Default configuration to start with.
                        This can be either the full path to a config file,
                        or a dict with the actual configuration.
    :param overrides: (optional) Full path to a file (ignoring config_name) of a file with overrides.
    :return: Mapping with the assembled settings.
    """
    # Load global configurations (service type, SMTP url and port, etc)
    files = []
    if not config_name:
        raise LoadConfigException('config_name required')
    # parts = config_name.split('.')
    ext = config_name.split('.')[-1]
    if ext not in LEGAL_EXTS:
        raise LoadConfigException('Only yaml or json files supported')
    conf = {}
    if base_config:
        if isinstance(base_config, dict):
            conf = copy.deepcopy(base_config)
            base_config = None
        elif not isinstance(base_config, str):
            raise LoadConfigException('base_config must be str or dict')

    files = _build_file_list(config_name,
                             application=application,
                             base_config=base_config,
                             overrides=overrides)

    # site_dirs = platformdirs.site_config_dir(application, multipath=True)
    # files += [path.join(d, config_name) for d in site_dirs.split(':')]
    # files += [path.join(platformdirs.user_config_dir(application), config_name)]
    #
    # venv = environ.get('VIRTUAL_ENV')
    # if venv:
    #     if application:
    #         files += [path.join(venv, 'config', application, config_name)]
    #     else:
    #         files += [path.join(venv, 'config', config_name)]
    #
    # if overrides:
    #     files += [overrides]

    for file in files:
        if path.exists(file):
            with open(file, 'r') as f:
                filename = path.split(file)[1]
                ext = filename.split('.')[-1]
                if ext == 'json':
                    newconf = json.load(f)
                else:
                    newconf = yaml.safe_load(f)
                _merge_dict(conf, newconf)
    return conf


def _merge_dict(d1: collections.abc.Mapping, d2: collections.abc.Mapping) -> None:
    """
    Modify d1 in place from d2. If an entry in d1 and the corresponding entry in d2 are
    both mappings, merge the two in place. Otherwise, any entry in d2 replaces any existing
    value in d1.
    :param d1: Mapping to be updated
    :param d2: Mapping to update
    :return: The modified d1
    """
    for k, v2 in d2.items():
        v1 = d1.get(k)  # returns None if v1 has no value for this key
        if isinstance(v1, collections.abc.Mapping) and isinstance(v2, collections.abc.Mapping):
            _merge_dict(v1, v2)
        else:
            d1[k] = v2

    return d1


def _build_file_list(config_name: str,
                     application: str = None,
                     base_config: Union[dict, str] = None,
                     overrides: str = None,
                     ) -> List[str]:
    """
    Build list of files to load config from. (This is a separate function to facilitate unit tests.)
    :param config_name:
    :param application:
    :param base_config:
    :param overrides:
    :return:
    """
    files = []
    if isinstance(base_config, str):
        files += [base_config]

    site_dirs = platformdirs.site_config_dir(application, multipath=True)
    files += [path.join(d, config_name) for d in site_dirs.split(':')]
    files += [path.join(platformdirs.user_config_dir(application), config_name)]

    venv = environ.get('VIRTUAL_ENV')
    if venv:
        if application:
            files += [path.join(venv, 'config', application, config_name)]
        else:
            files += [path.join(venv, 'config', config_name)]

    if overrides:
        files += [overrides]

    return files