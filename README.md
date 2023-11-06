# COMBINE_SETTINGS
Build configuration settings from a hierarchy of files.

`combine_settings` constructs a configuration for an application, combining settings from a list of
configuration files. Files are read in order from most generic to most specific,
with each found configuration updating settings from the previous files. Settings can be system-wide,
user-specific (possibly read-only to the user),
and specific to a virtual environment.
An application can also specify default settings, and overrides that replace anything
loaded from the configurations.

Yes, there are other packages that let an application load a configuration.
I needed something that flexibly merges application configurations from multiple
sources: application or library defaults, system-wide, and user and environment specific.

## Operation
### Determining Configurations to Combine
`combine_settings` uses [`platformdirs`](https://pypi.org/project/platformdirs/)
to find the OS-specific location of configuration files for an application.
Existing configuration files are loaded in order. Settings from each extend or
replace settings found in previous files.

Settings are loaded in the following order, where `application` is the name
(if any) supplied by the caller. Except where otherwise noted, the file
name in each directory is from the `config_name` parameter:

* If the `base_config` parameter is a dict, use the configuration it specifies.
* If, instead, `base_config` is a string, the file it points to. (This is an explicit path to the file.)
* One or more files in system-wide application configuration directories as determined by `platformdirs.site_config_dir(application, multipath=True`).
* A file in the user-specific application configuration file as determined by `platformdirs.user_config_dir(application)`.
* If running in a virtual environment, a file in the `$VIRTUAL_ENV/config/application` directory.
* Finally, settings given by the `overrides` parameter, either a file explicitly mentioned or explicit dict.

Note that the first two items allow the application to specify application-specific
defaults. The virtual environment case supports settings specific to a virtual
environment, perhaps for testing. And the last allows for special-case overrides.

### Merging Configurations
As each configuration file or explicit dict is loaded, its content is used to recursively update
settings in the previously assembled configuration.

When a `latest` set of settings is loaded, it is used to update the `previous`
dict of settings from previous sources. The update works as follows:

For each `key` in `latest.keys()`:
* If `prev[key]` and `latest[key]` are both dicts, then recursively update `prev[key]` from `latest[key]`.
* Otherwise, set `prev[key]` to `latest[key]`, even if `latest[key]` is None.

## Usage
```python3.7
from combine_settings import load_config

config = load_config(config_name: str,
                     application: Optional[str] = '',
                     base_config: Optional[Union[dict, str]] = None,
                     overrides: Optional[Union[dict, str]] = None,
                     ) -> dict
```
Where:
* `config_name` is the name of the configuration file to
look for in each directory. The file name extension must be either .yml, .yaml, or .json.
(YAML and json formats are supported.)
* `base_config` specifies a default configuration for the application. 
It can be either the absolute path to a configuration file to load or a dict with the default configuration.
* `application` is an application name to use with `platformdirs`.
* `overrides` specifies explicit settings that update whatever was loaded
using the standard process. It can either be the full path to a file
to load or a dict with settings.
This can be useful for, for example, testing.

As a potential aid for user configuration, you can get the list of files
that will be searched on your particular installation.

```python3.7
paths = config_file_list(config_name: str,
                        application: Optional[str] = '',
                        base_config: Optional[str] = None,
                        overrides: Optional[str] = None,
                        ) -> List[str]
```
The parameters are the same as for `load_config()`, except `overerides`
and `base_config` are ignored if they aren't strings. The return is
a list of full paths to files that will be searched, in the order of search.
## Testing
```bash
pip install coverage platformdirs pyYAML
coverage run -m unittest
coverage report -m
```
## Build
```bash
pip install build
python -m build
```
