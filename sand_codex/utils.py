import tarfile
import time
from io import BytesIO
from contextlib import contextmanager
from sand_codex.exceptions import TimeoutException
import signal


def text_to_tar_stream(text: str, name: str):
    tar_stream = BytesIO()
    tar = tarfile.TarFile(fileobj=tar_stream, mode="w")
    file = text.encode("utf8")
    tarinfo = tarfile.TarInfo(name=name)
    tarinfo.size = len(file)
    tarinfo.mtime = time.time()
    tar.addfile(tarinfo, BytesIO(file))
    tar.close()
    tar_stream.seek(0)
    return tar_stream
