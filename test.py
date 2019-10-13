from sand_codex.worker import Worker
import docker

client = docker.from_env()
worker = Worker(client, "sandcodex_worker_python", command='python codes/{0}/code.py {1}')
worker.launch()
a = worker.exec("""
import sys
print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))
""", ['test', 'test'])
print(a)