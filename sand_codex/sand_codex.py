import logging


class SandCodex:
    def __init__(self, scheduler_config: dict, log_level: int = logging.NOTSET):
        self.log_level = log_level
        self.scheduler_config = scheduler_config
        self.schedulers = {}
        self.logger = logging.getLogger("sandcodex")
        self.logger.setLevel(log_level)
        self.logger.info("Init SandCodex")
