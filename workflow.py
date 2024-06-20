import yaml

class Workflow:
    def __init__(self, name):
        self.name = name

    @staticmethod
    def load_config(config_file):
        return yaml.load(config_file, Loader=yaml.SafeLoader)['workflows']
