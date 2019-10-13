import docker
import uuid
from sand_codex.exceptions import ContainerException
from sand_codex.utils import text_to_tar_stream, timeout_func
import asyncio
import time


class Worker:

    def __init__(self, client: docker.client.DockerClient, image: str, command: str):
        "Initialize Worker"
        self.id = uuid.uuid4()
        self.image = image
        self.client = client
        self.container = None
        self.command = command
        self.active_exec = 0

    def launch(self):
        self.container = self.client.containers.run(image=self.image, detach=True, network_mode='none', name=self.id)

    def exec(self, code, arguments=[], timeout=10):
        if not self.up:
            raise ContainerException(f'[Worker {self.id}]Can\'t exec "{command}", the container is not up.')
        self.active_exec += 1
        try:
            code_id = uuid.uuid4()
            tar_stream = text_to_tar_stream(code, name='code.py')
            self.container.exec_run(f'mkdir -p codes/{code_id}')
            self.container.put_archive(path=f'/home/worker/codes/{code_id}', data=tar_stream)
            code, stream = self.container.exec_run(self.command.format(code_id, " ".join(arguments)), stream=True)
            ret = ""
            with timeout_func(timeout):
                for line in stream:
                    ret += line.decode()
            self.container.exec_run(f'rm -rf codes/{code_id}')
        except Exception as e:
            raise e
        finally:
            self.active_exec -= 1
        return ret
        
    def kill(self):
        i = 0
        while self.active_exec != 0 or i > 60:
            time.sleep(1)
        self.container.kill()

    @property
    def up(self):
        if not self.container:
            return False
        return self.container.status == "created"
