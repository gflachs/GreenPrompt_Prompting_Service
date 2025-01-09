import logging
import sys

class Logger:
    def __init__(self, filename=None):
        if filename is None:
            # Log to console
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s"
            )
        else:
            logging.basicConfig(
                filename=filename,  
                filemode="w",        
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s"
            )

    def info(self, message):
        logging.info(message)
    
    def error(self, message):
        logging.error(message)
        
    def warning(self, message):
        logging.warning(message)
        
    def debug(self, message):
        logging.debug(message)
        

file_logger = Logger("./logs/llm_registry.log")
console_logger = Logger()