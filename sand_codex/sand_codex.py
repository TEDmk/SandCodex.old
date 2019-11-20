import logging
import docker
from sand_codex.exceptions import ParametersException
from sand_codex.scheduler import Scheduler


class SandCodex:
    def __init__(
        self,
        docker_client: docker.client.DockerClient,
        config: dict,
        log_level: int = logging.NOTSET,
    ):
        self.log_level = log_level
        self.logger = logging.getLogger("sandcodex")
        self.logger.setLevel(log_level)
        self.logger.info("Initializing SandCodex")
        self.client = docker_client
        self.log_level = log_level
        self.config = config
        self.schedulers = {}
        self.actions = {}
        self._set_schedulers()

    def _set_schedulers(self):
        if "schedulers" not in self.config:
            raise ParametersException("'schedulers' is not specified in config")
        if not isinstance(self.config["schedulers"], dict):
            raise ParametersException("config['schedulers'] should be a dict")
        for name, config in self.config["schedulers"].items():
            self.schedulers[name] = Scheduler(
                name, self.client, config["image"], config["command"], self.log_level
            )
            self.logger.info(f"Scheduler '{name}' added")

    def exit(self):
        for name, scheduler in self.schedulers:
            scheduler.exit()
