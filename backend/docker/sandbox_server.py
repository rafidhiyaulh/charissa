import contextlib
import io
import json
import os
import socketserver
import traceback

_SOCKET_PATH = "/tmp/sandbox.sock"
_globals = {"__name__": "__main__"}


def run_code(code: str) -> dict:
    stdout = io.StringIO()
    result = {"stdout": "", "traceback": ""}
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, _globals)
    except Exception:
        result["traceback"] = traceback.format_exc()
    result["stdout"] = stdout.getvalue()
    return result


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for line in self.rfile:
            request = json.loads(line)
            response = run_code(request["code"])
            self.wfile.write((json.dumps(response) + "\n").encode())


if __name__ == "__main__":
    if os.path.exists(_SOCKET_PATH):
        os.remove(_SOCKET_PATH)
    with socketserver.UnixStreamServer(_SOCKET_PATH, Handler) as server:
        os.chmod(_SOCKET_PATH, 0o777)
        server.serve_forever()
