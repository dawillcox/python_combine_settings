import yaml
import json
import platformdirs
from os import path, environ
from typing import Union, List, Optional, Mapping
import copy


class LoadConfigException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


LEGAL_EXTS: set = set(['yml', 'yaml', 'json'])


def load_config(config_name: str,
                application: str = '',
                base_config: Optional[Union[Mapping, str]] = None,
                overrides: Optional[Union[Mapping, str]] = None,
                ) -> Mapping:
    """
    Load a configuration by merging multiple files.

    :param config_name: Name of each configuration file to load. (mandatory)
    :param application: Application name to use with platformdirs
    :param base_config: Default configuration to start with.
                        This can be either the full path to a config file
                        or a dict with the actual configuration.
    :param overrides:   Full path to a file (ignoring config_name) of a file
                        with overrides or a dict with the actual override settings.
    :return: Mapping with the assembled settings.
    """

    if not config_name:
        raise LoadConfigException('config_name required')
    ext = config_name.split('.')[-1]
    if ext not in LEGAL_EXTS:
        raise LoadConfigException('Only yaml or json files supported')
    conf = {}
    if base_config:
        if isinstance(base_config, Mapping):
            conf = copy.deepcopy(base_config)
            base_config = None
        elif not isinstance(base_config, str):
            raise LoadConfigException('base_config must be str or dict')

    if isinstance(overrides, Mapping):
        final_overrides = copy.deepcopy(overrides)
        overrides = None
    else:
        final_overrides = {}

    files = config_file_list(config_name,
                             application=application,
                             base_config=base_config,
                             overrides=overrides)

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

    _merge_dict(conf, final_overrides)

    return conf


def _merge_dict(d1: Mapping, d2: Mapping) -> None:
    """
    Modify d1 in place from d2. If an entry in d1 and the corresponding entry in d2 are
    both mappings, merge the two in place. Otherwise, any entry in d2 replaces any
    existing value in d1. Note that d1 is updated in place, so the original content is
    lost.
    :param d1: Mapping to be updated
    :param d2: Mapping to update
    :return: The modified d1
    """
    for k, v2 in d2.items():
        v1 = d1.get(k)  # returns None if v1 has no value for this key
        if isinstance(v1, Mapping) and isinstance(v2, Mapping):
            _merge_dict(v1, v2)
        else:
            d1[k] = v2

    return d1


def config_file_list(config_name: str,
                     application: str = '',
                     base_config: Optional[Union[Mapping,  str]] = None,
                     overrides: Optional[Union[Mapping,  str]] = None,
                     ) -> List[str]:
    """
    Return list of files that will be loaded
    :param config_name: Name of configuration files
    :param application: Calling application, if appropriate
    :param base_config: Optional base configuration file
    :param overrides: Optional final override file
    :return: List of files in order searched
    """
    files = []
    if isinstance(base_config, str):
        files.append(base_config)

    site_dirs = platformdirs.site_config_dir(application, multipath=True)
    files.extend([path.join(d, config_name) for d in site_dirs.split(':')])
    files.append(path.join(platformdirs.user_config_dir(application), config_name))

    venv = environ.get('VIRTUAL_ENV')
    if venv:
        files.append(path.join(venv, 'config', application, config_name))

    if isinstance(overrides, str):
        files.append(overrides)

    return files
