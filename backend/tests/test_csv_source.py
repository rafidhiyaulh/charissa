import pytest

from charissa.data.csv_source import load_csv
from charissa.executor.docker_executor import DockerExecutor


@pytest.fixture
def executor():
    ex = DockerExecutor()
    yield ex
    ex.close()


def test_load_csv_creates_dataframe(tmp_path, executor):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text("product,amount\napple,3\nbanana,5\n")

    result = load_csv(executor, str(csv_path))

    assert result["traceback"] == ""
    assert "apple" in result["stdout"]

    followup = executor.run("print(len(sales))")
    assert followup["stdout"].strip() == "2"
