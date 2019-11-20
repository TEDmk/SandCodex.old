from .mock.fake_docker_client import fake_client
from sand_codex.worker import Worker


def test_worker_return():
    fake = fake_client({
        "exec_start.return_value": (
            b"test",
            b"test"
        )
    })
    worker = Worker(fake, "test", "test")
    worker.start()
    output = worker.exec('test')
    expected_output = "testtest"
    assert expected_output == output
