import logging
import sys
from datetime import datetime

class DailyLogger:
    
    def __init__(self, log_dir="app/log"):
        self.log_dir = log_dir
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def make_log(self, info):
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_filename = f"{self.log_dir}/log_{current_date}.log"

        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(log_filename, mode='a')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(info)
        self.logger.removeHandler(file_handler)