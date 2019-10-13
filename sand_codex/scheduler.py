from sand_codex.worker import Worker
import docker


class Scheduler:

    def __init__(self, image: str, command: str):
        self.client = docker.from_env()
        self.worker_list = []
        self.image = image
        self.command = command

    def _add_worker(self):
        worker = Worker(client=self.client, image=self.image, command=self.command)
        worker.launch()
        self.worker_list.append(worker)

    def _delete_worker(self):
        worker = self.worker.pop()
        worker.kill()
