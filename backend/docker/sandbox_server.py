import contextlib
import io
import json
import socketserver
import traceback

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
    with socketserver.ThreadingTCPServer(("0.0.0.0", 8765), Handler) as server:
        server.serve_forever()
