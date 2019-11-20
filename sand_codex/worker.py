import docker
import time
import logging
import uuid
import threading
from enum import Enum
from sand_codex.exceptions import ContainerException
from sand_codex.utils import text_to_tar_stream


class Status(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    ERROR = 2
    TIMEOUT = 3
    DONE = 4


class Worker:
    def __init__(
        self,
        client: docker.client.DockerClient,
        image: str,
        command: str,
        max_execs: int = 3,
        timeout_kill: int = 60,
        delta_time: float = 0.5,
        log_level: int = logging.NOTSET,
    ):
        "Initialize Worker"
        self.id = uuid.uuid4()
        self.image = image
        self.client = client
        self.container = None
        self.command = command
        self.logger = logging.getLogger(f"sc.worker.{self.id}")
        self.logger.setLevel(log_level)
        self.log_level = log_level
        self._execs = {}
        self.timeout_kill = timeout_kill
        self.delta_time = delta_time

    def start(self):
        self.container = self.client.containers.run(
            image=self.image, detach=True, network_mode="none", name=self.id
        )

    def exec(self, code, arguments=[], timeout: int = 10):
        code_id = uuid.uuid4()
        thread = threading.Thread(target=self._exec, args=(code_id, code, arguments))
        self._execs[code_id] = {
            "command": self.command.format(
                uuid=code_id, parameters=" ".join(arguments)
            ),
            "thread": thread,
            "return": "",
            "status": Status.NOT_STARTED,
            "start_time": time.time(),
            "duration": None,
            "timeout": timeout,
        }
        thread_timeout = threading.Thread(target=self._timeout_handler, args=(code_id,))
        thread.start()
        thread_timeout.start()
        return code_id

    def _timeout_handler(self, code_id):
        self._check_code_id(code_id)
        time.sleep(self._execs[code_id]["timeout"])
        if self._execs[code_id]["status"] not in [Status.ERROR, Status.DONE]:
            killed = self._kill_from_command(self._execs[code_id]["command"])
            if killed:
                self._execs[code_id]["status"] = Status.TIMEOUT

    def _exec(self, code_id: str, code: str, arguments=[]):
        self._check_code_id(code_id)
        self._check_up()
        try:
            tar_stream = text_to_tar_stream(code, name="code.py")
            self.container.exec_run(f"mkdir -p codes/{code_id}")
            self.container.put_archive(
                path=f"/home/worker/codes/{code_id}", data=tar_stream
            )
            command = self._execs[code_id]["command"]
            return_code, stream = self.container.exec_run(command, stream=True)
            self._execs[code_id]["status"] = Status.RUNNING
            ret = ""
            for line in stream:
                if isinstance(line, bytes):
                    self._execs[code_id]["return"] += line.decode()
            self.container.exec_run(f"rm -rf codes/{code_id}")
            self._execs[code_id]["status"] = Status.DONE
        except Exception as e:
            self._execs[code_id]["status"] = Status.ERROR
            message = f"Error catched: {e}"
            self.logger.error(message)
            raise e
        finally:
            self._execs[code_id]["duration"] = (
                time.time() - self._execs[code_id]["start_time"]
            )
        return ret

    def get_info(self, code_id):
        self._check_code_id(code_id)
        return {
            k: v
            for (k, v) in self._execs[code_id].items()
            if k in ["status", "return", "start_time", "duration"]
        }

    def get_sync_info(
        self, code_id, wait_for=[Status.ERROR, Status.DONE, Status.TIMEOUT]
    ):
        self._check_code_id(code_id)
        while self.get_info(code_id)["status"] not in wait_for:
            time.sleep(self.delta_time)
        return self.get_info(code_id)

    def _kill_from_command(self, command):
        pid = self._pid_from_command(command)
        if not pid:
            return False
        self._check_up()
        code, res = self.container.exec_run(f"kill {pid}")
        if code == 0:
            return True
        else:
            return False

    def _pid_from_command(self, command):
        self._check_up()
        code, res = self.container.exec_run(f"ps -o pid -o args")
        if code != 0:
            message = f"ps command doesn't work '{res}'"
            self.logger.error(message)
            raise ContainerException(message)
        lines = res.decode().split("\n")
        for line in lines:
            fields = line.split()
            if command.strip() == str(" ".join(fields[1:])):
                return fields[0]
        return False

    def kill(self):
        if self.up:
            self.container.kill()

    def _check_up(self):
        if not self.up:
            message = (
                f"[Worker {self.id}] Can't do this action, the container is not up."
            )
            self.logger.error(message)
            raise ContainerException(message)

    def _check_code_id(self, code_id):
        if code_id not in self._execs:
            message = f"This codeID doesn't exist"
            self.logger.error(message)
            raise ContainerException(message)

    @property
    def up(self):
        if not self.container:
            return False
        return self.container.status == "created" or self.container.status == "running"
