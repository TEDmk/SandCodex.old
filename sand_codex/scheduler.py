from sand_codex.worker import Worker
import docker
import logging


class Scheduler:
    def __init__(
        self,
        name: str,
        docker_client: docker.client.DockerClient,
        image: str,
        command: str,
        log_level: int = logging.NOTSET,
    ):
        self.name = name
        self.client = docker_client
        self.worker_list = []
        self.image = image
        self.command = command
        self.logger = logging.getLogger(f"sc.scheduler.{self.name}")
        self.logger.setLevel(log_level)
        self.log_level = log_level
        self.stop = False

    def start(self):
        self._add_worker()
        while not self.stop():
            pass

    def _add_worker(self):
        worker = Worker(client=self.client, image=self.image, command=self.command)
        self.logger.info(f"Add new worker: {worker}")
        worker.start()
        self.worker_list.append(worker)

    def _delete_worker(self):
        worker = self.worker.pop()
        self.logger.info(f"Delete worker: {worker}")
        worker.kill()

    def exit(self):
        self.logger.info(f"Exiting {self.name} scheduler")
        self.stop = True
        self.logger.info(f"Delete alls {len(self.worker_list)} worker(s)")
        for worker in self.worker_list:
            worker.kill()
        self.logger.debug(f"Close scheduler")
