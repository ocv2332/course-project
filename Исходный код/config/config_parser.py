from configparser import SafeConfigParser

section_names = 'urls', 'codes', 'messages', 'errors', 'values', 'paths', 'headers', 'stylesheets'


class ConfigParser:
    def __init__(self, filepath):
        parser = SafeConfigParser()
        found = parser.read(filepath, encoding="utf-8")
        if not found:
            raise FileNotFoundError("No config file found")
        for name in section_names:
            self.__dict__.update(parser.items(name))
