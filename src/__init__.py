import config_builder

class LoadConfigException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

def load_config(config_name: str, **kwargs):
    return config_builder.load_config(str, **kwargs)