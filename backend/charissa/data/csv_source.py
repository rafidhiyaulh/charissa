import re

from charissa.executor.docker_executor import DockerExecutor


def clean_varname(name: str) -> str:
    name = re.sub(r"\W", "_", name)
    return f"_{name}" if name[0].isdigit() else name


def load_csv(executor: DockerExecutor, local_path: str, varname: str | None = None) -> dict:
    """Uploads a local CSV into the sandbox and loads it into a pandas DataFrame."""
    with open(local_path, "rb") as f:
        data = f.read()

    filename = local_path.split("/")[-1]
    if varname is None:
        varname = clean_varname(filename.rsplit(".", 1)[0])

    container_path = executor.upload_bytes(data, filename)
    code = f"import pandas as pd\n{varname} = pd.read_csv('{container_path}')\nprint({varname}.head())"
    return executor.run(code)
