import concurrent.futures
import io
import json
import os
import tarfile
import time

import docker

_IMAGE_NAME = "charissa-sandbox"
_DOCKERFILE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docker")
_SOCKET_PATH = "/tmp/sandbox.sock"
_DATA_DIR = "/data"


def _docker_client() -> docker.DockerClient:
    if os.environ.get("DOCKER_HOST"):
        return docker.from_env()
    for candidate in (os.path.expanduser("~/.docker/run/docker.sock"), "/var/run/docker.sock"):
        if os.path.exists(candidate):
            return docker.DockerClient(base_url=f"unix://{candidate}")
    return docker.from_env()


class DockerExecutor:
    """Runs Python code inside an isolated, network-disabled container, one per session.

    State (variables) persists across `run()` calls within the same instance:
    a single long-lived Python process inside the container holds the namespace,
    and each `run()` talks to it via `docker exec` over a unix socket local to
    the container (no published ports, no container-to-internet access).
    """

    def __init__(self):
        self._client = _docker_client()
        self._client.images.build(path=_DOCKERFILE_DIR, dockerfile="sandbox.Dockerfile", tag=_IMAGE_NAME)
        self._container = self._client.containers.run(
            _IMAGE_NAME,
            detach=True,
            mem_limit="512m",
            network_disabled=True,
        )
        self._wait_for_socket()

    def _wait_for_socket(self, retries: int = 50):
        for _ in range(retries):
            exit_code, _ = self._container.exec_run(["test", "-S", _SOCKET_PATH])
            if exit_code == 0:
                return
            time.sleep(0.1)
        raise RuntimeError("sandbox container did not become ready")

    def run(self, code: str, timeout: float = 10.0) -> dict:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                self._container.exec_run,
                ["python", "/sandbox_client.py", code],
            )
            try:
                exit_code, output = future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                return {"stdout": "", "traceback": f"execution timed out after {timeout}s"}
        return json.loads(output.decode())

    def upload_bytes(self, data: bytes, filename: str) -> str:
        """Copies bytes into the container's /data dir. Returns the in-container path."""
        self._container.exec_run(["mkdir", "-p", _DATA_DIR])
        tar_buffer = io.BytesIO()
        with tarfile.TarFile(fileobj=tar_buffer, mode="w") as tar:
            info = tarfile.TarInfo(name=filename)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        tar_buffer.seek(0)
        self._container.put_archive(_DATA_DIR, tar_buffer)
        return f"{_DATA_DIR}/{filename}"

    def close(self):
        self._container.stop(timeout=1)
        self._container.remove()
