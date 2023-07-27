# CONFIG_BUILDER
`config_builder` constructs a configuration for an application by combining settings from a list of
configuration files. Files are read in order from most generic to most specific,
with each updating settings from the previous files.

Yes, there are other packages that let an application load a configuration.
I wanted something that merged application configurations from multiple
sources

## Operation
### Determining Configurations to Combine
`config_builder` uses [`platformdirs`](https://pypi.org/project/platformdirs/)
to find the OS-specific location of configuration files for an application.
Existing configuration files are loaded in order. Settings from each extend or
replace settings found in previous files.

Settings are loaded in the following order, where `application` is the name
(if any) supplied by the caller. Except where otherwise noted, the file
name in each directory is from the `config_name` parameter:

* If the `base_config` parameter is a dict, the configuration it specifies.
* If, instead, `base_config` is a string, the file it points to. (This is an explicit path to the file.)
* One or more files in system-wide application configuration directories as determined by `platformdirs.site_config_dir(application, multipath=True`).
* A file in the user-specific application configuration file as determined by `platformdirs.user_config_dir(application)`.
* If running in a virtual environment, a file in the `$VIRTUAL_ENV/config/application` directory.
* Finally, a file explicitly mentioned by the `overrides` parameter.

Note that the first two items allow the application to specify application-specific
defaults. The virtual environment case supports settings specific to a virtual
environment, perhaps for testing. And the last allows for special-case overrides.

### Update Process
As each partial configuration is loaded, its dict is used to recursively updates
in the previously assembled configuration.

For each `latest` dict loaded from a file, the `prev` dict is updated as follows:

For each `key` in `latest.keys()`:
* If `prev[key]` and `latest[key]` are both dicts, then recursively update `prev[key]` from `latest[key]`.
* Otherwise, set `prev[key]` to `latest[key]`, even if `latest[key]` is None.

## Usage
```python
config = config_builder(config_name: str,
                        application: str = None,
                        base_config: Union[dict, str] = None,
                        overrides: str = None
                       )

```
Where:
* `config_name` (mandatory) is the name of the configuration file to look for in each directory.
* `base_config` (optional) specifies a default configurations for the application. It can be either the absolute path to a configuration file to load, or a dict with the default configuration.
* `application` (optional) is an application name to use with `plataformdirs`.
* `overrides`(optional) is the full pathname of a file that overrides any settings found earlier. This can be use for, for example, testing.
