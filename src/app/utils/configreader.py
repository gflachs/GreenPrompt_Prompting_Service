import configparser
from typing import List, Tuple, Any

class ConfigReader:
    _instance = None
    
    @staticmethod
    def get_instance():
        if ConfigReader._instance is None:
            ConfigReader._instance = ConfigReader()
        return ConfigReader._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigReader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the config reader with a default configuration file."""
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

    def get(self, section: str, option: str) -> str:
        """Retrieve a value from the configuration file.

        Args:
            section (str): The section in the config file.
            option (str): The option within the section.

        Returns:
            str: The value of the specified option.
        """
        return self.config.get(section, option)