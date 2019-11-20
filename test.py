from sand_codex import SandCodex, Worker
from sand_codex.worker import Status
import logging
import docker
import time


# logging.basicConfig(
#     format='[%(levelname)s] %(asctime)s - %(name)s :: %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     level=logging.DEBUG)

docker_client = docker.from_env()

# sand_codex = SandCodex(docker_client, {
#         "schedulers": {
#             "Python3": {
#                 "image": "sandcodex_worker_python:latest",
#                 "command": "python codes/{uuid}/code.py {parameters}"
#             },
#         },
#         "configuration": {
#             "minimum_workers": 3,
#             "default_timeout": 10,
#         },
#     }, log_level=logging.DEBUG)


# with open("example.py", "r") as f:
#     text = f.read()
#     run_id = sand_codex.run("Python3", text)

w = Worker(
    client=docker_client,
    image="sandcodex_worker_python:latest",
    command="python codes/{uuid}/code.py {parameters}",
)


w.start()
i = w.exec(
    "from random import choice; print(''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789%^*(-_=+)') for i in range(15)]));import time; time.sleep(4)",
)
print(w.get_sync_info(i))
