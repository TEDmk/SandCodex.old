from sand_codex import SandCodex
import docker
import logging

logging.basicConfig(format=FORMAT)

sand_codex = SandCodex({
        "Python3": {
            "image": "sandcodex_worker_python:latest",
            "command": "python codes/{0}/code.py {1}"
        },
    }, log_level=logging.DEBUG)
